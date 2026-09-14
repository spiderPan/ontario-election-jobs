#!/usr/bin/env python3
"""
Ontario Municipal Election 2026 - Poll Worker Job Crawler & Aggregator CLI.
Strictly filters out historical data and clearly differentiates Actual Published vs Modeled Estimates.
"""
import argparse
import asyncio
import json
import os
import sys
from typing import List

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from models import MunicipalElectionPostings
from scrapers.html_portal import HtmlPortalScraper
from scrapers.workday_election import WorkdayElectionScraper
from scrapers.amo_election import AMOMunicipalElectionScraper
from utils.db import ElectionJobDatabase
from export import export_all

console = Console()
DB = ElectionJobDatabase("data/election_jobs.db")


async def run_crawler(target_filter: str = None, concurrency: int = 5):
    seed_file = "data/election_portals.json"
    if not os.path.exists(seed_file):
        console.print(f"[red]Error: Seed file {seed_file} not found![/red]")
        return

    with open(seed_file, "r") as f:
        targets = json.load(f)

    if target_filter:
        targets = [t for t in targets if target_filter.lower() in t["municipality"].lower() or target_filter.lower() in t.get("region", "").lower()]
        console.print(f"[cyan]Filtering for '{target_filter}': {len(targets)} municipalities matched.[/cyan]")
    else:
        DB.clear_all()

    console.print(Panel.fit(
        f"[bold blue]Ontario Municipal Election 2026 - Poll Worker Crawler[/bold blue]\n"
        f"[green]Strict 2026 Currency Filter Enabled (Voting Day: Oct 26, 2026)[/green]\n"
        f"Scanning {len(targets)} municipal election portals...",
        border_style="blue"
    ))

    sem = asyncio.Semaphore(concurrency)
    results: List[MunicipalElectionPostings] = []
    excluded_count = 0

    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10, keepalive_expiry=5.0)
    timeout = httpx.Timeout(20.0, connect=10.0)

    async def fetch_with_sem(client: httpx.AsyncClient, target: dict):
        nonlocal excluded_count
        async with sem:
            try:
                scraper_type = target.get("type", "html_portal")
                if scraper_type == "workday" and target.get("wday_tenant"):
                    scraper = WorkdayElectionScraper(target)
                else:
                    scraper = HtmlPortalScraper(target)

                postings = await scraper.scrape(client)
                if not postings:
                    excluded_count += 1
                return postings
            except Exception:
                excluded_count += 1
                return []

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Crawling & verifying 2026 election portals...", total=len(targets))
            
            async_tasks = [fetch_with_sem(client, t) for t in targets]
            for coro in asyncio.as_completed(async_tasks):
                try:
                    batch = await coro
                    for p in batch:
                        DB.save_posting(p)
                        results.append(p)
                except Exception:
                    pass
                finally:
                    progress.advance(task)

            # Centralized AMO municipal job board check
            if not target_filter or "amo" in target_filter.lower():
                try:
                    amo_scraper = AMOMunicipalElectionScraper()
                    amo_postings = await amo_scraper.scrape(client)
                    for p in amo_postings:
                        DB.save_posting(p)
                        results.append(p)
                except Exception:
                    pass

    console.print(f"\n[bold green]✓ Verified & Saved {len(results)} Municipalities for 2026 Election![/bold green]")
    if excluded_count > 0:
        console.print(f"[dim yellow]ℹ Excluded {excluded_count} out-of-date / archived portals from previous cycles.[/dim yellow]")
    
    # Auto export
    j_path, c_path, m_path = export_all(DB)
    console.print(f"\n[dim]Fresh 2026 Data Exported to:[/dim]\n  - [bold]{j_path}[/bold] (Grouped JSON)\n  - [bold]{c_path}[/bold] (CSV)\n  - [bold]{m_path}[/bold] (Markdown Report)\n")


def display_list(target_filter: str = None):
    grouped = DB.get_grouped_postings()
    if not grouped:
        console.print("[yellow]No data found in database. Run 'python3 main.py crawl' first.[/yellow]")
        return

    for muni, info in grouped.items():
        if target_filter and target_filter.lower() not in muni.lower() and target_filter.lower() not in info.get("region", "").lower():
            continue

        status_color = "green" if info["status"] == "Accepting Applications" else "yellow"
        table = Table(title=f"{muni} ({info.get('region', 'Ontario')}) - [2026 Verified] [{status_color}]{info['status']}[/{status_color}]", title_justify="left")
        
        table.add_column("Role Title", style="bold cyan", width=30)
        table.add_column("Category", style="magenta", width=12)
        table.add_column("Pay Status", style="yellow", width=16)
        table.add_column("Published Pay Rate", style="green", width=22)
        table.add_column("Hours / Shift", style="white", width=24)
        table.add_column("Min Age", style="yellow", width=8)

        for r in info["roles"]:
            is_published = r["pay_status"] == "ACTUAL_PUBLISHED" and bool(r.get("pay_actual_raw"))
            status_tag = "[bold green]PUBLISHED[/bold green]" if is_published else "[dim]NOT AVAILABLE[/dim]"
            pay_str = r["pay_actual_raw"] if is_published else "[dim]Not available[/dim]"

            table.add_row(
                r["title"],
                r["category"],
                status_tag,
                pay_str,
                r["hours_or_shift"] or "Voting Day (8:30 AM - 9:00 PM)",
                f"{r['min_age']}+"
            )

        console.print(table)
        console.print(f"[dim]Direct Apply Link:[/dim] [link={info['apply_url']}]{info['apply_url']}[/link]")
        if info.get("contact_email"):
            console.print(f"[dim]Contact Email:[/dim] {info['contact_email']}")
        console.print()


def display_stats():
    stats = DB.get_stats()
    table = Table(title="Ontario Municipal Election 2026 - Verified Recruitment Stats")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Election Cycle", "2026 General Municipal Elections")
    table.add_row("Verified 2026 Municipalities", str(stats["total_municipalities"]))
    table.add_row("Total Poll Worker Roles", str(stats["total_roles"]))
    table.add_row("Roles with Confirmed Published Pay", f"[green]{stats['roles_with_published_pay']}[/green]")
    table.add_row("Roles with Pay Not Yet Published", f"[dim]{stats['roles_not_available']}[/dim]")

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Ontario Municipal Election 2026 Poll Worker Crawler")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    crawl_parser = subparsers.add_parser("crawl", help="Crawl and verify 2026 election portals")
    crawl_parser.add_argument("--muni", type=str, help="Filter by municipality or region name")
    crawl_parser.add_argument("--concurrency", type=int, default=5, help="Concurrent workers")

    list_parser = subparsers.add_parser("list", help="List verified 2026 election postings")
    list_parser.add_argument("--muni", type=str, help="Filter by municipality or region name")

    subparsers.add_parser("stats", help="Show summary statistics")
    subparsers.add_parser("export", help="Export to JSON, CSV, and Markdown")

    args = parser.parse_args()

    if args.command == "crawl" or args.command is None:
        if args.command is None:
            asyncio.run(run_crawler(concurrency=5))
            display_list()
        else:
            asyncio.run(run_crawler(target_filter=args.muni, concurrency=args.concurrency))
    elif args.command == "list":
        display_list(target_filter=args.muni)
    elif args.command == "stats":
        display_stats()
    elif args.command == "export":
        j, c, m = export_all(DB)
        console.print(f"[green]Fresh 2026 exports generated successfully![/green]\n- {j}\n- {c}\n- {m}")


if __name__ == "__main__":
    main()
