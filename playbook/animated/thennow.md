# "Then vs now" series (approved by the user 11 Nov 2026)

Look: the shared card paper with the printed-ink finish and the shared SAFE zones (animated.md section 0). The video STARTS
IN THE PAST (the hook title: "Cost of a US home: 1995 vs 2025"), the camera rides the tip of the line
forward year by year (a tick per year; no year pill, the x axis shows the years), dotted event markers drop in as the line passes them
(soft hit + piano note), an optional comparison line (income, wages, inflation) runs underneath with the gap shaded, a
ratio tag AT THE TIP shows "= 3.9x / median income" beside a bracket between the two dots (no compare line: "+X% since
1995" under the tip label); it turns to "= ?x" over the last year, then the camera pulls back to the whole climb, the answer
is hidden ("2025: ??x median income") and revealed in gold. ~31 s. Same video for YouTube and Buffer; Buffer cover =
thumbnailOffset `thumb_ms` from SLUG-build.json (the whole climb with the answer hidden).
Renderer: `python3 scripts/thennow_short/thennow_short.py data.json OUTDIR SLUG` (read its docstring). Never change the
look, timing or sound inside the renderer; only the data changes.

REWIND OPENING (user-approved 11 Nov 2026, renderer default): the video opens on the whole climb with today's values
("$???") and the answer ("??x") hidden, rewinds to the first year in ~1.1 s (faint ghost of the
full line, tape-rewind sound), lands on a hit as the hook title pops and its gold marker sweeps in; short reveal hold so
it loops. Buffer cover = thumbnailOffset `thumb_ms` from SLUG-build.json (33 ms = that first frame). Same video on YouTube.

## 1. What makes an episode
- One yearly series of 10-40 years with no gaps (main line), optionally a comparison line in the SAME unit (house price
  vs income, rent vs wages, a price vs the minimum wage). The renderer works out the ratio, % change and every headline
  number itself ({start}, {end}, {ratio_start}, {ratio_end}, {pct}, {times}); never type a derived number.
- TITLE (user rule 11 Nov 2026): obvious and attractive, "<What> : {y0} vs {y1}" with the gold marker on "{y0} vs {y1}",
  e.g. headline_q ["Cost of a US home:", "{y0} vs {y1}", "{y0} vs {y1}"]; answer headline_a ["{start} → {end}",
  "{ratio_start}x → {ratio_end}x income", "{ratio_end}x"] (no compare line: ["{start} → {end}", "{pct} since {y0}", "{pct}"]). Each line max 26 characters. The years in the title are the data's real first and last years
  (never the calendar year if the data stops earlier). The CAPTION hook still leads with the PAST value.
- THE KEY NUMBER LIVES IN THE CHART (user rule 11 Nov 2026): the ratio sits at the tip between the two dots, not in a
  pill under the title; nothing sits between the title and the chart but the event labels.
- A good episode has a clear long-term change AND a comparison or a turn that tells a story (the gap widening, a
  crash and recovery). Flat or noisy series are not eligible.
- Colours: main line blue (red if the main line is itself a cost/problem such as debt), comparison teal, the gap
  light red when the main line outruns the comparison (gap_colour "teal" if the comparison pulls ahead: good news).
- Inflation: when comparing a price with itself over decades, prefer a comparison line (wages, income) over raw prices;
  if no comparison exists, say "not adjusted for inflation" in the caption, or use a real (inflation-adjusted) series.

- RATIO WORDING (user rule, 11 Nov 2026): a price compared with income is shown as "N x income", the way people talk
  about it: tip tag "= 3.9x median income", answer box "1995: 3.9x → 2025: 4.7x median income", headline_a e.g.
  ["{start} → {end}", "{ratio_start}x → {ratio_end}x income", "{ratio_end}x"] (ratio_style "times", the renderer default).
  Never "years of income". Label the comparison line by what the data is: a median is "median income" (never
  "average income", which is the mean and a different, higher number); a true mean may be called "average income".
  Captions use the same "3.9x" wording.

## 2. The data library (no downloads needed)
- Every verified series lives in `playbook/animated/data/<id>.json`: {"id", "years", "main": {"label", "values",
  "note", "source"}, "compare": {...} (optional), "checked": [second-source notes]}. Episodes refer to it with
  "series": "<id>". Once a series is in the library it is never fetched again; later episodes only add the newest
  year(s), confirmed from the official release page.
- How to get a new series without downloads: WebSearch "FRED <series name>" (FRED, fred.stlouisfed.org, carries most
  US and many UK series from the Census Bureau, BLS, BEA, the Fed, the BIS, the OECD, the ONS and the Bank of England),
  WebFetch the series page, then the "View All" table page it links (fred.stlouisfed.org/data/<ID>) which lists every
  observation. Quarterly or monthly series: compute the yearly average in code and say "yearly average" in the source
  line. Second source: the publisher's own release page for at least the first and last values (e.g. the Census income
  report, the ONS bulletin). If a full series cannot be confirmed, skip the idea (never fill gaps or guess).
- £-level UK series (ONS median house price and earnings, Land Registry average prices) are often only in data files;
  if the user has supplied a file it is in the library; otherwise use FRED indexes and end on "+X%" / "{times}".

## 3. Events (`playbook/animated/events.json`)
- A shared list of verified dated events with short labels (max ~18 characters) and the regions they apply to. Use at
  most 5 per episode (3-4 is best), only events that line up with a visible turn or change in THIS line, never as
  decoration. New events need two sources before they are added to the list.

## 4. Choosing the best idea (the idea bank `playbook/animated/thennow_bank.jsonl`)
Same method as howbig.md section 3 (add up to 8 ideas per run, re-score every unused idea out of 100, strong unused
ideas wait in the bank), with these scores:
- Story (25): size of the change and how surprising the comparison is (computed from the verified data).
- Relatable (20): something viewers buy or feel (homes, rent, food, fuel, wages, pensions, famous companies).
- Topical (20): a new release of this series in the last 14 days, or the topic in today's news.
- Data strength (15): series in the library or fully confirmed today from FRED plus the publisher; else not eligible.
- Proven (10): from playbook/brain/scorecard.md for series "thennow"; 5 when there is not enough data.
- Variety (10): 10 if the episode and subject differ from the last two thennow posts, 5 if one matches, 0 if both.
No repeats: the same series id + years is never posted twice; a follow-up needs a newer year of data and 180 days.

## 5. Episodes (registry ids)
- `housing`: house prices or rent vs income/wages (UK, US, regions).
- `cost_of_living`: everyday prices vs wages (fuel, food items, energy bills, childcare, tuition), or one price's climb.
- `pay_jobs`: wages, minimum wage, pensions, unemployment over time.
- `money_markets`: interest rates, inflation, the pound/dollar, stock indices, government debt over time.
- `company`: a household-name company's revenue/profit/share price over 10-40 years (annual reports, 10-K via SEC or
  FRED where available), with events like product launches.
- `news` (bonus): a long-term series behind today's headline. min_score 75.
