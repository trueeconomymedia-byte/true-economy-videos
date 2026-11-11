# Clip Scheduler - rules (documentary clips cut by the user, 1 min+, posted ~4 per week)

## Storage (this repo)
- clips/ready/<file>: clips waiting to be posted. clips/posted/<file>: posted clips kept for reuse.
- playbook/clips_index.json: one entry per clip {file, documentary, added, priority ("normal"|"high"), notes, last_posted, posts:[{date, time_utc, platforms:{platform: buffer_post_id}, status}]}.
- playbook/clips_log.jsonl: one line per post attempt (for learning times): {date, clip, documentary, platform, post_id, local_time_uk, weekday, window, status, metrics?}.
- The user attaches clips in chat with a template message (Documentary, Clips attached, Priority, Notes). The chat session copies them into clips/ready/ and adds index entries. The scheduled task only reads/moves/posts.

## Weekly target and day choice
- Target 4 clip posts per rolling week (Mon-Sun UK). Count clips_log.jsonl posts with status scheduled/sent this week. No more than 1 per day; never 3 posting days in a row; prefer a gap day between posts. If the week's target is already met, do nothing. If few days remain and the target is behind, post today.
- If clips/ready/ has no video files: stop silently (no message).

## Which clip
- Priority "high" first. Else the newest documentary's clips during its first 7 days. Else the clip waiting longest; avoid the same documentary as the previous post; avoid a clip posted in the last 60 days; if ready/ is empty, reuse from posted/ (oldest last_posted, at least 60 days ago).

## When to post (UK time; dueAt in Europe/London with correct offset)
- Default windows (UK): 11:30, 13:30, 15:00, 20:45. Add small random jitter of +-0..12 minutes so it does not look mechanical.
- Exclude any window within 2 hours of anything already in Buffer (list_posts scheduled/sent, all channels) including the daily card queue slots (e.g. 18:30), Markets Daily (23:03 UK) its scheduled second story (20:00 UK next day) and the Animated Shorts post (17:00 UK, set in the morning).
- Learning: read clips_log.jsonl and pull results for past clip posts (mcp__Buffer__list_posts includeMetrics true, or get_aggregated_post_metrics). Normalise per platform (a post's views vs that platform's median clip views). Require at least 12 clip posts overall and at least 3 in a window before trusting it. If reliable: ~80% choose among the best windows (and best weekdays), ~20% explore another window. If two windows are statistically similar treat as equal. If metrics are unavailable (e.g. plan limits), keep defaults and say so once in the final message. Per-platform differences are allowed (separate times are NOT needed: post to all platforms at the same time unless the data clearly separates them).
- Never schedule in the past; dueAt must be at least 30 minutes after now. If today's remaining windows are all excluded, post nothing today.

