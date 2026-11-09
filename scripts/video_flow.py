#!/usr/bin/env python3
"""True Economy Shorts template video: 10 s, 4K portrait (2160x3840), 30 fps.
usage: python3 video_template.py chart.svg out.mp4 [background]   background = 'chips' (procedural) or path to a photo/frame
The card (black bar + logo + white paper) is rebuilt crisp from the user's template; only the filtered background changes per topic."""
import sys, re, subprocess, math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SVG, OUT = sys.argv[1], sys.argv[2]
BG = sys.argv[3] if len(sys.argv) > 3 else "chips"
LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAADQAAAAwCAAAAAB7ggYhAAADjUlEQVR42p2W308cVRTHP+fO7E+G7q5YqKyiUMAEoyFtxBpCow+Gl6o18cX4x/UP6LuJ8Uf0obFKNUTCDyMGaaLgIrAsDCw7M/f4MDt0WRhZvS+TzZ7Pved8z497Rbh8KenL8D9WOiRXQPLfGBARMZQu2IjpthJ59gsQK5I1cfiKICK2ZY17fhurGsX6xLjJjAy0nRKMGBEgtN2nr+6rArR3G3j9/Xg3e2QjRoHc0Y6fGE+0vw8e75FASnRcHSvmIv+vrbV1ezJXqpINdr5eFcDJlfLXJ8sqsvfdzw0SKE6jU3QOH60t1+oE/e8ATlDbrGMV8dw/Zu6ORWFjaTs8gwCsBMdPlx/WtsHkrAoW9euHAPhsbbbul7PLi5Ge5UkAi7/70+frewIiBUQweJVEKbv+xRPdWdxKlHFByTdVWt9/s9SMbbKRYKF51M6KwuZnL+6sHkKHe03UXXq0cmBAUAVBjT4rXBH/h5mNreAcBFpbWqm3JVG0q8jFDQ++3T2mCzrZWqvbOAIFDFEHk8nZwDyRoBMSEL4CUNFzNVgMAqBy13ypGmC7WkNV41DO1+1xAJRmP6zmyHaendpPEYBkCsOz89NZB6KOMN3ODpKudi84xdzMe7e9voK0Ojd0006yVKrB4MuvvV32Ar+J6JWQX4Dn77zklZ+byHvGdo+Zy6E+Ik43fgmGJvKDeBfiTnVPDjaWn1aGXv34Ru6Cjaspg0Sj5pHTaPz65yfXBno+KVkLQzeKvbsn1gLK47HR3qHku7+QjIgz2VMrwhiNQDGs/HakUOgxJgVRpLUWNuEEkHa+3PR5rUl7LeZ9RAtOK9ArhUjiMLulENcp50+2e7tqVIUg+ptKFL3x0XCP95MIqBTNob35wUQ+FRLBYON2BlVFTWDM5Kdz5UaKeiKxtYiqkICRGX7rtjomVXLF9TxVR0QLJyiI0czo/Py4puZJsa6XLSiosXUbH16qvntvBLF6GRT74tycKlrr2vJQaQ/AqU7dmxxXm+StC1IBKpN3pq0hVG/klRAYvP7mrVm/4UVOqnt9I1O3pr14ls5NLADT/S9c20f2HFPLXrjEY9XGJ8dttv8UgPDUYpwicSyt4sqPv18Cgdh8MTiuNDAWYxzVKLJiHIBmKfBJgdwwE6oB3FY8CbX9D0bPBqZzgbbxPBcVAdV26ylWlfQql44HlXT28JnmTk/Pmn9/UElPT7d/ANnncqYfvJHOAAAAAElFTkSuQmCC"
import base64, io
W, H, FPS = 2160, 3840, 30
DUR = round(float(os.environ.get("LOOP_LEN", 10)) * FPS) / FPS
AUDIO = os.environ.get("AUDIO")
S = 2                                      # 1080-space -> 4K
CARD = (0, 296, 2160, 3360)               # x0, bar top, x1, bottom of white
BAR_B = 474
CH_X, CH_Y = 132, 620                       # chart canvas origin (1896 x 2600)
rng = np.random.default_rng(7)
random.seed(7)

