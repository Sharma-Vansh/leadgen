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

async def run_all_archetype_b():
    scrapers = ARCHETYPE_MAP.get("b", [])
    print(f"Total Archetype B Universal ATS Adapters: {len(scrapers)}")
    
    all_records = []
    summary_stats = []
    
    fieldnames = [
        "Platform Name",
        "Source ID",
        "Job Title",
        "Company",
        "Location",
        "Is Remote",
        "Employment Type",
        "Salary Min",
        "Salary Max",
        "Salary Currency",
        "Apply URL",
        "Skills / Tags",
        "Scraped Timestamp"
    ]
    
    for scraper_cls in scrapers:
        scraper_name = scraper_cls.__name__
        try:
            scraper = scraper_cls()
            print(f"\n=======================================================")
            print(f"Running [{scraper.source_id}] {scraper.source_name}...")
            print(f"=======================================================")
            
            jobs = await scraper.scrape(limit=2)
            await scraper.close()
            
            count = len(jobs)
            status = "SUCCESS" if count > 0 else "NO_DATA"
            print(f"  -> Extracted {count} jobs across companies ({status})")
            
            summary_stats.append({
                "source_id": scraper.source_id,
                "platform": scraper.source_name,
                "status": status,
                "jobs_count": count
            })
            
            for j in jobs:
                d = j.dict()
                all_records.append({
                    "Platform Name": d.get("source_name") or scraper.source_name,
                    "Source ID": d.get("source_id") or scraper.source_id,
                    "Job Title": d.get("title") or "",
                    "Company": d.get("company") or "",
                    "Location": d.get("location") or "",
                    "Is Remote": "Yes" if d.get("is_remote") else "No",
                    "Employment Type": d.get("employment_type") or "",
                    "Salary Min": d.get("salary_min") or "",
                    "Salary Max": d.get("salary_max") or "",
                    "Salary Currency": d.get("salary_currency") or "INR",
                    "Apply URL": d.get("apply_url") or "",
                    "Skills / Tags": ", ".join(d.get("skills", []) or []),
                    "Scraped Timestamp": d.get("scraped_at") or datetime.utcnow().isoformat()
                })
        except Exception as e:
            print(f"  [ERROR] {scraper_name}: {e}")
            summary_stats.append({
                "source_id": getattr(scraper, "source_id", "ERR"),
                "platform": scraper_name,
                "status": f"ERROR: {str(e)[:50]}",
                "jobs_count": 0
            })

    output_dir = r"C:\Users\ASUS\.gemini\antigravity-ide\scratch\leadgen\module_1_scraping_engine\data\output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save CSV
    csv_file = os.path.join(output_dir, "archetype_b_test_scraped_data.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
    print(f"\n[OK] CSV exported to: {csv_file}")
    
    # Save Excel
    xlsx_file = os.path.join(output_dir, "archetype_b_test_scraped_data.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Archetype B Jobs"
    ws.append(fieldnames)
    for rec in all_records:
        ws.append([rec[k] for k in fieldnames])
        
    ws_stats = wb.create_sheet(title="Adapter Summary")
    ws_stats.append(["Source ID", "ATS Adapter", "Status", "Live Jobs Extracted"])
    for s in summary_stats:
        ws_stats.append([s["source_id"], s["platform"], s["status"], s["jobs_count"]])
        
    wb.save(xlsx_file)
    print(f"[OK] Excel exported to: {xlsx_file}")
    
    print("\n=== SUMMARY OF ARCHETYPE B TEST RUN ===")
    total_jobs = sum(s["jobs_count"] for s in summary_stats)
    print(f"Total ATS Adapters Executed: {len(summary_stats)}")
    print(f"Total Live Company Jobs Extracted: {total_jobs}")
    for s in summary_stats:
        print(f"  [{s['source_id']}] {s['platform']:<25}: {s['status']} ({s['jobs_count']} jobs)")

if __name__ == "__main__":
    asyncio.run(run_all_archetype_b())
