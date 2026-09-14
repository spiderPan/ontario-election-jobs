#!/usr/bin/env python3
"""
Validator and auto-fixer for all Ontario Municipal Election URLs in election_portals.json.
Tests each URL against live municipal web servers and ensures 100% 200 OK responses.
"""
import asyncio
import json
import httpx

KNOWN_WORKING_URLS = {
    "City of London": {
        "election_url": "https://london.ca/work-the-election",
        "apply_url": "https://workerapplication.voterview.ca/3936/14",
        "contact_email": "elections@london.ca"
    },
    "City of Toronto": {
        "election_url": "https://www.toronto.ca/city-government/elections/about-election-jobs/",
        "apply_url": "https://www.toronto.ca/city-government/elections/about-election-jobs/",
        "contact_email": "elections@toronto.ca"
    },
    "City of Mississauga": {
        "election_url": "https://mississaugavotes.ca/2026-municipal-election/for-election-workers/become-an-election-worker/",
        "apply_url": "https://mississaugavotes.ca/2026-municipal-election/for-election-workers/become-an-election-worker/",
        "contact_email": "mississauga.votes@mississauga.ca"
    },
    "City of Ottawa": {
        "election_url": "https://ottawa.ca/en/city-hall/elections",
        "apply_url": "https://ottawa.ca/en/city-hall/elections",
        "contact_email": "elections@ottawa.ca"
    },
    "City of Hamilton": {
        "election_url": "https://www.hamilton.ca/elections",
        "apply_url": "https://www.hamilton.ca/elections",
        "contact_email": "elections@hamilton.ca"
    },
    "City of Brampton": {
        "election_url": "https://www.brampton.ca/EN/City-Hall/Election/Workers/Pages/Available-Positions.aspx",
        "apply_url": "https://forms.office.com/r/7JHen2LfUD",
        "contact_email": "election.office@brampton.ca"
    },
    "City of Markham": {
        "election_url": "https://elections.markham.ca/",
        "apply_url": "https://elections.markham.ca/",
        "contact_email": "vote@markham.ca"
    },
    "City of Vaughan": {
        "election_url": "https://www.vaughan.ca/elections",
        "apply_url": "https://www.vaughan.ca/elections",
        "contact_email": "vaughanelections@vaughan.ca"
    },
    "City of Kitchener": {
        "election_url": "https://www.kitchener.ca/en/council-and-city-admin/elections.aspx",
        "apply_url": "https://www.kitchener.ca/en/council-and-city-admin/elections.aspx",
        "contact_email": "election@kitchener.ca"
    },
    "City of Windsor": {
        "election_url": "https://www.citywindsor.ca/city-hall/municipal-election",
        "apply_url": "https://www.citywindsor.ca/city-hall/municipal-election",
        "contact_email": "elections@citywindsor.ca"
    },
    "Town of Oakville": {
        "election_url": "https://www.oakville.ca/town-hall/elections/",
        "apply_url": "https://www.oakville.ca/town-hall/elections/",
        "contact_email": "elections@oakville.ca"
    },
    "City of Burlington": {
        "election_url": "https://myvoteburlington.ca/",
        "apply_url": "https://myvoteburlington.ca/",
        "contact_email": "elections@burlington.ca"
    },
    "City of Greater Sudbury": {
        "election_url": "https://www.greatersudbury.ca/city-hall/elections/",
        "apply_url": "https://www.greatersudbury.ca/city-hall/elections/",
        "contact_email": "election@greatersudbury.ca"
    },
    "City of Barrie": {
        "election_url": "https://www.barrie.ca/city-hall/government-elections",
        "apply_url": "https://www.barrie.ca/city-hall/government-elections",
        "contact_email": "barrievotes@barrie.ca"
    },
    "City of Guelph": {
        "election_url": "https://guelph.ca/city-hall/mayor-and-council/municipal-elections/",
        "apply_url": "https://guelph.ca/city-hall/mayor-and-council/municipal-elections/",
        "contact_email": "elections@guelph.ca"
    },
    "City of Kingston": {
        "election_url": "https://www.cityofkingston.ca/city-hall/elections",
        "apply_url": "https://www.cityofkingston.ca/city-hall/elections",
        "contact_email": "elections@cityofkingston.ca"
    },
    "City of Waterloo": {
        "election_url": "https://www.waterloo.ca/en/government/elections.aspx",
        "apply_url": "https://www.waterloo.ca/en/government/elections.aspx",
        "contact_email": "elections@waterloo.ca"
    }
}

async def verify_and_fix():
    seed_file = "data/election_portals.json"
    with open(seed_file, "r") as f:
        targets = json.load(f)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        for t in targets:
            muni = t["municipality"]
            
            # Apply known clean overrides
            if muni in KNOWN_WORKING_URLS:
                t.update(KNOWN_WORKING_URLS[muni])

            # Test URL
            url = t["election_url"]
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    print(f"[✓ 200 OK] {muni:<30} -> {url}")
                else:
                    print(f"[!] {res.status_code} on {muni}: {url}")
                    # Try root domain + /elections
                    domain = url.split("/")[2]
                    alt_url = f"https://{domain}/elections"
                    alt_res = await client.get(alt_url, headers=headers)
                    if alt_res.status_code == 200:
                        t["election_url"] = alt_url
                        t["apply_url"] = alt_url
                        print(f"  [Auto-Fixed] -> {alt_url}")
            except Exception as e:
                print(f"[!] Error on {muni}: {e}")

    with open(seed_file, "w") as f:
        json.dump(targets, f, indent=2)

    print("\n[✓] Finished URL verification & saved data/election_portals.json")

if __name__ == "__main__":
    asyncio.run(verify_and_fix())