# ---------------- background (filtered topic image) ----------------
BW, BH = 2700, 4600
def motif_chips():
    im = Image.new("L", (BW, BH), 90)
    d = ImageDraw.Draw(im)
    # circuit traces on a 70px grid with 45-degree bends
    for _ in range(170):
        x, y = random.randrange(0, BW, 70), random.randrange(0, BH, 70)
        pts = [(x, y)]
        for _ in range(random.randint(3, 7)):
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)])
            n = random.randint(2, 9) * 70
            x, y = x + dx * n, y + dy * n
            pts.append((x, y))
        wdt = random.choice([8, 10, 14])
        d.line(pts, fill=random.choice([150, 165, 180, 60]), width=wdt, joint="curve")
        d.ellipse((pts[0][0] - wdt * 1.6, pts[0][1] - wdt * 1.6, pts[0][0] + wdt * 1.6, pts[0][1] + wdt * 1.6), fill=170)
        d.ellipse((pts[-1][0] - wdt * 1.6, pts[-1][1] - wdt * 1.6, pts[-1][0] + wdt * 1.6, pts[-1][1] + wdt * 1.6), outline=180, width=6)
    # chip packages with pin rows
    for _ in range(9):
        cx, cy = random.randrange(100, BW - 700), random.randrange(100, BH - 700)
        s = random.choice([420, 560, 700])
        d.rectangle((cx, cy, cx + s, cy + s), fill=60, outline=190, width=10)
        d.rectangle((cx + s * .2, cy + s * .2, cx + s * .8, cy + s * .8), fill=110, outline=200, width=6)
        for i in range(12):
            t = s * (i + .5) / 12
            for (a, b, c, e) in [(cx + t, cy - 36, cx + t, cy), (cx + t, cy + s, cx + t, cy + s + 36),
                                 (cx - 36, cy + t, cx, cy + t), (cx + s, cy + t, cx + s + 36, cy + t)]:
                d.line((a, b, c, e), fill=190, width=10)
    return im

