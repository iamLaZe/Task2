# Tarang receipt reader
Reads a bill photo with a Gemini vision model (newest Flash model the key can use; override with `MODEL=` in `.env`), then applies rule checks to decide `approve` or `review`. Without a key the app starts and returns a polite "no API key" message.

## Run (clean machine, Python 3.10+)
```
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # put GEMINI_API_KEY in .env (app starts without it, shows a polite error)
uvicorn src.app:app --port 8000    # open http://localhost:8000
```
API: `POST /api/read` (multipart: photo, category, amount_claimed, expense_date, grade, vehicle_no, name)
-> `{fields, decision, reason}`.

## The screen
Pick a claim from the latest batch (the photo loads automatically if it is in `data/images/`), or
drop any bill photo and type the claim. You get APPROVE / REVIEW, the fields read from the bill
next to what the rep typed, and a pass/fail list of checks. Duplicate memory starts with all
already-paid bills and grows as you test; use "Reset duplicate memory" between demos.

## Regenerate predictions / evaluate
Put the receipt photos in `data/images/`, then:
```
python -m src.make_predictions     # writes predictions.csv (cached in cache.json)
python -m src.evaluate 100         # accuracy on 100 train claims
```

## Decisions I made
- `approve` only if ALL checks pass (photo readable, amount within Rs 10 of bill, date matches,
  not a duplicate vs train+test, fuel bill shows vehicle no., lodging GST invoice/name/limit,
  food <= 2500, high read confidence, not altered, amount < 2000). Everything else -> `review`.
- NOT a blanket "under Rs 2,000 = approve": duplicates and altered bills hide in small claims.
- Pen notes, Rs 10 rounding and daily Rs 30 parking are allowed by policy and are not flagged.
- Photos: path stripped, .jpg/.jpeg both tried, EXIF + 90/270 retry for sideways, missing -> review.
