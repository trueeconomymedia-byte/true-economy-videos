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
