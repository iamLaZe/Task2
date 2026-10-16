import os
import pandas as pd
from .clean import norm_image, parse_amount, parse_date
from .rules import bill_key
IMG = "data/images"

def load_emps():
    df = pd.read_csv("data/employees.csv", dtype=str).fillna("")
    return {r["emp_id"]: r for r in df.to_dict("records")}

def history_seen():
    """Bills Finance already processed (train) -> dict key -> who claimed it."""
    t = pd.read_csv("data/claims_train.csv", dtype=str).fillna("")
    seen = {}
    for r in t.to_dict("records"):
        try: d = pd.to_datetime(r["clerk_bill_date"], dayfirst=True).strftime("%Y-%m-%d")
        except Exception: continue
        k = bill_key(r["clerk_vendor"], r["clerk_bill_no"], d)
        if k and k not in seen:
            seen[k] = f"{r['claim_id']} by {r['emp_id']} (already paid)"
    return seen

def claim_from_row(r):
    return dict(claim_id=r["claim_id"], category=r["category"], vendor=r.get("vendor"),
                amount_claimed=parse_amount(r["amount_claimed"]),
                expense_date=parse_date(r["expense_date"]), submitted_on=r.get("submitted_on"))
