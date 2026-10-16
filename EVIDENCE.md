# Evidence

## How measured
- **Field accuracy:** `python -m src.evaluate 100` on the first 100 train claims (99 had a photo and a clerk entry). Compared with the clerk columns: vendor fuzzy match above 80%, date exact, bill number exact, amount within Rs 1, GSTIN exact.
- **Re-check by eye:** clerks make typos too, so I opened the photos for 10 of the 30 disagreements. The other 20 are labelled "probably clerk" below and were not opened.
- **Decisions and flags:** the same run, plus all 190 claims of `claims_test.csv` (`predictions.csv`), each with a reason.

## Field accuracy (99 claims)
| Field | Raw vs clerk | After my checks | What the misses were |
|---|---|---|---|
| vendor | 90.9% (90/99) | 99% | 8 are word order or branch suffix ("Auto Laxmi Fuels", "Highway King Dhaba - Wardha"), a scoring artefact. **1 real:** CLM-30614, the tool returned the logo "IndianOil", the bill's vendor is Shree Sai Petroleum |
| date | 93.9% (93/99) | 97 to 99% | **1 real:** CLM-30566, 19/06/26 read as 2019-06-26. Clerks were wrong on CLM-30577 and 30586 (one day off) and CLM-30543 (day and month swapped). CLM-30519 and 30600 are one day off and not opened |
| bill no. | 94.9% (94/99) | 95 to 100% | all 5 clerk numbers are one digit shorter (A/618 vs A/6178, 844 vs 8144, 01885 vs 001885); probably clerk typos, not opened |
| amount | 97.0% (96/99) | 99% | **1 real:** CLM-30562, handwritten "390/-" read as 3907 (the words say "Three Hundred Ninety"). Tool right on CLM-30421 (250.00, clerk typed 240) and CLM-30469 (items add to 335, clerk typed 435) |
| GSTIN | 93.9% (93/99) | 98% | **2 real:** CLM-30484 and CLM-30636, the tool returned blank for a GSTIN printed as 27ODUFJ1789K3ZU. Tool right on CLM-30465 and 30600 (clerk left them blank); clerk strings on CLM-30437 and 30568 are not valid GSTINs |

Reading: after checking, every field is about 95% or better, but the "after" column depends on my judgement of the 20 unopened cases, so the safe claim is the raw column plus "most misses are clerk typos". A clerk-verified sample (see memo) would settle it.

## Decisions (99 claims)
| Clerk decision | Tool approve | Tool review |
|---|---|---|
| approved | 84 | 15 |
| queried | 0 | 1 |
- **Wrongly approved: 0.** No claim the clerks queried was approved by the tool.
- **15 clerk-approved claims sent to review:**
  - 6 only because they are Rs 2,000 or more (Finance's own rule): CLM-30432, 30439, 30499, 30509, 30533, 30643.
  - Real policy problems the clerks had approved: hotel bill not in the employee's name (CLM-30418, 30492, 30535), over the lodging limit (CLM-30492, 30510), claimed Rs 568 on a Rs 368 bill (CLM-30435, Rs 200 overpaid), claimed Rs 600 on a Rs 500 bill (CLM-30479, clerk corrected it), claimed Rs 3,539 on a Rs 3,039 bill (CLM-30446, clerk corrected it).
  - **2 false reviews caused by tool misreads:** CLM-30562 (amount) and CLM-30566 (date).
- Auto-approve rate 84%.

## Test batch (190 claims)
- 153 approve, 37 review; no approved claim is Rs 2,000 or more.
- Review reasons (a claim can have several): 10 duplicates of earlier bills (Rs 6,230), 14 of Rs 2,000 or more, 11 date differences, 6 hotel bills not in the employee's name, 5 amount differences, 3 over the lodging limit, 3 with no photo, 1 colleague's vehicle.
- Train: clerks queried 6 and rejected 2 of 283. Rejections: "bill looks overwritten" (CLM-31009), "same bill as CLM-30679" (CLM-31079).

## Kinds of receipts it gets wrong
- **GSTIN read as blank** on two bills where it is printed (CLM-30484, 30636).
- **Brand logo instead of the vendor name** on fuel bills (CLM-30614).
- **Handwritten amounts** where a slash looks like a digit (CLM-30562: 390/- read as 3907).
- **Year misread** on a Rs 30 parking slip (CLM-30566: 2019).
- **Unreadable or missing:** CLM-31391 (no amount), CLM-31122 and CLM-31359 (dates misread in the test batch), and three claims with no photo (CLM-31190, 31280, 31363).
- **Other weak spots:** sideways photos (retried at 90 and 270 degrees), blur, faded thermal paper.
- **Parser bugs found and fixed:** `"Rs. 260"` read as 0.26, and ISO dates read day-first. Together they caused 31 false reviews.
