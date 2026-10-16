"""
LeadGen - Zero-Code Company Attachment Utility
Add new companies to Archetype B ATS without modifying backend code!

Usage:
  1. Interactive mode (just run it and answer prompts):
     python add_company.py

  2. Command-line mode:
     python add_company.py --name "Canva" --ats "greenhouse" --slug "canva"
     python add_company.py --url "https://boards.greenhouse.io/canva"
"""
import sys
import json
import asyncio
import argparse
from pathlib import Path
from urllib.parse import urlparse
import httpx

REGISTRY_PATH = Path(__file__).resolve().parent / "module_1_scraping_engine" / "archetypes" / "archetype_b_universal_ats" / "registry.json"

ATS_TEMPLATES = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=1",
    "workday": "https://{slug}.{instance}.myworkdayjobs.com/wday/cxs/{slug}/{board}/jobs"
}

def detect_from_url(url: str):
    """Auto-detects ATS and slug from a public job board URL."""
    url_lower = url.lower()
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]

    if "greenhouse.io" in url_lower:
        slug = path_parts[0] if path_parts else ""
        return "greenhouse", slug
    elif "ashbyhq.com" in url_lower:
        slug = path_parts[0] if path_parts else ""
        return "ashby", slug
    elif "lever.co" in url_lower:
        slug = path_parts[0] if path_parts else ""
        return "lever", slug
    elif "smartrecruiters.com" in url_lower:
        slug = path_parts[0] if path_parts else ""
        return "smartrecruiters", slug
    elif "myworkdayjobs.com" in url_lower:
        # e.g., nvidia.wd5.myworkdayjobs.com
        host_parts = parsed.netloc.split(".")
        slug = host_parts[0]
        return "workday", slug
    return None, None

