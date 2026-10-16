import os, re
from dateutil import parser as dp

_INDEX = {}

def _index(img_dir):
    """All image files under img_dir (any depth) -> list of (lowercase stem, path)."""
    if img_dir not in _INDEX:
        items = []
        for root, _, files in os.walk(img_dir):
            for f in files:
                stem, ext = os.path.splitext(f)
                if ext.lower() in (".jpg", ".jpeg", ".png", ".webp", ".heic"):
                    items.append((stem.lower().strip(), os.path.join(root, f)))
        _INDEX[img_dir] = items
    return _INDEX[img_dir]

def norm_image(name, img_dir):
    """Find the photo for an image_file value. Handles phone paths, .jpg/.jpeg, case,
    ' (1)' copies and prefixes added to the file name. None = photo missing."""
    if not isinstance(name, str) or not name.strip():
        return None
    base = os.path.basename(name.replace("\\", "/").strip())
    stem = os.path.splitext(base)[0].lower().strip()
    stem = re.sub(r"\s*\(\d+\)$", "", stem)
    items = _index(img_dir)
    exact = [p for s, p in items if re.sub(r"\s*\(\d+\)$", "", s) == stem]
    if exact: return exact[0]
    loose = [p for s, p in items if stem and stem in s]
    return loose[0] if len(loose) == 1 else None

def parse_amount(s):
    """'Rs. 1,250', '2,352.00', '588/-' -> float. Takes the first real number."""
    if s is None: return None
    m = re.search(r"\d+(?:\.\d+)?", str(s).replace(",", ""))
    return float(m.group(0)) if m else None

def parse_date(s):
    """ISO (YYYY-MM-DD) is read as-is; everything else is day-first (Indian style)."""
    s = str(s).strip()
    try:
        if re.match(r"^\d{4}-\d{1,2}-\d{1,2}", s):
            return dp.parse(s, yearfirst=True, dayfirst=False).date().isoformat()
        return dp.parse(s, dayfirst=True).date().isoformat()
    except Exception:
        return None
