"""Decision rules. approve ONLY if every hard check passes; otherwise review."""
import re
from datetime import date
from difflib import SequenceMatcher

LIMITS = {"M1": 3000, "M2": 3000, "M3": 4500}   # per night, before GST
AUTO_LIMIT = 2000        # Finance's proposed auto-approve line
AMT_TOL = 10             # policy: rounding to nearest Rs 10 accepted
DATE_TOL_DAYS = 3        # rep types dates by hand; allow small slips

def _norm(s): return re.sub(r"[^A-Z0-9]", "", (s or "").upper())

def bill_key(vendor, number, bill_date):
    """Same bill = same vendor + bill number + date (amount deliberately NOT included:
    the Hotel Shubham bill was claimed twice with different amounts)."""
    num = _norm(number)
    if not num or not bill_date: return None
    return (re.sub(r"[^a-z0-9]", "", (vendor or "").lower()), num, bill_date)

def decide(claim, ex, emp, seen, emps=None):
    """Returns (decision, reason_text, checks). checks = list of {name, ok, hard, msg}."""
    checks = []
    def chk(name, ok, good, bad, hard=True):
        checks.append(dict(name=name, ok=bool(ok), hard=hard, msg=good if ok else bad))

    if ex is None:
        chk("Photo readable", False, "", "No readable bill photo - query rep to re-upload")
        return "review", "No readable bill photo - query rep to re-upload", checks
    amt, cl = ex.get("total_amount"), claim.get("amount_claimed")
    if amt is None:
        chk("Bill amount read", False, "", "Could not read the bill amount")
        return "review", "Could not read the bill amount", checks
    chk("Photo readable", True, "Bill photo read", "")

    conf = float(ex.get("confidence") or 0)
    chk("Read confidence", conf >= 0.8, f"Read confidence {conf:.0%}",
        f"Low read confidence ({conf:.0%}) - photo unclear")
    chk("Not altered", not ex.get("altered"), "No sign of overwriting",
        "Printed numbers look overwritten / altered")

    if cl is None:
        chk("Amount matches", False, "", "No claimed amount to compare with the bill")
    else:
        chk("Amount matches", abs(amt - cl) <= AMT_TOL,
            f"Claimed Rs {cl:g} matches bill Rs {amt:g}",
            f"Claimed Rs {cl:g} but bill says Rs {amt:g}")

    bd, ed = ex.get("receipt_date"), claim.get("expense_date")
    if not bd:
        chk("Bill date", False, "", "Bill date not found")
    elif ed:
        try:
            gap = abs((date.fromisoformat(bd) - date.fromisoformat(ed)).days)
        except ValueError:
            gap = 0
        chk("Date matches", gap <= DATE_TOL_DAYS, "Bill date matches expense date",
            f"Bill dated {bd} but expense date typed {ed}")
        sub = claim.get("submitted_on")
        if sub and bd > sub:
            chk("Date not in future", False, "", f"Bill date {bd} is after submission {sub}")
    else:
        chk("Date matches", True, "No expense date given", "", hard=False)

    cat = claim.get("category")
    key = bill_key(ex.get("vendor"), ex.get("receipt_number"), bd)
    if key is None:
        if cat == "Parking":
            chk("Bill number", True, "Parking slip without number - allowed", "", hard=False)
        else:
            chk("Bill number", False, "", "Bill number not found - cannot check for duplicates")
    else:
        chk("Not a duplicate", key not in seen, "Bill not seen before",
            f"DUPLICATE - same bill already claimed: {seen.get(key)}")

    if cat == "Fuel":
        veh = _norm(emp.get("vehicle_no"))
        on_bill = _norm(ex.get("vehicle_no"))
        if not on_bill:
            chk("Vehicle number", False, "", "Fuel bill shows no vehicle number")
        elif veh and veh in on_bill:
            chk("Vehicle number", True, "Vehicle number matches the claimant", "")
        else:
            other = next((e.get("name") for e in (emps or {}).values()
                          if _norm(e.get("vehicle_no")) and _norm(e["vehicle_no"]) in on_bill), None)
            chk("Vehicle number", False, "",
                f"Bill shows {other}'s vehicle - colleague's bill?" if other
                else "Vehicle number on bill does not match the claimant")
    if cat == "Food":
        chk("Food limit", amt <= 2500, "Within Rs 2,500 per bill",
            f"Food bill Rs {amt:g} exceeds Rs 2,500 - needs prior approval")
    if cat == "Lodging":
        lim = LIMITS.get(emp.get("grade"), 3000)
        chk("Lodging limit", amt <= lim * 1.18, f"Within grade limit Rs {lim}/night + GST",
            f"Rs {amt:g} is over the Rs {lim}/night (+GST) limit")
        chk("GST invoice", bool(ex.get("gstin")), "GSTIN present", "No GSTIN - not a GST tax invoice")
        first = (emp.get("name") or "").split()[0].lower() if emp.get("name") else ""
        chk("Billed to employee", bool(first) and first in (ex.get("billed_to") or "").lower(),
            "Hotel bill is in the employee's name", "Hotel bill is not in the employee's name")

    chk("Under Rs 2,000", amt < AUTO_LIMIT, "Under the Rs 2,000 auto-approve line",
        f"Rs {amt:g} is Rs 2,000 or more - clerk check", hard=True)

    # vendor typed by rep vs on bill: informational only
    rv, bv = (claim.get("vendor") or ""), (ex.get("vendor") or "")
    if rv and bv:
        sim = SequenceMatcher(None, rv.lower(), bv.lower()).ratio()
        chk("Vendor", sim >= 0.5, "Vendor matches what rep typed",
            f"Rep typed '{rv}', bill says '{bv}'", hard=False)

    bad = [c["msg"] for c in checks if c["hard"] and not c["ok"]]
    return ("review", "; ".join(bad), checks) if bad else ("approve", "All checks passed", checks)
