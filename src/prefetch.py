"""Read many photos in parallel, with a progress line per photo and a disk cache."""
import json, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .extract import extract

def prefetch(jobs, cache, cache_file, workers=None):
    """jobs: list of (id, photo_path). Fills cache[id] and saves it to cache_file."""
    todo = [(i, p) for i, p in jobs if p and i not in cache]
    workers = workers or int(os.getenv("WORKERS", "2"))
    print(f"Reading {len(todo)} photos ({len(jobs) - len(todo)} cached/no photo), {workers} at a time...", flush=True)
    def one(i, p):
        s = time.time()
        try: return i, extract(p), time.time() - s, None
        except Exception as e: return i, None, time.time() - s, f"{type(e).__name__}: {e}"
    done = 0
    with ThreadPoolExecutor(workers) as pool:
        for f in as_completed([pool.submit(one, i, p) for i, p in todo]):
            i, d, dt, err = f.result(); done += 1
            if d:
                cache[i] = d
                with open(cache_file, "w") as fh: json.dump(cache, fh)
                msg = "ok" if d else "FAILED " + " ".join(str(err).split())[:300]
                print(f"[{done}/{len(todo)}] {i}  {msg}  ({dt:.0f}s)", flush=True)