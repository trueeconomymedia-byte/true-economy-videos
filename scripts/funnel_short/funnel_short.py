#!/usr/bin/env python3
"""True Economy FUNNEL animation style (approved by the user 10 Nov 2026). Renderer contract shared by every
animation style in playbook/animated/registry.json:

    python3 funnel_short.py data.json OUTDIR SLUG

Writes to OUTDIR:
  SLUG-auto.mp4          opens fully zoomed out (full chart, answer hidden) and zooms straight in, no still moment; the hook
                         title fades as the chart moves up and the money bar (amount + gold/dark-red bar) takes its place
                         (user default 11 Nov 2026) -> Buffer, thumbnailOffset 33 (first frame)
  SLUG-youtube.mp4       the SAME video -> sent to the user, who posts YouTube by hand
  SLUG-thumb-tease.png   full chart with the answer hidden -> YouTube custom thumbnail
  SLUG-thumb-answer.png  full chart with the answer
  SLUG-qa-auto.jpg, SLUG-qa-youtube.jpg  contact sheets of key frames: LOOK at them
Exit codes: 0 ok; 3 unsupported shape (a stage at or below zero, or more than 5 steps); 4 numbers do not add up.

data.json is EITHER the company format (make_flow.py keys, $ billions):
  company, period, rev, cogs, opex, other, tax, segments[{lines,value}], cogs_name, opex_name, tax_name, other_label,
  source, and the REPORTED totals gp, op, pbt, ni (always copy them from the release so labels match it)
OR the generic format (salary, government, prices, household, news):
  headline_q [line1, line2, words to mark gold]   e.g. ["You earn £35,000.", "How much do you keep?", "£35,000"]
  headline_a [line1, line2, words to mark gold]   e.g. ["You keep £28,900", "of your £35,000", "£28,900"]
  fmt {prefix, suffix, decimals}                  "$","B",1 -> $92.3B | "£","",0 -> £35,000 | "£","",2 -> £1.38
  start {value, label}                            the top of the funnel, e.g. {"value":35000,"label":"Salary"}
  segments [{lines:[...], value}]                 optional bands across the funnel mouth (max 3 shown; the rest -> Other)
  steps [{kind:"cost"|"gain", amt, name, stage, val, note?}]  1-5 steps, in order; cost = red stream peeling off,
        gain = teal stream joining (e.g. borrowing); val = amount left after the step (> 0); the LAST step's val is the
        gold payoff and its stage label is not shown (the gold box says it)
  share {style:"per", sym:"¢", of:"$1"} | {style:"pct", of:"pay"} | null   small line under each stage value
  final {text, sub, tease, tease_sub}             gold box, e.g. "£28,900 take-home" / "83p of every £1" / "£?? kept" / ...
  pill {in, left}                                 counter words (default "in" / "left")
  source                                          source line shown on the wide shot
  logo_key (optional)                             looks for scripts/assets/logos/<logo_key>.png|svg
Needs: node + playwright (pre-installed), ffmpeg, numpy, scipy. Fonts: Lora (scripts/assets) and Inter (system).
"""
import json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def fmt_money(v, fmt):
    p, s, d = fmt.get("prefix", "$"), fmt.get("suffix", "B"), fmt.get("decimals", 1)
    a = abs(v)
    if s == "B" and a < 1: return f"{p}{round(a*1000)}M"
    return f"{p}{a:,.{d}f}{s}"

def from_company(d):
    rev = d["rev"]; gp = d.get("gp", rev - d["cogs"]); op = d.get("op", gp - d["opex"])
    oth = d.get("other", 0); pbt = d.get("pbt", op + oth); ni = d.get("ni", pbt - d["tax"])
    fmt = {"prefix": "$", "suffix": "B", "decimals": 1}
    m = lambda v: fmt_money(v, fmt)
    steps = [{"kind": "cost", "amt": d["cogs"], "name": d.get("cogs_name", "Cost of revenue"), "stage": "Gross profit", "val": gp}]
    if abs(oth) < 0.015 * rev:
        note = None
        if oth: note = ("+" if oth > 0 else "−") + m(oth) + " " + (d.get("other_label", "other income") if oth > 0 else "other costs")
        steps.append({"kind": "cost", "amt": d["opex"], "name": d.get("opex_name", "R&D, sales & admin"),
                      "stage": "Profit before tax", "val": pbt, "note": note, "width_amt": gp - pbt})
    else:
        steps.append({"kind": "cost", "amt": d["opex"], "name": d.get("opex_name", "R&D, sales & admin"), "stage": "Operating profit", "val": op})
        if oth > 0: steps.append({"kind": "gain", "amt": oth, "name": d.get("other_label", "Other income"), "stage": "Profit before tax", "val": pbt})
        else: steps.append({"kind": "cost", "amt": -oth, "name": d.get("other_label", "Other costs"), "stage": "Profit before tax", "val": pbt})
    if d["tax"] >= 0: steps.append({"kind": "cost", "amt": d["tax"], "name": d.get("tax_name", "Tax"), "stage": "Net income", "val": ni})
    else: steps.append({"kind": "gain", "amt": -d["tax"], "name": d.get("tax_name", "Tax benefit"), "stage": "Net income", "val": ni})
    c = f"{round(ni / rev * 100)}¢"; co = d["company"]
    return {"headline_q": [f"{co} made {m(rev)}.", "How much did it keep?", m(rev)],
            "headline_a": [f"{co} kept {c}", "of every $1 it made", c],
            "fmt": fmt, "start": {"value": rev, "label": "Revenue"}, "segments": d.get("segments", []), "steps": steps,
            "share": {"style": "per", "sym": "¢", "of": "$1"},
            "final": {"text": f"{m(ni)} kept", "sub": f"{c} of every $1 became profit",
                      "tease": "$?? kept", "tease_sub": "How much of every $1 became profit?"},
            "source": d["source"], "logo_key": d.get("logo_key", co), **({"logo": d["logo"]} if d.get("logo") else {})}

