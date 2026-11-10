#!/usr/bin/env python3
"""True Economy "How X makes money?" FUNNEL SHORT (approved by the user 10 Nov 2026).

Usage:  python3 funnel_short.py data.json OUTDIR SLUG
data.json = the make_flow.py data keys (values in $ billions): company, period, rev, cogs, opex, other, tax,
            optional reported totals gp, op, pbt, ni (ALWAYS give them from the release so labels match it),
            segments[{lines:[...], value}], other_label, cogs_name, opex_name, tax_name, source; optional logo (path).
Writes to OUTDIR:
  SLUG-funnel-auto.mp4     cold open (full chart with the answer hidden, then it rewinds into the funnel) -> Buffer
  SLUG-funnel-youtube.mp4  starts straight on the hook -> the user posts it to YouTube by hand
  SLUG-thumb-tease.png     full chart, answer hidden ("$?? kept") -> YouTube custom thumbnail
  SLUG-thumb-answer.png    full chart with the answer
  SLUG-qa-auto.jpg / SLUG-qa-youtube.jpg  contact sheets of key frames to LOOK at
Exit code 4 = reported totals do not tie to the parts (data error).
Exit code 3 = this company's numbers are not supported (a loss at any stage): use the make_flow.py card instead.
Needs: node + playwright (pre-installed), ffmpeg, numpy, scipy. Fonts: Lora (scripts/assets) and Inter (system).
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    data_path, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = json.load(open(data_path))
    gp = d.get("gp", d["rev"] - d["cogs"]); op = d.get("op", gp - d["opex"])
    pbt = d.get("pbt", op + d.get("other", 0)); ni = d.get("ni", pbt - d["tax"])
    for name, calc, rep in (("gp", d["rev"] - d["cogs"], gp), ("op", gp - d["opex"], op), ("pbt", op + d.get("other", 0), pbt), ("ni", pbt - d["tax"], ni)):
        if abs(calc - rep) > 0.0051 * d["rev"] + 0.06:
            print(f"CHECK: reported {name} {rep} differs from the parts ({calc:.2f}) by more than rounding; fix data.json"); sys.exit(4)
    if min(gp, op, pbt, ni) <= 0:
        print(f"UNSUPPORTED: loss at a stage (gp {gp:.2f}, op {op:.2f}, pbt {pbt:.2f}, ni {ni:.2f}); use make_flow.py")
        sys.exit(3)
    for k in ("company", "rev", "cogs", "opex", "tax", "source"):
        assert k in d, f"data.json missing {k}"
    subprocess.run(["node", os.path.join(HERE, "funnel_render.js"), data_path, outdir, slug], check=True)
    for v in ("auto", "youtube"):
        beats = os.path.join(outdir, f"{slug}-beats-{v}.json")
        wav = os.path.join(outdir, f"{slug}-{v}.wav")
        subprocess.run([sys.executable, os.path.join(HERE, "funnel_audio.py"), beats, wav], check=True)
        silent = os.path.join(outdir, f"{slug}-{v}-silent.mp4")
        final = os.path.join(outdir, f"{slug}-funnel-{v}.mp4"); tmp = final + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, final); os.remove(silent); os.remove(wav)
        b = json.load(open(beats))
        ts = [0.05, b["cold"] + 2.0] + [s["b"] + 1.2 for s in b["steps"]] + [b["kt"] + 1.6, b["pull1"] + 1.0, b["total"] - 0.1]
        sel = "+".join(f"eq(n,{int(t*30)})" for t in ts)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf", f"select='{sel}',scale=360:-1,tile={len(ts)}x1",
                        "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-{v}.jpg")], check=True)
        print(f"done {v}: {final} ({b['total']:.1f}s)")
    print("thumbnails:", os.path.join(outdir, f"{slug}-thumb-tease.png"), os.path.join(outdir, f"{slug}-thumb-answer.png"))

if __name__ == "__main__":
    main()
