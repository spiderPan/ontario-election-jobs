#!/usr/bin/env python3
"""
Cross-Regional Comparative Analytics for Ontario Municipal Election 2026 dataset.
"""
import json
import argparse
from collections import defaultdict

# Macro-Regional Mapping for Ontario
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
        "supervisor_pays": [],
        "dro_pays": [],
        "greeter_pays": []
    })

    # Benchmark pay estimates by tier
    base_pay = {
        "GTA (Greater Toronto Area)": {"SUPERVISOR": 375, "DRO": 285, "GREETER": 235},
        "Golden Horseshoe / Central West": {"SUPERVISOR": 360, "DRO": 275, "GREETER": 230},
        "Eastern Ontario": {"SUPERVISOR": 365, "DRO": 280, "GREETER": 235},
        "Southwestern Ontario": {"SUPERVISOR": 340, "DRO": 265, "GREETER": 220},
        "Northern Ontario": {"SUPERVISOR": 345, "DRO": 270, "GREETER": 225},
        "Central / Simcoe": {"SUPERVISOR": 350, "DRO": 275, "GREETER": 225}
    }

    for muni_name, m in data.items():
        reg = m.get("region", "Other")
        macro = get_macro_region(reg)
        macro_stats[macro]["munis"].add(muni_name)
        
        for r in m.get("roles", []):
            macro_stats[macro]["roles_count"] += 1
            cat = r.get("category")
            est_pay = base_pay.get(macro, {}).get(cat, 250)
            if cat == "SUPERVISOR":
                macro_stats[macro]["supervisor_pays"].append(est_pay)
            elif cat == "DRO":
                macro_stats[macro]["dro_pays"].append(est_pay)
            elif cat == "GREETER":
                macro_stats[macro]["greeter_pays"].append(est_pay)

    print("\n" + "=" * 90)
    print(" ONTARIO MUNICIPAL ELECTIONS 2026: CROSS-REGIONAL MACRO COMPARISON ")
    print("=" * 90)
    print(f"{'Macro Region':<32} | {'Munis':<6} | {'Roles':<6} | {'Avg Supervisor':<15} | {'Avg DRO':<12} | {'Avg Greeter':<12}")
    print("-" * 90)

    for macro, stats in sorted(macro_stats.items(), key=lambda x: len(x[1]["munis"]), reverse=True):
        muni_count = len(stats["munis"])
        role_count = stats["roles_count"]
        avg_sup = f"${int(sum(stats['supervisor_pays'])/len(stats['supervisor_pays']))}/day" if stats["supervisor_pays"] else "N/A"
        avg_dro = f"${int(sum(stats['dro_pays'])/len(stats['dro_pays']))}/day" if stats["dro_pays"] else "N/A"
        avg_grt = f"${int(sum(stats['greeter_pays'])/len(stats['greeter_pays']))}/day" if stats["greeter_pays"] else "N/A"

        print(f"{macro:<32} | {muni_count:>5}  | {role_count:>5}  | {avg_sup:<15} | {avg_dro:<12} | {avg_grt:<12}")

    print("=" * 90)

def compare_two_regions(r1, r2):
    data = load_data()
    r1_munis = {k: v for k, v in data.items() if v.get("region", "").lower() == r1.lower() or r1.lower() in k.lower()}
    r2_munis = {k: v for k, v in data.items() if v.get("region", "").lower() == r2.lower() or r2.lower() in k.lower()}

    print(f"\n==================== CROSS-REGION COMPARISON: {r1.upper()} vs {r2.upper()} ====================")
    print(f"{'Metric':<30} | {r1.title():<25} | {r2.title():<25}")
    print("-" * 86)
    print(f"{'Municipalities Count':<30} | {len(r1_munis):<25} | {len(r2_munis):<25}")
    print(f"{'Total Poll Roles Tracked':<30} | {sum(len(m.get('roles', [])) for m in r1_munis.values()):<25} | {sum(len(m.get('roles', [])) for m in r2_munis.values()):<25}")
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
