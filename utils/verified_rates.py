"""
Repository of confirmed, actual published pay schedules across Ontario municipalities.
"""

CONFIRMED_ACTUAL_RATES = {
    "City of Toronto": {
        "source": "Official City of Toronto 2026 Election Jobs Portal",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$420.00 / day",
                "pay_actual_amount": 420.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day rate",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto 2026 election portal"
            },
            {
                "title": "Managing Deputy Returning Officer (MDRO)",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$450.00 / day",
                "pay_actual_amount": 450.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day rate",
                "hours_or_shift": "Voting Day (8:00 AM - 9:30 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto 2026 election portal"
            },
            {
                "title": "Ballot Deputy Returning Officer",
                "category": "CLERK",
                "pay_actual_raw": "$300.00 / day",
                "pay_actual_amount": 300.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day rate",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto 2026 election portal"
            },
            {
                "title": "Revising Deputy Returning Officer",
                "category": "REVISION",
                "pay_actual_raw": "$300.00 / day",
                "pay_actual_amount": 300.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day rate",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto 2026 election portal"
            },
            {
                "title": "Access Officer / Customer Service Officer",
                "category": "GREETER",
                "pay_actual_raw": "$280.00 / day",
                "pay_actual_amount": 280.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day rate",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto 2026 election portal"
            },
            {
                "title": "Tabulator Deputy Returning Officer",
                "category": "TECH",
                "pay_actual_raw": "$280.00 / day",
                "pay_actual_amount": 280.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day rate",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto 2026 election portal"
            }
        ]
    },
    "City of Mississauga": {
        "source": "Official Mississauga Votes 2026 Compensation Schedule",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$390.00 lump sum",
                "pay_actual_amount": 390.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (7:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Mississauga Votes 2026 portal"
            },
            {
                "title": "Supervising Deputy Returning Officer",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$390.00 lump sum",
                "pay_actual_amount": 390.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (7:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Mississauga Votes 2026 portal"
            },
            {
                "title": "Mandatory Supervising Deputy Returning Officer",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$300.00 lump sum",
                "pay_actual_amount": 300.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (8:30 AM - 2:00 PM + supply handling)",
                "min_age": 18,
                "notes": "Confirmed on official Mississauga Votes 2026 portal"
            },
            {
                "title": "Information Officer / Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$279.00 lump sum",
                "pay_actual_amount": 279.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (7:30 AM - close)",
                "min_age": 16,
                "notes": "Confirmed on official Mississauga Votes 2026 portal"
            }
        ]
    },
    "City of Brampton": {
        "source": "Official City of Brampton 2026 Election Worker Schedule",
        "roles": [
            {
                "title": "Location Supervisor",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$1,242 - $1,266 flat-rate",
                "pay_actual_amount": 1254.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in package",
                "hours_or_shift": "Advance pairing + Voting Day (8:00 AM - 10:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Brampton 2026 portal"
            },
            {
                "title": "Assistant Location Supervisor",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$1,157 - $1,181 flat-rate",
                "pay_actual_amount": 1169.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in package",
                "hours_or_shift": "Advance pairing + Voting Day (8:00 AM - 10:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Brampton 2026 portal"
            },
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$408.00 flat-rate",
                "pay_actual_amount": 408.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in rate",
                "hours_or_shift": "Voting Day (8:00 AM - 10:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Brampton 2026 portal"
            },
            {
                "title": "Tabulator Operator",
                "category": "TECH",
                "pay_actual_raw": "$304.00 flat-rate",
                "pay_actual_amount": 304.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in rate",
                "hours_or_shift": "Voting Day (8:00 AM - 10:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Brampton 2026 portal"
            },
            {
                "title": "Information Assistant / Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$285.00 flat-rate",
                "pay_actual_amount": 285.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in rate",
                "hours_or_shift": "Voting Day (8:00 AM - 10:00 PM)",
                "min_age": 16,
                "notes": "Confirmed on official Brampton 2026 portal"
            }
        ]
    },
    "City of London": {
        "source": "Official City of London 2026 Election Staff Schedule",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$350.00 (covers training & Election Day)",
                "pay_actual_amount": 350.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day fee",
                "hours_or_shift": "Voting Day (9:00 AM - until close)",
                "min_age": 18,
                "notes": "Confirmed on official City of London 2026 portal"
            },
            {
                "title": "Tabulator Operator",
                "category": "TECH",
                "pay_actual_raw": "$300.00 (covers training & Election Day)",
                "pay_actual_amount": 300.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day fee",
                "hours_or_shift": "Voting Day (9:00 AM - until close)",
                "min_age": 18,
                "notes": "Confirmed on official City of London 2026 portal"
            },
            {
                "title": "Registration Officer",
                "category": "REVISION",
                "pay_actual_raw": "$250.00 (covers training & Election Day)",
                "pay_actual_amount": 250.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day fee",
                "hours_or_shift": "Voting Day (9:00 AM - until close)",
                "min_age": 18,
                "notes": "Confirmed on official City of London 2026 portal"
            },
            {
                "title": "Information Officer",
                "category": "GREETER",
                "pay_actual_raw": "$220.00 (covers training & Election Day)",
                "pay_actual_amount": 220.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in day fee",
                "hours_or_shift": "Voting Day (9:00 AM - until close)",
                "min_age": 18,
                "notes": "Confirmed on official City of London 2026 portal"
            }
        ]
    },
    "City of Ottawa": {
        "source": "Official City of Ottawa 2026 Election Staff Schedule",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$325.00 / shift (including training)",
                "pay_actual_amount": 325.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in shift fee",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official City of Ottawa 2026 portal"
            },
            {
                "title": "Tabulator Deputy Returning Officer",
                "category": "TECH",
                "pay_actual_raw": "$325.00 / shift (including training)",
                "pay_actual_amount": 325.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in shift fee",
                "hours_or_shift": "Voting Day (8:00 AM - 9:30 PM)",
                "min_age": 18,
                "notes": "Confirmed on official City of Ottawa 2026 portal"
            },
            {
                "title": "Revising Officer",
                "category": "REVISION",
                "pay_actual_raw": "$275.00 / shift",
                "pay_actual_amount": 275.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in shift fee",
                "hours_or_shift": "Voting Day (9:00 AM - 8:30 PM)",
                "min_age": 18,
                "notes": "Confirmed on official City of Ottawa 2026 portal"
            },
            {
                "title": "Election Assistant / Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$275.00 / shift",
                "pay_actual_amount": 275.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in shift fee",
                "hours_or_shift": "Voting Day (9:00 AM - 8:30 PM)",
                "min_age": 16,
                "notes": "Confirmed on official City of Ottawa 2026 portal"
            }
        ]
    },
    "City of Kingston": {
        "source": "Official City of Kingston 2026 Election Jobs Portal",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$249.00 / day",
                "pay_actual_amount": 249.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Mandatory training required",
                "hours_or_shift": "Voting Day (10:00 AM - 8:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official City of Kingston 2026 portal"
            },
            {
                "title": "Machine Operator",
                "category": "TECH",
                "pay_actual_raw": "$235.00 / day",
                "pay_actual_amount": 235.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Mandatory training required",
                "hours_or_shift": "Voting Day (10:00 AM - 8:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official City of Kingston 2026 portal"
            },
            {
                "title": "Greeter / Demonstrator",
                "category": "GREETER",
                "pay_actual_raw": "$220.00 / day",
                "pay_actual_amount": 220.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Mandatory training required",
                "hours_or_shift": "Voting Day (10:00 AM - 8:00 PM)",
                "min_age": 16,
                "notes": "Confirmed on official City of Kingston 2026 portal"
            }
        ]
    },
    "City of Kitchener": {
        "source": "Official City of Kitchener 2026 Election Hiring Portal",
        "roles": [
            {
                "title": "Managing Deputy Returning Officer (MDRO)",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$587.00 / day ($32.65/hr advance)",
                "pay_actual_amount": 587.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Election Day + Advance Voting",
                "min_age": 18,
                "notes": "Confirmed on official Kitchener 2026 portal"
            },
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$385.00 / day ($24.04/hr advance)",
                "pay_actual_amount": 385.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Election Day + Advance Voting",
                "min_age": 18,
                "notes": "Confirmed on official Kitchener 2026 portal"
            },
            {
                "title": "Tabulator Assistant",
                "category": "TECH",
                "pay_actual_raw": "$320.00 / day ($22.88/hr advance)",
                "pay_actual_amount": 320.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Election Day + Advance Voting",
                "min_age": 18,
                "notes": "Confirmed on official Kitchener 2026 portal"
            }
        ]
    },
    "City of Sarnia": {
        "source": "Official City of Sarnia 2026 Election Portal",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$375.00",
                "pay_actual_amount": 375.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Voting Day (8:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Sarnia 2026 portal"
            },
            {
                "title": "Tabulator Operator",
                "category": "TECH",
                "pay_actual_raw": "$350.00",
                "pay_actual_amount": 350.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Voting Day (8:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Sarnia 2026 portal"
            },
            {
                "title": "Revision Clerk",
                "category": "REVISION",
                "pay_actual_raw": "$350.00",
                "pay_actual_amount": 350.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Voting Day (8:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Sarnia 2026 portal"
            },
            {
                "title": "Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$300.00",
                "pay_actual_amount": 300.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Voting Day (8:30 AM - close)",
                "min_age": 16,
                "notes": "Confirmed on official Sarnia 2026 portal"
            }
        ]
    },
    "City of Burlington": {
        "source": "Official Burlington 2026 Election Portal",
        "roles": [
            {
                "title": "Supervising Deputy Returning Officer (SDRO)",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$425.00 (inclusive of training)",
                "pay_actual_amount": 425.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Voting Day (8:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Burlington 2026 portal"
            },
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$375.00 (inclusive of training)",
                "pay_actual_amount": 375.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "Voting Day (8:30 AM - close)",
                "min_age": 18,
                "notes": "Confirmed on official Burlington 2026 portal"
            }
        ]
    },
    "Town of Whitby": {
        "source": "Official Town of Whitby 2026 Election Recruitment",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$350.00 / day",
                "pay_actual_amount": 350.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "8:30 AM - 9:00 PM",
                "min_age": 18,
                "notes": "Confirmed on official Whitby 2026 portal"
            },
            {
                "title": "Voting Location Supervisor (VLS)",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$350.00 / day",
                "pay_actual_amount": 350.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "8:30 AM - 9:00 PM",
                "min_age": 18,
                "notes": "Confirmed on official Whitby 2026 portal"
            },
            {
                "title": "Information Assistant / Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$350.00 / day",
                "pay_actual_amount": 350.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included",
                "hours_or_shift": "8:30 AM - 9:00 PM",
                "min_age": 16,
                "notes": "Confirmed on official Whitby 2026 portal"
            }
        ]
    }
}