def _noise(scale, seed):
    r = np.random.default_rng(seed)
    g = r.random((BH // scale + 2, BW // scale + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((BW, BH), Image.BICUBIC), dtype=np.float32) / 255
def motif_contours():            # topographic map lines
    s = int(os.environ.get("SEED", 7)); f = 0.6 * _noise(900, s) + 0.3 * _noise(350, s + 1) + 0.1 * _noise(120, s + 2)
    ph = (f * 16) % 1.0; line = np.abs(ph - 0.5) > 0.455
    a = np.full((BH, BW), 90, np.uint8); a[line] = 175
    return Image.fromarray(a)
def motif_graph():               # graph paper + rising/falling data lines
    im = Image.new("L", (BW, BH), 90); d = ImageDraw.Draw(im)
    for x in range(0, BW, 90): d.line((x, 0, x, BH), fill=120, width=3 if x % 450 else 6)
    for y in range(0, BH, 90): d.line((0, y, BW, y), fill=120, width=3 if y % 450 else 6)
    for _ in range(7):
        y = random.randrange(600, BH - 600); pts = []
        for x in range(-100, BW + 200, 90):
            y += random.randint(-150, 140); y = min(max(y, 200), BH - 200); pts.append((x, y))
        d.line(pts, fill=random.choice([170, 190, 60]), width=random.choice([8, 12]), joint="curve")
        for p in pts[::3]: d.rectangle((p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12), fill=200)
    return im
def motif_skyline():             # layered city blocks
    im = Image.new("L", (BW, BH), 85); d = ImageDraw.Draw(im)
    for layer, (base_y, fill, hmax) in enumerate([(BH * 0.62, 110, 1500), (BH * 0.74, 135, 1700), (BH * 0.88, 165, 1900)]):
        x = -50
        while x < BW:
            w = random.randint(140, 320); h = random.randint(300, hmax)
            d.rectangle((x, base_y - h, x + w, BH), fill=fill, outline=fill + 25, width=4)
            for wy in range(int(base_y - h + 40), int(base_y), 80):
                for wx in range(x + 24, x + w - 24, 56):
                    if random.random() < 0.45: d.rectangle((wx, wy, wx + 20, wy + 34), fill=fill + 55)
            x += w + random.randint(0, 40)
    return im
def motif_halftone():            # halftone dot field with a soft diagonal swell
    im = Image.new("L", (BW, BH), 90); d = ImageDraw.Draw(im); step = 54
    f = _noise(1200, int(os.environ.get("SEED", 7)) + 5)
    for yy in range(0, BH, step):
        for xx in range(0, BW, step):
            r = 4 + 20 * float(f[min(yy, BH - 1), min(xx, BW - 1)]) ** 1.5
            d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=175)
    return im
def motif_candles():             # candlestick chart
    im = Image.new("L", (BW, BH), 90); d = ImageDraw.Draw(im); y = BH * 0.5; step = 76
    for x in range(40, BW, step):
        o = y; c = y + random.randint(-170, 170); hi = min(o, c) - random.randint(20, 150); lo = max(o, c) + random.randint(20, 150)
        up = c < o; col = 185 if up else 60
        d.line((x, hi, x, lo), fill=col, width=7); d.rectangle((x - 22, min(o, c), x + 22, max(o, c) + 4), fill=col, outline=190, width=3)
        y = min(max(c, 500), BH - 500)
    return im
def motif_globe():               # latitude / longitude lines
    im = Image.new("L", (BW, BH), 90); d = ImageDraw.Draw(im); cx, cy, R = BW * 0.55, BH * 0.45, 1500
    for k in range(-6, 7):
        d.ellipse((cx - R * abs(math.cos(k * math.pi / 14)), cy - R, cx + R * abs(math.cos(k * math.pi / 14)), cy + R), outline=170, width=7)
    for k in range(-5, 6):
        yy = cy + R * math.sin(k * math.pi / 12); rx = R * math.cos(k * math.pi / 12)
        d.arc((cx - rx, yy - 0.18 * rx, cx + rx, yy + 0.18 * rx), 0, 360, fill=170, width=7)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=190, width=10)
    return im
MOTIFS = {"chips": motif_chips, "contours": motif_contours, "graph": motif_graph, "skyline": motif_skyline,
          "halftone": motif_halftone, "candles": motif_candles, "globe": motif_globe}
