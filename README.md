# true-economy-videos: system map (read this first in any new chat)
Last updated 8 Nov 2026. This repo is the shared brain of the True Economy social media system. Scheduled tasks clone it on every run, so rules written here change how they behave.

## What runs automatically (scheduled tasks, all in the user's Claude account)
| Task | When | What it does |
|---|---|---|
| True Economy Daily Post | every day 08:17 UK | picks a series (series.json rotation), researches and verifies, builds a card + looping music video, QA, queues to Buffer on every channel |
| True Economy Markets Daily (18:03 New York) | every day 23:03 UK | Stock Market Today + other market stories; posts instantly (story 2 is scheduled for the next day 12:00 NY) |
| True Economy Clip Scheduler | every day 10:07 UK | schedules the user's documentary clips (clips/ready) at good times, about 4 per week |
| True Economy Brain (weekly analytics) | Sundays 20:47 UK | pulls Buffer metrics, scores series/captions/platforms, writes insights, queues BIG changes for the user's approval |
(Older "How [Co] Makes Money v2" and "Stock Market Today v2" tasks are disabled; their jobs moved into Daily Post / Markets Daily.)
Buffer: org 6adf54d19b9a53d2d59f8e6c, channels TikTok trueeconomy (6ae0b3432f1f5ed648eb0059), Instagram trueeconomymedia (6adf56b92f1f5ed648d90b17), Facebook True Economy (6adf56082f1f5ed648d904e0). Free plan: 3 channels, 10 scheduled posts per channel. Music loops: Google Drive library, indexed in scripts/loops_index.json.

## Where the rules live (newest entry in playbook/feedback.md always wins)
- playbook/brand.md: template, paper look, colours, headline style, "clarity first" chart rules, caption limits (Instagram max 5 hashtags, Facebook reel title + news-style caption).
- playbook/feedback.md: every user correction, dated. Includes: paper card surface (greige 237,234,227, textured logo tab, static, sharpened), Stock Market Today stays PLAIN WHITE (shadow kept), US vs UK central-axis layout, fallback rule (a failed series never ends a run, never publish unverified numbers), web-fetch method, brain rules.
- playbook/series.json (14 series, 4-week rotation, fallbacks, backgrounds), markets.md, clips.md.
- playbook/log.jsonl, markets_log.jsonl: what was posted (no repeats).
- playbook/brain/: the self-improving loop (README.md there explains it): posts.jsonl, metrics.jsonl, scorecard.md, insights.md, guidance.md (soft caption guidance), decisions.jsonl (pending/approved/declined big changes), routing.json (series x platform exclusions), config.json (thresholds + what needs approval).

## Code (scripts/, tested: do not change template geometry)
te_lib.py (card library, 948x1300 canvas), make_flow.py / make_mkts.py / make_post_*.py (card builders), video_card.py / video_flow.py (paper-surface videos), video_mkts.py (Stock Market Today, plain white), te_paper.py (static paper texture), loop_music.py, b64_extract.py, fetch_mkts.py, brain_ingest.py / brain_analyze.py / brain_decide.py.

## How the user wants it to work
- Runs unattended; asks approval only for BIG changes (dropping/replacing series, adding series or rotation, stopping a series on a platform, posting times, big caption-rule changes). Every recommendation must be backed by data (brain thresholds in brain/config.json). Approve a brain decision with `python3 scripts/brain_decide.py approve <id>` (list pending: `... list`).
- New series idea: run `python3 scripts/brain_analyze.py --rank`, name the weakest eligible series to replace with evidence, or suggest a 4-post trial if data is thin.
- To change any scheduled task: use the scheduling tools (list/update triggers); prefer putting rule changes in playbook/feedback.md rather than editing prompts.
- User preferences are also saved in Claude memory (shared across chats).

## Starter message for a new chat
"Read the README and playbook in the true-economy-videos repo (trueeconomymedia-byte), list my scheduled tasks, then help me with: <what you want>."
