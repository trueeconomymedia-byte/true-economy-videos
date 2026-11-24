#!/usr/bin/env python3
"""True Economy Shorts card video, FLAT style (user-approved 22 Nov 2026, new default for Daily Post and Markets Daily non-stock cards).
Same background as the Animated Shorts: the card paper (assets_public/True-Economy_card-paper_*.png) full frame, unchanged; NO black banner/tab,
NO cut-paper edge, NO shadow; the chart canvas (948x1300 at 2x, origin 132,620) is printed onto it with the printed-ink finish (scripts/anim_shared/ink.py).
Animations (ribbon streaks, pulses, chevrons, sweep) work exactly as in video_card_legacy.py. usage: python3 video_card_flat.py chart.svg out.mp4 [ignored background arg]
env: LOOP_LEN, AUDIO, SEED as before. The previous look (banner + torn paper + topic background) is scripts/video_card_legacy.py."""
import sys, re, subprocess, math, random, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SVG, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 2160, 3840, 30
DUR = round(float(os.environ.get("LOOP_LEN", 10)) * FPS) / FPS
AUDIO = os.environ.get("AUDIO")
CH_X, CH_Y = 0, 620
rng = np.random.default_rng(7)
random.seed(int(os.environ.get("SEED", 7)))
_here = os.path.dirname(os.path.abspath(__file__))
for _d in (os.path.join(_here, "anim_shared"), "/tmp/tev/scripts/anim_shared"):
    if os.path.exists(os.path.join(_d, "ink.py")): sys.path.insert(0, _d); break
