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
        "title": "Voting Location Supervisor / Supervisory Returning Officer / MDRO",
        "patterns": [
            r"Voting Location Supervisor", r"Voting Place Supervisor",
            r"Supervisory Returning Officer", r"Supervising Deputy Returning Officer",
            r"\bSRO\b", r"\bSDRO\b", r"\bVLS\b", r"\bVPS\b",
            r"Managing Deputy Returning Officer", r"\bMDRO\b",
            r"Location Supervisor", r"Assistant Location Supervisor",
            r"^Poll Supervisor", r"Area Supervisor", r"Site Supervisor"
        ],
        "default_min_age": 18,
        "description": "Supervises overall voting place operations and election personnel. Resolves voter inquiries, oversees optical scan tabulators/ballot security, coordinates poll opening and closing, and liaises directly with the Municipal Clerk."
    },
    {
        "category": "DRO",
        "title": "Deputy Returning Officer (DRO)",
        "patterns": [
            r"Deputy Returning Officer", r"\bDRO\b", r"Deputy Returning Officers",
            r"Revision DRO", r"Express DRO", r"Residence Care DRO", r"Ballot Deputy Returning Officer", r"Ballot DRO"
        ],
        "default_min_age": 18,
        "description": "Administers statutory declarations and oaths, issues official ballots to qualified electors, maintains ballot box custody, operates tabulators, protects elector secrecy, and reconciles ballot accounting tallies at poll close."
    },
    {
        "category": "TECH",
        "title": "Tabulator Operator / Machine Operator",
        "patterns": [
            r"Tabulator Operator", r"Tabulator Clerk", r"Tabulator DRO", r"Tabulator Officer", r"Tabulator Assistant",
            r"\bTDRO\b", r"\bTA\b", r"Machine Operator", r"Technical Support"
        ],
        "default_min_age": 18,
        "description": "Sets up, tests, and operates electronic ballot tabulators at voting places. Troubleshoots ballot feed issues and assists voters in inserting ballots securely into tabulators."
    },
    {
        "category": "CLERK",
        "title": "Poll Clerk / Ballot Clerk / Election Assistant",
        "patterns": [
            r"Ballot Clerk", r"Poll Clerk", r"Voting Clerk", r"Election Clerk",
            r"Ballot Officer", r"Election Assistant", r"Standby"
        ],
        "default_min_age": 18,
        "description": "Greets electors, checks names against the official Voters' List, verifies acceptable voter identification under the Municipal Elections Act, maintains the poll record, and guides voters to tabulators."
    },
    {
        "category": "GREETER",
        "title": "Information Officer / Greeter / Access Officer / Line Monitor",
        "patterns": [
            r"Information Assistant", r"Information Officer", r"Greeter", r"Line Monitor",
            r"Line Management", r"Customer Service Assistant", r"Customer Service Officer",
            r"Entrance Greeter", r"Access Officer", r"Voter Assistance Officer", r"Demonstrator"
        ],
        "default_min_age": 16,
        "description": "Welcomes electors at facility entrances, checks voter information cards, directs voters to appropriate voting tables, assists electors requiring accessibility accommodations, and maintains organized queue lines."
    },
    {
        "category": "REVISION",
        "title": "Registration Officer / Revision Officer",
        "patterns": [
            r"Revision Officer", r"Registration Officer", r"Voter Registration Official",
            r"Registration Clerk", r"Revision Clerk", r"Revisions Clerk", r"Voters List Clerk",
            r"Revising Officer", r"Revising Deputy Returning Officer", r"Revising DRO"
        ],
        "default_min_age": 18,
        "description": "Processes voter list additions, corrections, and address updates. Verifies proof of identity and residency, administers declarations of qualifications, and issues official Certificates to Vote."
    },
    {
        "category": "STUDENT",
        "title": "Youth / Student Election Worker",
        "patterns": [
            r"Youth Election Worker", r"Student Election Worker",
            r"Youth Ambassador", r"High School Election Assistant", r"Youth Worker"
        ],
        "default_min_age": 16,
        "description": "Assists election staff with greeting electors, wayfinding, accessibility support, and general election day logistics. Open to high school students aged 16-17 looking for civic engagement experience."
    }
]

DAY_RATE_EXPLICIT = re.compile(
    r'(?:(?:pay(?:\s*rates?)?|rate\s*(?:of\s*pay)?|compensation|honorarium|fee)\s*(?:for\s*(?:this\s*)?(?:position|election\s*day\s*worked))?\s*(?:is|:)?\s*|[-–—]\s*)\$([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)(?:\s*(?:–|-|to)\s*\$?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?))?',
    re.IGNORECASE
)
ELECTION_DAY_RATE = re.compile(
    r'election\s*day\s*:\s*\$([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)',
    re.IGNORECASE
)
DAY_RATE_SUFFIX = re.compile(
    r'\$([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\s*(?:/(?:day|shift|flat|honorarium)|per\s*(?:day|shift|voting\s*day|election\s*day)|honorarium|flat\s*rate|lump\s*sum|for\s*(?:mandatory\s*)?training|for\s*(?:election|voting)\s*day|for\s*the\s*day|\(covers\s*[^)]+\)|inclusive\s*of\s*training)',
    re.IGNORECASE
)
HOURLY_PATTERN = re.compile(
    r'(?:[-–—:]\s*)?\$([0-9]{2}(?:\.[0-9]{2})?)\s*(?:/(?:hr|hour)|per\s*hour|hourly|\s*an\s*hour|\(hourly\s*rate\))',
    re.IGNORECASE
)
TRAINING_PATTERN = re.compile(
    r'\$([0-9]{2,3}(?:\.[0-9]{2})?)\s*(?:for\s*(?:mandatory\s*)?training|training\s*(?:rate|fee|stipend|allowance|pay))',
    re.IGNORECASE
)
SHIFT_PATTERN = re.compile(
    r'([0-1]?[0-9](?::[0-9]{2})?\s*(?:am|pm|a\.m\.|p\.m\.)\s*(?:to|-|–)\s*[0-1]?[0-9](?::[0-9]{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
    re.IGNORECASE
)
AGE_PATTERN = re.compile(r'at\s*least\s*([0-9]{2})\s*years\s*of\s*age|([0-9]{2})\s*\+\s*years\s*old|minimum\s*age\s*of\s*([0-9]{2})', re.IGNORECASE)


