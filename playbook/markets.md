# Markets Daily (conditional posts) - rules for the 18:03 New York task

## Cadence and caps
- Task runs every day at 18:03 America/New_York (2 h after the US close; = 23:03 UK most of the year). Weekends: only crypto/commodity/central-bank stories can fire; the stock-market story needs an open session.
- At most 4 conditional posts per rolling 7 days (count markets_log.jsonl `status` posted or scheduled, from the last 7 days). At most 2 per night: story #1 posts instantly, story #2 is scheduled (see below). Never a third.
- Quiet day = post nothing and say so in one short message. Never invent a reason to post.
- No repeat: same event/topic not within 48 h (check markets_log.jsonl).

## Candidate stories (score each 0-100: size x surprise x audience interest; must pass its gate)
1. stock_market: S&P 500 |move| >= 1.0%, or record high / lowest close in 6+ months, or Nasdaq/Dow >= 1.5%, or a named major market-moving event, or a world index >= 2%. Pipeline: fetch_mkts.py + make_mkts.py + video_mkts.py (the tested Stock Market Today card).
2. central_bank: a Fed, Bank of England or ECB (also BoJ) rate decision announced today. Always passes. Card: the new rate, change, vote split, one-line reason, and what it means (mortgages/savings). Verify on the bank's own site.
3. data_surprise: US/UK CPI, jobs, or GDP released today and the headline number differs from the consensus forecast by >= 0.2 pts, or is a multi-year high/low. Card: the number vs forecast vs previous. Verify on BLS/BEA/ONS and a forecast from Reuters/Bloomberg/Trading Economics.
4. markets_move: Bitcoin |24 h move| >= 7%, or a record/round-number milestone; gold, silver or oil |move| >= 3% or an all-time high; USD/GBP/EUR/JPY major pair |move| >= 1.5%. Card: the move, the level, and the main reason from news.
Choose the strongest as story #1 (instant). Story #2 only if it also passes its gate.

## Second story = scheduled
- Post it next day at 20:00 UK time (Europe/London; GMT +00:00, BST +01:00) with mode customScheduled and dueAt. (Changed 10 Nov 2026 by the user: 17:00 UK now belongs to the Animated Shorts task, and Markets Daily makes way.) Only if it is still relevant a day later: central_bank and data_surprise yes; markets_move and stock_market only if it is a milestone/record; otherwise drop and log as skipped.
- Rewrite the wording as "yesterday". Check the weekly cap and that the scheduled-post limit (about 10 per channel) is not full.

## Card design (same template and rules as the daily post)
- Use /tmp/te_lib.py and brand.md rules (title headroom, source line, footer, colours: loss red #E23B3B, gain green #1FA35C, blue #0760F1, yellow marker). "Clarity first" rules in brand.md apply: same kind = same colour, only the gap/problem is red, related items on one chart with dotted guides, plain-words labels, no collisions.
- stock_market uses make_mkts.py (do not edit its layout). Others are built with te_lib.py in a new design per story; ONE big idea, key numbers large, fill the white area.

## Music and background (vary them like the daily post)
- Music: loops_index.json track chosen by mood (down/negative: tension; up/positive: uplift); random among top 3; never the same title as the last post in markets_log.jsonl or log.jsonl. Video length = the loop length (6-10 s).
- Background motif: options chips, contours, graph, skyline, halftone, candles, globe. Suggested: stock_market candles/graph, central_bank skyline/globe, data_surprise graph/halftone, markets_move globe/candles/contours. Never the same motif as the previous post (check bg in markets_log.jsonl AND log.jsonl). SEED = YYYYMMDD mod 1000. Third CLI argument of video_card.py / video_mkts.py.

## Captions (per platform; British spelling, no financial advice, no buy/sell)
- TikTok: metadata.tiktok.title hook < 90 chars with the number; text 1-2 lines + question + 3-5 hashtags, < 300 chars.
- Instagram: reel, shouldShareToFeed true; hook + 2-3 lines + call to action; NO hashtags in text; firstComment AT MOST 5 hashtags total.
- Facebook: reel; assets[0].video.metadata.title = headline with the key number, < 70 chars (this fills Buffer's Reel Title); caption = short news article ~900-1,300 chars: headline line, 4-6 short paragraphs (what happened with key numbers, why / the split behind it, plain-words context, balanced so-what, comments question), Source line with date, at most 2 hashtags.
- YouTube (if connected): title < 70 chars ending #Shorts, categoryId 25 (News) , 2 sentences + 3 hashtags. X/Threads/Bluesky/Mastodon: <= 270 chars, <= 2 hashtags. LinkedIn: 2-3 sentences, <= 3 hashtags.
