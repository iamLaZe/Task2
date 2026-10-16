import os, tempfile
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .clean import norm_image, parse_amount, parse_date
from .data import load_emps, history_seen, claim_from_row, IMG
from .pipeline import process
load_dotenv()

app = FastAPI(title="Tarang Receipt Reader")
app.mount("/static", StaticFiles(directory="static"), name="static")
EMPS = load_emps()
HISTORY = history_seen()
SEEN = dict(HISTORY)               # bills seen so far (history + this session)
try:
    SAMPLES = pd.read_csv("data/claims_test.csv", dtype=str).fillna("").to_dict("records")
except Exception:
    SAMPLES = []

def has_key(): return bool(os.getenv("GEMINI_API_KEY"))

@app.get("/")
def home(): return FileResponse("static/index.html")

@app.get("/api/status")
def status():
    return {"has_key": has_key(), "model": os.getenv("MODEL", "gemini-2.5-flash"),
            "history_bills": len(HISTORY), "session_bills": len(SEEN) - len(HISTORY)}

@app.get("/api/employees")
def employees(): return list(EMPS.values())

@app.get("/api/samples")
def samples():
    return [dict(r, has_image=bool(norm_image(r["image_file"], IMG))) for r in SAMPLES]

@app.get("/api/sample-image/{claim_id}")
def sample_image(claim_id: str):
    r = next((r for r in SAMPLES if r["claim_id"] == claim_id), None)
    p = norm_image(r["image_file"], IMG) if r else None
    return FileResponse(p) if p else JSONResponse({"error": "No photo on the server for this claim."}, 404)

@app.post("/api/reset")
def reset():
    SEEN.clear(); SEEN.update(HISTORY)
    return {"ok": True}

@app.post("/api/read")
async def read(photo: UploadFile | None = File(None),
               claim_id: str = Form(""), emp_id: str = Form(""), category: str = Form("Food"),
               vendor: str = Form(""), expense_date: str = Form(""), amount_claimed: str = Form(""),
               rep_comment: str = Form(""), submitted_on: str = Form("")):
    """Receipt photo + the claim as the rep entered it -> fields, decision, reasons."""
    if not has_key():
        return JSONResponse({"error": "No API key configured. Add GEMINI_API_KEY to the .env file "
                             "and restart the server (see README)."}, 503)
    tmp = None
    try:
        if photo is not None and photo.filename:
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            tmp.write(await photo.read()); tmp.close(); path = tmp.name
        else:
            r = next((r for r in SAMPLES if r["claim_id"] == claim_id), None)
            path = norm_image(r["image_file"], IMG) if r else None
            if not path:
                return JSONResponse({"error": "Please attach a receipt photo."}, 422)
        claim = dict(claim_id=claim_id or None, category=category, vendor=vendor,
                     amount_claimed=parse_amount(amount_claimed),
                     expense_date=parse_date(expense_date) if expense_date else None,
                     submitted_on=submitted_on or None)
        emp = EMPS.get(emp_id, {})
        res = process(claim, emp, path, SEEN, EMPS)
    except Exception as e:
        return JSONResponse({"error": f"Could not process this receipt: {e}"}, 500)
    finally:
        if tmp: os.unlink(tmp.name)
    if res["error"] and res["ex"] is None:
        return JSONResponse({"error": "The reading service failed or the photo is unreadable "
                             f"({res['error']}). Try again in a minute.", "decision": "review",
                             "reason": res["reason"]}, 502)
    return {"fields": res["ex"], "decision": res["decision"], "reason": res["reason"],
            "checks": res["checks"], "claim": claim, "employee": emp.get("name")}