## Captions (read the clip yourself)
- Download the clip from the repo (git pull) and extract about 12-20 frames with ffmpeg (1 per 3-5 s, plus the first 3 s), view them (Read) and read the burned-in captions and on-screen text. Rebuild what is said; use only facts shown or said. Never invent figures. If the captions are unreadable, say so and skip the clip (log reason), try the next clip.
- Per platform, same limits as the rest of the channel: TikTok title hook < 90 chars + 1-2 lines + question + 3-5 hashtags (< 300 chars). Instagram reel (shouldShareToFeed true): hook + 2-3 lines + call to action ("Full documentary on YouTube"), no hashtags in text, firstComment AT MOST 5 hashtags. Facebook reel: assets[0].video.metadata.title = headline (< 70 chars; fills Reel Title) and a news-article caption ~900-1,300 chars (headline line, 4-6 short paragraphs, comments question, at most 2 hashtags). YouTube (if connected): title < 70 chars ending #Shorts, categoryId 27, 2 sentences + 3 hashtags (Shorts must be vertical and under 3 minutes). British spelling, no financial advice.
- If a clip is longer than a platform allows (Facebook reels about 90 s, Instagram reels about 3 min; check Buffer's error) use Facebook type "post" for long videos or skip that platform and say so.

## Publishing
- Host: raw URL https://raw.githubusercontent.com/trueeconomymedia-byte/true-economy-videos/main/clips/ready/<file> (URL-encode spaces). Verify with curl -sI = 200 first.
- Buffer: for each connected channel create_post mode "customScheduled" with dueAt, schedulingType "automatic" (NOT addToQueue, so daily slots are untouched). After success get_post to confirm status/time and log it. Buffer copies the media at creation; move files to clips/posted/ on the NEXT run once Buffer shows the post as sent.

## Landscape -> Short step (added 10 Nov 2026; runs after reading the clip, before captions/publishing)
- Check orientation: `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 <clip>`. Landscape = width > height (any kind of video). Vertical (or square) clips SKIP this step and are scheduled as they are.
- Landscape: make a 9:16 Short with the approved script, UNCHANGED (never edit it, never re-implement it): `python3 /tmp/tev/scripts/landscape_to_short.py IN OUT.mp4 "Title line 1" "Title line 2" "words to mark gold"`.
  - Setup: needs ffmpeg, numpy, scipy, Pillow (pip install --break-system-packages scipy numpy pillow if missing). The script reads Lora from /usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf; if that file is missing: `mkdir -p /usr/share/fonts/truetype/google-fonts && cp /tmp/tev/scripts/assets/Lora-Variable.ttf /usr/share/fonts/truetype/google-fonts/`.
  - Approved look (do not change): 1080x1920; whole video at full width, centred vertically, never cropped; Shorts card paper background (warm greige +6%, embossed tooth) with a soft shadow above and below the video; two-line title, centred, Lora Bold, directly above the video, no box, no bar; gold #FACB3A marker across the lower half of the key words, punctuation outside the marker (e.g. "Why bonds rise when" / "stocks fall?" with "stocks fall" marked); H.264 CRF 17, original audio as AAC 192k.
  - TITLE HAS NO GOLD MARKER (user, 11 Nov 2026): pass "" as the third argument so the title is plain Lora Bold ink; gold is used ONLY in the spoken captions (next section). Older wording below about marking title words is superseded.
  - Title: write a fresh title for EACH clip from the details the user uploaded with it (index notes/documentary) and what the clip says. Two short lines (each must fit the 1080 px width at Lora Bold 76 px: about 22 characters max per line), plain words, a question or a clear claim, British spelling, no invented facts. The marked words must appear exactly (same case) inside ONE of the two lines. Check the result with a frame (Read) for fit, clipping and marker position; shorten the title and re-run if it overflows.
  - Save the Short as clips/ready/<original-stem>-short.mp4 and post THAT file (host URL, verify 200, Buffer). Keep the original landscape file in clips/ready/ renamed nothing, but record in clips_index.json: {"short_file": ..., "short_title": [line1, line2, marked]}. Move both to posted/ together once sent. Do not schedule the original landscape file and do not schedule both.
  - Duration limits: YouTube Shorts must stay under 3 minutes; the Facebook/Instagram rules above still apply to the Short.
  - If the script fails twice, log the reason, try the next clip, and tell the user in the final message.

## Thumbnail cover frame (added 10 Nov 2026; runs on EVERY clip that gets posted, after the Short step)
- Goal: the best visual frame of the whole video shows for the first 0.2 s so it becomes the cover/thumbnail. Nothing changes size or position: the frame sits in the video's own slot, the title (the hook) stays as it is, audio and sync are untouched.
- Run `python3 /tmp/tev/scripts/cover_frame.py SRC TARGET OUT.mp4 [SLOT_Y SLOT_H]` (scripts/cover_frame.py; do not change it).
  - Landscape clip: SRC = original landscape clip, TARGET = the Short from landscape_to_short.py, SLOT_H = round(1080*height/width) rounded down to even, SLOT_Y = (1920-SLOT_H)//2 (the same numbers the Short script uses). Example for 1920x1080: `... 656 608`.
  - Vertical clip: SRC = TARGET = the clip, no slot arguments (the frame covers the whole picture).
- The script scores one frame per second (sharpness, contrast, colour; skips near-black/blown-out/flat frames) and writes the top 5 as OUT.cand1..5.jpg. LOOK at them (Read) and, if the top pick is poor (blurry, mid-transition, text cut off, nothing readable), re-run with `--at <seconds>` using the best candidate time. Hold is 0.2 s (`--hold`, do not change unless the user asks).
- Replace the clip/Short with the covered version (same file name in clips/ready/ as before, e.g. <stem>-short.mp4 for a landscape clip; for a vertical clip save as <stem>-cover.mp4 and post that, keep the original), look at a frame at 0.05 s and at 0.5 s (cover frame vs normal start, layout identical), then host and post it. Record "cover_at" (seconds) in clips_index.json.
- YouTube Shorts may not use the first frame as its thumbnail; mention it once in the final message only if a YouTube channel is connected.

## Spoken captions under the video (user-approved style B, 11 Nov 2026; landscape clips, runs after the Short step, before the cover frame)
- Look: Inter Bold 58 px, ink #111111, one centred line 48 px below the video, gold #FACB3A marker on the lower half of ONE key word/number/short phrase per caption. The title above has no marker, so gold only ever means "the key word being said now". Built by scripts/captions.py (do not change its look).
- Safe zones (checked 11 Nov): title y ~364-550 and captions y ~1330-1400 sit inside every platform's safe area (nothing in the top 250 px, nothing below y 1440, text inside x 120-960) and inside Facebook's 4:5 feed crop (y 285-1635). captions.py shrinks a long phrase to fit x 120-960 and never draws below y 1440.
- 1) Transcribe: `pip install --break-system-packages faster-whisper` then `python3 scripts/transcribe.py <clip> /tmp/words.json --prompt "<key terms from the index notes and frames, e.g. 60/40, S&P 500, Federal Reserve>"` (model small.en; needs huggingface.co allowed in the account's network settings; if the download fails, try `--model base.en` once, then post WITHOUT spoken captions and say so in the final message).
- 2) Review /tmp/words.draft.json against the frames and fix misheard words (names, numbers, finance terms); never add words that were not said. Phrases: 2-5 words, one line, about 24 characters max, split at natural pauses.
- 3) Mark for retention: set "mark" to the ONE most important word or number in a phrase (numbers, the subject, the change: "60%", "bonds", "rates cut", "the fall"); leave filler phrases unmarked ("" ) so roughly half the phrases carry gold. The marked text must appear exactly (same case) in the phrase. Save as /tmp/captions.json.
- 4) `python3 scripts/captions.py clips/ready/<stem>-short.mp4 /tmp/captions.json /tmp/<stem>-cap.mp4 SLOT_Y SLOT_H` (same slot numbers as the cover frame), then replace clips/ready/<stem>-short.mp4 with it. LOOK at 3 frames (start, middle, a marked phrase): one line, centred, below the video, marker on the right words. Save the reviewed captions to clips/captions/<stem>.json and record "captions": true in clips_index.json.
- 5) Then run the cover frame step with TARGET = the captioned Short.
- Vertical clips already have burned-in captions: skip this step.

## Platforms (user, 11 Nov 2026; overrides older wording about posting to every channel)
- Clip Shorts are scheduled in Buffer to TikTok ONLY. Do not post clips to Facebook or Instagram (or any other Buffer channel).
- YouTube: the user uploads by hand. Each run sends the user (SendUserFile, display "attach") the exact posted file plus a thumbnail JPG (the cover frame: a full 1080x1920 frame at 0.05 s of the posted file), then a SendUserMessage with a ready-to-paste YouTube title (under 70 characters, ending #Shorts), a 2-sentence description and 3 hashtags. YouTube may not use the first frame as the thumbnail, hence the separate JPG.
- Files in clips/ready/ whose names contain "-short" (e.g. -short.mp4, -short-cap.mp4) or end "-cover.mp4" are generated versions, never separate clips; only entries in clips_index.json are clips. Move every file listed for a clip (file, short_file, cover file) to posted/ together.
