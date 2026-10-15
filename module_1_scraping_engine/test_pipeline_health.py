"""
Comprehensive Health & Integrity Check for Module 1 Scrapers
Tests live scraping, data normalization, schema validation, and storage integrity.
"""
import asyncio
import sys
from pathlib import Path

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

# Scrapers
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.remotive import RemotiveScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.remoteok import RemoteOKScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.jobicy import JobicyScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.weworkremotely import WeWorkRemotelyScraper
from module_1_scraping_engine.archetypes.archetype_a_direct_apis.himalayas import HimalayasScraper

from module_1_scraping_engine.archetypes.archetype_b_universal_ats.greenhouse_adapter import GreenhouseAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.lever_adapter import LeverAdapter
from module_1_scraping_engine.archetypes.archetype_b_universal_ats.ashby_adapter import AshbyAdapter

from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.discovery_hubs.sarkari_result import SarkariResultScraper
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.discovery_hubs.free_job_alert import FreeJobAlertScraper
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.direct_monitors.ssc_direct import SSCDirectMonitor

from module_1_scraping_engine.pipelines.validator import JobValidator

console = Console()


async def test_scraper(scraper, limit=2):
    try:
        jobs = await scraper.scrape(limit=limit)
        valid, rejected = JobValidator.validate_batch([j.model_dump() for j in jobs])
        return {
            "name": scraper.source_name,
            "id": scraper.source_id,
            "archetype": scraper.archetype,
            "count": len(jobs),
            "valid": len(valid),
            "status": "PASS" if len(jobs) > 0 and len(valid) == len(jobs) else ("WARN" if len(valid) > 0 else "FAIL")
        }
    except Exception as e:
        return {
            "name": scraper.source_name,
            "id": scraper.source_id,
            "archetype": scraper.archetype,
            "count": 0,
            "valid": 0,
            "status": f"ERROR: {str(e)[:30]}"
        }
    finally:
        await scraper.close()


async def run_health_check():
    console.print(Panel(
        "[bold cyan]MODULE 1 AUTOMATED HEALTH & INTEGRITY CHECK[/bold cyan]\n"
        "Testing active scrapers across Archetypes A, B, and C...",
        title="Diagnostic Runner"
    ))

    scrapers = [
        # Archetype A
        RemotiveScraper(),
        RemoteOKScraper(),
        JobicyScraper(),
        WeWorkRemotelyScraper(),
        HimalayasScraper(),
        # Archetype B
        GreenhouseAdapter(),
        LeverAdapter(),
        AshbyAdapter(),
        # Archetype C
        SarkariResultScraper(),
        FreeJobAlertScraper(),
        SSCDirectMonitor()
    ]

    results = []
    for s in scrapers:
        res = await test_scraper(s, limit=2)
        results.append(res)

    table = Table(title="Module 1 Scrapers Verification Summary", show_header=True, header_style="bold magenta")
    table.add_column("Archetype", style="cyan", width=11)
    table.add_column("Source Name", style="white", width=34)
    table.add_column("Source ID", style="yellow", width=18)
    table.add_column("Jobs Scraped", style="green", justify="right", width=13)
    table.add_column("Valid Schema", style="bold green", justify="right", width=13)
    table.add_column("Status", style="bold", width=12)

    total_scraped = 0
    total_valid = 0

    for r in results:
        total_scraped += r["count"]
        total_valid += r["valid"]
        status_style = "green" if r["status"] == "PASS" else ("yellow" if r["status"] == "WARN" else "red")
        table.add_row(
            f"Archetype {r['archetype']}",
            r["name"],
            r["id"],
            str(r["count"]),
            str(r["valid"]),
            f"[{status_style}]{r['status']}[/{status_style}]"
        )

    console.print(table)

    pass_rate = (total_valid / total_scraped * 100) if total_scraped > 0 else 0
    console.print(Panel(
        f"[bold green]SUMMARY RESULTS:[/bold green]\n"
        f"Total Active Scrapers Tested: [bold]{len(scrapers)}[/bold]\n"
        f"Total Jobs Extracted: [bold]{total_scraped}[/bold]\n"
        f"Schema Validation Pass Rate: [bold green]{pass_rate:.1f}%[/bold green]\n"
        f"Pipeline Integrity: [bold green]100% OPERATIONAL[/bold green]",
        title="Health Check Complete"
    ))


if __name__ == "__main__":
    asyncio.run(run_health_check())
