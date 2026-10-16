import asyncio
import os
import sys
import csv
from datetime import datetime
import openpyxl

# Add project root to sys.path
sys.path.insert(0, r"C:\Users\ASUS\.gemini\antigravity-ide\scratch\leadgen")

from module_1_scraping_engine.run_scraper import ARCHETYPE_MAP
from module_1_scraping_engine.pipelines.validator import JobValidator
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

async def run_all_archetype_c():
    scrapers = ARCHETYPE_MAP.get("c", [])
    print(f"Total Archetype C Government & PSU Adapters: {len(scrapers)}")
    
    all_records = []
    summary_stats = []
    
    fieldnames = [
        "Platform Name",
        "Source ID",
        "Job Title",
        "Conducting Body / Department",
        "Location",
        "Is Remote",
        "Employment Type",
        "Official Domain Verified",
        "Salary (Scale / Raw)",
        "Apply / Notification URL",
        "Skills / Qualifications",
        "Scraped Timestamp"
    ]
    
    for scraper_cls in scrapers:
        scraper_name = scraper_cls.__name__
        scraper = None
        try:
            scraper = scraper_cls()
            print(f"\n=======================================================")
            print(f"Running [{scraper.source_id}] {scraper.source_name}...")
            print(f"=======================================================")
            
            jobs = await scraper.scrape(limit=10)
            await scraper.close()
            
            # Validate through standard schema validator
            valid_jobs, rejected = JobValidator.validate_batch([j.model_dump() for j in jobs])
            
            count = len(valid_jobs)
            status = "SUCCESS" if count > 0 else "NO_DATA"
            print(f"  -> Extracted & Validated {count} government/PSU notices ({status})")
            
            summary_stats.append({
                "source_id": scraper.source_id,
                "platform": scraper.source_name,
                "status": status,
                "jobs_count": count
            })
            
            for j in valid_jobs:
                d = j.model_dump()
                apply_url = d.get("apply_url") or ""
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)
                
                all_records.append({
                    "Platform Name": d.get("source_name") or scraper.source_name,
                    "Source ID": d.get("source_id") or scraper.source_id,
                    "Job Title": d.get("title") or "",
                    "Conducting Body / Department": d.get("company") or "Government of India",
                    "Location": d.get("location") or "All India",
                    "Is Remote": "Yes" if d.get("is_remote") else "No",
                    "Employment Type": d.get("employment_type") or "full_time",
                    "Official Domain Verified": "Yes" if is_official else "Pending Review",
                    "Salary (Scale / Raw)": d.get("salary_raw") or "Pay Matrix as per 7th CPC / PSU Scale",
                    "Apply / Notification URL": apply_url,
                    "Skills / Qualifications": ", ".join(d.get("skills", []) or []),
                    "Scraped Timestamp": d.get("scraped_at") or datetime.utcnow().isoformat()
                })
        except Exception as e:
            sid = getattr(scraper, "source_id", "ERR") if scraper else "ERR"
            print(f"  [ERROR] {scraper_name}: {e}")
            summary_stats.append({
                "source_id": sid,
                "platform": scraper_name,
                "status": f"ERROR: {str(e)[:50]}",
                "jobs_count": 0
            })

    output_dir = r"C:\Users\ASUS\.gemini\antigravity-ide\scratch\leadgen\module_1_scraping_engine\data\output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save CSV
    csv_file = os.path.join(output_dir, "archetype_c_test_scraped_data.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
    print(f"\n[OK] CSV exported to: {csv_file}")
    
    # Save Excel
    xlsx_file = os.path.join(output_dir, "archetype_c_test_scraped_data.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Archetype C Govt Jobs"
    ws.append(fieldnames)
    for rec in all_records:
        ws.append([rec[k] for k in fieldnames])
        
    ws_stats = wb.create_sheet(title="Govt Adapter Summary")
    ws_stats.append(["Source ID", "Government / PSU Adapter", "Status", "Live Notices Extracted"])
    for s in summary_stats:
        ws_stats.append([s["source_id"], s["platform"], s["status"], s["jobs_count"]])
        
    wb.save(xlsx_file)
    print(f"[OK] Excel exported to: {xlsx_file}")
    
    print("\n=== SUMMARY OF ARCHETYPE C TEST RUN ===")
    total_jobs = sum(s["jobs_count"] for s in summary_stats)
    print(f"Total Government & PSU Adapters Executed: {len(summary_stats)}")
    print(f"Total Live Government Notices Extracted: {total_jobs}")
    for s in summary_stats:
        print(f"  [{s['source_id']}] {s['platform']:<45}: {s['status']} ({s['jobs_count']} notices)")

if __name__ == "__main__":
    asyncio.run(run_all_archetype_c())
