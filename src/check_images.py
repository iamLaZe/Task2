"""python -m src.check_images  -> are the photos found? is the API key working?"""
import os, sys
import pandas as pd
from dotenv import load_dotenv
from .clean import norm_image, _index
from .data import IMG
load_dotenv()
files = _index(IMG)
print(f"Photos found in {IMG}: {len(files)}")
print("Example files on disk:", [os.path.basename(p) for _, p in files[:3]])
for name in ("claims_train", "claims_test"):
    d = pd.read_csv(f"data/{name}.csv", dtype=str).fillna("")
    found = d.image_file.map(lambda x: norm_image(x, IMG) is not None)
    print(f"{name}: {found.sum()}/{len(d)} claims have a photo on disk")
    print("  e.g. not found:", d.image_file[~found].head(3).tolist())
print("GEMINI_API_KEY set:", bool(os.getenv("GEMINI_API_KEY")))
p = next((p for _, p in files), None)
if p and os.getenv("GEMINI_API_KEY"):
    from .extract import extract, list_models
    try: print("Models your key can use:", list_models())
    except Exception as e: print("Could not list models:", e)
    import time; t = time.time()
    try: print("Test read OK:", extract(p), f"({time.time()-t:.0f}s)")
    except Exception as e: print("Test read FAILED:", type(e).__name__, e)
