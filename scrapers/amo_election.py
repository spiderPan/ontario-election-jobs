"""
Scraper for the Association of Municipalities of Ontario (AMO) job board for election roles.
"""
import hashlib
from typing import List
import httpx
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from models import MunicipalElectionPostings, ElectionRole
from utils.election_parser import extract_roles_from_content, parse_status_from_text


class AMOMunicipalElectionScraper(BaseScraper):
    BASE_URL = "https://jobs.amo.on.ca/"

    async def scrape(self, client: httpx.AsyncClient) -> List[MunicipalElectionPostings]:
        postings: List[MunicipalElectionPostings] = []
        try:
            res = await self.safe_get(client, self.BASE_URL)
            if not res or res.status_code != 200:
                return []

            soup = BeautifulSoup(res.text, "html.parser")
            job_rows = soup.select(".c-job-card, article.js-job-card, .job-item, .views-row")
            
            for row in job_rows:
                text = row.get_text(" ", strip=True)
                if not any(kw in text.lower() for kw in ["election", "returning officer", "dro", "poll clerk", "voting"]):
                    continue

                title_elem = row.select_one(".c-job-card__title, h2 a, h3 a, a")
                if not title_elem:
                    continue

                title = title_elem.get_text(" ", strip=True).replace("Position:", "").strip()
                link = row.find("a", href=True)
                href = link["href"] if link else ""
                full_url = f"https://jobs.amo.on.ca{href}" if href.startswith("/") else href

                # Employer / Municipality
                org_elem = row.select_one(".c-job-card__organization, .field--name-field-employer")
                muni_name = org_elem.get_text(" ", strip=True).replace("Organization:", "").strip() if org_elem else "Ontario Municipality"

                roles = extract_roles_from_content(title + "\n" + text)
                if not roles:
                    roles = [ElectionRole(title=title, role_category="POLL_WORKER")]

                posting_id = hashlib.md5(f"AMO_{muni_name}_{title}".encode()).hexdigest()
                postings.append(MunicipalElectionPostings(
                    id=posting_id,
                    municipality=muni_name,
                    region_or_county="Ontario",
                    election_portal_url=self.BASE_URL,
                    apply_url=full_url or self.BASE_URL,
                    status="Accepting Applications",
                    election_date="October 26, 2026",
                    is_verified_2026=True,
                    roles=roles,
                    raw_text_snippet=text[:300]
                ))

        except Exception:
            pass

        return postings
