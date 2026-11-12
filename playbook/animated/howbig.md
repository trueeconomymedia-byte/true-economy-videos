# "How big is it really?" series (approved by the user 11 Nov 2026)

Look: the shared card paper with the printed-ink finish and the shared SAFE zones (animated.md section 0). ONE
constant reference the whole video: **1 square = 1 hour of the money**. Day 1 fills hour by hour (00:00, 01:00 ...)
with a tick per hour, the camera pulls back to the first week, then the first months, then the whole period laid out
as a calendar (a year: one row per month; a quarter: three month blocks side by side, 7 days a row, month names
above). Captions (user, 11 Nov 2026): 1 Day, 1 Week = .., 1 Month = .., and the gold box 1 Quarter = .. / 1 Year = ..;
the counter reads "N hours = £X" in plain ink under a PROGRESS BAR at the BOTTOM (user, 12 Nov 2026: replaces the black counter pill;
light tint track, the colour fill grows with every hour of the period). The key sits at the TOP, under the title: one
square "= 1 hour (£X)" (the per-hour amount). EVERY episode is titled "Visualising" / "<Owner>'s <period> <measure>" (the period
and measure), with the gold marker on "<Owner>'s" ONLY (user, 12 Nov 2026). The money counter is hidden
("£??") while the last stage fills; the total is revealed in gold at the end. Calm news-style sound (ticks, soft
patter, glides, low hits, warm piano reveal). 28.5 s. NO cold open (user, 11 Nov 2026: the rewind was off-putting): Buffer gets the same video as YouTube, and its
cover is set with thumbnailOffset = `thumb_ms` from SLUG-build.json (the finished grid with the total hidden).
Renderer: `python3 scripts/howbig_short/howbig_short.py data.json OUTDIR SLUG` (read its docstring for the data
format). Never change the look, timing or sound inside the renderer; only the data changes.

Why hours (user decision, 11 Nov 2026): the reference must never change during the video (no "100 salaries, then
10,000 salaries"), and every square must still be a visible block at the end. One hour of a yearly total is about
0.011% of it: 8,760 squares for a year (about 7 px each), 2,000-2,200 for a quarter (about 12 px each).

## 1. What makes an episode
- A money total over a fixed period of 42-366 days: a year, a financial year or a company quarter. The renderer
  works out per hour, per day, per week and the stage totals itself; the task never types a derived number.
- The per-hour figure must be striking on its own. Rough guide: at least £100,000 an hour for public money and
  companies, or a person's pay where the per-hour figure dwarfs a normal wage (the UK median full-time salary is
  about £20 an hour; compare in the caption, not on screen).
- Colour: `red` for a cost or a problem (debt interest, losses, fraud, fines), `blue` for neutral totals (budgets,
  revenue, profit, pay), `teal` for money coming in that is good news for the viewer.
- Sources: the total from a named primary source (ONS, OBR, HM Treasury, NHS England, a company's earnings release
  or annual report, a club's accounts...) plus a second source, both dated. The period start and end dates must be
  the ones that total covers (financial year 1 April - 31 March, a company's exact fiscal quarter dates).

## 2. Writing the data
- headline_q (USER STANDARD, 12 Nov 2026, every episode): line 1 is always "Visualising"; line 2 names WHOSE money,
  the period and the measure; the gold marker goes on the owner word ONLY. Examples: ["Visualising", "Shell's Q3 profit",
  "Shell's"], ["Visualising", "Microsoft's Q1 profit", "Microsoft's"], ["Visualising", "the UK's debt interest",
  "UK's"], ["Visualising", "the NHS's 2025-26 budget", "NHS's"], ["Visualising", "Haaland's yearly pay", "Haaland's"].
  Line 2 max 26 characters (shorten the period: Q3, 2025-26, yearly). The per-hour shock lives in the key ("■ = 1 hour (£X)")
  and the captions, not the title.
- headline_a: the total, e.g. ["One year of interest:", "{total}.", "{total}"]. Max 26 characters per line
  after filling (the renderer refuses longer lines, exit 4).
- key: what one square is, short ("1 hour of interest", "1 hour of profit", "1 hour of his pay").
- final/tease: leave them out; the defaults are "1 Year = {total}" / "1 Quarter = {total}" and "1 Year = £??" / "1 Quarter = £??".
- source: the primary source and its date; the renderer adds "· {total} ÷ N hours".
- Captions: never give the total away in the first line (it is the payoff). Use the per-hour figure as the hook and
  put the comparison with a normal wage or a familiar cost in the caption text.

## 3. Choosing the best idea (the idea bank)
The bank is `playbook/animated/howbig_bank.jsonl`, one idea per line:
{"id", "episode", "subject", "repeat_key", "where": "where the numbers come from", "status": "unused" | "used" |
"rejected", "added", "used_on", "score_last", "notes"}.
Every run where this series is allowed:
1. Add up to 8 NEW ideas (today's news first, then evergreen), skipping any whose repeat_key is already in the bank
   with status used (unless it qualifies as a follow-up, rule 4).
2. Score EVERY unused idea again, out of 100 (scores change as news fades):
   - Shock (25): how striking the per-hour figure is for a first-time viewer (computed from the verified total).
   - Relatable (20): a subject UK viewers know and care about (public money, household-name companies, famous people).
   - Topical (20): in the news in the last 7 days or a new release in the last 14 days (fades to 0 after that).
   - Data strength (15): two dated sources, the total and its exact period confirmed. No two sources = not eligible.
   - Proven (10): from playbook/brain/scorecard.md for series "howbig" and the episode; 5 when there is not enough data.
   - Variety (10): 10 if the episode and subject area differ from the last two howbig posts, 5 if one matches, 0 if both.
   Then apply animated.md section 2 extras: + trial_boost from anim_plan.py; -15 if the same episode was the last
   animated post. The best idea that reaches the episode's min_score (60, news 75) is the candidate for this series.
3. Strong unused ideas stay in the bank for the next run, so a new idea only gets posted if it beats the best one
   already waiting. Mark rejected ideas (data cannot be verified, unsupported shape) with the reason.
4. No repeats: a repeat_key that was used is never posted again, EXCEPT as a follow-up with a newer official figure
   for a later period, at least 180 days after the first, with the change in the caption ("up from ...").
   The same company is not used twice within 30 days in this series, and never the same company and quarter that
   the funnel series or the Daily Post covered in the last 7 days (check both logs).
5. After posting, set the idea's status to "used" with used_on; commit the bank with the log.

## 4. Episodes (registry ids)
- `public_cost`: a public cost or problem per hour (debt interest, benefit fraud and error, PFI payments, a fine).
  Data: ONS public sector finances, OBR, DWP fraud and error statistics, NAO reports.
- `public_budget`: what a public service costs per hour (NHS England, defence, state pension, schools, the BBC
  licence fee income). Data: HM Treasury PESA, departmental annual reports, OBR.
- `company`: a household-name company's profit, revenue or tax per hour for its latest quarter or year.
  Data: the earnings release plus the 10-Q/10-K or annual report (GAAP / IFRS as reported).
- `pay`: a famous person's pay or a fortune's growth per hour (top footballers, FTSE 100 CEOs, the richest people's
  yearly gain). Data: club accounts or a reliable dated report plus a second source, company annual reports
  (single-figure remuneration), the Sunday Times Rich List. Never a private individual.
- `news` (bonus): a money total in today's news that fits (a record fine, a new contract, a bailout). min_score 75.
