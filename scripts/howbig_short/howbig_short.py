#!/usr/bin/env python3
"""True Economy "HOW BIG IS IT REALLY?" animation style (approved by the user 11 Nov 2026). Same renderer contract as
every animation style in playbook/animated/registry.json:

    python3 howbig_short.py data.json OUTDIR SLUG

1 square = 1 HOUR of the money. Day 1 fills hour by hour (00:00, 01:00 ...), then the camera pulls back to the first
week, then the first months, then the whole period laid out as a calendar; the total stays hidden ("£??") until the
gold reveal. Writes to OUTDIR:
  SLUG-auto.mp4          cold open (finished grid, total hidden, rewinds into Day 1) -> posted through Buffer
  SLUG-youtube.mp4       starts straight on Day 1 -> sent to the user, who posts YouTube by hand
  SLUG-thumb-tease.png   finished grid with the total hidden -> YouTube custom thumbnail
  SLUG-thumb-answer.png  finished grid with the total
  SLUG-qa-auto.jpg, SLUG-qa-youtube.jpg  contact sheets of key frames: LOOK at them
  SLUG-build.json        every number the video shows (all derived numbers are computed here, never typed)
Exit codes: 0 ok; 3 unsupported (period under 42 or over 366 days, total not above zero, under £1 an hour);
4 data problem (missing field, a marker word not in its headline line, a headline line too long, a placeholder unknown).

data.json (the task writes ONLY the source numbers and words; per-hour/day/week figures come from the script):
  total     the money for the whole period, in currency units, e.g. 97600000000 (two sources)
  currency  "£" | "$" | "€"
  period    {"start": "2025-04-01", "end": "2026-03-31"}   inclusive dates the total covers (a year, a financial
            year or a company quarter; 42-366 days). Years are laid out by calendar month, shorter periods in rows of
            14 days.
  colour    "red" (a cost or a problem: debt interest, losses, fines) | "blue" (neutral: budgets, revenue, pay)
            | "teal" (money coming in that is good news: profit for savers, tax receipts)
  headline_q [line1, line2, words to mark gold]  e.g. ["UK debt interest costs", "{hour} every hour.", "{hour}"]
  headline_a [line1, line2, words to mark gold]  e.g. ["One year of interest:", "{total}.", "{total}"]
  key       what one square is, e.g. "1 hour of interest" (shown as "= 1 hour of interest (£11.1m)")
  final     gold answer box, e.g. "{total} a year"
  tease     optional, default "{cur}?? a year" (or "{cur}?? a quarter" for periods under 200 days)
  source    e.g. "Source: ONS & OBR, debt interest 2025-26 (Apr 2026)"  (" · {total} ÷ N hours" is added)
  Placeholders, filled from the computed numbers: {hour} {day} {week} {total} {cur} {hours}
  Each headline line must fit 2 lines at the series' title size: about 24 characters per line after filling.
Needs: node + playwright (pre-installed), ffmpeg, numpy, scipy, opencv-python, Pillow. Fonts: Lora (scripts/assets), Inter (system).
"""
import json, os, subprocess, sys, calendar, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
MAXLINE = 26

def money(v, cur):
    a = abs(v)
    if a >= 1e9: return f"{cur}{a/1e9:.{1 if a >= 1e10 else 2}f}bn"
    if a >= 1e6: return f"{cur}{a/1e6:.1f}m"
    if a >= 1e3: return f"{cur}{round(a):,}"
    return f"{cur}{a:.2f}"

def fail(code, msg): print(msg); sys.exit(code)

def rows_for(start, end):
    days = (end - start).days + 1
    if days >= 300:                                     # a year: one row per calendar month
        rows, d = [], start
        while d <= end:
            last = dt.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
            n = (min(last, end) - d).days + 1
            rows.append([d.strftime("%b"), n, d.day == 1 and min(last, end) == last]); d = min(last, end) + dt.timedelta(days=1)
        if rows[0][1] < 7: rows[1] = [rows[0][0] + "–" + rows[1][0], rows[0][1] + rows[1][1], False]; rows.pop(0)
        if rows[-1][1] < 7: rows[-2] = [rows[-2][0] + "–" + rows[-1][0], rows[-2][1] + rows[-1][1], False]; rows.pop()
        s3 = 3; full = all(r[2] for r in rows[:3])
        label = "3 months" if full else f"{sum(r[1] for r in rows[:3])} days"
    else:                                               # a quarter or similar: rows of 14 days, labelled by start date
        rows, d = [], start
        while d <= end:
            n = min(14, (end - d).days + 1); rows.append([f"{d.day} {d.strftime('%b')}", n, False]); d += dt.timedelta(days=n)
        if rows[-1][1] < 7 and len(rows) > 1: rows[-2][1] += rows[-1][1]; rows.pop()
        s3 = 2; label = f"{sum(r[1] for r in rows[:2])} days"
    return [[r[0], r[1]] for r in rows], s3, label, days

