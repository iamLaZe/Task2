# Submission Form – Task 2

## 1. Github Repo URL

https://github.com/iamLaZe/Task2

## 2. What did you build, and what decision does it support for Nilesh? State the number and the rupees.

I built a tool that reads a bill photo and fills in the vendor, date, bill number, GSTIN and amount. It then compares the bill with what the rep claimed and says approve or review, with a reason.

The decision it supports for Nilesh is this: don’t approve everything under Rs 2,000. Approve only the claims where every check passes. On the latest batch of 190 claims, the tool approved 153 and sent 37 to a clerk. Among those 37 were ten bills that had already been claimed before, worth about Rs 6,200. A plain “under Rs 2,000” rule would have paid them.

On time, a clerk costs Rs 38,000 a month and spends about 3.5 minutes per claim, which works out to roughly Rs 10.7 a claim, or about Rs 25,600 a month at 2,400 claims. Since the tool approved around 80% of the latest batch without a clerk opening them, about Rs 20,000 a month of that typing time is freed, assuming Nagpur is typical of the company. Salaries are fixed, so that turns into cash only if the clerks are moved to other work, such as chasing the duplicates the tool finds.

## 3. What do you expect predictions.csv to score on the hidden answers, field by field and on the approve/review decision, and why? Say how you estimated it.

**Fields:** I expect amount to be the strongest, in the mid-to-high nineties. Date and bill number should come next, in the mid-nineties. GSTIN and vendor should be a little lower, in the low-to-mid nineties.

**Decision:** I expect very few wrong approvals, because the tool is strict. The error I expect is the other direction: some claims sent to a clerk that were actually fine, because a field was misread.

**How I estimated it:** I ran the tool on past claims where the clerks had typed the answers, compared the two, and opened the photos for the disagreements. Many disagreements turned out to be clerk typing mistakes, not tool mistakes, so the real accuracy is probably a bit better than the raw match. The test batch has no answers, so this is an estimate from the older claims.

## 4. How do you know it works? What you measured it against, how you got those answers, how many receipts, and the kinds of receipt it gets wrong.

I measured it against the clerk columns in the past claims file, which is what Tarang’s clerks typed from each photo. I ran the tool on the photos of the first hundred of those claims, and 99 had both a photo and a clerk entry to compare. Because clerks make typing mistakes too, I opened the photos for about ten of the disagreements to see who was right. Most of those turned out to be clerk slips, such as a wrong amount, a dropped digit in a bill number or a date one day off. I did not open the rest, so I treated them as probable clerk typos, which is a judgement. On this sample the tool matched the clerks in the nineties on every field, and it never approved a claim the clerks had queried.

The kinds of receipt it gets wrong are handwritten amounts where a slash looks like a digit (“390/-” read as 3,907), fuel bills where the brand logo is taken as the vendor, a year misread on a small parking slip, a GSTIN left blank on two bills where it was printed, and claims with no photo or an unreadable one.

## 5. Did you change, narrow, or push back on Nilesh's ask? What, when, and why.

Yes. Nilesh asked for anything under Rs 2,000 to be approved straight from the photo. I changed that to “approve only if every check passes”, and I made that choice while building, since there was no one to ask. Almost all claims are small, so the Rs 2,000 line filters very little, and the duplicates, wrong amounts and colleagues’ bills are mostly in the small claims. Claims of Rs 2,000 or more still go to a clerk, as he wanted.

I also did not promise the 95% accuracy he asked for. I showed what I measured and asked for a sample checked by his clerks to settle it. And I told him the time saved is only real money if the clerks are moved to other work.

## 6. What is wrong with what you are handing us, or with the data we handed you? Be specific: bugs, shortcuts, files or columns you did not trust, photos or rows that looked wrong.

My first version had two bugs. It read “Rs. 260” as 0.26, and it mixed up day and month in some dates. Together they sent about thirty good claims to review. I fixed both before the final file. The tool still misreads some bills, as I described in answer 4. One photo failed on the first run and needed a retry, and the amount on one claim could not be read at all.

