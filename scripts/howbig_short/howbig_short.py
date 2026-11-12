#!/usr/bin/env python3
"""True Economy "HOW BIG IS IT REALLY?" animation style (approved by the user 11 Nov 2026). Same renderer contract as
every animation style in playbook/animated/registry.json:

    python3 howbig_short.py data.json OUTDIR SLUG

1 square = 1 HOUR of the money. Day 1 fills hour by hour (00:00, 01:00 ...), then the camera pulls back to the first
week, then the first months, then the whole period laid out as a calendar; the total stays hidden ("£??") until the
gold reveal. Writes to OUTDIR:
  SLUG-youtube.mp4       starts straight on Day 1 -> sent to the user, who posts YouTube by hand
  SLUG-auto.mp4          the SAME video (no cold open: the user found the rewind off-putting) -> posted through Buffer
                         with metadata.thumbnailOffset = SLUG-build.json "thumb_ms" (the finished grid, total hidden)
  SLUG-thumb-tease.png   finished grid with the total hidden -> YouTube custom thumbnail
  SLUG-thumb-answer.png  finished grid with the total
  SLUG-qa-youtube.jpg    contact sheet of key frames: LOOK at it
  SLUG-build.json        every number the video shows (all derived numbers are computed here, never typed)
Exit codes: 0 ok; 3 unsupported (period under 42 or over 366 days, total not above zero, under £1 an hour);
4 data problem (missing field, a marker word not in its headline line, a headline line too long, a placeholder unknown).

data.json (the task writes ONLY the source numbers and words; per-hour/day/week figures come from the script):
  total     the money for the whole period, in currency units, e.g. 97600000000 (two sources)
  currency  "£" | "$" | "€"
  period    {"start": "2025-04-01", "end": "2026-03-31"}   inclusive dates the total covers (a year, a financial
            year or a company quarter; 42-366 days). Up to 4 months: one calendar block per month side by side
            (7 days a row); longer: one row per month. Captions: 1 Day, 1 Week = .., 1 Month = .., 1 Quarter/1 Year = ..
  colour    "red" (a cost or a problem: debt interest, losses, fines) | "blue" (neutral: budgets, revenue, pay)
            | "teal" (money coming in that is good news: profit for savers, tax receipts)
  headline_q [line1, line2, words to mark gold]  e.g. ["UK debt interest costs", "{hour} every hour.", "{hour}"]
  headline_a [line1, line2, words to mark gold]  e.g. ["One year of interest:", "{total}.", "{total}"]
  key       what one square is, e.g. "1 hour of interest" (kept for the build; on screen the key is simply "■ = £11.1m",
            user 12 Nov 2026); the counter sits under a progress bar (no black pill)
  final     optional gold answer box, default "{whole} = {total}" (e.g. "1 Year = £97.6bn", "1 Quarter = $36.6bn")
  tease     optional, default "{whole} = {cur}??"
  logo      optional, e.g. "shell": a transparent PNG the USER added at scripts/assets/logos/shell.png, shown centred
            above the title (y 170-285, above the safe zone: user, 12 Nov 2026, visible once the Short is opened);
            laid on the finished frames EXACTLY as supplied (no printed-ink finish, no texture or recolouring), only scaled
  source    e.g. "Source: ONS & OBR, debt interest 2025-26 (Apr 2026)"  (" · {total} ÷ N hours" is added)
  Placeholders, filled from the computed numbers: {hour} {day} {week} {month} {total} {cur} {hours} {whole}
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

BW, BH, GD, GM, GMX = 3, 8, 0.7, 2.2, 4.0      # day block 3 x 8 hours; gaps between days, rows and month blocks (world units)

def months_in(start, end):
    """[(label, ndays, full_month)] for each calendar month in the period; a partial first/last month under 7 days is merged"""
    out, d = [], start
    while d <= end:
        last = dt.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
        n = (min(last, end) - d).days + 1
        out.append([d.strftime("%b"), n, d.day == 1 and min(last, end) == last]); d = min(last, end) + dt.timedelta(days=1)
    if len(out) > 1 and out[0][1] < 7: out[1] = [out[0][0] + "–" + out[1][0], out[0][1] + out[1][1], False]; out.pop(0)
    if len(out) > 1 and out[-1][1] < 7: out[-2] = [out[-2][0] + "–" + out[-1][0], out[-2][1] + out[-1][1], False]; out.pop()
    return out

def layout(start, end):
    """World positions of every day block. Up to 4 months: one calendar block per month, side by side (7 days a row),
    month name above. Longer: one row per month, month name on the left (the approved year layout)."""
    months = months_in(start, end); days, labels = [], []; h = 0
    if len(months) <= 4:
        bw = 7 * (BW + GD) - GD
        for m, (lab, n, full) in enumerate(months):
            x0 = m * (bw + GMX); labels.append([lab, x0 + bw / 2, -2.6, "middle", 30, h])
            for i in range(n): days.append([x0 + (i % 7) * (BW + GD), (i // 7) * (BH + GM)])
            h += n * 24
        rows0 = -(-months[0][1] // 7); maxrows = max(-(-n // 7) for _, n, _ in months)
        W = len(months) * (bw + GMX) - GMX
        views = {"day": [0, 0, BW, BH], "week": [0, 0, bw, BH], "month": [0, -4.5, bw, rows0 * (BH + GM) - GM + 4.5],
                 "all": [0, -4.5, W, maxrows * (BH + GM) - GM + 4.5]}
        box = [120, 640, 840, 820]; mbox = [120, 660, 840, 680]     # month stage a bit smaller: room for its caption
    else:
        for r, (lab, n, full) in enumerate(months):
            labels.append([lab, -0.9, r * (BH + GM) + BH / 2, "end", 22, h])
            for c in range(n): days.append([c * (BW + GD), r * (BH + GM)])
            h += n * 24
        maxrow = max(n for _, n, _ in months)
        views = {"day": [0, 0, BW, BH], "week": [0, 0, 7 * (BW + GD) - GD, BH], "month": [0, 0, months[0][1] * (BW + GD) - GD, BH],
                 "all": [0, 0, maxrow * (BW + GD) - GD, len(months) * (BH + GM) - GM]}
        box = [150, 640, 810, 820]; mbox = box
    return months, days, labels, views, box, mbox

def main():
    data_path, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = json.load(open(data_path))
    for k in ("total", "currency", "period", "headline_q", "headline_a", "key", "source"):
        if k not in d: fail(4, f"data.json missing {k}")
    start, end = (dt.date.fromisoformat(d["period"][k]) for k in ("start", "end"))
    days = (end - start).days + 1
    if not 42 <= days <= 366: fail(3, f"UNSUPPORTED: the period is {days} days (42-366 only)")
    total = float(d["total"]); cur = d["currency"]
    if total <= 0: fail(3, "UNSUPPORTED: total must be above zero")
    hours = days * 24; ph = total / hours
    if ph < 1: fail(3, f"UNSUPPORTED: {money(ph, cur)} an hour is too small for this format")
    months, daypos, labels, views, box, mbox = layout(start, end)
    m0 = months[0]; m0days = m0[1]
    txt = {"hour": money(ph, cur), "day": money(ph * 24, cur), "week": money(ph * 168, cur), "month": money(ph * 24 * m0days, cur),
           "total": money(total, cur)}
    whole = "1 Year" if days >= 360 else "1 Quarter" if 88 <= days <= 93 else f"{days} days"
    cap = {"week": f"1 Week = {txt['week']}", "month": (f"1 Month = {txt['month']}" if m0[2] else f"{m0days} days = {txt['month']}"),
           "whole": whole}
    fill = {**txt, "cur": cur, "hours": f"{hours:,}", "whole": whole}
    def F(s):
        try: return s.format(**fill)
        except KeyError as e: fail(4, f"CHECK: unknown placeholder {e} in '{s}'")
    hq = [F(x) for x in d["headline_q"]]; ha = [F(x) for x in d["headline_a"]]
    for h in (hq, ha):
        if h[2] not in h[0] and h[2] not in (h[1] or ""): fail(4, f"CHECK: marker '{h[2]}' is not in the headline {h[:2]}")
        for line in h[:2]:
            if len(line) > MAXLINE: fail(4, f"CHECK: headline line '{line}' is {len(line)} characters (max {MAXLINE}); shorten it")
    tease = F(d.get("tease", "{whole} = {cur}??"))
    g = {"per_hour": ph, "currency": cur, "colour": d.get("colour", "red"), "days": daypos, "labels": labels, "views": views, "box": box, "mbox": mbox,
         "month_hours": m0days * 24, "cap": cap,
         "day1": f"{start.day} {start.strftime('%B %Y')}", "txt": txt, "headline_q": hq, "headline_a": ha, "key": F(d["key"]),
         "final": F(d.get("final", "{whole} = {total}")), "tease": tease, "source": F(d["source"]) + f" · {txt['total']} ÷ {hours:,} hours",
         "hours": hours, "ndays": days}
    logo_png = None
    if d.get("logo"):   # user-supplied logo only (scripts/assets/logos/<name>.png, transparent); never drawn or downloaded
        lp = os.path.join(HERE, "..", "assets", "logos", f"{d['logo']}.png")
        if not os.path.exists(lp): fail(4, f"CHECK: logo file {lp} not found (only logos the user has added)")
        # UNALTERED LOGO (user rule, 12 Nov 2026): the logo is NOT drawn in the page and never goes through the printed-ink
        # finish; it is laid on the finished frames exactly as supplied (true colours, no texture), only scaled.
        from PIL import Image
        LH = 115
        with Image.open(lp) as li:
            li = li.convert("RGBA"); lw = round(LH * li.size[0] / li.size[1])
            logo_png = os.path.join(outdir, f"{slug}-logo-{lw}x{LH}.png"); li.resize((lw, LH), Image.LANCZOS).save(logo_png)
        logo_xy = (540 - lw // 2, 170)
    gpath = os.path.join(outdir, f"{slug}-build.json"); json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"{d.get('subject', slug)}: {txt['total']} over {days} days = {txt['hour']} an hour, {txt['day']} a day, {txt['week']} a week")
    subprocess.run(["node", os.path.join(HERE, "howbig_render.js"), gpath, outdir, slug], check=True)
    for v in ("youtube",):
        beats = os.path.join(outdir, f"{slug}-beats-{v}.json"); wav = os.path.join(outdir, f"{slug}-{v}.wav")
        subprocess.run([sys.executable, os.path.join(HERE, "howbig_audio.py"), beats, wav], check=True)
        silent = os.path.join(outdir, f"{slug}-{v}-silent.mp4"); final = os.path.join(outdir, f"{slug}-{v}.mp4"); tmp = final + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, final); os.remove(silent); os.remove(wav)
        if logo_png:
            tmp2 = final + ".logo.mp4"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-i", logo_png, "-filter_complex",
                            f"[0:v][1:v]overlay={logo_xy[0]}:{logo_xy[1]}:format=auto,format=yuv420p", "-c:v", "libx264", "-crf", "17",
                            "-preset", "veryfast", "-r", "30", "-c:a", "copy", "-movflags", "+faststart", tmp2], check=True)
            os.replace(tmp2, final)
        b = json.load(open(beats))
        ts = b["qa"]
        sel = "+".join(f"eq(n\\,{max(0, int(t * 30))})" for t in ts)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf", f"select='{sel}',scale=320:-1,tile={len(ts)}x1",
                        "-frames:v", "1", "-vsync", "0", os.path.join(outdir, f"{slug}-qa-{v}.jpg")], check=True)
        print(f"done {v}: {final} ({b['total']:.1f}s)")
    if logo_png:
        from PIL import Image
        lg = Image.open(logo_png).convert("RGBA")
        for nm in ("thumb-tease", "thumb-answer"):
            tp = os.path.join(outdir, f"{slug}-{nm}.png"); im = Image.open(tp).convert("RGBA"); im.alpha_composite(lg, logo_xy); im.convert("RGB").save(tp)
        os.remove(logo_png)
    import shutil; shutil.copyfile(os.path.join(outdir, f"{slug}-youtube.mp4"), os.path.join(outdir, f"{slug}-auto.mp4"))
    g["thumb_ms"] = b["thumb_ms"]; json.dump(g, open(gpath, "w"), ensure_ascii=False, indent=1)
    print(f"Buffer cover: thumbnailOffset {b['thumb_ms']} (finished grid, total hidden)")
    print("thumbnails:", os.path.join(outdir, f"{slug}-thumb-tease.png"), os.path.join(outdir, f"{slug}-thumb-answer.png"))

if __name__ == "__main__":
    main()