def parse_status_from_text(text: str) -> str:
    lower = text.lower()
    if any(p in lower for p in [
        "applications are now closed", "recruitment closed", "no longer accepting applications",
        "recruitment has now closed", "recruitment for the 2026", "recruitment is now closed",
        "applications are closed", "applications closed", "we are no longer accepting",
        "recruitment for this election has ended", "full and no longer available"
    ]):
        return "Closed"
    if any(p in lower for p in ["applications will open", "recruitment will begin", "portal opening soon", "recruitment opening"]):
        return "Opening Soon"
    if any(p in lower for p in [
        "accepting applications", "applications are open", "apply online today",
        "complete your application online", "now accepting applications", "applications now open"
    ]):
        return "Accepting Applications"
    return "Information Portal"


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
    """Extract roles and accurately capture officially published pay rates."""
    found_roles: List[ElectionRole] = []

    # Smart chunking by headings or role patterns as well as blank lines
    role_all_patterns = [p for rd in ROLE_DEFINITIONS for p in rd["patterns"]]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    blocks = []
    current_block = []
    for line in lines:
        is_role_heading = any(re.search(rf'^(?:###?\s*|[-•*]\s*)?{p}', line, re.IGNORECASE) for p in role_all_patterns)
        if is_role_heading and current_block:
            blocks.append('\n'.join(current_block))
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append('\n'.join(current_block))

    # Also include standard double-newline blocks if long text was provided
    if len(blocks) <= 1:
        blocks = [b.strip() for b in re.split(r'\n{2,}|\r\n\r\n', text) if len(b.strip()) > 20]

    roles_by_cat: Dict[str, ElectionRole] = {}

    for block in blocks:
        for role_def in ROLE_DEFINITIONS:
            cat = role_def["category"]

            first_line = block.split('\n')[0] if '\n' in block else block
            matched = any(
                re.search(pat, first_line, re.IGNORECASE) or 
                (len(block) < 800 and re.search(pat, block, re.IGNORECASE)) 
                for pat in role_def["patterns"]
            )
            if matched:
                day_explicit = DAY_RATE_EXPLICIT.search(block)
                election_day_match = ELECTION_DAY_RATE.search(block)
                day_suffix = DAY_RATE_SUFFIX.search(block)
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
                pay_actual_amount = None
                pay_actual_raw = None
                pay_status = "NOT_AVAILABLE"
                pay_notes = "Rate not yet published by municipality"

                if election_day_match:
                    amt_str = election_day_match.group(1).replace(',', '')
                    pay_actual_amount = float(amt_str)
                    pay_actual_raw = f"${pay_actual_amount:g}/day"
                    if hourly_match:
                        pay_actual_raw += f" (${hourly_match.group(1)}/hr advance)"
                    pay_status = "ACTUAL_PUBLISHED"
                    pay_notes = "Published on official municipal portal"
                elif day_explicit:
                    amt_str = day_explicit.group(1).replace(',', '')
                    pay_actual_amount = float(amt_str)
                    range_str = day_explicit.group(2).replace(',', '') if len(day_explicit.groups()) > 1 and day_explicit.group(2) else None
                    if range_str:
                        pay_actual_raw = f"${pay_actual_amount:g} - ${float(range_str):g}"
                    else:
                        pay_actual_raw = f"${pay_actual_amount:g}/day"
                    pay_status = "ACTUAL_PUBLISHED"
                    pay_notes = "Published on official municipal portal"
                elif day_suffix:
                    amt_str = day_suffix.group(1).replace(',', '')
                    pay_actual_amount = float(amt_str)
                    pay_actual_raw = f"${pay_actual_amount:g}/day"
                    pay_status = "ACTUAL_PUBLISHED"
                    pay_notes = "Published on official municipal portal"
                elif hourly_match:
                    pay_actual_amount = float(hourly_match.group(1))
                    pay_actual_raw = f"${pay_actual_amount:g}/hour"
                    pay_type = "HOURLY"
                    pay_status = "ACTUAL_PUBLISHED"
                    pay_notes = "Published on official municipal portal"

                desc = role_def.get("description")

                role_obj = ElectionRole(
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
                )

                if cat not in roles_by_cat:
                    roles_by_cat[cat] = role_obj
                elif roles_by_cat[cat].pay_status == "NOT_AVAILABLE" and role_obj.pay_status == "ACTUAL_PUBLISHED":
                    roles_by_cat[cat] = role_obj

    found_roles = list(roles_by_cat.values())

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