My checking is also thin. I measured on about a hundred past claims, and I opened only some of the disagreements, so the accuracy figures lean on my judgement about the rest. The cost per photo and the company-wide savings are estimates, not billed or measured figures. The duplicate memory only knows the past claims and the current session, and it forgets everything when the server restarts.

On the data, I did not trust the clerk columns as the truth. They contain slips, such as wrong amounts, digits dropped from bill numbers and dates a day off, and the clerks approved some claims that broke the policy, like a hotel bill not in the employee’s name and a claim Rs 200 above its bill. The rep-typed dates and amounts come in many formats, some image names carried old phone paths or the wrong extension, and a few photos never arrived.

## 7. What does checking one claim cost, and what would a month cost at Tarang's volume (about 2,400 photo claims a month)? Show the arithmetic.

Each claim is one call to a paid vision model. I did not get a real invoice, so I am assuming about Rs 0.3 per photo. At 2,400 claims a month, that is 2,400 × Rs 0.3, about Rs 720 a month. For comparison, a clerk costs about Rs 10.7 per claim (Rs 38,000 a month and 3.5 minutes per claim), which is about Rs 25,600 a month for the same volume. Even if my estimate is several times too low, the tool stays far cheaper than typing and well under Nilesh’s limit of what a clerk costs per photo. Reading is the only paid step; the checks are plain code and cost nothing.

## 8. What did you deliberately leave out, and why that rather than something else?

I left out any login, database or connection to the expense app, because the brief asked for one endpoint and one screen and those would cost time without helping the decision. I did not train or fine-tune a model, since a ready-made vision model plus clear rules was enough at this volume and could be checked by hand. I did not check GSTINs against the government registry, because it needs outside access and nobody asked for it. And I did not read every past claim: I chose a smaller set so I could look at the disagreements myself, which tells me more than a bigger number I never opened.

## 9. Anything you built or found that nobody asked for?

I built a duplicate check that ignores the amount, so the same bill claimed twice with slightly different amounts is still caught, which is the Hotel Shubham case Priya described. I also added a check that a fuel bill shows the claimant’s own vehicle, and names the colleague when it shows someone else’s. For hotels, it checks that the bill is in the employee’s name and within the grade limit, and it also looks for bills that have been altered. I made sure not to flag things the policy allows, such as pen notes, rounding to the nearest Rs 10 and the daily Rs 30 parking slips. In the data, I found that the clerks had approved some claims that broke the policy, and the tool would have stopped them.

## 10. What did you use AI for? Which tools and models, where they helped, where they misled you, what you threw away. Link your three-minute screen recording here.

Inside the product, a Gemini vision model reads the bill photo. While building, I used Claude to find bugs, to check results against the photos, and to draft the memo and the evidence file, which I then changed substantially to match what I understood the task to need. It helped most in finding the amount and date bugs and in telling real tool errors apart from clerk typos. It misled me in places. Early drafts used guessed figures for accuracy and savings, and I replaced them with measured ones. The vision model itself also misreads some bills, as described above.

Screen recording: https://drive.google.com/drive/folders/15I_aU3ThLakB-OBLQEvEAmFU6hdm5eO1?usp=sharing

## 11. Someone picks this up on Monday and you are unreachable. The three things they need to know.

First, how to run it: put the API key in the .env file, put the receipt photos in the data/images folder, and start it with `uvicorn src.app:app --port 8000`. The README has the steps, and “Reset duplicate memory” should be clicked before any demo. Second, the rule: a claim is approved only when every check passes, and anything of Rs 2,000 or more always goes to a clerk, so don’t go back to “under Rs 2,000 approve”. Third, what is still open: the accuracy needs a sample of about two hundred bills checked by a clerk before anyone calls it proven, the cost per photo needs the first real invoice, and Nilesh still has to decide what to do about the duplicate claims found.