# Funnel series (approved 10 Nov 2026)

Look: full paper background, big Lora title at the top with the gold marker, money pours from a full-width funnel
mouth down a flow chart; costs peel off to the right in red, money joining (e.g. borrowing) comes in teal, the
final stream turns gold and the answer lands in a gold box; the camera follows each step, then pulls back to the
whole chart. Calm news-style sound (quiet swooshes, clear counter ticks, warm piano reveal). 30-36 s.
Renderer: `python3 scripts/funnel_short/funnel_short.py data.json OUTDIR SLUG` (read its docstring for the data
format). Never change the look, timing or sound inside the renderer; only the data changes.

OPENING AND MONEY BAR (user default 11 Nov 2026, renderer default; never override): ONE video for every platform. It
opens fully zoomed out (the whole chart, answer hidden, under the hook title) and zooms in from the very first frame
(no still moment), lands just above the funnel mouth so the top segment labels are readable, drifts slowly over them
(~1.5 s), then moves down to the first stage. As it moves, the hook title is pushed up and fades out, and the MONEY BAR
takes its place: the running amount ("$92.3B in", "$62.6B left") in big ink type over a short thick bar that starts
all gold and turns dark red from the right as each cost is taken. A band of clear paper separates the bar from the
chart. No black pill. At the end it pulls back to the whole chart and the answer title. Buffer cover = thumbnailOffset 33.

## Writing the data (all episodes)
- The story is always: a starting amount -> pieces taken off (or added) -> what is left, which is the payoff.
- 1-5 steps. Merge small items into one step called "Everything else" or "Other costs"; 3-4 steps is best.
- Every `val` must be the amount left after that step and above zero; the renderer refuses numbers that do not add up.
- headline_q asks the question with the starting number marked gold; headline_a answers it with the payoff marked.
  Each line fits about 22 characters at full size (longer lines shrink automatically, keep them short anyway).
- final.text is the payoff in the gold box; final.tease/tease_sub hide it for the cold open and the thumbnail.
- Plain words for every label; British spelling; currency symbol of the country.
- Every number: a named primary source plus a second source, dated; compute derived numbers in code.

## Episodes

### earnings: How much did [Company] keep?
- Data: the company's latest quarterly earnings release (GAAP), checked against the 10-Q/10-K or a second reputable
  source. Use the COMPANY data format (make_flow.py keys) and always include the reported totals gp, op, pbt, ni.
- Eligible: a company that reported in the last 10 days with a profit at every stage (the renderer exits 3 for
  losses: try the next company). Never the same company and quarter twice in this series. If the Daily Post task
  made a "How X makes money" card for the same company and quarter in the last 7 days (playbook/log.jsonl), choose a
  different company.
- Prefer household names and the biggest movers of the week. Segments: up to 3 bands (the two largest + Other).
- Logo: only if the user has added one at scripts/assets/logos/<company>.png (logo_key = company name). Never draw,
  download or recreate a company logo.

### salary: Where your salary goes
- Data: official tax rates for the current tax year (GOV.UK income tax and National Insurance rates; IRS brackets,
  Social Security and Medicare for the US; the official tax authority elsewhere). Compute the deductions in code and
  check the take-home against a second source (an established take-home pay calculator).
- Variants: country, salary level (e.g. the national median, £30k, £50k, £100k), a named job using an official pay
  figure (e.g. a nurse's band from NHS pay scales). Say which tax year and assumptions (e.g. "England, no student
  loan, 5% workplace pension") in the source line.
- Steps: income tax -> National Insurance (or Social Security + Medicare) -> pension -> student loan (if used);
  final = take-home. pill {"in": "earned", "left": "left"}; share {"style": "pct", "of": "pay"}.
- Freshness: new tax year (6 April UK), Budget changes, or a salary statistic in the news.

### government: Where the government's money went
- Data: ONS Public sector finances (monthly, UK) or the US Treasury Monthly Treasury Statement; cross-check with the
  OBR or CBO monthly review. Use the latest month (or the fiscal year to date when clearer).
- Shape: start = tax and other receipts (segments: the 2 biggest taxes + Other); a teal gain step for borrowing
  when spending exceeded receipts; then spending peels (largest first, max 4 including "Everything else"); the final
  gold amount is the most striking line (often debt interest). Make sure the steps add up exactly.
- Eligible: a new monthly release in the last 10 days that has not been covered.

### price: What's really in the price
- Data: US gasoline (EIA "Gasoline explained" price components, monthly), UK petrol and diesel (fuel duty and VAT
  from GOV.UK plus the latest pump price from the RAC or the government's weekly road fuel prices), UK energy bills
  (Ofgem price cap breakdown, quarterly). Other everyday items only with an official or industry breakdown.
- Steps: taxes first, then the other parts; final = the striking part (e.g. "only 52p is the fuel itself").
- Eligible: new data (new price cap, a big pump-price move, a new monthly EIA breakdown).

### household: Where the average household's money goes
- Data: ONS Family Spending (UK, annual) or BLS Consumer Expenditure Survey (US, annual), plus the matching income
  figure from the same release; cross-check totals with a second official table.
- Shape: start = average income; steps: taxes -> housing -> food -> transport -> everything else; final = what is
  left to save (if it is not above zero, use a different income group or tell the story with spending only).
- Variants: income groups (lowest vs highest fifth), regions, countries.

### news (bonus): a money story from today's news
- Only when today's news has a real money flow that fits the funnel (a Budget measure applied to a salary, a record
  fine split, a big deal or bonus pool, a government package). Needs score 75 or more, two sources, and must be
  explainable in 3-5 steps. If in doubt, skip.