def main():
    data_path, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = json.load(open(data_path))
    for k in ("total", "currency", "period", "headline_q", "headline_a", "key", "final", "source"):
        if k not in d: fail(4, f"data.json missing {k}")
    start, end = (dt.date.fromisoformat(d["period"][k]) for k in ("start", "end"))
    rows, s3, s3label, days = rows_for(start, end)
    if not 42 <= days <= 366: fail(3, f"UNSUPPORTED: the period is {days} days (42-366 only)")
    total = float(d["total"]); cur = d["currency"]
    if total <= 0: fail(3, "UNSUPPORTED: total must be above zero")
    hours = days * 24; ph = total / hours
    if ph < 1: fail(3, f"UNSUPPORTED: {money(ph, cur)} an hour is too small for this format")
    s3days = sum(r[1] for r in rows[:s3])
    txt = {"hour": money(ph, cur), "day": money(ph * 24, cur), "week": money(ph * 168, cur), "stage3": money(ph * 24 * s3days, cur),
           "total": money(total, cur)}
    fill = {**txt, "cur": cur, "hours": f"{hours:,}"}
    def F(s):
        try: return s.format(**fill)
        except KeyError as e: fail(4, f"CHECK: unknown placeholder {e} in '{s}'")
    hq = [F(x) for x in d["headline_q"]]; ha = [F(x) for x in d["headline_a"]]
    for h in (hq, ha):
        if h[2] not in h[0] and h[2] not in h[1]: fail(4, f"CHECK: marker '{h[2]}' is not in the headline {h[:2]}")
        for line in h[:2]:
            if len(line) > MAXLINE: fail(4, f"CHECK: headline line '{line}' is {len(line)} characters (max {MAXLINE}); shorten it")
    tease = F(d.get("tease", "{cur}?? a year" if days >= 200 else "{cur}?? a quarter"))
    g = {"per_hour": ph, "currency": cur, "colour": d.get("colour", "red"), "rows": rows, "stage3_rows": s3, "stage3_label": s3label,
         "day1": f"{start.day} {start.strftime('%B %Y')}", "txt": txt, "headline_q": hq, "headline_a": ha, "key": F(d["key"]),
         "final": F(d["final"]), "tease": tease, "source": F(d["source"]) + f" · {txt['total']} ÷ {hours:,} hours",
         "hours": hours, "days": days}
    gpath = os.path.join(outdir, f"{slug}-build.json"); json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"{d.get('subject', slug)}: {txt['total']} over {days} days = {txt['hour']} an hour, {txt['day']} a day, {txt['week']} a week")
    subprocess.run(["node", os.path.join(HERE, "howbig_render.js"), gpath, outdir, slug], check=True)
    for v in ("auto", "youtube"):
        beats = os.path.join(outdir, f"{slug}-beats-{v}.json"); wav = os.path.join(outdir, f"{slug}-{v}.wav")
        subprocess.run([sys.executable, os.path.join(HERE, "howbig_audio.py"), beats, wav], check=True)
        silent = os.path.join(outdir, f"{slug}-{v}-silent.mp4"); final = os.path.join(outdir, f"{slug}-{v}.mp4"); tmp = final + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, final); os.remove(silent); os.remove(wav)
        b = json.load(open(beats))
        ts = [0.05] + [t for t in b["qa"][1:]] if v == "auto" else [t - b["cold"] for t in b["qa"][1:]]
        sel = "+".join(f"eq(n\\,{max(0, int(t * 30))})" for t in ts)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf", f"select='{sel}',scale=320:-1,tile={len(ts)}x1",
                        "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-{v}.jpg")], check=True)
        print(f"done {v}: {final} ({b['total']:.1f}s)")
    print("thumbnails:", os.path.join(outdir, f"{slug}-thumb-tease.png"), os.path.join(outdir, f"{slug}-thumb-answer.png"))

if __name__ == "__main__":
    main()
