from .extract import extract
from .rules import decide, bill_key

def process(claim, emp, img_path, seen, emps=None, cached=None, record=True, fetch=True):
    """Read the bill (unless cached), apply the rules.
    Returns dict(ex, decision, reason, checks, error). Raises RuntimeError('NO_API_KEY') if no key."""
    ex, err = cached, None
    if ex is None and img_path:
        if fetch:
            try: ex = extract(img_path)
            except RuntimeError: raise
            except Exception as e: ex, err = None, f"{type(e).__name__}: {e}"
        else:
            err = "reading failed - run again to retry"
    dec, why, checks = decide(claim, ex, emp, seen, emps)
    if err: why = f"Reading failed ({err}); " + why
    if ex and record:
        k = bill_key(ex.get("vendor"), ex.get("receipt_number"), ex.get("receipt_date"))
        if k and k not in seen:
            seen[k] = f"{claim.get('claim_id') or 'earlier claim'} by {emp.get('name') or emp.get('emp_id') or 'unknown'}"
    return dict(ex=ex, decision=dec, reason=why, checks=checks, error=err)