def from_photo(path):
    im = Image.open(path).convert("L")
    r = max(BW / im.width, BH / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    return im.crop((0, 0, BW, BH))
base = MOTIFS[BG]() if BG in MOTIFS else from_photo(BG)
base = base.filter(ImageFilter.GaussianBlur(7))                      # out-of-focus depth
a = np.asarray(base, dtype=np.float32) / 255
# paper-like cloud + crease texture (same muted olive-grey look as the template)
def cloud(w, h, scale, seed):
    r = np.random.default_rng(seed)
    g = r.random((h // scale + 2, w // scale + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255
paper = 0.5 * cloud(BW, BH, 400, 1) + 0.3 * cloud(BW, BH, 120, 2) + 0.2 * cloud(BW, BH, 30, 3)
lum = 0.45 + (a - 0.35) * 0.30 + (paper - 0.5) * 0.30
lum = np.clip(lum, 0, 1)
tone = np.stack([lum * 255 * 0.70 + 55, lum * 255 * 0.68 + 52, lum * 255 * 0.62 + 46], axis=2)  # olive-grey like the template
yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
vig = 1 - 0.22 * (((xx - BW / 2) / (BW / 2)) ** 2 + ((yy - BH / 2) / (BH / 2)) ** 2)
bg_img = Image.fromarray(np.clip(tone * vig[..., None], 0, 255).astype(np.uint8))
del a, paper, lum, tone, yy, xx, vig
grain_bank = [rng.normal(0, 6.5, (H, W, 1)).astype(np.float32) for _ in range(6)]

# ---------------- card shadow: lifts the white card off the background (static, baked into the background; STYLE: soft shadow above/below the card + thin contact shadow) ----------------
def _shadow():
    from PIL import ImageDraw
    sx0, sy0, sx1, sy1 = CARD
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([0, sy0 + 28, W, sy1 + 52], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(52)), dtype=np.float32) / 255
    m2 = Image.new("L", (W, H), 0); ImageDraw.Draw(m2).rectangle([0, sy0 + 6, W, sy1 + 10], fill=255)
    m2 = np.asarray(m2.filter(ImageFilter.GaussianBlur(10)), dtype=np.float32) / 255
    return ((1 - 0.62 * m) * (1 - 0.45 * m2))[..., None].astype(np.float32)
import sys as _s0, os as _o0; _s0.path.insert(0, _o0.path.dirname(_o0.path.abspath(__file__)))
from te_paper import Paper
SHADOW = _shadow() * Paper.lit_shadow(W, H, CARD)   # + light-from-above shadow (paper look)

def bg_frame(t):
    p = (t / DUR) * 2 * math.pi            # every motion repeats exactly once per clip => seamless loop
    z = 1.0 - 0.03 * (1 - math.cos(p))
    ww, hh = W * z * 1.05, H * z * 1.05
    cx = BW / 2 + 70 * math.sin(p); cy = BH / 2 + 90 * math.sin(p + 1.0)
    im = bg_img.resize((W, H), Image.BILINEAR, box=(cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2))
    arr = np.asarray(im, dtype=np.float32) * SHADOW + grain_bank[int(t * FPS) % 6]
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------------- card (crisp rebuild) ----------------
card = np.full((H, W, 3), 0, np.uint8)
x0, y0, x1, y1 = CARD
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))   # also works under python3 -I
from te_paper import Paper                                      # static textured paper surface (user-approved 8 Nov 2026)
PAP = Paper(x1 - x0, y1 - y0, CH_X - x0, CH_Y - y0)
card_full = PAP.card_u8()
_paper_src = card_full.copy()
card_full[: BAR_B - y0, :, :] = PAP.bar(BAR_B - y0)          # textured soft-black tab (matches reference black)
PAP.stamp_logo(card_full, _paper_src, BAR_B - y0)             # new E logo cut from the card's own paper
PAP.lit(card_full, BAR_B - y0)                                # light from above: gradient, bottom lip, top highlight
chart_bg = card_full[CH_Y - y0:CH_Y - y0 + 2600, CH_X - x0:CH_X - x0 + 1896].astype(np.float32)

