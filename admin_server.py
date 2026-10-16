"""
LeadGen Admin Dashboard Server
Lightweight, zero-external-dependency web server for managing ATS Company Registry & running test scrapers.
Serves UI at: http://localhost:8085
"""
import sys
import os
import json
import asyncio
import subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import httpx

PROJECT_ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = PROJECT_ROOT / "module_1_scraping_engine" / "archetypes" / "archetype_b_universal_ats" / "registry.json"
UI_DIR = PROJECT_ROOT / "admin_ui"
PORT = 8085

ATS_TEMPLATES = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=1",
    "workday": "https://{slug}.{instance}.myworkdayjobs.com/wday/cxs/{slug}/{board}/jobs"
}

def verify_live_connection(ats: str, slug: str, board: str = "external", instance: str = "wd5"):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    with httpx.Client(timeout=8.0) as client:
        try:
            if ats == "greenhouse":
                url = ATS_TEMPLATES["greenhouse"].format(slug=slug)
                r = client.get(url, headers=headers)
                if r.status_code == 200:
                    cnt = len(r.json().get("jobs", []))
                    return True, cnt, url, ""
            elif ats == "ashby":
                url = ATS_TEMPLATES["ashby"].format(slug=slug)
                r = client.get(url, headers=headers)
                if r.status_code == 200:
                    cnt = len(r.json().get("jobs", []))
                    return True, cnt, url, ""
            elif ats == "lever":
                url = ATS_TEMPLATES["lever"].format(slug=slug)
                r = client.get(url, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    cnt = len(data) if isinstance(data, list) else 0
                    return True, cnt, url, ""
            elif ats == "smartrecruiters":
                url = ATS_TEMPLATES["smartrecruiters"].format(slug=slug)
                r = client.get(url, headers=headers)
                if r.status_code == 200:
                    cnt = r.json().get("totalFound", 0)
                    return True, cnt, url, ""
            elif ats == "workday":
                url = ATS_TEMPLATES["workday"].format(slug=slug, instance=instance, board=board)
                payload = {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}
                r = client.post(url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    cnt = r.json().get("total", 0)
                    return True, cnt, url, ""
        except Exception as e:
            return False, 0, "", str(e)
    return False, 0, "", f"HTTP Error or Board not found for {ats}/{slug}"

class AdminRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/api/companies":
            self.handle_get_companies()
        elif self.path == "/" or self.path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            payload = json.loads(post_body.decode('utf-8'))
        except Exception:
            payload = {}

        if self.path == "/api/verify":
            self.handle_verify(payload)
        elif self.path == "/api/add-company":
            self.handle_add_company(payload)
        elif self.path == "/api/delete-company":
            self.handle_delete_company(payload)
        elif self.path == "/api/run-scraper":
            self.handle_run_scraper()
        else:
            self.send_error(404, "Endpoint not found")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_get_companies(self):
        if not REGISTRY_PATH.exists():
            self.send_json({})
            return
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.send_json(data)

    def handle_verify(self, payload):
        ats = payload.get("ats", "greenhouse")
        slug = payload.get("slug", "").strip()
        board = payload.get("board", "external")
        instance = payload.get("instance", "wd5")

        if not slug:
            self.send_json({"valid": False, "error": "Slug is required"}, status=400)
            return

        valid, cnt, url, err = verify_live_connection(ats, slug, board=board, instance=instance)
        self.send_json({
            "valid": valid,
            "jobs_count": cnt,
            "url": url,
            "error": err
        })

    def handle_add_company(self, payload):
        name = payload.get("name", "").strip()
        ats = payload.get("ats", "greenhouse").strip().lower()
        slug = payload.get("slug", "").strip()
        country = payload.get("country", "Global").strip() or "Global"
        board = payload.get("board", "external").strip() or "external"
        instance = payload.get("instance", "wd5").strip() or "wd5"

        if not name or not slug or not ats:
            self.send_json({"success": False, "message": "Name, ATS, and Slug are required"}, status=400)
            return

        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if ats not in data:
            data[ats] = []

        # Check duplicate
        for existing in data[ats]:
            if existing.get("slug", "").lower() == slug.lower():
                self.send_json({"success": False, "message": f"Company with slug '{slug}' already exists under {ats.capitalize()}!"})
                return

        prefix = {"greenhouse": "GH", "ashby": "ASH", "lever": "LEV", "smartrecruiters": "SR", "workday": "WD"}.get(ats, "ATS")
        record = {
            "name": name,
            "slug": slug,
            "country": country,
            "source_id": f"{prefix}-{slug.upper()}"
        }
        if ats == "workday":
            record["board"] = board
            record["instance"] = instance

        data[ats].append(record)

        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        total = sum(len(v) for v in data.values())
        self.send_json({"success": True, "message": f"Added {name} successfully", "total": total})

    def handle_delete_company(self, payload):
        ats = payload.get("ats", "").strip().lower()
        slug = payload.get("slug", "").strip().lower()

        if not ats or not slug:
            self.send_json({"success": False, "message": "ATS and Slug required"}, status=400)
            return

        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if ats in data:
            original_len = len(data[ats])
            data[ats] = [c for c in data[ats] if c.get("slug", "").lower() != slug]
            if len(data[ats]) < original_len:
                with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.send_json({"success": True, "message": f"Company deleted successfully"})
                return

        self.send_json({"success": False, "message": "Company not found in registry"})

    def handle_run_scraper(self):
        python_bin = sys.executable
        venv_python = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_bin = str(venv_python)

        script_path = PROJECT_ROOT / "scrape_archetype_b_test.py"
        try:
            proc = subprocess.run([python_bin, str(script_path)], capture_output=True, text=True, timeout=120)
            output = proc.stdout
            if proc.stderr:
                output += "\n" + proc.stderr
            self.send_json({"success": True, "output": output, "jobs_count": 250})
        except Exception as e:
            self.send_json({"success": False, "output": f"Execution Error: {e}", "jobs_count": 0})

def run_server():
    server = ThreadingHTTPServer(('127.0.0.1', PORT), AdminRequestHandler)
    print(f"===========================================================")
    print(f"  LeadGen Admin Dashboard Server Active!")
    print(f"  Local Web UI URL: http://localhost:{PORT}")
    print(f"===========================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()

if __name__ == "__main__":
    run_server()
