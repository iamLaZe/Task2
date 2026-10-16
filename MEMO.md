# Memo: receipt reading tool
**To:** Nilesh Agrawal, Finance Controller  **From:** Kabir Nanda  **Re:** What to switch on, and what it saves

## Recommendation
1. **Use the tool to fill vendor, bill date, bill no., GSTIN and amount.** Clerks check a pre-filled screen instead of typing.
2. **Do not auto-approve on "under Rs 2,000".** Approve only when every check passes: photo readable, amount within Rs 10 of the bill, date matches, not a duplicate, fuel bill shows the claimant's vehicle, hotel bill is a GST invoice in the employee's name, within policy limits. 90% of claims are under Rs 2,000, so the cap alone barely filters anything, and that is where the problems are.
3. Pen notes, Rs 10 rounding and the daily Rs 30 parking slips are allowed by policy and are **not** flagged.

**Why not the Rs 2,000 rule.** In the latest Nagpur batch (190 claims) the tool sent 37 to a clerk; 18 of those are under Rs 2,000 (Rs 7,842) and would have been paid under the blanket rule. They include **10 bills already claimed before (Rs 6,230)**, 1 colleague's fuel bill, and claims where the amount differs from the bill. Priya's "same Hotel Shubham bill twice with different amounts" is exactly this: the duplicate check ignores the amount. All 14 claims of Rs 2,000+ also go to a clerk.

## What it saves (Nagpur batch; company figures are my ×10 scaling, assumes Nagpur is typical)
| Item | Figure |
|---|---|
| Typing cost today | 2,400 claims x 3.5 min = 140 hrs/month, about Rs 25,600 (Rs 10.7/claim) |
| Claims a clerk need not open | 153 of 190 = 80%; about 112 hrs/month, **about Rs 20,000/month** company-wide |
| Wrong or doubtful payments stopped | Duplicates Rs 6,230 + amount mismatches Rs 3,302 + colleague bill Rs 300 = about Rs 9,800 in this batch, **flagged, not yet confirmed**; roughly Rs 1 lakh per similar batch company-wide, if confirmed |
| Cost per photo | about Rs 0.3 on a Gemini Flash-class model (estimate; check the first invoice). Well under the Rs 10 clerk cost |
| Cost of false queries | At most a few x Rs 45; the tool sends doubtful claims to a clerk, not back to the rep |

On 99 train claims, the clerks approved 3 hotel bills not in the employee's name, 2 over the lodging limit and one claim of Rs 568 against a Rs 368 bill (Rs 200 overpaid); the tool sent all of them to a clerk and approved nothing the clerks had queried. Clerk typing errors (wrong amounts, dropped digits in bill numbers, dates one day off) also showed up, so the tool is not being compared with a perfect baseline.

Honest notes: clerk salaries are fixed, so the typing saving is **cash only if the two clerks are redeployed** (for example to chasing duplicates). The recovered-money figure is the bigger prize, but it is upper-bound until a clerk opens the flagged bills. Auto-approved claims are paid in the weekly run, so reps are never slower than today.

## What I need from you
1. Approval to replace "under Rs 2,000" with "passes all checks".
2. About 200 bills verified by a clerk, to measure field accuracy properly (on 99 train claims the raw match was amount 97%, bill no. 95%, date and GSTIN 94%, vendor 91%; most misses were clerk typos, but a verified sample would settle it).
3. A decision on the duplicates: recover from salary, or warn first (policy section 8).
4. Confirmation that daily Rs 30 parking for Rohan, Pooja and Harshal is normal.
5. An API key and a monthly budget (a few hundred rupees).
