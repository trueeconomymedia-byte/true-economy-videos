#!/usr/bin/env python3
"""True Economy Shorts template video: 10 s, 4K portrait (2160x3840), 30 fps, constant money flow, seamless loop.
usage: python3 video_flow.py chart.svg out.mp4 [background]   (needs chart.ribbons.json next to the svg)
background = 'chips' (procedural circuit pattern) or a path to a photo; it is filtered to the muted olive-grey look."""
import sys, re, subprocess, math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SVG, OUT = sys.argv[1], sys.argv[2]
BG = sys.argv[3] if len(sys.argv) > 3 else "chips"
LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAADQAAAAwCAAAAAB7ggYhAAADjUlEQVR42p2W308cVRTHP+fO7E+G7q5YqKyiUMAEoyFtxBpCow+Gl6o18cX4x/UP6LuJ8Uf0obFKNUTCDyMGaaLgIrAsDCw7M/f4MDt0WRhZvS+TzZ7Pved8z497Rbh8KenL8D9WOiRXQPLfGBARMZQu2IjpthJ59gsQK5I1cfiKICK2ZY17fhurGsX6xLjJjAy0nRKMGBEgtN2nr+6rArR3G3j9/Xg3e2QjRoHc0Y6fGE+0vw8e75FASnRcHSvmIv+vrbV1ezJXqpINdr5eFcDJlfLXJ8sqsvfdzw0SKE6jU3QOH60t1+oE/e8ATlDbrGMV8dw/Zu6ORWFjaTs8gwCsBMdPlx/WtsHkrAoW9euHAPhsbbbul7PLi5Ge5UkAi7/70+frewIiBUQweJVEKbv+xRPdWdxKlHFByTdVWt9/s9SMbbKRYKF51M6KwuZnL+6sHkKHe03UXXq0cmBAUAVBjT4rXBH/h5mNreAcBFpbWqm3JVG0q8jFDQ++3T2mCzrZWqvbOAIFDFEHk8nZwDyRoBMSEL4CUNFzNVgMAqBy13ypGmC7WkNV41DO1+1xAJRmP6zmyHaendpPEYBkCsOz89NZB6KOMN3ODpKudi84xdzMe7e9voK0Ojd0006yVKrB4MuvvV32Ar+J6JWQX4Dn77zklZ+byHvGdo+Zy6E+Ik43fgmGJvKDeBfiTnVPDjaWn1aGXv34Ru6Cjaspg0Sj5pHTaPz65yfXBno+KVkLQzeKvbsn1gLK47HR3qHku7+QjIgz2VMrwhiNQDGs/HakUOgxJgVRpLUWNuEEkHa+3PR5rUl7LeZ9RAtOK9ArhUjiMLulENcp50+2e7tqVIUg+ptKFL3x0XCP95MIqBTNob35wUQ+FRLBYON2BlVFTWDM5Kdz5UaKeiKxtYiqkICRGX7rtjomVXLF9TxVR0QLJyiI0czo/Py4puZJsa6XLSiosXUbH16qvntvBLF6GRT74tycKlrr2vJQaQ/AqU7dmxxXm+StC1IBKpN3pq0hVG/klRAYvP7mrVm/4UVOqnt9I1O3pr14ls5NLADT/S9c20f2HFPLXrjEY9XGJ8dttv8UgPDUYpwicSyt4sqPv18Cgdh8MTiuNDAWYxzVKLJiHIBmKfBJgdwwE6oB3FY8CbX9D0bPBqZzgbbxPBcVAdV26ylWlfQql44HlXT28JnmTk/Pmn9/UElPT7d/ANnncqYfvJHOAAAAAElFTkSuQmCC"
W, H, FPS = 2160, 3840, 30
DUR = round(float(os.environ.get("LOOP_LEN", 10)) * FPS) / FPS   # whole number of frames
FLASHES = max(1, round(DUR))                                       # about one tile flash per second
AUDIO = os.environ.get("AUDIO")                                   # optional loop wav, exactly DUR long
S = 2                                      # 1080-space -> 4K
DY = int(os.environ.get("DY", 0))          # card stays where the template has it
CS = float(os.environ.get("CS", 0))        # chart content shifted down inside the card (1080-space units = chart units)          # shift the whole card down so it is vertically centred (Facebook feed crops top/bottom)
CARD = (64, 296 + DY, 2094, 3360 + DY)     # x0, bar top, x1, bottom of white
BAR_B = 472 + DY
CH_X, CH_Y = 66, 476 + DY                       # chart canvas origin (2028 x 2882)
rng = np.random.default_rng(7)
random.seed(int(os.environ.get("SEED", 7)))

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
def from_photo(path):
    im = Image.open(path).convert("L")
    r = max(BW / im.width, BH / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    return im.crop((0, 0, BW, BH))
base = motif_chips() if BG == "chips" else from_photo(BG)
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

def bg_frame(t):
    p = (t / DUR) * 2 * math.pi            # every motion repeats exactly once per clip => seamless loop
    z = 1.0 - 0.03 * (1 - math.cos(p))
    ww, hh = W * z * 1.05, H * z * 1.05
    cx = BW / 2 + 70 * math.sin(p); cy = BH / 2 + 90 * math.sin(p + 1.0)
    im = bg_img.resize((W, H), Image.BILINEAR, box=(cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2))
    arr = np.asarray(im, dtype=np.float32) + grain_bank[int(t * FPS) % 6]
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------------- card (crisp rebuild) ----------------
card = np.full((H, W, 3), 0, np.uint8)
x0, y0, x1, y1 = CARD
paper_card = 250 + rng.normal(0, 1.1, (y1 - y0, x1 - x0, 1)) + 1.2 * np.asarray(
    Image.fromarray((rng.random((y1 // 60, x1 // 60)) * 255).astype(np.uint8)).resize((x1 - x0, y1 - y0), Image.BICUBIC), dtype=np.float32)[..., None] / 255
card_full = np.clip(paper_card, 0, 255).astype(np.uint8).repeat(3, axis=2)
card_full[: BAR_B - y0, :, :] = 0
import base64, io
logo = Image.open(io.BytesIO(base64.b64decode(LOGO_B64))).convert("L")
logo = logo.resize((logo.width * 4, logo.height * 4), Image.LANCZOS)
la = np.asarray(logo, dtype=np.float32)
la = np.clip((la - 70) / (185 - 70), 0, 1) * 232                      # firm up the edges, keep the original soft white
lx, ly = 56 * S - x0, 168 * S + DY - y0
card_full[ly:ly + la.shape[0] // 2, lx:lx + la.shape[1] // 2, :] = np.asarray(
    Image.fromarray(la.astype(np.uint8)).resize((la.shape[1] // 2, la.shape[0] // 2), Image.LANCZOS))[..., None]
chart_bg = card_full[CH_Y - y0:CH_Y - y0 + 2882, CH_X - x0:CH_X - x0 + 2028].astype(np.float32)

# ---------------- chart layers (all static except the money streaks) ----------------
import json
svg = open(SVG).read()
groups = dict(re.findall(r'<g id="(\w+)">(.*?)\n</g>', svg, re.S))
def render(ids, name):
    body = "".join(f'<g id="{i}">{groups[i]}</g>' for i in ids)
    open(f"/tmp/{name}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1014 1441" width="2028" height="2882"><g transform="translate(0,{CS})">{body}</g></svg>')
    subprocess.run(["rsvg-convert", "-w", "2028", f"/tmp/{name}.svg", "-o", f"/tmp/{name}.png"], check=True)
    return Image.open(f"/tmp/{name}.png").convert("RGBA")
paper = Image.fromarray(chart_bg.astype(np.uint8)).convert("RGBA")
paper.alpha_composite(render(["title", "kpis", "segments", "footer", "source"], "ly_static"))
chart_static = paper
L_labels = render(["labels"], "ly_labels")
TILES = json.load(open(SVG.replace(".svg", ".tiles.json")))
L_spine = render(["spine"], "ly_spine")
BASE = np.array([238, 238, 236], np.float32); TINT = {-1: np.array([246, 176, 171], np.float32), 1: np.array([172, 226, 196], np.float32)}
def chart_state(t):
    img = chart_static.copy()                                  # chart itself is static: no animation
    lay = Image.new("RGBA", (2028, 2882), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, (x, y, w, h, sg) in enumerate(TILES):               # losers flash red, winners flash green (2 soft pulses per loop)
        k = 0.5 + 0.5 * math.sin((t / DUR) * 2 * math.pi * FLASHES - math.pi / 2)
        c = BASE * (1 - 0.85 * k) + TINT[sg] * (0.85 * k)
        d.rounded_rectangle([x * 2, (y + CS) * 2, (x + w) * 2, (y + h + CS) * 2], radius=12, fill=tuple(int(v) for v in c) + (255,))
    img.alpha_composite(lay)
    img.alpha_composite(L_spine)
    img.alpha_composite(L_labels)
    return np.asarray(img)[..., :3].astype(np.float32)

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       *(["-i", AUDIO] if AUDIO else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]), "-t", f"{DUR:.4f}", "-c:v", "libx264", "-preset", "medium", "-crf", "24",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k" if AUDIO else "64k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
n = int(DUR * FPS)
for f in range(n):
    t = f / FPS
    fr = bg_frame(t)
    st = chart_state(t)
    fr[y0:y1, x0:x1] = card_full
    fr[CH_Y:CH_Y + 2882, CH_X:CH_X + 2028] = np.clip(st, 0, 255).astype(np.uint8)
    ff.stdin.write(fr.tobytes())
    if f % 30 == 0: print("frame", f, flush=True)
ff.stdin.close(); ff.wait()
print("done", OUT)
