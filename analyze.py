#!/usr/bin/env python3
"""
Python Data Analytics Script for the Ontario Municipal Election 2026 Poll Worker dataset.
Strictly analyzes confirmed published data.
"""
import json
import csv
from collections import Counter, defaultdict

def run_analytics():
    with open("data/election_jobs_by_municipality.json", "r") as f:
        data = json.load(f)

    total_munis = len(data)
    total_roles = sum(len(m.get("roles", [])) for m in data.values())

    print("=" * 60)
    print(" ONTARIO MUNICIPAL ELECTION 2026 - POLL WORKER ANALYTICS ")
    print("=" * 60)
    print(f"Total Municipalities: {total_munis}")
    print(f"Total Poll Positions: {total_roles}")
    print()

    # 1. Regional Breakdown
    region_counter = Counter(m.get("region", "Unknown") for m in data.values())
    print("1. TOP REGIONS / COUNTIES BY MUNICIPALITY COUNT:")
    print("-" * 60)
    for reg, count in region_counter.most_common(10):
        print(f"  - {reg:<25}: {count:>2} municipalities")
    print()

    # 2. Role Category Composition
    role_counter = Counter()
    for m in data.values():
        for r in m.get("roles", []):
            role_counter[r.get("category", "OTHER")] += 1

    print("2. ROLE CATEGORY COMPOSITION:")
    print("-" * 60)
    for cat, count in role_counter.most_common():
        pct = (count / total_roles) * 100
        print(f"  - {cat:<20}: {count:>3} roles ({pct:>5.1f}%)")
    print()

    # 3. Minimum Age Requirements
    age_counter = Counter()
    for m in data.values():
        for r in m.get("roles", []):
            age_counter[f"{r.get('min_age', 18)}+"] += 1

    print("3. MINIMUM AGE ELIGIBILITY:")
    print("-" * 60)
    for age, count in age_counter.items():
        print(f"  - Age {age:<10}: {count:>3} positions ({count/total_roles*100:.1f}%)")
    print()

    # 4. Confirmed Published Rates Summary
    published_roles = []
    for m_name, m in data.items():
        for r in m.get("roles", []):
            if r.get("pay_status") == "ACTUAL_PUBLISHED" and r.get("pay_actual_raw"):
                published_roles.append((m_name, r.get("title"), r.get("pay_actual_raw")))

    print("4. CONFIRMED PUBLISHED PAY SCHEDULES:")
    print("-" * 60)
    if published_roles:
        for muni, title, pay in published_roles:
            print(f"  - {muni:<22} | {title:<30} : {pay}")
    else:
        print("  - No compensation tariffs currently published by tracked portals.")
    print("=" * 60)

if __name__ == "__main__":
    run_analytics()
