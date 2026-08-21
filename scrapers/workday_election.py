"""
Scraper for municipalities utilizing Workday ATS for election positions.
"""
import hashlib
from typing import List, Dict, Any, Optional
import httpx

from scrapers.base import BaseScraper
from models import MunicipalElectionPostings, ElectionRole
from utils.election_parser import extract_roles_from_content, parse_status_from_text


class WorkdayElectionScraper(BaseScraper):
    def __init__(self, target_config: Dict[str, Any], timeout: float = 25.0):
        super().__init__(timeout=timeout)
        self.config = target_config
        self.municipality = target_config["municipality"]
        self.region = target_config.get("region")
        self.tier = target_config.get("tier", "Single-tier / Lower-tier")
        self.domain = target_config.get("wday_domain", "wd3.myworkdayjobs.com")
        self.tenant = target_config.get("wday_tenant")
        self.client_id = target_config.get("wday_client_id")
        self.portal_url = target_config.get("election_url")

    async def scrape(self, client: httpx.AsyncClient) -> List[MunicipalElectionPostings]:
        if not self.tenant or not self.client_id:
            return []

        cxs_base = f"https://{self.domain}/wday/cxs/{self.tenant}/{self.client_id}"
        site_base = f"https://{self.domain}/en-US/{self.client_id}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.headers["User-Agent"]
        }

        roles: List[ElectionRole] = []
        apply_url = self.portal_url

        try:
            for kw in ["election", "dro", "poll"]:
                payload = {
                    "appliedFacets": {},
                    "limit": 10,
                    "offset": 0,
                    "searchText": kw
                }
                res = await client.post(f"{cxs_base}/jobs", json=payload, headers=headers, timeout=self.timeout)
                if res.status_code != 200:
                    continue

                data = res.json()
                for item in data.get("jobPostings", []):
                    title = item.get("title", "")
                    path = item.get("externalPath", "")
                    job_url = f"{site_base}/job{path}"
                    apply_url = job_url

                    # Detail call
                    detail_res = await client.get(f"{cxs_base}/job{path}", headers=headers, timeout=self.timeout)
                    desc = ""
                    if detail_res.status_code == 200:
                        desc = detail_res.json().get("jobPostingInfo", {}).get("jobDescription", "")

                    parsed_roles = extract_roles_from_content(title + "\n" + desc)
                    if parsed_roles:
                        roles.extend(parsed_roles)
                    else:
                        roles.append(ElectionRole(
                            title=title,
                            role_category="DRO" if "DRO" in title.upper() else "POLL_WORKER",
                            description=desc[:300] if desc else "Workday Election Staff Posting"
                        ))

            if not roles:
                return []

            posting_id = hashlib.md5(f"{self.municipality}_workday_2026".encode()).hexdigest()
            return [MunicipalElectionPostings(
                id=posting_id,
                municipality=self.municipality,
                region_or_county=self.region,
                municipal_tier=self.tier,
                election_portal_url=self.portal_url,
                apply_url=apply_url,
                has_direct_apply=True,
                status="Accepting Applications",
                election_date="October 26, 2026",
                roles=roles,
                requirements=["Legally entitled to work in Canada", "Must attend mandatory training session"]
            )]

        except Exception as e:
            return []
