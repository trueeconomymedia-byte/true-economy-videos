#!/usr/bin/env python3
"""True Economy "THEN VS NOW" animation style (approved by the user 11 Nov 2026). Same renderer contract as every
animation style in playbook/animated/registry.json:

    python3 thennow_short.py data.json OUTDIR SLUG

Starts in the past on one value ("In 1995, a new US home cost $133,000."), the camera rides the tip of the line forward
year by year (a tick per year), dotted event markers drop in as it passes them, an optional comparison line (e.g. income)
runs underneath with the gap shaded, then the camera pulls back to the whole climb and the answer lands in gold.
Writes to OUTDIR:
  SLUG-youtube.mp4       the video -> sent to the user, who posts YouTube by hand
  SLUG-auto.mp4          the SAME video -> Buffer, with metadata.thumbnailOffset = "thumb_ms" in SLUG-build.json (33 = first frame)
  REWIND OPENING (approved by the user 11 Nov 2026, on by default; "cold_open": false turns it off): the first frame is the
  whole climb with today's values ("$???") and the answer ("??x") hidden; the line rewinds to the first year in ~1.1 s
  (faint ghost of the full line, tape-rewind sound + year ticks), lands on a hit, the title pops
  and the gold marker sweeps in; the reveal hold is short so the end frame loops back into the first frame.
  SLUG-thumb-tease.png   the first frame (whole climb, today's value and answer hidden) -> YouTube custom thumbnail
  SLUG-thumb-answer.png  the whole climb with the answer
  SLUG-qa-youtube.jpg    contact sheet of key frames: LOOK at it
  SLUG-build.json        every number the video shows (all derived numbers computed here, never typed)
Exit codes: 0 ok; 3 unsupported (fewer than 10 or more than 40 yearly points, a gap in the years, a value not above
zero, more than 5 events); 4 data problem (missing field, series not in the library, lengths differ, an event outside
the years, a marker word not in its headline line, a headline line over 26 characters, unknown placeholder).

data.json:
  series     id of a verified series in playbook/animated/data/<id>.json (the data library: years, main.values,
             compare.values, sources) - OR give "years", "main" and optional "compare" lists inline (also add the
             series to the library so it is never fetched twice)
  start_year, end_year   optional: trim the library series (10-40 years)
  currency   "$" | "£" | "€" | "" ; suffix optional, e.g. "%" for rates
  main_label     short label at the tip, e.g. "typical new home"
  compare_label  optional, e.g. "median income"; ratio_style "times" (default, user rule 11 Nov 2026: tip tag "= 3.9x median income",
             answer "1995: 3.9x → 2025: 4.7x median income") | "years" ("= 3.9 years of income"); ratio_label the words
             after the ratio, default "median income" (times) / "years of income" (years). Say "median" when the data is a
             median (never call a median "average")
  colour     main line: "blue" (default) | "red" | "teal"; gap_colour "red" (main outruns compare, default) | "teal"
  events     [[year, "label"], ...] at most 5, each verified (playbook/animated/events.json), inside the years
  headline_q [line1, line2, words to mark gold]  e.g. ["Cost of a US home:", "{y0} vs {y1}", "{y0} vs {y1}"] (user rule 11 Nov 2026)
  headline_a [line1, line2, words to mark gold]  e.g. ["{start} → {end}", "{ratio_start}x → {ratio_end}x income", "{ratio_end}x"]
  final, tease  optional; defaults (times): "{y0}: {ratio_start}x → {y1}: {ratio_end}x median income" / "... → {y1}: ??x median income"
             (without a compare line: "{y0}: {start} → {y1}: {end}" / "... → {y1}: {cur}??")
  source     e.g. "Source: U.S. Census Bureau & HUD via FRED (MSPUS, MEHOINUSA646N)"
  Placeholders: {y0} {y1} {start} {end} {cstart} {cend} {ratio_start} {ratio_end} {pct} {times} {cur}
Needs: node + playwright (pre-installed), ffmpeg, numpy, scipy, opencv-python, Pillow. Fonts: Lora (scripts/assets), Inter (system).
"""
import json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIB = os.path.join(ROOT, "playbook", "animated", "data")
MAXLINE = 26

def fmt(v, cur, suf=""):
    a = abs(v)
    if a >= 1e9: s = f"{a/1e9:.{1 if a >= 1e10 else 2}f}bn"
    elif a >= 1e6: s = f"{a/1e6:.1f}m"
    elif a >= 1e5: s = f"{round(a/1000)*1000:,}"
    elif a >= 1e4: s = f"{round(a/10)*10:,}"
    elif a >= 100: s = f"{round(a):,}"
    else: s = f"{a:.2f}"
    return ("−" if v < 0 else "") + cur + s + suf

def fail(code, msg): print(msg); sys.exit(code)

