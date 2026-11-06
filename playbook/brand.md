# True Economy brand and template rules (the task must follow these on every post)

## Template (fixed, never changes)
- The card is the user's Canva card: black bar with the "E" logo on top, white paper area below, over a blurred grey topic background in the video.
- The chart canvas is 1014 x 1441 (the whole white area, title included). Everything fills that area; no empty bottom third.
- Fixed positions (Facebook's feed crops the top and bottom of vertical video): title baseline 1 at y=137 (the headroom above is deliberate), footer takeaway line at y=H-100 (1341), source line at y=H-57 (1384). Left margin x=72, content width 870 (right edge 942). The chart body lives between `Card.top` and `Card.bottom` (H-150).
- `scripts/te_lib.py` builds all of this: Card.title / subtitle / kpi_row / footer / source. Use it for every new card. make_flow.py is the original reference post ("How Nvidia makes money?") and is still used for the How (company) series.
- Pure flat vector: paths only, text outlined, solid colours (no opacity, gradients, images, filters, drop shadows). Must stay sharp when imported into Canva. Groups must be flat (no nested groups except flag clip-paths).
- Title: Charter bold serif, up to 92 px, two lines max, yellow marker (#EDE22E) behind the key word. Subtitle 24 px grey Inter Medium. Footer 30 px Inter Bold, one punchy takeaway sentence. Source line 15 px grey: "Source: <names> · <year/date>" with real middle dots.

## Colours
- True Economy red #E23B3B (negative, loss, danger, "the highlight country/company"), blue #0760F1 (primary), dark blue #0548B5, light blue #5B9BFF / #8DB8FF, yellow #EDE22E (marker, highlights, "net/keeps"), green #1FA35C (gains only), ink #111111, grey #555555, pale box #EEEEEC.
- Red must be the exact True Economy red, never orange-ish.

## Style (from the user's stated preferences)
- Clean, professional Vox look. Not childish, not presentation-like. No decorative circles. Flags/icons are fine when they carry meaning.
- Bold type, plenty of white space, a clear hierarchy: ONE big idea per card, readable at phone size (smallest label 15 px, key numbers 26 px+).
- Likes: bar charts with bold values, donut/pie, dot grids ("100 people" style), flow/Sankey, slope charts, ranked lists with flags, comparison splits.
- Centred or evenly balanced layouts; no lopsided empty areas; no blank screens.
- Smooth motion only. No jitter or shake.

## Creative freedom
- Every post should look newly designed for its topic (new chart form, new composition) while the chrome above and the colours/fonts stay identical. Vary: chart type, layout, how the key number is staged, which element is highlighted in red or yellow.
- Never copy the exact layout of the previous post in the log. If the feedback file says the user disliked something, do not repeat it.

## Video (scripts/video_card.py)
- 4K vertical 2160x3840, 30 fps, length = the music loop (6-10 s), seamless loop; the first frame equals the last frame (platforms use the first frame as the thumbnail). The card, title, subtitle, footer and source never move. Only the animation layer moves: money streaks (flow ribbons), pulsing highlights (Card.pulse), or a soft sweep. Register animation through Card.ribbon / Card.pulse or pass anim={...} to Card.save.

## Clarity first (applies to every post; checked in final QA)
Before building, write one line: "the one comparison/idea is ___". Then:
1. Colour logic matches meaning. Things of the same kind get the SAME colour (e.g. bought and sold are both blue; never different shades just for variety). Only the difference, gap or problem is True Economy red. A positive item that reduces a red total is green and carries a short note such as "cuts the gap". Keep each colour's meaning across the whole card.
2. Show relationships on ONE chart, not in separate sections. A derived figure (gap, net, share) is drawn on the same scale, aligned under or over its source, joined by thin dotted guide lines.
3. Build breakdowns as a visible sum: number the steps (1. 2. 3.) and write the arithmetic in the last label (e.g. "$1,260bn − $328bn = the trade deficit"). Direction must be obvious.
4. Labels are for a first-time viewer: plain words with the number in the sentence ("US buys $1,260bn more than it sells"). No labels that only make sense if you already know the topic. Units and year visible.
5. No collisions: check every label against every dotted line, bar and flag in the render; shorten the label or move it so it ends before the line. Do this on the SVG render BEFORE building the video.
6. Final QA question, answered by looking at the frame: "Could a confused viewer explain each section back in one sentence, and see in 3 seconds what is compared and what the gap is?" If not, simplify or relabel and rebuild before queueing.

## Caption limits
- Instagram: at most 5 hashtags in total (caption + firstComment combined). TikTok 3-5. Facebook at most 2. YouTube 3. X/Threads/Bluesky at most 2. LinkedIn at most 3.
