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
    BASE_URL = "https://www.amo.on.ca/careers"

    async def scrape(self, client: httpx.AsyncClient) -> List[MunicipalElectionPostings]:
        postings: List[MunicipalElectionPostings] = []
        try:
            res = await client.get(self.BASE_URL, headers=self.headers, timeout=self.timeout)
            if res.status_code != 200:
                return []

            soup = BeautifulSoup(res.text, "html.parser")
            job_rows = soup.select(".views-row, .job-item, article")
            
            for row in job_rows:
                text = row.get_text(" ", strip=True)
                if not any(kw in text.lower() for kw in ["election", "returning officer", "dro", "poll clerk", "voting"]):
                    continue

                title_elem = row.select_one("h2 a, h3 a, .views-field-title a, a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")
                full_url = f"https://www.amo.on.ca{href}" if href.startswith("/") else href

                # Employer / Municipality
                employer_elem = row.select_one(".views-field-field-employer, .field--name-field-employer")
                muni_name = employer_elem.get_text(strip=True) if employer_elem else "Ontario Municipality"

                roles = extract_roles_from_content(title + "\n" + text)
                if not roles:
                    roles = [ElectionRole(title=title, role_category="POLL_WORKER")]

                posting_id = hashlib.md5(f"AMO_{muni_name}_{title}".encode()).hexdigest()
                postings.append(MunicipalElectionPostings(
                    id=posting_id,
                    municipality=muni_name,
                    region_or_county="Ontario",
                    election_portal_url=self.BASE_URL,
                    apply_url=full_url,
                    status="Accepting Applications",
                    election_date="October 26, 2026",
                    roles=roles,
                    raw_text_snippet=text[:300]
                ))

        except Exception:
            pass

        return postings
