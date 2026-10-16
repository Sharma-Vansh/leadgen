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
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.arbeitnow import ArbeitnowScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.themuse import TheMuseScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.workingnomads import WorkingNomadsScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.hasjob import HasjobScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.nodesk import NoDeskScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.landingjobs import LandingJobsScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.freelancer import FreelancerScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.adzuna import AdzunaScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.jooble import JoobleScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.usajobs import USAJobsScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.unstop import UnstopScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.internshala import InternshalaScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.reed import ReedScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.careerjet import CareerjetScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.career_one_stop import CareerOneStopScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.cutshort import CutshortScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.yc_jobs import YCJobsScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.python_org import PythonOrgScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.jobsora import JobsoraScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.placement_india import PlacementIndiaScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.web3_career import Web3CareerScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.builtin import BuiltInScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.remote_rocketship import RemoteRocketshipScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.wearedevelopers import WeAreDevelopersScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.peopleperhour import PeoplePerHourScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.freshersworld import FreshersworldScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.arc import ArcScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.jobspresso import JobspressoScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.jobs_ac_uk import JobsAcUkScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.oneforma import OneFormaScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.cryptojobslist import CryptoJobsListScraper

# Import Archetype B Universal ATS Adapters
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.greenhouse_adapter import GreenhouseAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.lever_adapter import LeverAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.ashby_adapter import AshbyAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.workday_adapter import WorkdayAdapter

# Import Archetype C Government & PSU Engine
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.discovery_hubs.sarkari_result import SarkariResultScraper
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.discovery_hubs.free_job_alert import FreeJobAlertScraper
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.direct_monitors.ssc_direct import SSCDirectMonitor

# Import Archetype D Community & Social Listeners
from module_1_scraping_engine.archetypes.archetype_d_community_social.listeners.telegram_listener import TelegramListener
from module_1_scraping_engine.archetypes.archetype_d_community_social.listeners.whatsapp_receiver import WhatsAppReceiver
from module_1_scraping_engine.archetypes.archetype_d_community_social.listeners.youtube_monitor import YouTubeMonitor

# Import Archetype E External Stealth Engine
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.naukri_scraper import NaukriScraper
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.linkedin_guest import LinkedInGuestScraper
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.indeed_parser import IndeedParser
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.foundit_scraper import FounditScraper
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.apna_adapter import ApnaAdapter
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.glassdoor_scraper import GlassdoorScraper
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.portals.workindia_scraper import WorkIndiaScraper
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.emitter.queue_publisher import QueuePublisher

console = Console()

SCRAPER_REGISTRY = {
    # Archetype A
    "remotive": RemotiveScraper,
    "remoteok": RemoteOKScraper,
    "jobicy": JobicyScraper,
    "weworkremotely": WeWorkRemotelyScraper,
    "wwr": WeWorkRemotelyScraper,
    "himalayas": HimalayasScraper,
    "arbeitnow": ArbeitnowScraper,
    "themuse": TheMuseScraper,
    "workingnomads": WorkingNomadsScraper,
    "hasjob": HasjobScraper,
    "nodesk": NoDeskScraper,
    "landingjobs": LandingJobsScraper,
    "freelancer": FreelancerScraper,
    "adzuna": AdzunaScraper,
    "jooble": JoobleScraper,
    "usajobs": USAJobsScraper,
    "unstop": UnstopScraper,
    "internshala": InternshalaScraper,
    "reed": ReedScraper,
    "careerjet": CareerjetScraper,
    "careeronestop": CareerOneStopScraper,
    "cutshort": CutshortScraper,
    "yc": YCJobsScraper,
    "ycombinator": YCJobsScraper,
    "pythonorg": PythonOrgScraper,
    "jobsora": JobsoraScraper,
    "placementindia": PlacementIndiaScraper,
    "web3career": Web3CareerScraper,
    "builtin": BuiltInScraper,
    "remoterocketship": RemoteRocketshipScraper,
    "wearedevelopers": WeAreDevelopersScraper,
    "peopleperhour": PeoplePerHourScraper,
    "freshersworld": FreshersworldScraper,
    "arc": ArcScraper,
    "jobspresso": JobspressoScraper,
    "jobsacuk": JobsAcUkScraper,
    "oneforma": OneFormaScraper,
    "cryptojobslist": CryptoJobsListScraper,
    # Archetype B
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "ashby": AshbyAdapter,
    "workday": WorkdayAdapter,
    # Archetype C
    "sarkariresult": SarkariResultScraper,
    "freejobalert": FreeJobAlertScraper,
    "ssc": SSCDirectMonitor,
    # Archetype D
    "telegram": TelegramListener,
    "whatsapp": WhatsAppReceiver,
    "youtube": YouTubeMonitor,
    # Archetype E
    "naukri": NaukriScraper,
    "linkedin": LinkedInGuestScraper,
    "indeed": IndeedParser,
    "foundit": FounditScraper,
    "apna": ApnaAdapter,
    "glassdoor": GlassdoorScraper,
    "workindia": WorkIndiaScraper
}

ARCHETYPE_MAP = {
    "a": [
        RemotiveScraper,
        RemoteOKScraper,
        JobicyScraper,
        WeWorkRemotelyScraper,
        HimalayasScraper,
        ArbeitnowScraper,
        TheMuseScraper,
        WorkingNomadsScraper,
        HasjobScraper,
        NoDeskScraper,
        LandingJobsScraper,
        FreelancerScraper,
        AdzunaScraper,
        JoobleScraper,
        USAJobsScraper,
        UnstopScraper,
        InternshalaScraper,
        ReedScraper,
        CareerjetScraper,
        CareerOneStopScraper,
        CutshortScraper,
        YCJobsScraper,
        PythonOrgScraper,
        JobsoraScraper,
        PlacementIndiaScraper,
        Web3CareerScraper,
        BuiltInScraper,
        RemoteRocketshipScraper,
        WeAreDevelopersScraper,
        PeoplePerHourScraper,
        FreshersworldScraper,
        ArcScraper,
        JobspressoScraper,
        JobsAcUkScraper,
        OneFormaScraper,
        CryptoJobsListScraper,
    ],
    "b": [GreenhouseAdapter, LeverAdapter, AshbyAdapter, WorkdayAdapter],
    "c": [SarkariResultScraper, FreeJobAlertScraper, SSCDirectMonitor],
    "d": [TelegramListener, WhatsAppReceiver, YouTubeMonitor],
    "e": [NaukriScraper, LinkedInGuestScraper, IndeedParser, FounditScraper, ApnaAdapter, GlassdoorScraper, WorkIndiaScraper]
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
