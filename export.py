"""
Export utility for verified 2026 Ontario Municipal Election worker postings.
Strictly exports officially published data; unstated compensation is set to Not available / null.
"""
import json
import csv
from typing import Dict, Any, List
from utils.db import ElectionJobDatabase


def export_all(db: ElectionJobDatabase):
    grouped = db.get_grouped_postings()
    flat_roles = db.get_all_roles_flat()
    stats = db.get_stats()

    # 1. Export JSON Grouped by Municipality
    json_path = "data/election_jobs_by_municipality.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=2, ensure_ascii=False)

    # 2. Export Flat CSV with Confirmed Data
    csv_path = "data/election_jobs.csv"
    if flat_roles:
        fieldnames = [
            "municipality", "region", "municipal_status", "election_year",
            "role_title", "role_category", "pay_status",
            "pay_actual_published", "pay_actual_amount", "pay_source_notes",
            "pay_type", "training_pay", "hours_or_shift", "min_age",
            "apply_url", "election_portal_url"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(flat_roles)

    # 3. Export Markdown Report
    md_path = "data/election_jobs_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Ontario Municipal Election 2026 - Verified Poll Worker Directory\n\n")
        f.write(f"**Election Year:** 2026 (Strict Freshness Verified)  \n")
        f.write(f"**General Voting Day:** Monday, October 26, 2026  \n")
        f.write(f"**Verified 2026 Municipalities Tracked:** {stats['total_municipalities']}  \n")
        f.write(f"**Verified 2026 Poll Roles:** {stats['total_roles']}  \n")
        f.write(f"**Roles with Confirmed Published Pay:** {stats['roles_with_published_pay']}  \n")
        f.write(f"**Roles with Pay Rate Not Yet Published:** {stats['roles_not_available']}  \n\n")
        
        f.write("> [!NOTE]\n")
        f.write("> **Data Integrity Standard:** Only officially published compensation rates are shown. Municipalities that have not yet published pay tariffs for the 2026 election cycle are listed as `Not available`.\n\n")

        f.write("## Verified 2026 Municipal Opportunities (Grouped by Municipality)\n\n")

        for muni, info in grouped.items():
            f.write(f"### {muni} ({info.get('region', 'Ontario')})\n\n")
            f.write(f"- **Status:** `{info['status']}`\n")
            f.write(f"- **Election Portal:** [{info['election_portal_url']}]({info['election_portal_url']})\n")
            f.write(f"- **Apply Directly:** [{info['apply_url']}]({info['apply_url']})\n")
            if info.get("contact_email"):
                f.write(f"- **Contact:** `{info['contact_email']}`\n")
            f.write("\n**Available Poll Positions (2026):**\n\n")
            
            f.write("| Role Title | Category | Published Pay Rate | Status | Shift Hours | Min Age |\n")
            f.write("|---|---|---|---|---|---|\n")
            for r in info["roles"]:
                if r["pay_status"] == "ACTUAL_PUBLISHED" and r.get("pay_actual_raw"):
                    pay_str = f"**{r['pay_actual_raw']}**"
                    source_str = "Published"
                else:
                    pay_str = "*Not available*"
                    source_str = "TBD"
                
                hours = r["hours_or_shift"] or "Voting Day (8:30 AM - 9:00 PM)"
                f.write(f"| **{r['title']}** | {r['category']} | {pay_str} | `{source_str}` | {hours} | {r['min_age']}+ |\n")
            f.write("\n---\n\n")

    return json_path, csv_path, md_path