# ---------------- chart layers (all static except the money streaks) ----------------
import json
svg = open(SVG).read()
groups = dict(re.findall(r'<g id="(\w+)">(.*?)</g>', svg, re.S))
def render(ids, name):
    body = "".join(f'<g id="{i}">{groups[i]}</g>' for i in ids)
    open(f"/tmp/{name}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 948 1300" width="1896" height="2600">{body}</svg>')
    subprocess.run(["rsvg-convert", "-w", "1896", f"/tmp/{name}.svg", "-o", f"/tmp/{name}.png"], check=True)
    return PAP.inkify(Image.open(f"/tmp/{name}.png").convert("RGBA"))        # ink printed into the paper
paper = Image.fromarray(chart_bg.astype(np.uint8)).convert("RGBA")
paper.alpha_composite(render(["title", "kpis", "segments", "spine", "footer", "source"], "ly_static"))
chart_static = paper
L_labels = render(["labels"], "ly_labels")
ribbons = json.load(open(SVG.replace(".svg", ".ribbons.json")))
GOLD = "#D9CD00"
PCOL = {"#3670D0": (54, 112, 208), "#B3CDEC": (54, 112, 208),
        "#D94437": (217, 68, 55), "#FFF205": (217, 205, 0), "#EDE22E": (208, 199, 30), "#FACB3A": (232, 178, 36)}
parts = []   # one record per money streak: ribbon geometry, lane, phase, cycles, colour
for (xs, ys0, ys1, xd, yd0, yd1, col) in ribbons:
    hgt = ((ys1 - ys0) + (yd1 - yd0)) / 2; ln = abs(xd - xs) + abs((yd0 - ys0)) * 0.3
    n = int(max(3, round(hgt * ln / 27 ** 2)))
    cyc = int(min(8, max(1, round(62 * DUR / max(ln, 1)))))
    for i in range(n):
        parts.append((xs, ys0, ys1, xd, yd0, yd1, (i + rng.random() * 0.8) / n, rng.random(), cyc, PCOL.get(col, (54, 112, 208))))
def bez(p0, p1, p2, p3, t):
    u = 1 - t; return u*u*u*p0 + 3*u*u*t*p1 + 3*u*t*t*p2 + t*t*t*p3
XMIN = min(r[0] for r in ribbons); XMAX = max(r[3] for r in ribbons)
def ss(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def front(t):   # chart x (948 units) the money has reached; starts moving at frame 1, sweeps source -> terminals, then keeps flowing
    u = min(max(t / 4.6, 0), 1)
    return XMIN - 40 + (XMAX - XMIN + 80) * (1 - (1 - u) ** 2)
def env(t): return 1.0   # constant flow, no fades: the clip is a seamless loop
def chart_state(t):
    e = env(t)
    img = chart_static.copy()
    if e > 0:
        lay = Image.new("RGBA", (1896 * 1, 2600 * 1), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for (xs, ys0, ys1, xd, yd0, yd1, ph, u, cyc, rgb) in parts:
            tt = (ph + cyc * t / DUR) % 1.0
            xm = (xs + xd) / 2
            def pos(q):
                x = bez(xs, xm, xm, xd, q); yt = bez(ys0, ys0, yd0, yd0, q); yb = bez(ys1, ys1, yd1, yd1, q)
                return x * 2, (yt * (1 - u) + yb * u) * 2
            q0 = tt; q1 = max(0.0, tt - 26 / max(abs(xd - xs) * 2, 1))
            edge = min(1.0, tt / 0.1, (1 - tt) / 0.1)
            px_ = bez(xs, xm, xm, xd, tt); gate = 1.0
            al = int(255 * 0.5 * e * max(edge, 0) * gate)
            if al <= 2: continue
            d.line([pos(q1), pos(q0)], fill=rgb + (al,), width=8)
        lay = lay.filter(ImageFilter.GaussianBlur(0.9))
        img.alpha_composite(lay)
    img.alpha_composite(L_labels)
    return np.asarray(img)[..., :3].astype(np.float32)

if os.environ.get("TESTT"):
    for tt in [float(x) for x in os.environ["TESTT"].split(",")]:
        fr = bg_frame(tt); st = chart_state(tt)
        fr[y0:y1, x0:x1] = card_full
        fr[CH_Y:CH_Y + 2600, CH_X:CH_X + 1896] = np.clip(st, 0, 255).astype(np.uint8)
        fr[y0:y1, x0:x1] = PAP.sharpen(fr[y0:y1, x0:x1], BAR_B - y0)      # whole-card sharpen (static paper, no per-frame grain)
        Image.fromarray(fr).save(f"/tmp/test_{tt}.png")
    sys.exit()
# ---------------- encode ----------------
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       *(["-i", AUDIO] if AUDIO else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]), "-t", f"{DUR:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k" if AUDIO else "64k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
n = int(DUR * FPS)
for f in range(n):
    t = f / FPS
    fr = bg_frame(t)
    st = chart_state(t)
    fr[y0:y1, x0:x1] = card_full
    fr[CH_Y:CH_Y + 2600, CH_X:CH_X + 1896] = np.clip(st, 0, 255).astype(np.uint8)
    fr[y0:y1, x0:x1] = PAP.sharpen(fr[y0:y1, x0:x1], BAR_B - y0)      # whole-card sharpen (static paper, no per-frame grain)
    ff.stdin.write(fr.tobytes())
    if f % 30 == 0: print("frame", f, flush=True)
ff.stdin.close(); ff.wait()
print("done", OUT)
