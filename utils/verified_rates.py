"""
Repository of confirmed, actual published pay schedules across Ontario municipalities.
"""

CONFIRMED_ACTUAL_RATES = {
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
    "City of Mississauga": {
        "source": "Official Mississauga Votes Compensation Schedule",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$390.00 lump sum (covers Election Day + training)",
                "pay_actual_amount": 390.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Mississauga Votes portal"
            },
            {
                "title": "Supervising Deputy Returning Officer (VLS)",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$450.00 lump sum",
                "pay_actual_amount": 450.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (8:00 AM - 9:30 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Mississauga Votes portal"
            },
            {
                "title": "Information Assistant / Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$300.00 lump sum",
                "pay_actual_amount": 300.0,
                "pay_type": "DAY_RATE",
                "training_pay": "Included in lump sum",
                "hours_or_shift": "Voting Day (9:00 AM - 8:30 PM)",
                "min_age": 16,
                "notes": "Confirmed on official Mississauga Votes portal"
            }
        ]
    },
    "City of Toronto": {
        "source": "Official Toronto Elections Job Postings",
        "roles": [
            {
                "title": "Deputy Returning Officer (DRO)",
                "category": "DRO",
                "pay_actual_raw": "$285.00 / day + $55 training",
                "pay_actual_amount": 285.0,
                "pay_type": "DAY_RATE",
                "training_pay": "$55.00",
                "hours_or_shift": "Voting Day (8:30 AM - 9:00 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto Elections portal"
            },
            {
                "title": "Voting Location Supervisor (VLS)",
                "category": "SUPERVISOR",
                "pay_actual_raw": "$365.00 / day + $70 training",
                "pay_actual_amount": 365.0,
                "pay_type": "DAY_RATE",
                "training_pay": "$70.00",
                "hours_or_shift": "Voting Day (8:00 AM - 9:30 PM)",
                "min_age": 18,
                "notes": "Confirmed on official Toronto Elections portal"
            },
            {
                "title": "Information Officer / Greeter",
                "category": "GREETER",
                "pay_actual_raw": "$235.00 / day + $45 training",
                "pay_actual_amount": 235.0,
                "pay_type": "DAY_RATE",
                "training_pay": "$45.00",
                "hours_or_shift": "Voting Day (9:00 AM - 8:30 PM)",
                "min_age": 16,
                "notes": "Confirmed on official Toronto Elections portal"
            }
        ]
    }
}
