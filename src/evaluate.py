"""python -m src.evaluate [N] -> accuracy on first N train claims vs clerk typing."""
import difflib, json, os, sys
import pandas as pd
from dotenv import load_dotenv
from .clean import norm_image, parse_amount
from .data import load_emps, claim_from_row, IMG
from .pipeline import process
from .prefetch import prefetch
load_dotenv()
if not os.getenv("GEMINI_API_KEY"): sys.exit("Set GEMINI_API_KEY in .env first.")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
CACHE = "cache_train.json"
emps = load_emps()
tr = pd.read_csv("data/claims_train.csv", dtype=str).fillna("").head(N)
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
rows = sorted(tr.to_dict("records"), key=lambda r: (r["submitted_on"], r["claim_id"]))
paths = {r["claim_id"]: norm_image(r["image_file"], IMG) for r in rows}
prefetch(list(paths.items()), cache, CACHE)

ok = {k: [] for k in ["vendor", "date", "bill_no", "amount", "gstin"]}
ours = dict(vendor="vendor", date="receipt_date", bill_no="receipt_number", amount="total_amount", gstin="gstin")
theirs = dict(vendor="clerk_vendor", date="clerk_bill_date", bill_no="clerk_bill_no", amount="clerk_bill_amount", gstin="clerk_gstin")
out, seen, miss = [], {}, []
for r in rows:
    res = process(claim_from_row(r), emps.get(r["emp_id"], {}), paths[r["claim_id"]], seen, emps,
                  cache.get(r["claim_id"]), fetch=False)
    ex = res["ex"]
    if ex and r["clerk_bill_no"]:
        try: cd = pd.to_datetime(r["clerk_bill_date"], dayfirst=True).strftime("%Y-%m-%d")
        except Exception: cd = ""
        c = dict(
            vendor=difflib.SequenceMatcher(None, str(ex.get("vendor")).lower(), r["clerk_vendor"].lower()).ratio() > 0.8,
            date=ex.get("receipt_date") == cd,
            bill_no=str(ex.get("receipt_number")).strip().upper() == r["clerk_bill_no"].strip().upper(),
            amount=abs((ex.get("total_amount") or -1) - (parse_amount(r["clerk_bill_amount"]) or -2)) <= 1,
            gstin=(ex.get("gstin") or "") == r["clerk_gstin"].strip())
        for k, v in c.items():
            ok[k].append(v)
            if not v: miss.append((r["claim_id"], k, ex.get(ours[k]), r[theirs[k]]))
    out.append((r["status"], res["decision"], r["claim_id"], res["reason"]))
print("\nFIELD ACCURACY (vs clerk typing - clerks can be wrong too):")
for k, v in ok.items(): print(f"  {k:8s} {sum(v)/max(len(v),1):.1%}  ({len(v)} compared)")
d = pd.DataFrame(out, columns=["clerk_status", "predicted", "claim_id", "reason"])
print("\nDECISIONS (clerk status vs ours)"); print(pd.crosstab(d.clerk_status, d.predicted))
print(f"approve rate: {(d.predicted=='approve').mean():.1%}")
print("\nWrongly approved (clerk queried/rejected):")
print(d[(d.predicted == "approve") & (d.clerk_status != "approved")].to_string(index=False))
print("\nWhy we sent clerk-approved claims to review:")
print(d[(d.predicted == "review") & (d.clerk_status == "approved")][["claim_id", "reason"]].to_string(index=False))
print("\nFIELD MISMATCHES (claim, field, ours, clerk) - open the photo for each:")
for m in miss: print("  ", m)
