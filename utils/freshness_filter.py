"""
Strict 2026 election freshness filter.
Filters out any historical postings from past cycles (e.g. 2022, 2018) that lack 2026 currency.
"""
import re
from typing import Tuple, Optional

YEAR_2026_REGEX = re.compile(r'\b2026\b|october\s*26(?:th)?\s*,?\s*2026|oct\.?\s*26\s*,?\s*2026', re.IGNORECASE)
HISTORICAL_YEARS_REGEX = re.compile(r'\b(2022|2018|2014|2010)\b', re.IGNORECASE)
PAST_ELECTION_DATES = re.compile(r'october\s*24\s*,?\s*2022|october\s*22\s*,?\s*2018', re.IGNORECASE)


def validate_2026_freshness(text: str, url: str) -> Tuple[bool, str, Optional[str]]:
    """
    Returns (is_valid_2026, reason, detected_year).
    Only returns True if the content is verified for the 2026 municipal election cycle.
    """
    if not text:
        return False, "Empty page content", None

    has_2026 = bool(YEAR_2026_REGEX.search(text)) or bool(YEAR_2026_REGEX.search(url))
    has_historical = bool(HISTORICAL_YEARS_REGEX.search(text))
    has_past_dates = bool(PAST_ELECTION_DATES.search(text))

    if has_2026:
        return True, "Verified 2026 election content", "2026"
    
    if has_past_dates or (has_historical and not has_2026):
        # Stale content from 2022 or earlier
        matched_hist = HISTORICAL_YEARS_REGEX.search(text)
        hist_year = matched_hist.group(1) if matched_hist else "Historical"
        return False, f"Out of date: Refers to {hist_year} election cycle and lacks 2026 update", hist_year

    # If neither 2026 nor historical years are explicitly mentioned, check if it is active generic election portal
    lower = text.lower()
    if any(kw in lower for kw in ["elections", "municipal election", "voters list", "candidate nomination", "work at an election"]):
        # Generic election portal without year tag -> mark as unconfirmed/stale if strictly 2026 requested
        return False, "Unconfirmed: No 2026 year tag found", None

    return False, "No active election content found", None
