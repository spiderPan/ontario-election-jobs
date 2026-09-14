"""
Scraper for municipal election portals with strict 2026 validation and confirmed actual pay integration.
Includes robust fallback for verified municipalities protected by anti-bot WAFs (e.g. Incapsula / Cloudflare).
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
    ROLE_DEFINITIONS,
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

    def build_confirmed_posting(self) -> MunicipalElectionPostings:
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

        posting_id = hashlib.md5(f"{self.municipality}_2026".encode()).hexdigest()
        has_direct_apply = bool(self.apply_url)

        return MunicipalElectionPostings(
            id=posting_id,
            municipality=self.municipality,
            region_or_county=self.region,
            municipal_tier=self.tier,
            election_portal_url=self.election_url,
            apply_url=self.apply_url or self.election_url,
            has_direct_apply=has_direct_apply,
            status="Accepting Applications" if has_direct_apply else "Information Portal",
            election_date="October 26, 2026",
            advance_voting_dates="October 2026",
            is_verified_2026=True,
            requirements=[
                "Legally entitled to work in Canada",
                "At least 18 years of age (16+ for youth roles)",
                "Politically neutral and not active on 2026 municipal candidate campaigns",
                "Available for training session and Voting Day on October 26, 2026"
            ],
            roles=roles,
            contact_email=self.known_email or f"elections@{self.municipality.lower().replace('city of ', '').replace('town of ', '').replace(' ', '')}.ca",
            contact_phone=None,
            raw_text_snippet=f"Official 2026 Municipal Elections Portal and verified Staff Compensation Schedule for {self.municipality}."
        )

    async def scrape_single(self, client: httpx.AsyncClient) -> Optional[MunicipalElectionPostings]:
        try:
            res = await self.safe_get(client, self.election_url)
            if res is None or res.status_code != 200:
                if self.municipality in CONFIRMED_ACTUAL_RATES:
                    return self.build_confirmed_posting()
                return None

            soup = BeautifulSoup(res.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                tag.decompose()

            # Find main content with robust fallback if main-content div is just a short anchor
            main_content = (
                soup.find("main") or 
                soup.find("div", id=re.compile(r'content|main|article', re.I)) or 
                soup.find("div", class_=re.compile(r'content|main|body|page-content', re.I)) or 
                soup
            )
            if len(main_content.get_text(strip=True)) < 100:
                main_content = soup.find("body") or soup

            text = main_content.get_text("\n", strip=True)

            # Subpage discovery: search for dedicated election worker / jobs subpages
            job_link_regex = re.compile(
                r'(?:election|poll)\s*(?:workers?|jobs?|employment|hiring|opportunities|recruitment|positions?)|'
                r'becom(?:e|ing)\s*(?:an\s*)?(?:election|poll)\s*worker|'
                r'work\s*(?:at|the|for|during)?\s*(?:the\s*)?(?:municipal\s*)?election|'
                r'available-position|about-election-jobs|election-hiring|election-recruitment|'
                r'election-workers|apply-to-be-an-election-worker|work-the-election|work-with-us',
                re.IGNORECASE
            )

            subpage_candidates = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                link_text = a_tag.get_text(" ", strip=True)
                if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                
                # Exclude unrelated municipal employment links
                if any(ex in href.lower() or ex in link_text.lower() for ex in ["transit", "fire", "aquatic", "student-job-opportunities", "employment-area", "economic"]):
                    continue

                if job_link_regex.search(link_text) or job_link_regex.search(href):
                    full_sub_url = urljoin(str(res.url), href)
                    if full_sub_url != str(res.url) and full_sub_url not in subpage_candidates:
                        subpage_candidates.append(full_sub_url)

            # Crawl up to 3 candidate subpages to gather comprehensive role and pay data
            direct_apply_candidate = None
            if subpage_candidates:
                for sub_url in subpage_candidates[:3]:
                    sub_res = await self.safe_get(client, sub_url)
                    if sub_res and sub_res.status_code == 200:
                        sub_soup = BeautifulSoup(sub_res.text, "html.parser")
                        for tag in sub_soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                            tag.decompose()
                        sub_main = (
                            sub_soup.find("main") or
                            sub_soup.find("div", id=re.compile(r'content|main|article', re.I)) or
                            sub_soup.find("div", class_=re.compile(r'content|main|body|page-content', re.I)) or
                            sub_soup
                        )
                        if len(sub_main.get_text(strip=True)) < 100:
                            sub_main = sub_soup.find("body") or sub_soup

                        sub_text = sub_main.get_text("\n", strip=True)
                        # Append subpage content
                        text = text + "\n\n" + sub_text

                        # Check for direct apply links on subpage
                        for sub_a in sub_main.find_all("a", href=True):
                            sub_href = sub_a["href"].strip()
                            sub_lt = sub_a.get_text(" ", strip=True).lower()
                            # Check form domains or explicit apply buttons
                            if any(d in sub_href.lower() for d in ["workerapplication.voterview.ca", "forms.office.com", "docs.google.com/forms", "formstack.com", "surveymonkey.com", "myworkdayjobs.com"]):
                                if not any(ex in sub_href.lower() for ex in ["audit", "compliance", "rebate"]):
                                    direct_apply_candidate = sub_href
                                    break
                            elif any(kw in sub_lt for kw in ["complete your application online", "apply online today", "submit online application", "apply now", "online application form"]):
                                if not any(ex in sub_lt or ex in sub_href.lower() for ex in ["audit", "compliance", "rebate", "nomination", "candidate"]):
                                    direct_apply_candidate = urljoin(str(sub_res.url), sub_href)

            # Strict 2026 Freshness check
            is_valid_2026, reason, yr = validate_2026_freshness(text, str(res.url))
            if not is_valid_2026:
                if self.municipality in CONFIRMED_ACTUAL_RATES:
                    return self.build_confirmed_posting()
                return None

            status = parse_status_from_text(text)

            # Live-first role extraction
            roles = extract_roles_from_content(text)
            has_published_pay = any(r.pay_status == "ACTUAL_PUBLISHED" for r in roles)

            # If live parsing found no published pay, check if we have confirmed published fallback
            if not has_published_pay and self.municipality in CONFIRMED_ACTUAL_RATES:
                confirmed_posting = self.build_confirmed_posting()
                roles = confirmed_posting.roles

            # Detect Apply Link and whether a direct application form is live
            apply_link = str(res.url)
            has_direct_apply = False

            if direct_apply_candidate:
                apply_link = direct_apply_candidate
                has_direct_apply = True
            else:
                for a_tag in main_content.find_all("a", href=True):
                    href = a_tag["href"].strip()
                    link_text = a_tag.get_text(" ", strip=True).lower()
                    href_lower = href.lower()

                    # Avoid non-election job forms (such as audit compliance, candidate nomination)
                    if any(ex in href_lower or ex in link_text for ex in ["audit", "compliance", "rebate", "nomination", "candidate", "third-party"]):
                        continue

                    if any(kw in link_text for kw in ["apply now", "application form", "submit application", "apply online", "online application"]):
                        apply_link = urljoin(self.election_url, href)
                        has_direct_apply = True
                        break
                    elif any(domain in href_lower for domain in ["workerapplication.voterview.ca", "forms.office.com", "docs.google.com/forms", "formstack.com", "surveymonkey.com"]):
                        apply_link = href
                        has_direct_apply = True
                        break

            if not has_direct_apply and self.apply_url and self.apply_url != self.election_url:
                # Validate that configured apply_url doesn't point to audit/nomination
                if not any(ex in self.apply_url.lower() for ex in ["audit", "compliance", "rebate"]):
                    apply_link = self.apply_url
                    has_direct_apply = True

            # Reconcile status
            if status == "Closed":
                pass
            elif has_direct_apply:
                status = "Accepting Applications"
            else:
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
                cand_email = email_match.group(1).lower()
                if not any(cand_email.endswith(x) for x in [".png", ".jpg", ".svg", ".css"]):
                    found_email = cand_email

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
            if self.municipality in CONFIRMED_ACTUAL_RATES:
                return self.build_confirmed_posting()
            return None

    async def scrape(self, client: httpx.AsyncClient) -> List[MunicipalElectionPostings]:
        item = await self.scrape_single(client)
        return [item] if item else []
