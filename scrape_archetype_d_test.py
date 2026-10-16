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

async def run_all_archetype_d():
    scrapers = ARCHETYPE_MAP.get("d", [])
    print(f"Total Archetype D Community & Social Listeners: {len(scrapers)}")
    
    all_records = []
    summary_stats = []
    
    fieldnames = [
        "Platform / Listener",
        "Source ID",
        "Job Title",
        "Company",
        "Location",
        "Is Remote",
        "Employment Type",
        "Salary (Scale / Raw)",
        "Eligible Batches",
        "Apply URL",
        "Skills / Tech Stack",
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
            print(f"  -> Processed & Validated {count} community opportunities ({status})")
            
            summary_stats.append({
                "source_id": scraper.source_id,
                "platform": scraper.source_name,
                "status": status,
                "jobs_count": count
            })
            
            for j in valid_jobs:
                d = j.model_dump()
                batches = d.get("batch_eligible") or []
                batch_str = ", ".join(str(b) for b in batches) if batches else "All Batches"
                
                all_records.append({
                    "Platform / Listener": d.get("source_name") or scraper.source_name,
                    "Source ID": d.get("source_id") or scraper.source_id,
                    "Job Title": d.get("title") or "",
                    "Company": d.get("company") or "Direct Hiring",
                    "Location": d.get("location") or "Remote / Hybrid",
                    "Is Remote": "Yes" if d.get("is_remote") else "No",
                    "Employment Type": d.get("employment_type") or "full_time",
                    "Salary (Scale / Raw)": d.get("salary_raw") or "Disclosed upon discussion",
                    "Eligible Batches": batch_str,
                    "Apply URL": d.get("apply_url") or "",
                    "Skills / Tech Stack": ", ".join(d.get("skills", []) or []),
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
    csv_file = os.path.join(output_dir, "archetype_d_test_scraped_data.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
    print(f"\n[OK] CSV exported to: {csv_file}")
    
    # Save Excel
    xlsx_file = os.path.join(output_dir, "archetype_d_test_scraped_data.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Archetype D Community Jobs"
    ws.append(fieldnames)
    for rec in all_records:
        ws.append([rec[k] for k in fieldnames])
        
    ws_stats = wb.create_sheet(title="Social Listener Summary")
    ws_stats.append(["Source ID", "Community / Social Channel", "Status", "Live Opportunities Ingested"])
    for s in summary_stats:
        ws_stats.append([s["source_id"], s["platform"], s["status"], s["jobs_count"]])
        
    wb.save(xlsx_file)
    print(f"[OK] Excel exported to: {xlsx_file}")
    
    print("\n=== SUMMARY OF ARCHETYPE D TEST RUN ===")
    total_jobs = sum(s["jobs_count"] for s in summary_stats)
    print(f"Total Community & Social Listeners Executed: {len(summary_stats)}")
    print(f"Total Live Community Opportunities Extracted: {total_jobs}")
    for s in summary_stats:
        print(f"  [{s['source_id']}] {s['platform']:<45}: {s['status']} ({s['jobs_count']} opportunities)")

if __name__ == "__main__":
    asyncio.run(run_all_archetype_d())