from ink import Inker
INK = Inker(W, H)
import json
svg = open(SVG).read()
groups = dict(re.findall(r'<g id="(\w+)">(.*?)\n</g>', svg, re.S))   # group closes on its own line, so flags may nest <g>
def render(ids, name):
    body = "".join(f'<g id="{i}">{groups[i]}</g>' for i in ids)
    open(f"/tmp/{name}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-66 0 1080 1300" width="2160" height="2600">{body}</svg>')
    subprocess.run(["rsvg-convert", "-w", "2160", f"/tmp/{name}.svg", "-o", f"/tmp/{name}.png"], check=True)
    return Image.open(f"/tmp/{name}.png").convert("RGBA")        # flat RGBA; the printed-ink finish is applied to the whole frame (anim_shared/ink.py)
TOPG = [g for g in groups if g == "labels" or g.startswith("top")]       # drawn above the animation
STATICG = [g for g in groups if g not in TOPG]                           # title, body, footer, source ... never move
chart_static = Image.new("RGBA", (2160, 2600), (0, 0, 0, 0)); chart_static.alpha_composite(render(STATICG, "ly_static"))
L_top = render(TOPG, "ly_top") if TOPG else None
AJ = SVG.replace(".svg", ".anim.json")
anim = json.load(open(AJ)) if os.path.exists(AJ) else {}
if "flow" not in anim and os.path.exists(SVG.replace(".svg", ".ribbons.json")):
    anim["flow"] = json.load(open(SVG.replace(".svg", ".ribbons.json")))
if not anim and os.environ.get("SWEEP") == "1": anim["sweep"] = {"rgb": [54, 112, 208], "alpha": 0.10}     # default sweep REMOVED (user, 7 Nov): static cards get no animation unless SWEEP=1
anim["flow"] = [[f[0] + 66, f[1], f[2], f[3] + 66] + list(f[4:]) for f in anim.get("flow", [])]
print("animation layers:", list(anim), flush=True)

PCOL = {"#3670D0": (54, 112, 208), "#B3C9ED": (54, 112, 208),
        "#D94437": (217, 68, 55), "#FFF205": (217, 205, 0), "#EDE22E": (208, 199, 30), "#FACB3A": (232, 178, 36)}
parts = []
for (xs, ys0, ys1, xd, yd0, yd1, col) in anim.get("flow", []):
    hgt = ((ys1 - ys0) + (yd1 - yd0)) / 2; ln = abs(xd - xs) + abs((yd0 - ys0)) * 0.3
    n = int(max(3, round(1.35 * hgt * ln / 27 ** 2)))
    cyc = int(min(8, max(1, round(62 * DUR / max(ln, 1)))))
    for i in range(n):
        parts.append((xs, ys0, ys1, xd, yd0, yd1, (i + rng.random() * 0.8) / n, rng.random(), cyc, PCOL.get(col, (54, 112, 208))))
BEHIND = bool(anim.get("red_behind"))     # red ribbon sits BEHIND the other ribbons: its flow bits are hidden wherever a non-red ribbon covers it (user 13 Nov)
FRONT_MASK = None
if BEHIND:
    FRONT_MASK = Image.new("L", (2160, 2600), 0); _md = ImageDraw.Draw(FRONT_MASK)
    for (xs, ys0, ys1, xd, yd0, yd1, col) in anim.get("flow", []):
        if PCOL.get(col) == (217, 68, 55): continue
        xm = (xs + xd) / 2; qs = [i / 80 for i in range(81)]
        top = [((xs*(1-q)**3 + 3*xm*(1-q)**2*q + 3*xm*(1-q)*q*q + xd*q**3) * 2, (ys0*((1-q)**3 + 3*(1-q)**2*q) + yd0*(3*(1-q)*q*q + q**3)) * 2) for q in qs]
        bot = [((xs*(1-q)**3 + 3*xm*(1-q)**2*q + 3*xm*(1-q)*q*q + xd*q**3) * 2, (ys1*((1-q)**3 + 3*(1-q)**2*q) + yd1*(3*(1-q)*q*q + q**3)) * 2) for q in qs]
        _md.polygon(top + bot[::-1], fill=255)
def bez(p0, p1, p2, p3, t):
    u = 1 - t; return u*u*u*p0 + 3*u*u*t*p1 + 3*u*t*t*p2 + t*t*t*p3
def chart_state(t):
    img = chart_static.copy()
    lay = Image.new("RGBA", (2160, 2600), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lay_red = Image.new("RGBA", (2160, 2600), (0, 0, 0, 0)) if BEHIND else None; d_red = ImageDraw.Draw(lay_red) if BEHIND else None
    for (xs, ys0, ys1, xd, yd0, yd1, ph, u, cyc, rgb) in parts:                  # money streaks along ribbons
        tt = (ph + cyc * t / DUR) % 1.0
        xm = (xs + xd) / 2
        def pos(q):
            x = bez(xs, xm, xm, xd, q); yt = bez(ys0, ys0, yd0, yd0, q); yb = bez(ys1, ys1, yd1, yd1, q)
            return x * 2, (yt * (1 - u) + yb * u) * 2
        q0 = tt; q1 = max(0.0, tt - 26 / max(abs(xd - xs) * 2, 1))
        edge = min(1.0, tt / 0.1, (1 - tt) / 0.1)
        al = int(255 * 0.5 * max(edge, 0))
        if al > 2: (d_red if (BEHIND and tuple(rgb) == (217, 68, 55)) else d).line([pos(q1), pos(q0)], fill=tuple(rgb) + (al,), width=8)
    for (dx_, dy_, dr_, drgb, dph, damp) in anim.get("dots", []):                   # twinkling dots: a soft white ripple travels across the dot grid, one pass per loop (periodic, so first frame = last frame)
        kk = 0.5 - 0.5 * math.cos(2 * math.pi * 8 * ((t / DUR + dph) % 1.0)); kk = kk ** 1.2
        if kk > 0.01: d.ellipse([(dx_ - dr_) * 2, (dy_ - dr_) * 2, (dx_ + dr_) * 2, (dy_ + dr_) * 2], fill=tuple(drgb) + (int(255 * damp * kk),))
    for (px, py, pw, ph_, rgb, cyc, rad) in anim.get("pulse", []):                # flashing rectangles (tile flash)
        k = 0.5 + 0.5 * math.sin((t / DUR) * 2 * math.pi * (cyc or max(1, round(DUR))) - math.pi / 2)
        d.rounded_rectangle([px * 2, py * 2, (px + pw) * 2, (py + ph_) * 2], radius=rad * 2, fill=tuple(rgb) + (int(255 * 0.45 * k),))
    for (ax, ay, aw, ah, argb, an, aalpha, asize, *_shp) in anim.get("arrows", []):
        ashape = _shp[0] if _shp else "arrow"; adir = _shp[1] if len(_shp) > 1 else "up"; avoid = _shp[2] if len(_shp) > 2 else []; fixcyc = _shp[3] if len(_shp) > 3 else None      # direction: "up" (growth) or "down" (fall); never sideways        # constant upward flow of solid rounded arrows inside a rectangle (focal gain block)
        rr = random.Random(int(ax * 7 + ay * 13 + aw))                             # fixed positions/phases/speeds/sizes -> identical every loop
        xs_ = [(i + rr.random()) / an for i in range(an)]; rr.shuffle(xs_)          # random look, but spread evenly across the width
        for i in range(an):
            cx = ax + aw * (0.06 + 0.88 * xs_[i]); ph = rr.random(); cyc = rr.choice([1, 1, 2]); cyc = fixcyc or cyc; sz = asize * (0.75 + 0.5 * rr.random())
            q = (ph + cyc * t / DUR) % 1.0                                           # 0 = bottom edge, 1 = top edge; integer cycles per loop = seamless
            cy = ay + ah * ((1 - q) if adir == "up" else q); edge = min(1.0, q / 0.16, (1 - q) / 0.16)
            al = int(255 * aalpha * max(edge, 0))
            for (rx, ry, rw_, rh_) in avoid:                                         # fade chevrons near text boxes so the text stays readable
                dd = math.hypot(max(rx - cx, 0, cx - rx - rw_), max(ry - cy, 0, cy - ry - rh_))
                al = int(al * (0.1 + 0.9 * min(1.0, dd / 30.0)))
            if al > 3:
                    if ashape == "chevron":                                         # thin open chevron "^" (first style)
                        a_, b_ = sz * 0.9, sz * 0.55
                        cpts = [(cx - a_, cy + b_), (cx, cy - b_), (cx + a_, cy + b_)] if adir == "up" else [(cx - a_, cy - b_), (cx, cy + b_), (cx + a_, cy - b_)]
                        d.line([(x_ * 2, y_ * 2) for x_, y_ in cpts], fill=tuple(argb) + (al,), width=max(2, int(sz * 0.42 * 2)), joint="curve")
                    else:                                                           # solid rounded up-arrow sprite
                        u = sz; H_ = u * 1.08
                        spr = (ARROW_MASK if adir == "up" else ARROW_MASK.transpose(Image.FLIP_TOP_BOTTOM)).resize((max(2, int(u * 2)), max(2, int(H_ * 2))), Image.LANCZOS).point(lambda v: v * al // 255)
                        lay.paste(tuple(argb) + (255,), (int((cx - u / 2) * 2), int((cy - H_ / 2) * 2)), spr)
    if "sweep" in anim:                                                              # soft diagonal light band, offscreen at t=0 and t=DUR
        sw = anim["sweep"]; u = t / DUR; cx = -300 + (2160 + 600) * u
        band = Image.new("RGBA", (2160, 2600), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
        a = int(255 * sw.get("alpha", 0.1))
        bd.polygon([(cx - 120, 0), (cx + 120, 0), (cx + 120 - 700, 2600), (cx - 120 - 700, 2600)], fill=tuple(sw.get("rgb", [54, 112, 208])) + (a,))
        lay = Image.alpha_composite(lay, band.filter(ImageFilter.GaussianBlur(40)))
    if BEHIND:                                                                       # red bits behind the blue ribbons: cut them out under the blue ribbons, then blue bits go on top
        ra = lay_red.getchannel("A"); ra = Image.composite(Image.new("L", ra.size, 0), ra, FRONT_MASK.filter(ImageFilter.GaussianBlur(0.8)))
        lay_red.putalpha(ra); lay = Image.alpha_composite(lay_red, lay)
    lay = lay.filter(ImageFilter.GaussianBlur(0.9)) if parts else lay
    img.alpha_composite(lay)
    if L_top is not None: img.alpha_composite(L_top)
    return np.asarray(img)   # RGBA uint8


def _make_arrow_mask():
    """rounded up-arrow mask (like the reference): polygon -> blur -> threshold -> soft edge"""
    S = 256; im = Image.new("L", (S, int(S * 1.08)), 0); dd = ImageDraw.Draw(im)
    P = [(0.50, 0.00), (1.00, 0.50), (0.93, 0.57), (0.64, 0.45), (0.64, 1.08), (0.36, 1.08), (0.36, 0.45), (0.07, 0.57), (0.00, 0.50)]
    pad = 14; dd.polygon([(pad + x * (S - 2 * pad), pad + y * (S - 2 * pad)) for x, y in P], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(9)).point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.GaussianBlur(1.6))
    return im
ARROW_MASK = _make_arrow_mask()


# ---------------- encode: transparent RGBA chart placed on the full-frame paper, printed-ink finish ----------------
STATIC_ONLY = not parts and not any(k in anim for k in ("dots", "pulse", "arrows", "sweep"))
def frame(t):
    full = np.zeros((H, W, 4), np.uint8); full[CH_Y:CH_Y + 2600, CH_X:CH_X + 2160] = chart_state(t)
    return INK.compose(full)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       *(["-i", AUDIO] if AUDIO else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]), "-t", f"{DUR:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k" if AUDIO else "64k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
n = int(DUR * FPS); cached = None
for f in range(n):
    if STATIC_ONLY and cached is not None: b = cached
    else:
        b = np.ascontiguousarray(frame(f / FPS)).tobytes()
        if STATIC_ONLY: cached = b
    ff.stdin.write(b)
    if f % 30 == 0: print("frame", f, flush=True)
ff.stdin.close(); ff.wait()
print("done", OUT)
