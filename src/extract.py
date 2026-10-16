import base64, io, json, os, re, time
from PIL import Image, ImageOps

PROMPT = """Read this Indian receipt/bill photo (it may be rotated). Return ONLY JSON:
{"vendor": str, "receipt_date": "YYYY-MM-DD", "receipt_number": str,
 "gstin": str, "total_amount": number, "vehicle_no": str, "billed_to": str,
 "altered": bool, "confidence": number}
Rules: use PRINTED values; ignore pen notes (doctor names, 'paid', head-count).
total_amount = final payable amount. gstin is 15 chars, "" if none.
vehicle_no "" if not on bill. altered=true ONLY if printed numbers look
overwritten/scratched/edited (not mere notes). confidence 0-1."""

GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$")
BASE = "https://generativelanguage.googleapis.com/v1beta"
_MODEL = {}
_BAD = set()   # models that answered 404 for this key (e.g. retired for new users)

class ExtractError(Exception):
    pass

def _prep(path, rotate=0):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if rotate: img = img.rotate(rotate, expand=True)
    img.thumbnail((1400, 1400))
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()

def list_models():
    """Models this key can use for generateContent."""
    import requests
    r = requests.get(f"{BASE}/models", params={"key": os.environ["GEMINI_API_KEY"], "pageSize": 200}, timeout=30)
    if r.status_code != 200:
        raise ExtractError(f"Listing models failed: HTTP {r.status_code} {r.text[:200]}")
    return [m["name"].split("/")[-1] for m in r.json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])]

def _pick_model(force=False):
    """MODEL from .env if it works, else the newest stable Flash model this key can use."""
    if _MODEL.get("m") and not force: return _MODEL["m"]
    names = list_models()
    want = os.getenv("MODEL", "").strip()
    def ver(n, suffix):
        m = re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-" + suffix, n)
        return float(m.group(1)) if m else None
    flash = sorted((n for n in names if ver(n, "flash") is not None), key=lambda n: ver(n, "flash"), reverse=True)
    lite = sorted((n for n in names if ver(n, "flash-lite") is not None), key=lambda n: ver(n, "flash-lite"), reverse=True)
    cands = ([want] if want in names else []) + flash + lite + \
            [n for n in ("gemini-flash-latest", "gemini-flash-lite-latest") if n in names]
    cands = [c for c in cands if c not in _BAD]
    if not cands:
        raise ExtractError("All Gemini models are out of free quota or unavailable for this key. "
                           "Wait for the daily reset (about midnight Pacific time), use a new key "
                           "from a different Google project, or enable billing.")
    _MODEL["m"] = cands[0]
    return cands[0]

_NOTHINK = {"on": True}

def _gen_config(model):
    """Ask for JSON and minimal 'thinking' so each read is fast."""
    cfg = {"temperature": 0, "responseMimeType": "application/json"}
    if _NOTHINK["on"]:
        if model.startswith("gemini-3"): cfg["thinkingConfig"] = {"thinkingLevel": "minimal"}
        elif model.startswith("gemini-2.5"): cfg["thinkingConfig"] = {"thinkingBudget": 0}
    return cfg

def _call(path, rotate):
    import requests
    body = {"contents": [{"parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": _prep(path, rotate)}},
                {"text": PROMPT}]}],
            }
    key = os.environ["GEMINI_API_KEY"]
    timeout = int(os.getenv("GEMINI_TIMEOUT", "120"))
    r = None
    for attempt in range(14):                      # free tier: back off on rate limits / slow replies
        model = _pick_model()
        body["generationConfig"] = _gen_config(model)
        try:
            r = requests.post(f"{BASE}/models/{model}:generateContent", params={"key": key},
                              json=body, timeout=timeout)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < 3: time.sleep(5); continue
            raise ExtractError(f"Gemini did not answer within {timeout}s (model {model}). "
                               "Try MODEL=gemini-3.5-flash in .env or check your internet.")
        if r.status_code == 400 and "thinking" in r.text.lower() and _NOTHINK["on"]:
            _NOTHINK["on"] = False; continue         # this model rejects the speed setting
        if r.status_code == 404:                   # model name not valid for this key
            _BAD.add(model); _MODEL.clear(); continue
        if r.status_code == 429:
            if re.search(r"limit: 0|PerDay|per day|daily", r.text, re.I):
                _BAD.add(model); _MODEL.clear(); continue      # this model's quota is gone -> next model
            m = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', r.text)
            if attempt < 13:
                time.sleep(min(float(m.group(1)) + 2 if m else 20, 60)); continue
        if r.status_code in (500, 503) and attempt < 13:
            time.sleep(8); continue
        break
    if r is None or r.status_code != 200:          # never print the URL: it contains the key
        raise ExtractError(f"Gemini HTTP {getattr(r, 'status_code', '?')} (model {model}): " + " ".join(getattr(r, 'text', '').split())[:400])
    try:
        txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
    except Exception:
        raise ExtractError("Gemini returned no readable answer: " + r.text[:200])

def extract(path):
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("NO_API_KEY")
    d = _call(path, 0)
    if float(d.get("confidence") or 0) < 0.5:       # maybe sideways, retry
        for rot in (90, 270):
            d2 = _call(path, rot)
            if float(d2.get("confidence") or 0) > float(d.get("confidence") or 0):
                d = d2
    g = (d.get("gstin") or "").upper().replace(" ", "")
    d["gstin"] = g if GSTIN_RE.match(g) else ""
    try: d["total_amount"] = float(d.get("total_amount"))
    except (TypeError, ValueError): d["total_amount"] = None
    return d
