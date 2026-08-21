"""
Scraper for municipal election portals with strict 2026 validation and confirmed actual pay integration.
"""
import re
import hashlib
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from models import MunicipalElectionPostings, ElectionRole
from utils.election_parser import (
    extract_roles_from_content,
    parse_status_from_text,
    extract_requirements
)
from utils.freshness_filter import validate_2026_freshness
from utils.verified_rates import CONFIRMED_ACTUAL_RATES

EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
PHONE_REGEX = re.compile(r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}')


class HtmlPortalScraper(BaseScraper):
    def __init__(self, target_config: Dict[str, Any], timeout: float = 20.0):
        super().__init__(timeout=timeout)
        self.config = target_config
        self.municipality = target_config["municipality"]
        self.region = target_config.get("region")
        self.tier = target_config.get("tier", "Single-tier / Lower-tier")
        self.election_url = target_config["election_url"]
        self.apply_url = target_config.get("apply_url", self.election_url)
        self.known_email = target_config.get("contact_email")

    async def scrape_single(self, client: httpx.AsyncClient) -> Optional[MunicipalElectionPostings]:
        try:
            res = await self.safe_get(client, self.election_url)
            if res is None or res.status_code != 200:
                return None

            soup = BeautifulSoup(res.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                tag.decompose()

            # Find main content
            main_content = (
                soup.find("main") or 
                soup.find("div", id=re.compile(r'content|main|article', re.I)) or 
                soup.find("div", class_=re.compile(r'content|main|body|page-content', re.I)) or 
                soup
            )

            text = main_content.get_text("\n", strip=True)

            # Strict 2026 Freshness check
            is_valid_2026, reason, yr = validate_2026_freshness(text, str(res.url))
            if not is_valid_2026:
                return None

            status = parse_status_from_text(text)

            # Check if this municipality has confirmed, verified actual rates
            if self.municipality in CONFIRMED_ACTUAL_RATES:
                confirmed_info = CONFIRMED_ACTUAL_RATES[self.municipality]
                roles = []
                for r in confirmed_info["roles"]:
                    role_meta = next((dr for dr in ROLE_DEFINITIONS if dr["category"] == r["category"]), {})
                    desc = r.get("description") or role_meta.get("description", f"Official 2026 election position for {self.municipality}.")
                    roles.append(ElectionRole(
                        title=r["title"],
                        role_category=r["category"],
                        pay_status="ACTUAL_PUBLISHED",
                        pay_actual_raw=r["pay_actual_raw"],
                        pay_actual_amount=r["pay_actual_amount"],
                        pay_source_notes=f"Actual rate: {r['notes']}",
                        pay_type=r["pay_type"],
                        training_pay=r["training_pay"],
                        hours_or_shift=r["hours_or_shift"],
                        min_age=r["min_age"],
                        description=desc
                    ))
            else:
                # Parse or model benchmark estimate
                roles = extract_roles_from_content(text)

            # Detect Apply Link and whether a direct application form is live
            apply_link = str(res.url)
            has_direct_apply = False

            for a_tag in main_content.find_all("a", href=True):
                href = a_tag["href"]
                link_text = a_tag.get_text(strip=True).lower()
                if any(kw in link_text for kw in ["apply now", "application form", "submit application", "work at the election", "work with us", "apply online", "online application"]):
                    apply_link = urljoin(self.election_url, href)
                    has_direct_apply = True
                    break
                elif any(domain in href.lower() for domain in ["forms.office.com", "docs.google.com/forms", "formstack.com", "surveymonkey.com", "myworkdayjobs.com", "dayforcehcm.com"]):
                    apply_link = href
                    has_direct_apply = True
                    break

            if not has_direct_apply and self.apply_url and self.apply_url != self.election_url:
                apply_link = self.apply_url
                has_direct_apply = True

            if not has_direct_apply and status == "Accepting Applications":
                status = "Information Portal"

            reqs = extract_requirements(text)
            if not reqs:
                reqs = [
                    "Legally entitled to work in Canada",
                    "At least 18 years of age (16+ for youth roles)",
                    "Politically neutral and not active on 2026 municipal candidate campaigns",
                    "Available for training session and Voting Day on October 26, 2026"
                ]

            found_email = self.known_email
            email_match = EMAIL_REGEX.search(text)
            if email_match and not found_email:
                found_email = email_match.group(1)

            phone_match = PHONE_REGEX.search(text)
            found_phone = phone_match.group(0) if phone_match else None

            snippet = " ".join(text[:400].split())
            posting_id = hashlib.md5(f"{self.municipality}_2026".encode()).hexdigest()

            return MunicipalElectionPostings(
                id=posting_id,
                municipality=self.municipality,
                region_or_county=self.region,
                municipal_tier=self.tier,
                election_portal_url=str(res.url),
                apply_url=apply_link,
                has_direct_apply=has_direct_apply,
                status=status,
                election_date="October 26, 2026",
                advance_voting_dates="October 2026",
                is_verified_2026=True,
                requirements=reqs,
                roles=roles,
                contact_email=found_email,
                contact_phone=found_phone,
                raw_text_snippet=snippet
            )

        except Exception:
            return None

    async def scrape(self, client: httpx.AsyncClient) -> List[MunicipalElectionPostings]:
        item = await self.scrape_single(client)
        return [item] if item else []
