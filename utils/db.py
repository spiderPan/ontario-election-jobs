"""
Database persistence and query engine with strict Actual vs Estimated pay separation.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import MunicipalElectionPostings, ElectionRole


class ElectionJobDatabase:
    def __init__(self, db_path: str = "data/election_jobs.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Postings Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS municipal_postings (
                    id TEXT PRIMARY KEY,
                    municipality TEXT UNIQUE NOT NULL,
                    region_or_county TEXT,
                    municipal_tier TEXT,
                    election_portal_url TEXT NOT NULL,
                    apply_url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    election_date TEXT DEFAULT 'October 26, 2026',
                    advance_voting_dates TEXT,
                    is_verified_2026 INTEGER DEFAULT 1,
                    requirements_json TEXT,
                    contact_email TEXT,
                    contact_phone TEXT,
                    raw_text_snippet TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Roles Table with Strict Actual vs Estimate Columns
            conn.execute("""
                CREATE TABLE IF NOT EXISTS election_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    posting_id TEXT NOT NULL,
                    municipality TEXT NOT NULL,
                    title TEXT NOT NULL,
                    role_category TEXT NOT NULL,
                    pay_status TEXT NOT NULL,
                    pay_is_estimated INTEGER NOT NULL,
                    pay_actual_raw TEXT,
                    pay_actual_amount REAL,
                    pay_estimated_amount REAL,
                    pay_source_notes TEXT,
                    pay_type TEXT,
                    training_pay TEXT,
                    hours_or_shift TEXT,
                    min_age INTEGER,
                    description TEXT,
                    FOREIGN KEY (posting_id) REFERENCES municipal_postings(id) ON DELETE CASCADE,
                    UNIQUE(posting_id, title)
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_muni_name ON municipal_postings(municipality)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_role_cat ON election_roles(role_category)")

    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM election_roles")
            conn.execute("DELETE FROM municipal_postings")

    def save_posting(self, posting: MunicipalElectionPostings):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            reqs_str = json.dumps(posting.requirements, ensure_ascii=False)
            
            conn.execute("""
                INSERT INTO municipal_postings (
                    id, municipality, region_or_county, municipal_tier,
                    election_portal_url, apply_url, status, election_date,
                    advance_voting_dates, is_verified_2026, requirements_json,
                    contact_email, contact_phone, raw_text_snippet, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    municipality=excluded.municipality,
                    region_or_county=excluded.region_or_county,
                    election_portal_url=excluded.election_portal_url,
                    apply_url=excluded.apply_url,
                    status=excluded.status,
                    is_verified_2026=excluded.is_verified_2026,
                    requirements_json=excluded.requirements_json,
                    contact_email=excluded.contact_email,
                    contact_phone=excluded.contact_phone,
                    raw_text_snippet=excluded.raw_text_snippet,
                    scraped_at=excluded.scraped_at
            """, (
                posting.id, posting.municipality, posting.region_or_county,
                posting.municipal_tier, posting.election_portal_url, posting.apply_url,
                posting.status, posting.election_date, posting.advance_voting_dates,
                1 if posting.is_verified_2026 else 0, reqs_str, posting.contact_email,
                posting.contact_phone, posting.raw_text_snippet, posting.scraped_at.isoformat()
            ))

            conn.execute("DELETE FROM election_roles WHERE posting_id = ?", (posting.id,))

            for role in posting.roles:
                conn.execute("""
                    INSERT INTO election_roles (
                        posting_id, municipality, title, role_category,
                        pay_status, pay_is_estimated, pay_actual_raw,
                        pay_actual_amount, pay_estimated_amount, pay_source_notes,
                        pay_type, training_pay, hours_or_shift, min_age, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    posting.id, posting.municipality, role.title, role.role_category,
                    role.pay_status, 1 if role.pay_is_estimated else 0,
                    role.pay_actual_raw, role.pay_actual_amount, role.pay_estimated_amount,
                    role.pay_source_notes, role.pay_type, role.training_pay,
                    role.hours_or_shift, role.min_age, role.description
                ))

    def get_grouped_postings(self) -> Dict[str, Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM municipal_postings WHERE is_verified_2026 = 1 ORDER BY municipality ASC")
            postings_rows = cursor.fetchall()
            
            result = {}
            for p in postings_rows:
                p_id = p["id"]
                muni = p["municipality"]
                
                r_cursor = conn.execute("SELECT * FROM election_roles WHERE posting_id = ? ORDER BY id ASC", (p_id,))
                roles_rows = r_cursor.fetchall()
                
                reqs = []
                if p["requirements_json"]:
                    try:
                        reqs = json.loads(p["requirements_json"])
                    except Exception:
                        pass

                roles_list = []
                for r in roles_rows:
                    roles_list.append({
                        "title": r["title"],
                        "category": r["role_category"],
                        "pay_status": r["pay_status"],
                        "pay_is_estimated": bool(r["pay_is_estimated"]),
                        "pay_actual_raw": r["pay_actual_raw"],
                        "pay_actual_amount": r["pay_actual_amount"],
                        "pay_estimated_amount": r["pay_estimated_amount"],
                        "pay_source_notes": r["pay_source_notes"],
                        "pay_type": r["pay_type"],
                        "training_pay": r["training_pay"],
                        "hours_or_shift": r["hours_or_shift"],
                        "min_age": r["min_age"],
                        "description": r["description"]
                    })

                result[muni] = {
                    "municipality": muni,
                    "region": p["region_or_county"],
                    "tier": p["municipal_tier"],
                    "status": p["status"],
                    "election_date": p["election_date"],
                    "election_year": "2026",
                    "is_verified_2026": True,
                    "election_portal_url": p["election_portal_url"],
                    "apply_url": p["apply_url"],
                    "contact_email": p["contact_email"],
                    "contact_phone": p["contact_phone"],
                    "requirements": reqs,
                    "roles_count": len(roles_list),
                    "roles": roles_list,
                    "scraped_at": p["scraped_at"]
                }
            return result

    def get_all_roles_flat(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT 
                    m.municipality,
                    m.region_or_county as region,
                    m.status as municipal_status,
                    '2026' as election_year,
                    r.title as role_title,
                    r.role_category,
                    r.pay_status,
                    CASE WHEN r.pay_is_estimated = 1 THEN 'TRUE' ELSE 'FALSE' END as pay_is_estimated,
                    r.pay_actual_raw as pay_actual_published,
                    r.pay_actual_amount,
                    r.pay_estimated_amount as pay_modeled_estimate,
                    r.pay_source_notes,
                    r.pay_type,
                    r.training_pay,
                    r.hours_or_shift,
                    r.min_age,
                    m.apply_url,
                    m.election_portal_url
                FROM election_roles r
                JOIN municipal_postings m ON r.posting_id = m.id
                WHERE m.is_verified_2026 = 1
                ORDER BY m.municipality ASC, r.title ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            total_munis = conn.execute("SELECT COUNT(*) FROM municipal_postings WHERE is_verified_2026 = 1").fetchone()[0]
            total_roles = conn.execute("""
                SELECT COUNT(*) FROM election_roles r 
                JOIN municipal_postings m ON r.posting_id = m.id 
                WHERE m.is_verified_2026 = 1
            """).fetchone()[0]
            
            actual_count = conn.execute("""
                SELECT COUNT(*) FROM election_roles r 
                JOIN municipal_postings m ON r.posting_id = m.id 
                WHERE m.is_verified_2026 = 1 AND r.pay_is_estimated = 0 AND r.pay_actual_amount IS NOT NULL
            """).fetchone()[0]

            estimated_count = total_roles - actual_count

            return {
                "total_municipalities": total_munis,
                "total_roles": total_roles,
                "roles_with_actual_published_pay": actual_count,
                "roles_with_modeled_estimate": estimated_count,
                "election_year": "2026"
            }
