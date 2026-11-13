# "Head to head" series (approved by the user 11 Nov 2026)

PURELY ECONOMICS (user rule): every round is an economic or business statistic (output, income, pay, prices,
jobs, debt, rates, growth, housing costs, company results). Never health, culture, sport or "quality of life" measures,
and never a verdict on which country, company or politician is "better" as a whole.

Look: the shared card paper with the printed-ink finish and the shared SAFE zones (animated.md section 0). Two rivals,
3-7 rounds (5 is best). Central axis: side A grows LEFT in blue, side B RIGHT in red; the better side of each round
keeps full colour and wins the point, the other fades to its light tint; a tie gives no point. Numbers count up as the
bars grow, both values HOLD for about a second before the point lands (so viewers can call it), the scoreboard pops.
SCOREBOARD (user default 13 Nov 2026): small and quiet, two touching colour squares with the scores (side A blue on
the left, side B red on the right, white numbers) and the side names in ink either side ("UK [1][3] Germany"); when a
side wins a point, ITS square flips over around its horizontal axis (~0.5 s) and shows the new number (the other stays
still). No black tab. Built into the renderer: never change it per episode.
TITLE (user default 13 Nov 2026): short and obvious, "<A> vs <B>:" on line 1 with the gold marker on "<A> vs <B>", and
the subject in one or two words on line 2, e.g. ["UK vs Germany:", "Economies", "UK vs Germany"],
["Apple vs Microsoft:", "Business", "Apple vs Microsoft"]. Not "5 economic rounds".
The camera zooms into each round with a slow drift, pulls back before the LAST round (the decider, shown as "?" with
"Final score: A ? – ? B"), then the winner lands in gold. About 34 s. Same video for YouTube and Buffer; Buffer cover
= thumbnailOffset `thumb_ms` from SLUG-build.json (the table with the decider hidden).
Renderer: `python3 scripts/h2h_short/h2h_short.py data.json OUTDIR SLUG` (read its docstring). Never change the look,
timing or sound inside the renderer; only the data changes.

## 1. Accuracy rules (the most important part of this series)
- LIKE FOR LIKE: each round compares the same measure, same definition, same unit, for both sides. Prefer ONE source
  that covers both sides with one definition (IMF World Economic Outlook / Fiscal Monitor, OECD, World Bank, Eurostat).
  When each side uses its own statistics office, both must follow the same international definition (e.g. ILO
  unemployment, CPI 12-month rate) and the round's "note" says the periods.
- SAME PERIOD: the same month/quarter/year for both sides where possible; never more than 6 months apart, and the
  note line shows both periods ("US: Oct 2026 · UK: Jun–Aug 2026").
- MONEY: convert in code only ("fx": rate + its source), at the average rate for the same year as the data (FRED
  AEXUSUK etc.), or use PPP figures from one international source; the sub/note says which ("in US$ at the 2025
  average rate", "adjusted for living costs (PPP)").
- SOURCES: every number on both sides has a named primary source plus a second source (or the same official table
  confirmed on a second site), with dates. The renderer refuses a side without a source (exit 4).
- DIRECTION: "better" is set from what economists normally treat as better (higher pay/GDP per person/growth; lower
  unemployment/inflation/debt). For anything ambiguous (interest rates, exchange rates, house prices) do NOT score
  it: leave it out.
- CHOOSE THEN ORDER: pick the 5 measures by importance for the matchup BEFORE looking at who wins them; only then
  order the rounds for suspense (the round that settles it last). Never pick measures to engineer a result.
- WORDS: sub-label max 8 words (the renderer refuses longer); dates and method go in "note". headline_a states the
  result and one factual nuance ("The US wins 3–2. But UK debt is lower."), no opinion.

## 2. The libraries
- `playbook/animated/h2h_rivalries.json`: the pairs (countries, cities/regions, companies, "then vs now" for one
  economy) and, per pair type, the measure set with the sources to use. Add new pairs and measures there (with sources).
- The idea bank `playbook/animated/h2h_bank.jsonl` works like howbig.md section 3 (add up to 8 ideas per run, re-score
  every unused idea out of 100, strong unused ideas wait):
  - Rivalry (25): how much viewers care about the pair (UK/US, household-name companies first).
  - Topical (20): both sides published fresh data in the last 14 days (same-week earnings, inflation/jobs releases),
    or the pair is in today's news (election, Budget, trade dispute, takeover).
  - Comparable data (25): all 5 rounds like for like and verified today; otherwise NOT eligible.
  - Proven (10): playbook/brain/scorecard.md for series "h2h"; 5 when there is not enough data.
  - Variety (20): pair type and pair differ from the last two h2h posts.
- No repeats: the same pair is not repeated within 90 days unless every round has newer data; the cross-series rule
  (animated.md) applies too.

## 3. Episodes (registry ids)
- `countries`: two economies (GDP per person PPP, median pay, unemployment, inflation, government debt; backups: GDP
  growth, house price to earnings, productivity).
- `companies`: two rivals for the same fiscal period (revenue, profit, profit margin, revenue growth, cash; backups:
  employees, revenue per employee). Each company's own filings.
- `places`: two cities/regions (median pay, house price to earnings, rent, unemployment, GDP per person).
- `then_now`: one economy, then vs now (e.g. UK 2000 vs today): only factual records, never a verdict on a person.
- `news` (bonus): a matchup behind today's headline. min_score 75.
