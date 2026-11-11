# Animated Shorts: how the daily decision works

One scheduled task runs every morning. It may post ONE animated Short at 17:00 UK, only when the rules below say so.
Series (animation styles) and their episodes are listed in `registry.json`. Each series has its own rules file
(e.g. `funnel.md`) and its own renderer with the shared contract `render data.json OUTDIR SLUG`.

## 0. Look rules shared by every series (user rule, 10 Nov 2026)
- BACKGROUND + INK (user-approved 11 Nov 2026): every series uses the True Economy card paper as the full-frame background,
  placed unchanged (assets_public/True-Economy_card-paper_2160x3840.png scaled to the output size; flat, no banner, no
  shadow), and the PRINTED-INK finish from scripts/anim_shared/ink.py (each element drawn flat in its palette colour,
  multiplied by the paper's own light/shade, slightly thinner on the tooth's high points and fine specks, ink-only
  unsharp mask; the bare paper stays exactly as supplied). Renderers send transparent RGBA frames through
  scripts/anim_shared/ink_pipe.py. No glow, drop shadow, outline or blur; never a different background.
- TITLE: each series has ONE fixed title position (its `title_zone` in registry.json); every episode of that series
  puts its title in exactly that place, at most 2 lines. Different series may use different title positions.
  Never move the title for a logo or anything else; a series' renderer owns this, the task never changes it.
- SAFE ZONES (user rule, 11 Nov 2026), for every series: all content inside x 60-1020 (Shorts/Reels zoom in); the title sits
  inside the 4:5 feed crop (y 285-1635) and below every app's top bar (nothing above y 340 except empty paper); nothing
  important below y 1600 (captions, buttons) or in the right 120 px of the lower half. New series must be built to this.

## 1. Hard limits (never broken; `python3 scripts/anim_plan.py` applies them)
- At most 1 animated Short per day across all series.
- Each series: at most 3 in any rolling 7 days (today + the 6 days before), and never on two days in a row.
- Each episode: its own `gap_days` and `max_in_7_days` from registry.json, and its `repeat_key` never repeats
  (e.g. the same company and quarter is never done twice).
- Paused series are never chosen. Only `allowed: true` series/episodes from anim_plan.py are candidates.
- With one series this means at most 3 a week on non-consecutive days; as more series are added the same rules
  let the task post every day.

## 2. Score each allowed episode (0-100), then pick
SERIES WITH AN IDEA BANK (registry `idea_bank`, e.g. howbig): pick that series' candidate with the rubric in its
rules file (it already includes topicality, data strength, performance and variety), then add the trial_boost and the
-15 same-episode-as-last-post penalty below; compare it with the other series' candidates on the same 0-100 scale.
Start from the episode `priority` (40-55) and add or subtract:
- Fresh data: +30 if the data behind it was released in the last 3 days and has not been covered; +15 if in the
  last 14 days. Stale data (older than the episode's normal update cycle) -10.
- In the news today: +15 if the topic is clearly in today's economic news (major outlets).
- Performance (only when playbook/brain/scorecard.md has a verdict for this series id with enough matured posts):
  strong +10, weak -10; "not enough data" = 0. Never invent this.
- Variety: -15 if the same EPISODE was the last animated post; -10 if the same episode ran in the last 7 days.
- Trial series: + `trial_boost` from anim_plan.py (helps a new style get ~1 post a week for its first 4 weeks).
- Verifiability: if the numbers cannot be confirmed from a named primary source plus a second source today, the
  candidate is dropped (score irrelevant).
Post the best candidate only if its score is at least its `min_score` (60 by default; the news bonus needs 75).
If the best candidate fails verification or the renderer exits 3/4, try the next one (same standard; never
loosen sourcing). If nothing qualifies: post nothing today and log a "skipped" line with the reasons.

## 3. Timing and posting
- Post time: 17:00 Europe/London today, Buffer mode `customScheduled`, schedulingType `automatic`.
  The run finishes by early afternoon; if 17:00 is less than 30 minutes away, skip the day.
- 17:00 belongs to Animated Shorts. Markets Daily schedules its second story at 20:00 UK (it makes way).
  Before scheduling, list Buffer posts for today: if something else sits within 60 minutes of 17:00, still post,
  and mention it in the final message.
- Channels: every connected Buffer channel that takes video EXCEPT YouTube (the user posts YouTube by hand), and
  never a platform that playbook/brain/routing.json excludes for this series id.
- Video: the renderer's `buffer` output (cold-open version: the full chart is the first frame). Add
  `"metadata": {"thumbnailOffset": 200}` to the video asset so the cover is that first frame.
- YouTube: SendUserFile the `youtube` output and the `thumb` image, plus a suggested YouTube title (under 70
  characters, ending #Shorts) and a 2-sentence description with 3 hashtags.

## 4. Files, hosting and the analytics link
- Host at `videos/anim_<series>_<episode>-<slug>-<YYYY-MM-DD>.mp4` (e.g. anim_funnel_earnings-nvidia-q3fy27-2026-11-20.mp4).
  The analytics task reads the series id from this file name, so every episode gets its own performance record.
  Keep only the newest 14 files per `anim_` prefix.
- Log every run in `log.jsonl`: one line per day {date, style, episode, topic, repeat_key, score, status
  ("scheduled" | "skipped"), reason, candidates: [{style, episode, score, why}], due, file, channels, post_ids,
  sources}. A skipped day is logged with status "skipped" and does not count towards the limits.

## 5. Adding a new animation series later
1. Design and approve it in a chat (the user approves the look).
2. Add its renderer folder under scripts/ with the shared contract and outputs, its rules file here, and an entry in
   registry.json with status "trial" and its fixed `title_zone`. CONSTANT ACROSS EVERY SERIES (user rule, 11 Nov 2026):
   the same card-paper background with the printed-ink finish (transparent frames through scripts/anim_shared/ink_pipe.py,
   never a different background) and the same SAFE ZONES from section 0 (x 60-1020, title inside the 4:5 feed crop and
   below y 340, nothing important below y 1600 or in the right 120 px of the lower half). Only the title POSITION within
   the safe zone may differ between series.
3. After `trial_weeks` the analytics decide; making it "active", pausing it or dropping it needs the user's approval.
