import asyncio
import os
import sys
import csv
from datetime import datetime
import openpyxl

# Add project root to sys.path
sys.path.insert(0, r"C:\Users\ASUS\.gemini\antigravity-ide\scratch\leadgen")

from module_1_scraping_engine.run_scraper import ARCHETYPE_MAP

async def run_all_archetype_a():
    scrapers = ARCHETYPE_MAP.get("a", [])
    print(f"Total Archetype A Scrapers to run: {len(scrapers)}")
    
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
            print(f"Running [{scraper.source_id}] {scraper.source_name}...")
            jobs = await scraper.scrape(limit=2)
            await scraper.close()
            
            count = len(jobs)
            status = "SUCCESS" if count > 0 else "NO_DATA"
            print(f"  -> Extracted {count} jobs ({status})")
            
            summary_stats.append({
                "source_id": scraper.source_id,
                "platform": scraper.source_name,
                "status": status,
                "jobs_count": count
            })
            
            for j in jobs:
                d = j.dict()
                all_records.append({
                    "Platform Name": scraper.source_name,
                    "Source ID": scraper.source_id,
                    "Job Title": d.get("title") or "",
                    "Company": d.get("company") or "",
                    "Location": d.get("location") or "",
                    "Is Remote": "Yes" if d.get("is_remote") else "No",
                    "Employment Type": d.get("employment_type") or "Full-time",
                    "Salary Min": d.get("salary_min") or "",
                    "Salary Max": d.get("salary_max") or "",
                    "Salary Currency": d.get("salary_currency") or "",
                    "Apply URL": d.get("apply_url") or "",
                    "Skills / Tags": ", ".join(d.get("skills", [])),
                    "Scraped Timestamp": d.get("scraped_at", datetime.now().isoformat())
                })
        except Exception as e:
            print(f"  -> ERROR running {scraper_name}: {e}")
            summary_stats.append({
                "source_id": getattr(scraper_cls, "source_id", "UNKNOWN"),
                "platform": scraper_name,
                "status": f"FAILED: {e}",
                "jobs_count": 0
            })
            
    # Export to CSV and XLSX
    out_dir = r"C:\Users\ASUS\.gemini\antigravity-ide\scratch\leadgen\module_1_scraping_engine\data\output"
    os.makedirs(out_dir, exist_ok=True)
    
    csv_path = os.path.join(out_dir, "archetype_a_test_scraped_data.csv")
    xlsx_path = os.path.join(out_dir, "archetype_a_test_scraped_data.xlsx")
    
    # 1. Write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_records:
            writer.writerow(r)
            
    # 2. Write XLSX with openpyxl
    wb = openpyxl.Workbook()
    ws_jobs = wb.active
    ws_jobs.title = "Scraped Jobs"
    ws_jobs.append(fieldnames)
    for r in all_records:
        ws_jobs.append([r[k] for k in fieldnames])
        
    ws_summary = wb.create_sheet(title="Platform Summary")
    ws_summary.append(["Source ID", "Platform Name", "Status", "Jobs Extracted"])
    for s in summary_stats:
        ws_summary.append([s["source_id"], s["platform"], s["status"], s["jobs_count"]])
        
    wb.save(xlsx_path)
        
    print(f"\n==========================================")
    print(f"FINISHED! Scraped {len(all_records)} jobs across {len(scrapers)} platforms.")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved XLSX: {xlsx_path}")
    print(f"==========================================")

if __name__ == "__main__":
    asyncio.run(run_all_archetype_a())
