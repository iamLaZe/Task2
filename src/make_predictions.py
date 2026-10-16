"""python -m src.make_predictions -> predictions.csv (results cached in cache.json)."""
import json, os, sys
import pandas as pd
from dotenv import load_dotenv
from .clean import norm_image
from .data import load_emps, history_seen, claim_from_row, IMG
from .pipeline import process
from .prefetch import prefetch
load_dotenv()
if not os.getenv("GEMINI_API_KEY"): sys.exit("Set GEMINI_API_KEY in .env first (see README).")
CACHE = "cache.json"
emps = load_emps()
test = pd.read_csv("data/claims_test.csv", dtype=str).fillna("")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
rows = sorted(test.to_dict("records"), key=lambda r: (r["submitted_on"], r["claim_id"]))
paths = {r["claim_id"]: norm_image(r["image_file"], IMG) for r in rows}
prefetch([(c, p) for c, p in paths.items()], cache, CACHE)

seen = history_seen()
out = {}
# oldest first, so the LATER copy of a double-claimed bill is the one flagged
for r in rows:
    res = process(claim_from_row(r), emps.get(r["emp_id"], {}), paths[r["claim_id"]], seen, emps,
                  cache.get(r["claim_id"]), fetch=False)
    ex = res["ex"] or {}
    out[r["claim_id"]] = dict(claim_id=r["claim_id"], vendor=ex.get("vendor", ""),
        receipt_date=ex.get("receipt_date", ""), receipt_number=ex.get("receipt_number", ""),
        gstin=ex.get("gstin", ""), total_amount=ex.get("total_amount", ""),
        decision=res["decision"], reason=res["reason"])
pd.DataFrame([out[c] for c in test.claim_id]).to_csv("predictions.csv", index=False)
d = pd.DataFrame(out.values())
print("\nwrote predictions.csv", len(d), "rows"); print(d.decision.value_counts().to_string())
failed = [c for c, p in paths.items() if p and c not in cache]
if failed: print(f"{len(failed)} photos failed to read - run the same command again to retry them.")
