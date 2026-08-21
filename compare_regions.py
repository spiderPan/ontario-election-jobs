#!/usr/bin/env python3
"""
Cross-Regional Comparative Analytics for Ontario Municipal Election 2026 dataset.
Compares verified municipal election portal coverage across regions.
"""
import json
import argparse
from collections import defaultdict

MACRO_REGIONS = {
    "GTA (Greater Toronto Area)": ["Toronto", "Peel", "York", "Halton", "Durham"],
    "Golden Horseshoe / Central West": ["Hamilton", "Waterloo", "Niagara", "Wellington", "Brant"],
    "Eastern Ontario": ["Ottawa", "Frontenac", "Peterborough", "Hastings", "Stormont Dundas Glengarry"],
    "Southwestern Ontario": ["Middlesex", "Essex", "Chatham-Kent", "Lambton"],
    "Northern Ontario": ["Sudbury", "Thunder Bay", "Algoma", "Nipissing"],
    "Central / Simcoe": ["Simcoe"]
}

def get_macro_region(region_name):
    for macro, regions in MACRO_REGIONS.items():
        if region_name in regions:
            return macro
    return "Other Ontario"

def load_data():
    with open("data/election_jobs_by_municipality.json", "r") as f:
        return json.load(f)

def run_macro_comparison():
    data = load_data()
    macro_stats = defaultdict(lambda: {
        "munis": set(),
        "roles_count": 0,
        "published_roles": 0
    })

    for muni_name, m in data.items():
        reg = m.get("region", "Other")
        macro = get_macro_region(reg)
        macro_stats[macro]["munis"].add(muni_name)
        
        for r in m.get("roles", []):
            macro_stats[macro]["roles_count"] += 1
            if r.get("pay_status") == "ACTUAL_PUBLISHED" and r.get("pay_actual_raw"):
                macro_stats[macro]["published_roles"] += 1

    print("\n" + "=" * 80)
    print(" ONTARIO MUNICIPAL ELECTIONS 2026: CROSS-REGIONAL COVERAGE MATRIX ")
    print("=" * 80)
    print(f"{'Macro Region':<35} | {'Munis':<6} | {'Roles':<6} | {'Published Rates':<16}")
    print("-" * 80)

    for macro, stats in sorted(macro_stats.items(), key=lambda x: len(x[1]["munis"]), reverse=True):
        muni_count = len(stats["munis"])
        role_count = stats["roles_count"]
        pub_count = f"{stats['published_roles']} roles" if stats['published_roles'] > 0 else "Pending (TBD)"

        print(f"{macro:<35} | {muni_count:>5}  | {role_count:>5}  | {pub_count:<16}")

    print("=" * 80)

def compare_two_regions(r1, r2):
    data = load_data()
    r1_munis = {k: v for k, v in data.items() if v.get("region", "").lower() == r1.lower() or r1.lower() in k.lower()}
    r2_munis = {k: v for k, v in data.items() if v.get("region", "").lower() == r2.lower() or r2.lower() in k.lower()}

    r1_pub = sum(len([r for r in m.get("roles", []) if r.get("pay_status") == "ACTUAL_PUBLISHED" and r.get("pay_actual_raw")]) for m in r1_munis.values())
    r2_pub = sum(len([r for r in m.get("roles", []) if r.get("pay_status") == "ACTUAL_PUBLISHED" and r.get("pay_actual_raw")]) for m in r2_munis.values())

    print(f"\n==================== CROSS-REGION COMPARISON: {r1.upper()} vs {r2.upper()} ====================")
    print(f"{'Metric':<30} | {r1.title():<25} | {r2.title():<25}")
    print("-" * 86)
    print(f"{'Municipalities Count':<30} | {len(r1_munis):<25} | {len(r2_munis):<25}")
    print(f"{'Total Poll Roles Tracked':<30} | {sum(len(m.get('roles', [])) for m in r1_munis.values()):<25} | {sum(len(m.get('roles', [])) for m in r2_munis.values()):<25}")
    print(f"{'Published Pay Roles':<30} | {f'{r1_pub} published':<25} | {f'{r2_pub} published':<25}")
    print(f"{'Sample Cities/Towns':<30} | {', '.join(list(r1_munis.keys())[:3]):<25} | {', '.join(list(r2_munis.keys())[:3]):<25}")
    print("=" * 86 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cross-Region Comparison CLI")
    parser.add_argument("--r1", type=str, help="First region to compare (e.g. Peel)")
    parser.add_argument("--r2", type=str, help="Second region to compare (e.g. York)")
    args = parser.parse_args()

    if args.r1 and args.r2:
        compare_two_regions(args.r1, args.r2)
    else:
        run_macro_comparison()
