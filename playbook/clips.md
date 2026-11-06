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
- Exclude any window within 2 hours of anything already in Buffer (list_posts scheduled/sent, all channels) including the daily card queue slots (e.g. 18:30), Markets Daily (23:03 UK) and its scheduled second story (17:00 UK next day).
- Learning: read clips_log.jsonl and pull results for past clip posts (mcp__Buffer__list_posts includeMetrics true, or get_aggregated_post_metrics). Normalise per platform (a post's views vs that platform's median clip views). Require at least 12 clip posts overall and at least 3 in a window before trusting it. If reliable: ~80% choose among the best windows (and best weekdays), ~20% explore another window. If two windows are statistically similar treat as equal. If metrics are unavailable (e.g. plan limits), keep defaults and say so once in the final message. Per-platform differences are allowed (separate times are NOT needed: post to all platforms at the same time unless the data clearly separates them).
- Never schedule in the past; dueAt must be at least 30 minutes after now. If today's remaining windows are all excluded, post nothing today.

## Captions (read the clip yourself)
- Download the clip from the repo (git pull) and extract about 12-20 frames with ffmpeg (1 per 3-5 s, plus the first 3 s), view them (Read) and read the burned-in captions and on-screen text. Rebuild what is said; use only facts shown or said. Never invent figures. If the captions are unreadable, say so and skip the clip (log reason), try the next clip.
- Per platform, same limits as the rest of the channel: TikTok title hook < 90 chars + 1-2 lines + question + 3-5 hashtags (< 300 chars). Instagram reel (shouldShareToFeed true): hook + 2-3 lines + call to action ("Full documentary on YouTube"), no hashtags in text, firstComment AT MOST 5 hashtags. Facebook reel: assets[0].video.metadata.title = headline (< 70 chars; fills Reel Title) and a news-article caption ~900-1,300 chars (headline line, 4-6 short paragraphs, comments question, at most 2 hashtags). YouTube (if connected): title < 70 chars ending #Shorts, categoryId 27, 2 sentences + 3 hashtags (Shorts must be vertical and under 3 minutes). British spelling, no financial advice.
- If a clip is longer than a platform allows (Facebook reels about 90 s, Instagram reels about 3 min; check Buffer's error) use Facebook type "post" for long videos or skip that platform and say so.

## Publishing
- Host: raw URL https://raw.githubusercontent.com/trueeconomymedia-byte/true-economy-videos/main/clips/ready/<file> (URL-encode spaces). Verify with curl -sI = 200 first.
- Buffer: for each connected channel create_post mode "customScheduled" with dueAt, schedulingType "automatic" (NOT addToQueue, so daily slots are untouched). After success get_post to confirm status/time and log it. Buffer copies the media at creation; move files to clips/posted/ on the NEXT run once Buffer shows the post as sent.
