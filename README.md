# Ontario Municipal Election 2026 - Poll Worker Jobs Crawler

A specialized web crawler and data aggregator designed specifically for **Ontario Municipal Election Poll Worker Jobs** for the **2026 Ontario Municipal Elections** (Voting Day: **Monday, October 26, 2026**).

---

## Key Features

- **Targeted Role Extraction**: Scrapes and parses specific election positions:
  - **Deputy Returning Officer (DRO)**
  - **Voting Location Supervisor (VLS) / Supervisory Returning Officer (SRO)**
  - **Poll Clerk / Ballot Clerk / Tabulator Operator**
  - **Information Assistant / Greeter / Line Monitor**
  - **Revision Officer / Registration Clerk**
  - **Youth / Student Election Worker** (ages 16–17)
  - **Election Logistics / Count Center Worker**
- **Compensation & Honorarium Parsing**: Normalizes day rates (e.g. `$280/day`), hourly rates (e.g. `$22.50/hr`), and mandatory training stipends (e.g. `$50`).
- **Grouped by Municipality**: Data is structured and organized cleanly by City / Town / Township.
- **Application Portal & Form Links**: Captures direct links to online application forms, PDFs, and contact emails.
- **Multi-Source Ingestion**:
  1. Dedicated Municipal Election Portals (e.g., `toronto.ca/elections`, `mississaugavotes.ca`, `hamilton.ca/elections`)
  2. Enterprise ATS Queries (Workday / Dayforce / Taleo)
  3. AMO (Association of Municipalities of Ontario) Centralized Job Board

---

## Quick Start

### 1. Installation

```bash
git clone <YOUR_REPO_URL>
cd ontario-election-jobs-crawler
pip install -r requirements.txt
```

### 2. Run the Crawler

Crawl all configured Ontario municipal election portals:
```bash
python3 main.py crawl
```

Crawl a specific municipality or region:
```bash
python3 main.py crawl --muni "Mississauga"
python3 main.py crawl --muni "Toronto"
python3 main.py crawl --muni "York"
```

### 3. View Results in Terminal

List all positions grouped by municipality with rich interactive tables:
```bash
python3 main.py list
python3 main.py list --muni "Ottawa"
```

### 4. Show Statistics & Pay Benchmarks

```bash
python3 main.py stats
```

### 5. Export Data

Generate fresh exports in JSON, CSV, and Markdown:
```bash
python3 main.py export
```

Exported files will be generated in `data/`:
- `data/election_jobs_by_municipality.json` — Grouped JSON structure
- `data/election_jobs.csv` — Flat spreadsheet of all roles
- `data/election_jobs_report.md` — Markdown summary report
- `data/election_jobs.db` — SQLite database

---

## 🌐 GitHub Pages & Automated Nightly Scraping

This repository includes a pre-configured GitHub Actions workflow in [`.github/workflows/nightly-crawl.yml`](.github/workflows/nightly-crawl.yml) that:
1. **Runs every night at 04:00 UTC** (Midnight EDT / 11:00 PM EST) via cron schedule.
2. **Cuts a fresh crawl** across all Ontario municipal portals and regenerates JSON, CSV, and Markdown datasets.
3. **Commits and pushes** updated data back to the repository automatically.
4. **Deploys the static web app** (`index.html`, `analytics.html`, and `data/`) directly to **GitHub Pages**.

### Setting up GitHub Pages

1. Create a repository on GitHub (e.g. `ontario-election-jobs-crawler`).
2. Push this codebase:
   ```bash
   git remote add origin git@github.com:<YOUR_USERNAME>/ontario-election-jobs-crawler.git
   git branch -M main
   git push -u origin main
   ```
3. In your GitHub repository:
   - Go to **Settings** > **Pages**.
   - Under **Build and deployment** > **Source**, select **GitHub Actions**.
   - Go to **Settings** > **Actions** > **General** > **Workflow permissions**, and select **Read and write permissions** (to allow data updates to be committed).
4. The workflow will automatically run and publish your site at `https://<YOUR_USERNAME>.github.io/ontario-election-jobs-crawler/`.

---

## Adding New Municipalities

Edit `data/election_portals.json` to add additional Ontario townships or cities:

```json
{
  "municipality": "Town of Oakville",
  "region": "Halton",
  "tier": "Lower-tier",
  "type": "html_portal",
  "election_url": "https://www.oakville.ca/town-hall/elections/working-at-an-election/",
  "apply_url": "https://www.oakville.ca/town-hall/elections/working-at-an-election/",
  "contact_email": "elections@oakville.ca"
}
```
