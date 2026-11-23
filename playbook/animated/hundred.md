# "Who gets what" series (id `hundred`; approved by the user 23 Nov 2026)

Look: the shared card paper with the printed-ink finish and the shared SAFE zones (animated.md section 0). A share-out
shown as a LEFT -> RIGHT flow in the user's flow-chart style (ribbons with little flowing dashes): the groups are SOLID
chunks on the left, each sized by how many households/people/taxpayers it holds and labelled with its % ("Bottom 50%",
"Middle 40%", "Upper 9%", "Top 1%"); each flows right into its share of the thing being divided (wealth, income, tax
paid...), with a big % beside it. A big group pinching into a thin share and a sliver fanning out into a wide one is
the whole story. ~17-20 s. Same video for every platform.
Renderer: `python3 scripts/hundred_short/hundred_short.py data.json OUTDIR SLUG` (read its docstring). Never change the
look, timing or sound inside the renderer; only the data changes.

FIXED DESIGN (all user rules, 22-23 Nov 2026; renderer defaults, never override):
- OPENING: the first frame is the finished chart with the LAST share hidden as "?%" (this is the cover, thumbnailOffset
  33); it rewinds to empty in about a second (never still), then plays. The ending is the same chart with the answer,
  so it loops.
- ONE THING AT A TIME: a chunk stacks on the left, its ribbon flows across, its % counts up on the right; then the next
  chunk stacks on top. No little blocks on the left (solid chunks), no outline on the right.
- NO WAIT AT THE "?%": the last ribbon follows straight on.
- COLOURS: red = the squeezed group (the problem), blue = the middle, teal = a separate upper group (never the same
  colour as the middle), gold = the last part (the reveal). Never more than 4-5 parts.
- REVEAL: the title lines rotate over from the question to the answer and the "?%" flips to the number on its gold
  marker. The answer title appears ONLY at the reveal, never in the opening.
- LABELS: plain tiers. Never "Next"; use "Upper 9%" (or another plain word that says what the group is).
- SOUND (this series' own, scripts/hundred_short/hundred_audio.py): its own key and tempo with a rolling piano bed; a
  soft knock as each chunk stacks; a QUIET pour whoosh for each ribbon; LOW soft stacking thuds, louder than the
  whoosh, as each % counts up (no high ring or chime anywhere); its own reveal (flip sweeps, deep double thud, warm low
  chord). Sound variations per episode are planned; until they exist use the default.

## 1. What makes an episode
- One whole divided between 3-5 groups of a population: who owns it, who earns it, who pays it. Left side = the
  population split into groups (must add to 100%); right side = each group's share of the whole (must add to 100%).
- The story must be a clear mismatch (a big group with a small share, a small group with a big share). If the shares
  roughly match the group sizes there is no episode.
- Play order = bottom group first, top group last. The LAST group is given as one group with a 2-part `split` (e.g.
  "Top 10%" -> "Upper 9%" + "Top 1%"); the second part is the gold reveal, so make it the most striking number.
- TITLES: question "Who owns / Britain's wealth?" style (2 lines, max 26 characters each, gold marker on the subject);
  answer = the single most striking true comparison, e.g. "The top 1% own as much / as the bottom 50%".
- THE ANSWER TITLE MUST BE LITERALLY TRUE OF THE NUMBERS ON SCREEN. "As much as" only if the two shares are equal as
  shown; if they differ (10% vs 9%) write "more than". Never round a number differently in the title and the chart.
- Say exactly what is counted, in the labels and captions: households or people or taxpayers; the country or region
  (Great Britain is not the UK); the period; wealth or income; before or after tax.

## 2. Accuracy (never loosened)
- Every share from a named primary source (ONS Wealth and Assets Survey, HMRC percentile and income tax statistics,
  DWP Households Below Average Income, Federal Reserve Distributional Financial Accounts, US Census, CBO, IRS SOI, World
  Inequality Database, Credit Suisse/UBS wealth report) AND confirmed by a second source, same period, same definition.
- All groups from the SAME release and period; never mix sources between groups. Shares that the source gives only
  for overlapping groups (top 10%, top 1%, top 50%) are turned into non-overlapping parts by subtraction IN CODE and the
  result must add to exactly 100; show whole numbers and make sure the rounded numbers still add to 100 (adjust nothing
  by hand: if rounding breaks the sum, use one decimal for all, or choose another split).
- If two official statements disagree after rounding (e.g. bottom 50% "9%" in one table and "10%" in the bulletin), use
  the published table values, say which in the log, and word the answer title so it is true either way.
- data.json needs `sources` (at least 2 pages) and `period`; the renderer refuses without them.
- No judgement words in titles or captions ("unfair", "greedy"); state the split and let viewers react.

## 3. Choosing the best idea (the idea bank `playbook/animated/hundred_bank.jsonl`)
Same method as howbig.md section 3 (add up to 8 ideas per run, re-score every unused idea out of 100, strong unused
ideas wait in the bank), with these scores:
- Mismatch (25): how lopsided the split is (computed from the verified figures).
- Relatable (20): something viewers place themselves in (wealth, pay, tax, homes, pensions, shares).
- Topical (20): a new release of the data in the last 30 days, or the subject in today's news (a budget, a tax row).
- Data strength (15): one primary release with every group, confirmed by a second source; else not eligible.
- Proven (10): from playbook/brain/scorecard.md for series "hundred"; 5 when there is not enough data.
- Variety (10): 10 if the episode and country differ from the last two hundred posts, 5 if one matches, 0 if both.
No repeats: the same subject + country + data release is never posted twice; a follow-up needs a newer release.

## 4. Episodes (registry ids)
- `wealth`: who owns the wealth (households or adults; a country, or the world).
- `income`: who earns the income (before or after tax).
- `tax`: who pays a tax (income tax by income group; who pays how much of the total).
- `assets`: who owns one kind of asset (shares, property, pensions, land).
- `world`: the world or a group of countries as the population (share of world GDP, wealth, emissions by population).
- `news` (bonus): the split behind today's headline. min_score 75.

## 5. Captions
Hook on the question or on the BIG group's small share; never give away the last (gold) number or the answer title in
the first line. Give the period, the source and what is counted in the Facebook article caption.
