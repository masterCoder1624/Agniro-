# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth_routes, user_routes, job_routes, filter_routes, mining_routes, url_routes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include all routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(job_routes.router, prefix="/job", tags=["Job"])
app.include_router(filter_routes.router, prefix="/filter", tags=["Filter"])
app.include_router(mining_routes.router, prefix="/mining", tags=["Mining"])
app.include_router(url_routes.router, prefix="/url", tags=["Url"])

@app.get("/")
def root():
    return {"message": "backend is running great dont worry  : 🚀"}

import os
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import Body, HTTPException
from pymongo import MongoClient


def _get_mongo_client():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")   # raises if unreachable
    return client


@app.get("/jobs")
def get_jobs():
    try:
        client = _get_mongo_client()
        db = client["scraping_leads"]
        collection = db["requirements"]

        # Sort by _id descending to ensure new data appears on top
        cursor = collection.find({}).sort("_id", -1)
        
        # Build filter logic
        filters_list = list(db["filters"].find({"active": True}))
        def is_blocked(doc):
            for f in filters_list:
                sec = f.get("sector", "")
                loc = f.get("location", "")
                emp = f.get("employees", "")
                
                doc_sec = str(doc.get("company_sector") or doc.get("industry") or doc.get("company_industry") or "")
                doc_loc = str(doc.get("location") or "")
                doc_emp = str(doc.get("company_employees") or doc.get("company_size") or "")
                
                if sec and sec.lower() in doc_sec.lower(): return True
                if loc and loc.lower() in doc_loc.lower(): return True
                if emp and emp.lower() in doc_emp.lower(): return True
            return False

        jobs_data = []
        for doc in cursor:
            if is_blocked(doc):
                continue
            
            # Match the new DB structure while keeping fallbacks for the old structure
            jobs_data.append({
                "id": str(doc["_id"]),
                "time": doc.get("posted") or doc.get("posted_date") or "--",
                "title": doc.get("title") or doc.get("job_title") or "--",
                "insides": doc.get("location") or "--",
                "company": doc.get("company") or doc.get("company_name") or "--",
                "profile_url": doc.get("url") or doc.get("job_url") or "--",
                "name": doc.get("company") or doc.get("company_name") or "--",
                "designation": doc.get("company_sector") or doc.get("industry") or doc.get("company_industry") or "--",
                "email": doc.get("company_url") or doc.get("company_website") or "--",
                "location": doc.get("location") or "--",
                "employees": doc.get("company_employees") or doc.get("company_size") or "--",
                "followers": doc.get("company_followers") or doc.get("followers") or "--",
                "status": "Delete"
            })

        return jobs_data
    except Exception as e:
        print(f"Failed to fetch jobs from MongoDB: {e}")
        return []

@app.get("/urls")
def get_urls(platform: str = "linkedin"):
    """
    Fetches the URLs from MongoDB for the specified platform.
    """
    try:
        client = _get_mongo_client()
        db = client["users_db"]
        collection = db["engines"]

        # Sort by _id descending to ensure new data appears on top
        cursor = collection.find({"platform": platform}).sort("_id", -1)
        urls_data = []
        for doc in cursor:
            urls_data.append({
                "id": str(doc["_id"]),
                "url": doc.get("url", "--"),
                "platform": doc.get("platform", platform),
                "status": doc.get("status", "active"),
                "created_at": doc.get("created_at", doc.get("submitted_at", "--"))
            })

        return urls_data
    except Exception as e:
        print(f"[get-urls] Failed to fetch URLs from MongoDB: {e}")
        return []