async def verify_endpoint(ats: str, slug: str, board: str = "external", instance: str = "wd5"):
    """Pings the public API to verify the company exists and returns job counts."""
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            if ats == "greenhouse":
                url = ATS_TEMPLATES["greenhouse"].format(slug=slug)
                r = await client.get(url, headers=headers)
                if r.status_code == 200:
                    cnt = len(r.json().get("jobs", []))
                    return True, cnt, url
            elif ats == "ashby":
                url = ATS_TEMPLATES["ashby"].format(slug=slug)
                r = await client.get(url, headers=headers)
                if r.status_code == 200:
                    cnt = len(r.json().get("jobs", []))
                    return True, cnt, url
            elif ats == "lever":
                url = ATS_TEMPLATES["lever"].format(slug=slug)
                r = await client.get(url, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    cnt = len(data) if isinstance(data, list) else 0
                    return True, cnt, url
            elif ats == "smartrecruiters":
                url = ATS_TEMPLATES["smartrecruiters"].format(slug=slug)
                r = await client.get(url, headers=headers)
                if r.status_code == 200:
                    cnt = r.json().get("totalFound", 0)
                    return True, cnt, url
            elif ats == "workday":
                url = ATS_TEMPLATES["workday"].format(slug=slug, instance=instance, board=board)
                payload = {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}
                r = await client.post(url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    cnt = r.json().get("total", 0)
                    return True, cnt, url
        except Exception as e:
            return False, 0, str(e)
    return False, 0, f"HTTP Error or Not Found for {ats}/{slug}"

def add_to_registry(name: str, ats: str, slug: str, country: str = "Global", board: str = None, instance: str = None):
    """Appends company to registry.json safely."""
    if not REGISTRY_PATH.exists():
        data = {"greenhouse": [], "ashby": [], "lever": [], "smartrecruiters": [], "workday": []}
    else:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    if ats not in data:
        data[ats] = []

    # Check duplicate
    for existing in data[ats]:
        if existing.get("slug", "").lower() == slug.lower():
            print(f"[!] Company with slug '{slug}' already exists under {ats.capitalize()} in registry!")
            return False

    prefix = {"greenhouse": "GH", "ashby": "ASH", "lever": "LEV", "smartrecruiters": "SR", "workday": "WD"}.get(ats, "ATS")
    record = {
        "name": name,
        "slug": slug,
        "country": country,
        "source_id": f"{prefix}-{slug.upper()}"
    }
    if ats == "workday":
        record["board"] = board or "external"
        record["instance"] = instance or "wd5"

    data[ats].append(record)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    total = sum(len(v) for v in data.values())
    print(f"\n[SUCCESS] Added '{name}' under {ats.capitalize()}!")
    print(f"Total companies in registry now: {total}")
    return True

async def main():
    parser = argparse.ArgumentParser(description="Add a new company to Archetype B ATS without writing code.")
    parser.add_argument("--name", help="Company Name (e.g. 'Webflow')")
    parser.add_argument("--ats", choices=["greenhouse", "ashby", "lever", "smartrecruiters", "workday"], help="ATS Type")
    parser.add_argument("--slug", help="Company Slug / identifier on the ATS")
    parser.add_argument("--url", help="Job board URL (auto-detects ATS and slug)")
    parser.add_argument("--country", default="Global", help="Country or coverage (default: Global)")
    parser.add_argument("--board", help="Workday board name (default: external)")
    parser.add_argument("--instance", help="Workday instance (e.g. wd5, wd12)")
    
    args = parser.parse_args()

    name = args.name
    ats = args.ats
    slug = args.slug
    url = args.url
    country = args.country
    board = args.board
    instance = args.instance

    # URL auto detection if provided
    if url:
        detected_ats, detected_slug = detect_from_url(url)
        if detected_ats and detected_slug:
            ats = detected_ats
            slug = detected_slug
            if not name:
                name = slug.capitalize()
            print(f"[+] Auto-detected from URL: ATS={ats.capitalize()}, Slug='{slug}'")
        else:
            print(f"[-] Could not auto-detect ATS from URL '{url}'. Please specify --ats and --slug manually.")
            return

    # Interactive mode if arguments are missing
    if not ats or not slug:
        print("="*60)
        print("  LEADGEN - ZERO-CODE COMPANY ATTACHMENT")
        print("="*60)
        input_url = input("\nEnter Job Board or Careers URL (or press Enter to specify manually): ").strip()
        if input_url:
            detected_ats, detected_slug = detect_from_url(input_url)
            if detected_ats and detected_slug:
                ats = detected_ats
                slug = detected_slug
                print(f" -> Auto-detected: {ats.capitalize()} (Slug: {slug})")
        
        if not ats:
            print("\nSelect ATS Platform:")
            print("  1. Greenhouse")
            print("  2. Ashby")
            print("  3. Lever")
            print("  4. SmartRecruiters")
            print("  5. Workday")
            choice = input("Enter choice (1-5): ").strip()
            ats_map = {"1": "greenhouse", "2": "ashby", "3": "lever", "4": "smartrecruiters", "5": "workday"}
            ats = ats_map.get(choice)
            if not ats:
                print("Invalid choice. Exiting.")
                return

        if not slug:
            slug = input(f"Enter {ats.capitalize()} Company Slug (e.g. 'airbnb' or 'openai'): ").strip()

        if not name:
            name = input("Enter Company Display Name (e.g. 'Airbnb'): ").strip() or slug.capitalize()
        
        country = input("Enter Country/Region (default 'Global'): ").strip() or "Global"

    print(f"\n[1/2] Verifying live connection for '{name}' on {ats.capitalize()}...")
    ok, count, endpoint = await verify_endpoint(ats, slug, board=board or "external", instance=instance or "wd5")
    
    if not ok:
        print(f"[-] Verification Warning: {endpoint}")
        confirm = input("Could not verify active jobs. Do you still want to add it? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return
    else:
        print(f"[+] Live verified! Found {count} active jobs at:")
        print(f"    {endpoint}")

    print(f"\n[2/2] Registering into system...")
    add_to_registry(name=name, ats=ats, slug=slug, country=country, board=board, instance=instance)
    print("\nDone! Next time you run the scraper, jobs from this company will be automatically scraped!")

if __name__ == "__main__":
    asyncio.run(main())
