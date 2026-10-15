"""
LeadGen Master Scraper CLI Runner
Usage:
  python run_scraper.py --archetype a
  python run_scraper.py --source remotive --limit 10
  python run_scraper.py --all
"""
import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Type

# Add leadgen root directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.validator import JobValidator
from module_1_scraping_engine.config import OUTPUT_DIR

# Import Archetype A Scrapers
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.remotive import RemotiveScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.remoteok import RemoteOKScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.jobicy import JobicyScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.weworkremotely import WeWorkRemotelyScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.himalayas import HimalayasScraper

# Import Archetype B Universal ATS Adapters
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.greenhouse_adapter import GreenhouseAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.lever_adapter import LeverAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.ashby_adapter import AshbyAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.workday_adapter import WorkdayAdapter

console = Console()

SCRAPER_REGISTRY = {
    # Archetype A
    "remotive": RemotiveScraper,
    "remoteok": RemoteOKScraper,
    "jobicy": JobicyScraper,
    "weworkremotely": WeWorkRemotelyScraper,
    "wwr": WeWorkRemotelyScraper,
    "himalayas": HimalayasScraper,
    # Archetype B
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "ashby": AshbyAdapter,
    "workday": WorkdayAdapter
}

ARCHETYPE_MAP = {
    "a": [RemotiveScraper, RemoteOKScraper, JobicyScraper, WeWorkRemotelyScraper, HimalayasScraper],
    "b": [GreenhouseAdapter, LeverAdapter, AshbyAdapter, WorkdayAdapter]
}


async def run_scraper_instance(scraper_cls: Type[BaseScraper], limit: int) -> List[StandardJobListing]:
    scraper = scraper_cls()
    console.print(f"[bold cyan]>> Starting Scraper:[/bold cyan] {scraper.source_name} ({scraper.source_id}) [Archetype {scraper.archetype}]")
    try:
        results = await scraper.scrape(limit=limit)
        return results
    finally:
        await scraper.close()


def print_results_table(listings: List[StandardJobListing]):
    if not listings:
        console.print("[yellow]No listings found or returned.[/yellow]")
        return

    table = Table(title="Scraped & Validated Job Listings", show_header=True, header_style="bold magenta")
    table.add_column("Source", style="cyan", width=12)
    table.add_column("Title", style="white", width=32)
    table.add_column("Company", style="green", width=20)
    table.add_column("Location", style="yellow", width=16)
    table.add_column("Salary (Est.)", style="bold green", width=18)
    table.add_column("Apply Link", style="blue", overflow="fold")

    for job in listings[:15]:
        sal_display = "Not Disclosed"
        if job.salary_min and job.salary_max:
            if job.salary_min == job.salary_max:
                sal_display = f"₹{job.salary_min:,.0f}"
            else:
                sal_display = f"₹{job.salary_min:,.0f} - ₹{job.salary_max:,.0f}"
        elif job.salary_raw:
            sal_display = job.salary_raw[:18]

        table.add_row(
            job.source_name,
            job.title[:30],
            job.company[:18],
            (job.location or "Remote")[:14],
            sal_display,
            job.apply_url[:40] + "..."
        )

    console.print(table)
    if len(listings) > 15:
        console.print(f"[dim]... and {len(listings) - 15} more listings.[/dim]")


async def main():
    parser = argparse.ArgumentParser(description="LeadGen Scraper CLI Runner")
    parser.add_argument("--archetype", "-a", choices=["a", "b", "c", "d", "e"], help="Run all scrapers for an archetype")
    parser.add_argument("--source", "-s", help="Run a specific source (e.g. remotive, remoteok, jobicy, wwr, himalayas)")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max jobs to fetch per scraper (default: 10)")
    parser.add_argument("--save", action="store_true", help="Save validated outputs to JSON in data/output")
    args = parser.parse_args()

    scrapers_to_run: List[Type[BaseScraper]] = []

    if args.source:
        src_key = args.source.lower().strip()
        if src_key not in SCRAPER_REGISTRY:
            console.print(f"[bold red]Error:[/bold red] Unknown source '{args.source}'. Available: {list(SCRAPER_REGISTRY.keys())}")
            return
        scrapers_to_run.append(SCRAPER_REGISTRY[src_key])
    elif args.archetype:
        scrapers_to_run = ARCHETYPE_MAP.get(args.archetype.lower(), [])
    else:
        # Default run Archetype A
        console.print("[dim]No specific source or archetype provided. Defaulting to Archetype A.[/dim]")
        scrapers_to_run = ARCHETYPE_MAP["a"]

    all_listings: List[StandardJobListing] = []

    console.print(Panel(
        f"[bold green]LeadGen Scraping Engine v1.0[/bold green]\n"
        f"Active Scrapers: {len(scrapers_to_run)} | Limit per scraper: {args.limit}",
        title="Pipeline Initialized"
    ))

    for scraper_cls in scrapers_to_run:
        listings = await run_scraper_instance(scraper_cls, limit=args.limit)
        all_listings.extend(listings)

    # Run through Validation Gate
    valid_listings, rejected_count = JobValidator.validate_batch([j.model_dump() for j in all_listings])

    console.print(f"\n[bold green][OK] Validation Complete:[/bold green] {len(valid_listings)} Valid Listings | {rejected_count} Rejected\n")
    print_results_table(valid_listings)

    # Save to file if requested or by default
    output_file = OUTPUT_DIR / "latest_scraped_jobs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([j.model_dump() for j in valid_listings], f, indent=2, ensure_ascii=False)
    console.print(f"[green]Saved {len(valid_listings)} records to [bold]{output_file}[/bold][/green]")


if __name__ == "__main__":
    asyncio.run(main())