def check(g):
    for k in ("headline_q", "headline_a", "start", "steps", "final", "source"):
        if k not in g: print(f"data.json missing {k}"); sys.exit(4)
    if not 1 <= len(g["steps"]) <= 5: print("UNSUPPORTED: 1-5 steps only"); sys.exit(3)
    tol = 0.006 * g["start"]["value"] + 10 ** -(g.get("fmt", {}).get("decimals", 1)) * 1.01
    run = g["start"]["value"]
    for s in g["steps"]:
        calc = run - s["amt"] if s["kind"] == "cost" else run + s["amt"]
        if s["val"] <= 0: print(f"UNSUPPORTED: '{s['stage']}' is {s['val']} (must stay above zero)"); sys.exit(3)
        if abs(calc - s["val"]) > tol:
            print(f"CHECK: after '{s['name']}' the parts give {calc:.3f} but val is {s['val']}; fix data.json"); sys.exit(4)
        run = s["val"]
    for line in (g["headline_q"], g["headline_a"]):
        if line[2] not in line[0] and line[2] not in line[1]: print(f"CHECK: marker '{line[2]}' is not in the headline"); sys.exit(4)

def main():
    data_path, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = json.load(open(data_path))
    g = from_company(d) if "rev" in d and "steps" not in d else d
    check(g)
    g.setdefault("ink", True)          # printed-ink finish on the card paper is the default (user-approved 11 Nov 2026)
    g.setdefault("title_mode", "fade") # user default 11 Nov 2026: hook title fades as the chart moves up, the money bar takes its place
    g.setdefault("bar_red", "dark")    # user default 11 Nov 2026: money bar = gold left, dark red taken
    g.setdefault("dash_density", 2); g.setdefault("dash_vary", True)   # user default 11 Nov 2026: twice the flow pieces, varied length and speed
    gpath = os.path.join(outdir, f"{slug}-funnel-data.json"); json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    # ONE video for every platform (user default 11 Nov 2026): opens fully zoomed out and zooms in at once; YouTube gets the same file
    subprocess.run(["node", os.path.join(HERE, "funnel_render.js"), gpath, outdir, slug], check=True, env={**os.environ, "FUNNEL_VARIANTS": "auto"})
    for v in ("auto",):
        beats = os.path.join(outdir, f"{slug}-beats-{v}.json")
        wav = os.path.join(outdir, f"{slug}-{v}.wav")
        subprocess.run([sys.executable, os.path.join(HERE, "funnel_audio.py"), beats, wav], check=True)
        silent = os.path.join(outdir, f"{slug}-{v}-silent.mp4")
        final = os.path.join(outdir, f"{slug}-{v}.mp4"); tmp = final + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, final); os.remove(silent); os.remove(wav)
        b = json.load(open(beats))
        ts = [0.05, b["cold"] + 2.0] + [s["b"] + 1.2 for s in b["steps"]] + [b["kt"] + 1.6, b["pull1"] + 1.0, b["total"] - 0.1]
        sel = "+".join(f"eq(n\\,{int(t*30)})" for t in ts)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf", f"select='{sel}',scale=360:-1,tile={len(ts)}x1",
                        "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-{v}.jpg")], check=True)
        print(f"done {v}: {final} ({b['total']:.1f}s)")
    for a, b_ in ((f"{slug}-auto.mp4", f"{slug}-youtube.mp4"), (f"{slug}-qa-auto.jpg", f"{slug}-qa-youtube.jpg")):
        shutil.copyfile(os.path.join(outdir, a), os.path.join(outdir, b_))
    print("thumbnails:", os.path.join(outdir, f"{slug}-thumb-tease.png"), os.path.join(outdir, f"{slug}-thumb-answer.png"))

if __name__ == "__main__":
    main()
