#!/usr/bin/env python3
"""True Economy "HEAD TO HEAD" animation style. Same renderer contract as every animation style in
playbook/animated/registry.json:

    python3 h2h_short.py data.json OUTDIR SLUG

Two rivals (countries, cities, companies, generations, choices) over 3-7 rounds, one like-for-like measure per round.
Central axis: side A grows LEFT in blue, side B RIGHT in red; the better side of each round keeps full colour and wins
the point, the other fades to its light tint; a tie gives no point. The scoreboard updates on every point. The camera
zooms into each round, pulls back before the LAST round (the decider, shown as "?" with the final score hidden), then
the winner lands in gold. ~30 s. ACCURACY RULES live in playbook/animated/h2h.md; this script enforces the mechanical ones.
Writes to OUTDIR:
  SLUG-youtube.mp4, SLUG-auto.mp4 (same video; Buffer cover = thumbnailOffset "thumb_ms" in SLUG-build.json: the table
  with the decider hidden), SLUG-thumb-tease.png, SLUG-thumb-answer.png, SLUG-qa-youtube.jpg, SLUG-build.json
Exit codes: 0 ok; 3 unsupported (fewer than 3 or more than 7 rounds, a negative value); 4 data problem (missing field,
a round without a source for each side, a conversion without rate + source, a marker word not in its headline line,
a headline line over 26 characters, unknown placeholder).

data.json:
  a, b          side names, short ("US", "UK", "Apple", "Gen Z") - A is drawn LEFT in blue, B RIGHT in red
  rounds        [{ "name": "Median full-time pay", "sub": "per year, in US$" (max 8 words),
                   "note": "2025 · UK converted at the 2025 average rate" (small grey line under the bars: dates, method),
                   "better": "high" | "low",
                   "fmt": {"prefix": "$", "suffix": "", "decimals": 0, "round_to": 100},
                   "a": {"value": 62608, "source": "..."},
                   "b": {"value": 39039, "fx": {"rate": 1.3192, "source": "FRED AEXUSUK 2025 average"}, "source": "..."}
                 }, ...]   in play order; the LAST round is the decider. Values are converted in code (value x rate).
  headline_q    [line1, line2, words to mark gold]  e.g. ["US vs UK: who is", "really better off?", "better off"]
  headline_a    [line1, line2, words to mark gold]  e.g. ["The {winner} wins {score}.", "But Americans earn more.", "{score}"]
  final, tease  optional; defaults "{a} {sa} – {sb} {b}" and "Final score: {a} ? – ? {b}"
  source        the source line, e.g. "Sources: BLS, ONS, CDC, US Dept of Labor, Acas, FRED (exchange rate)"
  Placeholders: {a} {b} {winner} {loser} {score} (winner's score first, e.g. "3–2") {sa} {sb}
Needs: node + playwright (pre-installed), ffmpeg, numpy, scipy, opencv-python, Pillow. Fonts: Lora (scripts/assets), Inter (system).
"""
import json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAXLINE = 26

def fail(code, msg): print(msg); sys.exit(code)

def fmt(v, f):
    r = f.get("round_to"); d = f.get("decimals", 0)
    if r: v = round(v / r) * r
    s = f"{v:,.{d}f}"
    return f.get("prefix", "") + s + f.get("suffix", "")

