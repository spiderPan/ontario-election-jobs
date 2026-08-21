"""
Parser for Ontario Municipal Election worker roles, compensation, stipends, and requirements.
Strictly extracts officially published pay rates. If unstated, pay is marked as NOT_AVAILABLE / null.
"""
import re
from typing import List, Tuple, Optional, Dict
from models import ElectionRole

ROLE_DEFINITIONS = [
    {
        "category": "SUPERVISOR",
        "title": "Voting Location Supervisor / Supervisory Returning Officer",
        "patterns": [
            r"Voting Location Supervisor", r"Voting Place Supervisor",
            r"Supervisory Returning Officer", r"\bSRO\b", r"\bVLS\b",
            r"Poll Supervisor", r"Area Supervisor", r"Site Supervisor"
        ],
        "default_min_age": 18,
        "description": "Supervises overall voting place operations and election personnel. Resolves voter inquiries, oversees optical scan tabulators/ballot security, coordinates poll opening and closing, and liaises directly with the Municipal Clerk."
    },
    {
        "category": "DRO",
        "title": "Deputy Returning Officer (DRO)",
        "patterns": [
            r"Deputy Returning Officer", r"\bDRO\b", r"Deputy Returning Officers"
        ],
        "default_min_age": 18,
        "description": "Administers statutory declarations and oaths, issues official ballots to qualified electors, maintains ballot box custody, operates tabulators, protects elector secrecy, and reconciles ballot accounting tallies at poll close."
    },
    {
        "category": "CLERK",
        "title": "Poll Clerk / Ballot Clerk / Tabulator Operator",
        "patterns": [
            r"Tabulator Operator", r"Tabulator Clerk", r"Ballot Clerk",
            r"Poll Clerk", r"Voting Clerk", r"Election Clerk"
        ],
        "default_min_age": 18,
        "description": "Greets electors, checks names against the official Voters' List, verifies acceptable voter identification under the Municipal Elections Act, maintains the poll record, and guides voters to tabulators."
    },
    {
        "category": "GREETER",
        "title": "Information Assistant / Greeter / Line Monitor",
        "patterns": [
            r"Information Assistant", r"Greeter", r"Line Monitor",
            r"Line Management", r"Customer Service Assistant", r"Entrance Greeter"
        ],
        "default_min_age": 16,
        "description": "Welcomes electors at facility entrances, checks voter information cards, directs voters to appropriate voting tables, assists electors requiring accessibility accommodations, and maintains organized queue lines."
    },
    {
        "category": "REVISION",
        "title": "Revision Officer / Voter Registration Clerk",
        "patterns": [
            r"Revision Officer", r"Voter Registration Official",
            r"Registration Clerk", r"Revisions Clerk", r"Voters List Clerk"
        ],
        "default_min_age": 18,
        "description": "Processes voter list additions, corrections, and address updates. Verifies proof of identity and residency, administers declarations of qualifications, and issues official Certificates to Vote."
    },
    {
        "category": "STUDENT",
        "title": "Youth / Student Election Worker",
        "patterns": [
            r"Youth Election Worker", r"Student Election Worker",
            r"Youth Ambassador", r"High School Election Assistant"
        ],
        "default_min_age": 16,
        "description": "Assists election staff with greeting electors, wayfinding, accessibility support, and general election day logistics. Open to high school students aged 16-17 looking for civic engagement experience."
    }
]

DAY_RATE_PATTERN = re.compile(
    r'\$\s*([0-9]{2,4}(?:\.[0-9]{2})?)\s*(?:/(?:day|shift|flat|honorarium)|per\s*(?:day|shift|voting\s*day)|honorarium|flat\s*rate|for\s*the\s*day)',
    re.IGNORECASE
)
HOURLY_PATTERN = re.compile(
    r'\$\s*([0-9]{2}(?:\.[0-9]{2})?)\s*(?:/(?:hr|hour)|per\s*hour|hourly|\s*an\s*hour)',
    re.IGNORECASE
)
TRAINING_PATTERN = re.compile(
    r'\$\s*([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:for\s*(?:mandatory\s*)?training|training\s*(?:rate|fee|stipend|allowance|pay))',
    re.IGNORECASE
)
SHIFT_PATTERN = re.compile(
    r'([0-1]?[0-9](?::[0-9]{2})?\s*(?:am|pm|a\.m\.|p\.m\.)\s*(?:to|-|–)\s*[0-1]?[0-9](?::[0-9]{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
    re.IGNORECASE
)
AGE_PATTERN = re.compile(r'at\s*least\s*([0-9]{2})\s*years\s*of\s*age|([0-9]{2})\s*\+\s*years\s*old|minimum\s*age\s*of\s*([0-9]{2})', re.IGNORECASE)


