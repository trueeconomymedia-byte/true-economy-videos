#!/usr/bin/env python3
"""True Economy "IF IT WERE 100" animation style (approved by the user and added to the Animated Shorts schedule 23 Nov 2026). Renderer contract:

    python3 hundred_short.py data.json OUTDIR SLUG

A row of 100 blocks (one household / person each) fills the top; each group pours DOWN as a ribbon with flowing dashes
into its share of the bar at the bottom (v2 flow style, 22 Nov 2026). One ribbon at a time; the last part of the last
group is hidden as "?%" until the gold reveal.
data.json:
  headline_q, headline_a   [line1, line2, words to mark gold] (max 26 characters a line)
  left_label, right_label   headers above the two bars, e.g. "100 households" / "Share of wealth"
  groups       play order, e.g. [{"name": "Bottom 50", "n": 50, "share": 9, "colour": "red"},
               {"name": "Middle 40", "n": 40, "share": 50},
               {"name": "Richest 10", "n": 10, "share": 41, "split": [{"name": "Next 9", "n": 9, "share": 31},
                                                                       {"name": "Richest 1", "n": 1, "share": 10}]}]
               the LAST group must have a 2-part "split" (the second part is the gold reveal); n sums to 100, shares to 100
  source       source line (shown on the final frame)
  sources      list of at least 2 pages the figures were checked against (primary first); not shown, kept in the build
  period       what the figures cover, e.g. "Great Britain, April 2020 to March 2022"
Colours per group/part: "red" (the squeezed group), "teal", default blue; the last part is always gold.
The video opens on the finished chart with the last share hidden as "?%" (the cover, thumb_ms 33), rewinds, then plays.
Exit codes: 0 ok; 3 unsupported (more than 5 parts, or a part under 1% of either side); 4 data problem (counts or shares
do not add up, headline too long, marker missing, fewer than 2 sources, no period).
"""
import json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); MAXLINE = 26
def fail(c, m): print(m); sys.exit(c)
def main():
    data_path, outdir, slug = sys.argv[1:4]; os.makedirs(outdir, exist_ok=True); d = json.load(open(data_path))
    for k in ("headline_q", "headline_a", "left_label", "right_label", "groups", "source", "sources", "period"):
        if k not in d: fail(4, f"data.json missing {k}")
    G = d["groups"]; last = G[-1]
    if len(G) < 2 or len(last.get("split", [])) != 2: fail(4, "CHECK: need 2+ groups and the last group must split into 2 parts")
    if sum(g["n"] for g in G) != 100: fail(4, "CHECK: the group sizes must add up to 100")
    if abs(sum(g["share"] for g in G) - 100) > 0.01: fail(4, "CHECK: the shares must add up to 100")
    if sum(p["n"] for p in last["split"]) != last["n"] or abs(sum(p["share"] for p in last["split"]) - last["share"]) > 0.01:
        fail(4, "CHECK: the split parts must add up to the last group")
    if len(d["sources"]) < 2: fail(4, "CHECK: every episode needs at least 2 sources")
    parts = G[:-1] + last["split"]
    if len(parts) > 5: fail(3, "UNSUPPORTED: at most 5 parts")
    if any(p["n"] < 1 or p["share"] < 1 for p in parts): fail(3, "UNSUPPORTED: every part needs at least 1% on both sides to be visible")
    for h in (d["headline_q"], d["headline_a"]):
        if h[2] not in h[0] and h[2] not in h[1]: fail(4, f"CHECK: marker '{h[2]}' is not in the headline")
        for line in h[:2]:
            if len(line) > MAXLINE: fail(4, f"CHECK: headline line '{line}' is {len(line)} characters (max {MAXLINE})")
    gpath = os.path.join(outdir, f"{slug}-build.json"); json.dump(d, open(gpath, "w"), ensure_ascii=False, indent=1)
    subprocess.run(["node", os.path.join(HERE, "hundred_render.js"), gpath, outdir, slug], check=True)
    beats = os.path.join(outdir, f"{slug}-beats-youtube.json"); wav = os.path.join(outdir, f"{slug}-youtube.wav")
    subprocess.run([sys.executable, os.path.join(HERE, "hundred_audio.py"), beats, wav], check=True)
    silent = os.path.join(outdir, f"{slug}-youtube-silent.mp4"); fp = os.path.join(outdir, f"{slug}-youtube.mp4"); tmp = fp + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, fp); os.remove(silent); os.remove(wav)
    b = json.load(open(beats)); sel = "+".join(f"eq(n\\,{max(0, int(t * 30))})" for t in b["qa"])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", fp, "-vf", f"select='{sel}',scale=320:-1,tile={len(b['qa'])}x1",
                    "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-youtube.jpg")], check=True)
    shutil.copyfile(fp, os.path.join(outdir, f"{slug}-auto.mp4"))
    d["thumb_ms"] = b["thumb_ms"]; json.dump(d, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"done: {fp} ({b['total']:.1f}s)")
if __name__ == "__main__": main()