@app.post("/add-url")
def add_url(payload: dict = Body(...)):
    """
    Accepts { "url": "...", "platform": "..." } from the Flutter dashboard,
    save sit to pending job i the mongoDB, and return a sucess job.
    """
    url: str = payload.get("url", "").strip()
    platform: str = payload.get("platform", "linkedin").strip().lower()

    # ── Basic server-side validation ──────────────────────────────────────────
    if not url:
        raise HTTPException(status_code=422, detail="URL must not be empty.")

    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=422, detail="URL must start with http:// or https://")

    # ── Persist to MongoDB ────────────────────────────────────────────────────
    try:
        client = _get_mongo_client()
        db = client["users_db"]
        pending = db["engines"]

        doc = {
            "url": url,
            "platform": platform,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        pending.insert_one(doc)
        print(f"[add-url] Queued for scraping: {url} ({platform})")
    except Exception as e:
        print(f"[add-url] Failed to save URL to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Could not save URL to database.")

    return {"message": "URL added successfully.", "url": url}


@app.delete("/delete-job/{job_id}")
def delete_job(job_id: str):
    """
    Deletes a job document from sorted_complete_leads by its MongoDB _id.
    """
    try:
        obj_id = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format.")

    try:
        client = _get_mongo_client()
        db = client["scraping_leads"]
        collection = db["requirements"]

        result = collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found.")

        print(f"[delete-job] Deleted job: {job_id}")
        return {"message": "Job deleted successfully.", "id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[delete-job] Failed to delete job: {e}")
        raise HTTPException(status_code=500, detail="Could not delete job from database.")


@app.delete("/delete-all-jobs")
def delete_all_jobs():
    """
    Deletes all job documents from sorted_complete_leads collection.
    """
    try:
        client = _get_mongo_client()
        db = client["scraping_leads"]
        collection = db["requirements"]

        result = collection.delete_many({})
        print(f"[delete-all-jobs] Deleted {result.deleted_count} jobs.")
        return {
            "message": "All jobs deleted successfully.", 
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        print(f"[delete-all-jobs] Failed to delete all jobs: {e}")
        raise HTTPException(status_code=500, detail="Could not clear jobs from database.")


@app.delete("/delete-url/{url_id}")
def delete_url(url_id: str):
    """
    Deletes a URL document from pending_urls by its MongoDB _id.
    """
    try:
        obj_id = ObjectId(url_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL ID format.")

    try:
        client = _get_mongo_client()
        db = client["users_db"]
        collection = db["engines"]

        result = collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="URL not found.")

        print(f"[delete-url] Deleted URL: {url_id}")
        return {"message": "URL deleted successfully.", "id": url_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[delete-url] Failed to delete URL: {e}")
        raise HTTPException(status_code=500, detail="Could not delete URL from database.")


# ─── Filters ───────────────────────────────────────────────────────────────

@app.post("/add-filter")
def add_filter(payload: dict = Body(...)):
    """
    Adds a new company blocking filter.
    """
    sector: str = payload.get("sector", "").strip()
    location: str = payload.get("location", "").strip()
    employees: str = payload.get("employees", "").strip()

    if not sector and not location and not employees:
        raise HTTPException(status_code=422, detail="At least one field is required.")

    doc = {
        "sector": sector,
        "location": location,
        "employees": employees,
        "active": True
    }
    try:
        client = _get_mongo_client()
        db = client["scraping_leads"]
        db["filters"].insert_one(doc)
    except Exception as e:
        print(f"[add-filter] Error: {e}")
        raise HTTPException(status_code=500, detail="Could not save filter.")

    return {"message": "Filter added successfully."}

@app.get("/filters")
def get_filters():
    try:
        client = _get_mongo_client()
        db = client["scraping_leads"]
        cursor = db["filters"].find({}).sort("_id", -1)
        filters_data = []
        for doc in cursor:
            filters_data.append({
                "id": str(doc["_id"]),
                "sector": doc.get("sector", ""),
                "location": doc.get("location", ""),
                "employees": doc.get("employees", ""),
                "active": doc.get("active", True)
            })
        return filters_data
    except Exception as e:
        print(f"[get-filters] Error: {e}")
        return []

@app.delete("/delete-filter/{filter_id}")
def delete_filter(filter_id: str):
    try:
        obj_id = ObjectId(filter_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid filter ID.")
    try:
        client = _get_mongo_client()
        db = client["scraping_leads"]
        result = db["filters"].delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Filter not found.")
        return {"message": "Filter deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[delete-filter] Error: {e}")
        raise HTTPException(status_code=500, detail="Could not delete filter.")


import subprocess
import sys

# ─── Mining Control Endpoints ───────────────────────────────────────────────

mining_process = None

import os

@app.post("/start-linkedin-mining")
def start_linkedin_mining():
    global mining_process
    if mining_process and mining_process.poll() is None:
        print("[mining] LinkedIn mining is already running")
        return {"message": "LinkedIn mining is already running"}
        
    # Corrected path to scrap.py in the plugs folder
    script_path = r"d:\new_app\plugs\scrap.py"
    try:
        # Run continuously in the background using the same python executable
        mining_process = subprocess.Popen(
            [sys.executable, script_path, "--platform", "linkedin", "--continuous"]
        )
        print(f"[mining] LinkedIn mining started with PID: {mining_process.pid}")
        return {"message": "LinkedIn mining started"}
    except Exception as e:
        print(f"[mining] Failed to start scraper: {e}")
        return {"message": f"Failed to start scraper: {e}"}

@app.post("/stop-linkedin-mining")
def stop_linkedin_mining():
    global mining_process
    if mining_process and mining_process.poll() is None:
        mining_process.terminate()
        try:
            mining_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            mining_process.kill()
        print("[mining] LinkedIn mining stopped")
        mining_process = None
        return {"message": "LinkedIn mining stopped"}
    else:
        print("[mining] LinkedIn mining is not running")
        return {"message": "LinkedIn mining is not running"}

@app.post("/start-indeed-mining")
def start_indeed_mining():
    global mining_process
    if mining_process and mining_process.poll() is None:
        print("[mining] Indeed mining is already running")
        return {"message": "Indeed mining is already running"}
        
    # Corrected path to scrap.py in the plugs folder
    script_path = r"d:\new_app\plugs\scrap.py"
    try:
        # Run continuously in the background using the same python executable
        mining_process = subprocess.Popen(
            [sys.executable, script_path, "--platform", "indeed", "--continuous"]
        )
        print(f"[mining] Indeed mining started with PID: {mining_process.pid}")
        return {"message": "Indeed mining started"}
    except Exception as e:
        print(f"[mining] Failed to start scraper: {e}")
        return {"message": f"Failed to start scraper: {e}"}

@app.post("/stop-indeed-mining")
def stop_indeed_mining():
    global mining_process
    if mining_process and mining_process.poll() is None:
        mining_process.terminate()
        try:
            mining_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            mining_process.kill()
        print("[mining] Indeed mining stopped")
        mining_process = None
        return {"message": "Indeed mining stopped"}
    else:
        print("[mining] Indeed mining is not running")
        return {"message": "Indeed mining is not running"}
@app.get("/jobs/export")
def export_jobs():
    """
    Backend Export: Generates an Excel file for all jobs.
    Useful for large datasets where client-side export might hit memory limits.
    """
    try:
        import pandas as pd
        from io import BytesIO
        from fastapi.responses import Response

        client = _get_mongo_client()
        db = client["scraping_leads"]
        collection = db["requirements"]
        
        cursor = collection.find({}).sort("_id", -1)
        
        # Build filter logic
        filters_list = list(db["filters"].find({"active": True}))
        def is_blocked(doc):
            for f in filters_list:
                sec = f.get("sector", "")
                loc = f.get("location", "")
                emp = f.get("employees", "")
                
                doc_sec = str(doc.get("company_sector") or doc.get("industry") or doc.get("company_industry") or "")
                doc_loc = str(doc.get("location") or "")
                doc_emp = str(doc.get("company_employees") or doc.get("company_size") or "")
                
                if sec and sec.lower() in doc_sec.lower(): return True
                if loc and loc.lower() in doc_loc.lower(): return True
                if emp and emp.lower() in doc_emp.lower(): return True
            return False

        # We reuse the same mapping logic as the main /jobs endpoint
        jobs_data = []
        for doc in cursor:
            if is_blocked(doc):
                continue
            jobs_data.append({
                "Time": doc.get("posted") or doc.get("posted_date") or "--",
                "Title": doc.get("title") or doc.get("job_title") or "--",
                "Insides": doc.get("location") or "--",
                "Company": doc.get("company") or doc.get("company_name") or "--",
                "Profile URL": doc.get("url") or doc.get("job_url") or "--",
                "Name": doc.get("company") or doc.get("company_name") or "--",
                "Designation": doc.get("company_sector") or doc.get("industry") or doc.get("company_industry") or "--",
                "Email": doc.get("company_url") or doc.get("company_website") or "--",
                "Location": doc.get("location") or "--",
                "Employees": doc.get("company_employees") or doc.get("company_size") or "--",
                "Followers": doc.get("company_followers") or doc.get("followers") or "--",
                "Status": "Delete"
            })

        if not jobs_data:
            raise HTTPException(status_code=404, detail="No jobs to export")

        df = pd.DataFrame(jobs_data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Jobs')
        output.seek(0)
        headers = {'Content-Disposition': 'attachment; filename="scraped_jobs.xlsx"'}
        return Response(
            content=output.getvalue(), 
            headers=headers, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except ImportError:
        raise HTTPException(status_code=501, detail="Backend Excel support not installed (pandas/openpyxl missing).")
    except Exception as e:
        print(f"[export-jobs] Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Excel file.")