def parse_status_from_text(text: str) -> str:
    lower = text.lower()
    if any(p in lower for p in ["applications are now closed", "recruitment closed", "no longer accepting applications"]):
        return "Closed"
    if any(p in lower for p in ["applications will open", "recruitment will begin", "portal opening soon"]):
        return "Opening Soon"
    return "Accepting Applications"


def extract_requirements(text: str) -> List[str]:
    reqs = []
    lower = text.lower()
    if "canadian citizen" in lower or "legally entitled to work in canada" in lower:
        reqs.append("Legally entitled to work in Canada / Canadian Citizen or PR")
    if "18 years" in lower:
        reqs.append("At least 18 years of age (16+ for youth roles)")
    elif "16 years" in lower:
        reqs.append("At least 16 years of age")
    if "neutral" in lower or "political neutrality" in lower or "campaign" in lower:
        reqs.append("Must remain politically neutral and not active on candidate campaigns")
    if "training" in lower:
        reqs.append("Must attend mandatory paid training session prior to Election Day")
    return reqs


def extract_roles_from_content(text: str) -> List[ElectionRole]:
    """Extract roles and only set pay when explicitly published."""
    found_roles: List[ElectionRole] = []
    seen_categories = set()

    blocks = [b.strip() for b in re.split(r'\n{2,}|\r\n\r\n', text) if len(b.strip()) > 20]

    for block in blocks:
        for role_def in ROLE_DEFINITIONS:
            cat = role_def["category"]
            if cat in seen_categories:
                continue

            matched = any(re.search(pat, block, re.IGNORECASE) for pat in role_def["patterns"])
            if matched:
                seen_categories.add(cat)
                
                day_match = DAY_RATE_PATTERN.search(block)
                hourly_match = HOURLY_PATTERN.search(block)
                training_match = TRAINING_PATTERN.search(block)
                shift_match = SHIFT_PATTERN.search(block)
                age_match = AGE_PATTERN.search(block)
                
                training_pay = f"${training_match.group(1)}" if training_match else None
                shift_hours = shift_match.group(1) if shift_match else "Voting Day (8:30 AM - 9:00 PM)"
                
                min_age = role_def["default_min_age"]
                if age_match:
                    found_age = next((g for g in age_match.groups() if g), None)
                    if found_age:
                        min_age = int(found_age)

                pay_type = "DAY_RATE"

                if day_match:
                    pay_actual_amount = float(day_match.group(1))
                    pay_actual_raw = f"${pay_actual_amount:g}/day"
                    pay_status = "ACTUAL_PUBLISHED"
                    pay_notes = "Published on official municipal portal"
                elif hourly_match:
                    pay_actual_amount = float(hourly_match.group(1))
                    pay_actual_raw = f"${pay_actual_amount:g}/hour"
                    pay_type = "HOURLY"
                    pay_status = "ACTUAL_PUBLISHED"
                    pay_notes = "Published on official municipal portal"
                else:
                    pay_actual_amount = None
                    pay_actual_raw = None
                    pay_status = "NOT_AVAILABLE"
                    pay_notes = "Rate not yet published by municipality"

                desc = role_def.get("description")

                found_roles.append(ElectionRole(
                    title=role_def["title"],
                    role_category=cat,
                    pay_status=pay_status,
                    pay_actual_raw=pay_actual_raw,
                    pay_actual_amount=pay_actual_amount,
                    pay_source_notes=pay_notes,
                    pay_type=pay_type,
                    training_pay=training_pay,
                    hours_or_shift=shift_hours,
                    description=desc,
                    min_age=min_age
                ))

    # Baseline fallback if specific roles weren't split in page text
    if not found_roles:
        for cat, title, min_age in [
            ("DRO", "Deputy Returning Officer (DRO)", 18),
            ("SUPERVISOR", "Voting Location Supervisor (VLS)", 18),
            ("GREETER", "Information Assistant / Greeter", 16)
        ]:
            role_meta = next((r for r in ROLE_DEFINITIONS if r["category"] == cat), {})
            found_roles.append(ElectionRole(
                title=title,
                role_category=cat,
                pay_status="NOT_AVAILABLE",
                pay_actual_raw=None,
                pay_actual_amount=None,
                pay_source_notes="Rate not yet published by municipality",
                pay_type="DAY_RATE",
                hours_or_shift="8:30 AM - 9:00 PM on October 26, 2026",
                description=role_meta.get("description", "Ontario Municipal Poll Worker Position"),
                min_age=min_age
            ))

    return found_roles