def main():
    data_path, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = json.load(open(data_path))
    for k in ("a", "b", "rounds", "headline_q", "headline_a", "source"):
        if k not in d: fail(4, f"data.json missing {k}")
    R = d["rounds"]
    if not 3 <= len(R) <= 7: fail(3, f"UNSUPPORTED: {len(R)} rounds (3-7 only)")
    out = []; sa = sb = 0
    for i, r in enumerate(R):
        for k in ("name", "sub", "better", "a", "b"):
            if k not in r: fail(4, f"round {i+1} missing {k}")
        vals = []
        for side in ("a", "b"):
            x = r[side]
            if not x.get("source"): fail(4, f"round {i+1} side {side}: every number needs its source")
            v = float(x["value"])
            if "fx" in x:
                if not (x["fx"].get("rate") and x["fx"].get("source")): fail(4, f"round {i+1} side {side}: a conversion needs a rate and its source")
                v *= float(x["fx"]["rate"])
            if v < 0: fail(3, f"UNSUPPORTED: round {i+1} has a negative value")
            vals.append(v)
        va, vb = vals; f = r.get("fmt", {})
        ta, tb = fmt(va, f), fmt(vb, f)
        if ta == tb: win = "tie"
        elif r["better"] == "high": win = "a" if va > vb else "b"
        else: win = "a" if va < vb else "b"
        sa += win == "a"; sb += win == "b"
        m = max(va, vb) or 1
        out.append({"name": r["name"], "sub": r["sub"], "note": r.get("note", ""), "fmt": f, "va": va, "vb": vb, "ta": ta, "tb": tb,
                    "fa": va / m, "fb": vb / m, "win": win, "better": r["better"]})
        if len(r["sub"].split()) > 8: fail(4, f"CHECK: round {i+1} sub-label is over 8 words; keep it short and put dates in 'note'")
    winner, loser = (d["a"], d["b"]) if sa > sb else (d["b"], d["a"]) if sb > sa else ("", "")
    fill = {"a": d["a"], "b": d["b"], "sa": sa, "sb": sb, "winner": winner or "nobody", "loser": loser or "nobody",
            "score": f"{max(sa, sb)}–{min(sa, sb)}"}
    def X(s):
        try: return s.format(**fill)
        except KeyError as e: fail(4, f"CHECK: unknown placeholder {e} in '{s}'")
    hq = [X(x) for x in d["headline_q"]]; ha = [X(x) for x in d["headline_a"]]
    for h in (hq, ha):
        if h[2] not in h[0] and h[2] not in h[1]: fail(4, f"CHECK: marker '{h[2]}' is not in the headline {h[:2]}")
        for line in h[:2]:
            if len(line) > MAXLINE: fail(4, f"CHECK: headline line '{line}' is {len(line)} characters (max {MAXLINE}); shorten it")
    g = {"a": d["a"], "b": d["b"], "rounds": out, "headline_q": hq, "headline_a": ha,
         "final": X(d.get("final", "{a} {sa} – {sb} {b}")), "tease": X(d.get("tease", "Final score: {a} ? – ? {b}")),
         "source": d["source"], "score": fill}
    gpath = os.path.join(outdir, f"{slug}-build.json"); json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    for i, r in enumerate(out): print(f"round {i+1} {r['name']}: {d['a']} {r['ta']} vs {d['b']} {r['tb']} -> {r['win']}")
    print(f"final: {d['a']} {sa} - {sb} {d['b']}")
    subprocess.run(["node", os.path.join(HERE, "h2h_render.js"), gpath, outdir, slug], check=True)
    beats = os.path.join(outdir, f"{slug}-beats-youtube.json"); wav = os.path.join(outdir, f"{slug}-youtube.wav")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "anim_shared", "beats_audio.py"), beats, wav], check=True)
    silent = os.path.join(outdir, f"{slug}-youtube-silent.mp4"); fp = os.path.join(outdir, f"{slug}-youtube.mp4"); tmp = fp + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, fp); os.remove(silent); os.remove(wav)
    b = json.load(open(beats))
    sel = "+".join(f"eq(n\\,{max(0, int(t * 30))})" for t in b["qa"])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", fp, "-vf", f"select='{sel}',scale=320:-1,tile={len(b['qa'])}x1",
                    "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-youtube.jpg")], check=True)
    shutil.copyfile(fp, os.path.join(outdir, f"{slug}-auto.mp4"))
    g["thumb_ms"] = b["thumb_ms"]; json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"done: {fp} ({b['total']:.1f}s); Buffer cover: thumbnailOffset {b['thumb_ms']}")
    print("thumbnails:", os.path.join(outdir, f"{slug}-thumb-tease.png"), os.path.join(outdir, f"{slug}-thumb-answer.png"))

if __name__ == "__main__":
    main()
