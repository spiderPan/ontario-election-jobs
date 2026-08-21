"""
Data models for Ontario municipal election worker postings with strict separation between ACTUAL published data and ESTIMATED analytical benchmarks.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ElectionRole(BaseModel):
    title: str = Field(description="Role title (e.g. Deputy Returning Officer, Voting Location Supervisor)")
    role_category: str = Field(default="POLL_WORKER", description="Category: SUPERVISOR, DRO, CLERK, GREETER, LOGISTICS, TECH")
    
    # STRICT SEPARATION: Actual vs Estimated
    pay_status: str = Field(default="HONORARIUM_UNPUBLISHED", description="ACTUAL_PUBLISHED | ESTIMATED_BENCHMARK | HONORARIUM_UNPUBLISHED")
    pay_is_estimated: bool = Field(default=False, description="True if value is an analytical estimate, False if actual published text")
    pay_actual_raw: Optional[str] = Field(default=None, description="Exact dollar amount scraped from page, or None if unstated")
    pay_actual_amount: Optional[float] = Field(default=None, description="Numeric parsed dollar amount strictly from page text")
    pay_estimated_amount: Optional[float] = Field(default=None, description="Analytical benchmark estimate based on municipal staffing policy")
    pay_source_notes: str = Field(default="Live municipal page", description="Explanation of pay data origin")
    
    pay_type: str = Field(default="UNKNOWN", description="DAY_RATE, HOURLY, HONORARIUM, or UNKNOWN")
    training_pay: Optional[str] = Field(default=None, description="Stipend or rate for mandatory training sessions")
    hours_or_shift: Optional[str] = Field(default=None, description="Shift timing, e.g. '8:30 AM - 9:00 PM on October 26, 2026'")
    description: Optional[str] = Field(default=None, description="Role responsibilities and key tasks")
    min_age: Optional[int] = Field(default=18, description="Minimum age requirement (typically 16 or 18)")


class MunicipalElectionPostings(BaseModel):
    id: str = Field(description="Unique hash or slug for the municipal election posting")
    municipality: str = Field(description="Name of the municipality (e.g. City of London, City of Toronto)")
    region_or_county: Optional[str] = Field(default=None, description="Region/County (e.g. Middlesex, Peel, York)")
    municipal_tier: Optional[str] = Field(default="Single-tier / Lower-tier", description="Single-tier or Lower-tier")
    election_portal_url: str = Field(description="URL to the municipality's official 2026 election portal")
    apply_url: str = Field(description="Direct link to election worker application form or portal")
    status: str = Field(default="Accepting Applications", description="Status: 'Accepting Applications', 'Opening Soon', 'Closed'")
    election_date: str = Field(default="October 26, 2026", description="General Voting Day")
    advance_voting_dates: Optional[str] = Field(default=None, description="Dates for advance polls if specified")
    is_verified_2026: bool = Field(default=True, description="Strict verification that content is from 2026 election cycle")
    requirements: List[str] = Field(default_factory=list, description="General eligibility requirements")
    roles: List[ElectionRole] = Field(default_factory=list, description="List of specific election roles available")
    contact_email: Optional[str] = Field(default=None, description="Election office contact email")
    contact_phone: Optional[str] = Field(default=None, description="Election office phone number")
    raw_text_snippet: Optional[str] = Field(default=None, description="Key snippet extracted from the page")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