def main():
    data_path, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = json.load(open(data_path))
    for k in ("main_label", "headline_q", "headline_a", "source"):
        if k not in d: fail(4, f"data.json missing {k}")
    if "series" in d:
        p = os.path.join(LIB, d["series"] + ".json")
        if not os.path.exists(p): fail(4, f"series '{d['series']}' is not in the data library ({p})")
        s = json.load(open(p)); years = s["years"]; main_v = s["main"]["values"]; comp = (s.get("compare") or {}).get("values")
    else:
        years = d["years"]; main_v = d["main"]; comp = d.get("compare")
    if comp is not None and len(comp) != len(main_v): fail(4, "main and compare have different lengths")
    if len(years) != len(main_v): fail(4, "years and values have different lengths")
    y0 = d.get("start_year", years[0]); y1 = d.get("end_year", years[-1])
    idx = [i for i, y in enumerate(years) if y0 <= y <= y1]
    years = [years[i] for i in idx]; main_v = [main_v[i] for i in idx]; comp = [comp[i] for i in idx] if comp else None
    if not 10 <= len(years) <= 40: fail(3, f"UNSUPPORTED: {len(years)} yearly points (10-40 only)")
    if any(b - a != 1 for a, b in zip(years, years[1:])): fail(3, "UNSUPPORTED: the years have a gap")
    if min(main_v) <= 0 or (comp and min(comp) <= 0): fail(3, "UNSUPPORTED: every value must be above zero")
    ev = d.get("events", [])
    if len(ev) > 5: fail(3, "UNSUPPORTED: at most 5 events")
    for e in ev:
        if not years[0] < e[0] <= years[-1]: fail(4, f"CHECK: event {e} is outside {years[0]}-{years[-1]}")
    cur = d.get("currency", ""); suf = d.get("suffix", "")
    F = lambda v: fmt(v, cur, suf)
    fill = {"y0": years[0], "y1": years[-1], "start": F(main_v[0]), "end": F(main_v[-1]), "cur": cur,
            "pct": f"{round((main_v[-1] / main_v[0] - 1) * 100):,}%", "times": f"{main_v[-1] / main_v[0]:.1f}×"}
    if comp:
        fill.update({"cstart": F(comp[0]), "cend": F(comp[-1]), "ratio_start": f"{main_v[0] / comp[0]:.1f}", "ratio_end": f"{main_v[-1] / comp[-1]:.1f}"})
    def X(s):
        try: return s.format(**fill)
        except KeyError as e: fail(4, f"CHECK: unknown or unavailable placeholder {e} in '{s}'")
    hq = [X(x) for x in d["headline_q"]]; ha = [X(x) for x in d["headline_a"]]
    for h in (hq, ha):
        if h[2] not in h[0] and h[2] not in h[1]: fail(4, f"CHECK: marker '{h[2]}' is not in the headline {h[:2]}")
        for line in h[:2]:
            if len(line) > MAXLINE: fail(4, f"CHECK: headline line '{line}' is {len(line)} characters (max {MAXLINE}); shorten it")
    rs = d.get("ratio_style", "times")      # user rule 11 Nov 2026: "3.9x median income" is how people talk about it
    if rs not in ("times", "years"): fail(4, f"CHECK: ratio_style must be 'times' or 'years', not {rs!r}")
    rl = d.get("ratio_label", "median income" if rs == "times" else "years of income")
    if comp:
        if rs == "times":
            final = X(d.get("final", "{y0}: {ratio_start}x  →  {y1}: {ratio_end}x " + rl))
            tease = X(d.get("tease", "{y0}: {ratio_start}x  →  {y1}: ??x " + rl))
        else:
            final = X(d.get("final", "{y0}: {ratio_start} years  →  {y1}: {ratio_end} years"))
            tease = X(d.get("tease", "{y0}: {ratio_start} years  →  {y1}: ?? years"))
    else:
        final = X(d.get("final", "{y0}: {start}  →  {y1}: {end}")); tease = X(d.get("tease", "{y0}: {start}  →  {y1}: {cur}??"))
    g = {"years": years, "main": main_v, "compare": comp, "currency": cur, "suffix": suf, "main_label": d["main_label"],
         "compare_label": d.get("compare_label", ""), "ratio_label": rl, "ratio_style": rs, "colour": d.get("colour", "blue"),
         "gap_colour": d.get("gap_colour", "red"), "events": ev, "headline_q": hq, "headline_a": ha, "final": final,
         "tease": tease, "source": d["source"], "numbers": fill, "cold_open": bool(d.get("cold_open", True))}
    gpath = os.path.join(outdir, f"{slug}-build.json"); json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"{d.get('subject', slug)}: {fill['start']} ({years[0]}) -> {fill['end']} ({years[-1]})"
          + (f", ratio {fill['ratio_start']} -> {fill['ratio_end']}" if comp else f", {fill['pct']}"))
    subprocess.run(["node", os.path.join(HERE, "thennow_render.js"), gpath, outdir, slug], check=True)
    beats = os.path.join(outdir, f"{slug}-beats-youtube.json"); wav = os.path.join(outdir, f"{slug}-youtube.wav")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "anim_shared", "beats_audio.py"), beats, wav], check=True)
    silent = os.path.join(outdir, f"{slug}-youtube-silent.mp4"); final_p = os.path.join(outdir, f"{slug}-youtube.mp4"); tmp = final_p + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, final_p); os.remove(silent); os.remove(wav)
    b = json.load(open(beats))
    sel = "+".join(f"eq(n\\,{max(0, int(t * 30))})" for t in b["qa"])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final_p, "-vf", f"select='{sel}',scale=320:-1,tile={len(b['qa'])}x1",
                    "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-youtube.jpg")], check=True)
    shutil.copyfile(final_p, os.path.join(outdir, f"{slug}-auto.mp4"))
    g["thumb_ms"] = b["thumb_ms"]; json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"done: {final_p} ({b['total']:.1f}s); Buffer cover: thumbnailOffset {b['thumb_ms']}")
    print("thumbnails:", os.path.join(outdir, f"{slug}-thumb-tease.png"), os.path.join(outdir, f"{slug}-thumb-answer.png"))

if __name__ == "__main__":
    main()
