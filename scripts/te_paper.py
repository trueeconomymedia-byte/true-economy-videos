"""True Economy card surface: static textured paper (user-approved 8 Nov 2026, "perfect" after the 9th iteration).
Fine paper tooth + soft crisp relief (high-passed, so NO blotches/patches from a distance), short soft fibres, warm tone.
Ink (every chart layer) is printed *into* the sheet: it takes the paper's light/shade and drops out a little on the high points.
The whole card is finally sharpened (unsharp mask).  EVERYTHING IS STATIC: identical every frame, so it compresses cleanly and
looks the same after each platform re-encodes (the old per-frame film grain shimmered on social media and is retired).
Tunables (env): PAPER_K (bare-paper texture strength, 0.72), PAPER_MIX (crisp-relief share, 0.55), PAPER_SHARP (1.0)."""
import os
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw

BASE = np.array([237, 234, 227], np.float32)                 # warm light greige, between the reference posts (user-approved 8 Nov 2026)
TINT = np.array([1.0, 0.98, 0.90], np.float32)
K = float(os.environ.get("PAPER_K", 0.72)); MIX = float(os.environ.get("PAPER_MIX", 0.55)); SHARP = float(os.environ.get("PAPER_SHARP", 1.0))

def _noise(r, w, h, sc):
    g = r.random((h // sc + 3, w // sc + 3)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255

def _hp(a, w, h, sig=24):                         # remove broad blotches: keep fine tooth only
    a = a.astype(np.float32)
    sm = cv2.GaussianBlur(cv2.resize(a, (w // 8, h // 8), interpolation=cv2.INTER_AREA), (0, 0), sig / 8 * 2)
    return a - cv2.resize(sm, (w, h), interpolation=cv2.INTER_CUBIC)

def _fine(w, h, seed=5, cloud_a=5, fib_a=0.9, fib_n=330):
    r = np.random.default_rng(seed); n = lambda sc: _noise(r, w, h, sc)
    Hh = 0.45 * n(3) + 0.30 * n(5) + 0.15 * n(11) + 0.10 * n(40)
    Hh = np.asarray(Image.fromarray((Hh * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9)), dtype=np.float32) / 255
    gy, gx = np.gradient(Hh); light = (-gx * 0.75 - gy * 0.65); light /= light.std()
    cloud = (0.6 * n(420) + 0.4 * n(150) - 0.5) * cloud_a
    f = Image.new("L", (w, h), 128); d = ImageDraw.Draw(f)
    for _ in range(int(w * h / fib_n)):                          # short soft fibres
        x = r.integers(0, w); y = r.integers(0, h); L = r.integers(6, 26); a = r.uniform(0, 3.1416)
        d.line([(x, y), (x + L * np.cos(a), y + L * np.sin(a))], fill=int(128 + r.choice([-1, 1]) * r.integers(8, 20)), width=1)
    fib = np.asarray(f.filter(ImageFilter.GaussianBlur(0.8)), dtype=np.float32) - 128
    return light * 7.0 + (Hh - 0.5) * 10 + cloud + fib * fib_a, Hh      # (no dark flecks: they read as splotches from a distance)

def _crisp(w, h, seed=5, amp=18):                                  # the earlier, crisper bumpy relief (luminance offsets)
    r = np.random.default_rng(seed); n = lambda sc: _noise(r, w, h, sc)
    H = 0.40 * n(7) + 0.30 * n(13) + 0.20 * n(28) + 0.10 * n(90)
    H = np.asarray(Image.fromarray((H * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.8)), dtype=np.float32) / 255
    gy, gx = np.gradient(H); light = (-gx * 0.75 - gy * 0.65); light /= light.std()
    return light * amp * 0.55 + (H - 0.5) * amp * 0.9

class Paper:
    def __init__(self, w, h, ch_x, ch_y, ch_w=1896, ch_h=2600):
        self.w, self.h, self.rx, self.ry, self.cw, self.ch = w, h, ch_x, ch_y, ch_w, ch_h
        v, self.Hh = _fine(w, h)
        v = _hp(v, w, h); self.v = v; rc = _hp(_crisp(w, h), w, h)
        self.fine = np.clip(BASE[None, None, :] + v[..., None] * TINT, 0, 255)                        # shade source for the ink
        self.bg = np.clip(BASE[None, None, :] + (K * (v + MIX * rc))[..., None] * TINT, 0, 255)       # the bare paper you see
        r2 = np.random.default_rng(9)
        s = np.clip(r2.normal(128, 40, (ch_h // 2, ch_w // 2)), 0, 255).astype(np.uint8)
        self.spk = np.asarray(Image.fromarray(s).resize((ch_w, ch_h), Image.BICUBIC), dtype=np.float32)[..., None] / 255 - 0.5
        self.tooth = np.clip((self.Hh[ch_y:ch_y + ch_h, ch_x:ch_x + ch_w] - 0.5) * 5.0, -1, 1)[..., None]
        self.shade = 0.55 + 0.45 * (self.fine[ch_y:ch_y + ch_h, ch_x:ch_x + ch_w] / BASE[None, None, :])
    def bar(self, rows):
        """the logo tab: printed soft black (17,17,17) with a hint of the paper tooth (not flat digital black)"""
        return np.clip(17 + 0.55 * self.v[:rows, :, None], 0, 255).astype(np.uint8).repeat(3, axis=2)
    def card_u8(self):
        return self.bg.astype(np.uint8)
    def inkify(self, img):
        """RGBA chart layer (chart-canvas sized) -> same layer printed into the paper"""
        a = np.asarray(img, dtype=np.float32)
        al = a[..., 3:4] / 255
        al = np.clip(al * (1 - 0.10 * np.clip(self.tooth, 0, 1) - 0.22 * np.clip(self.spk * 2, 0, 1)), 0, 1)
        rgb = np.clip(a[..., :3] * self.shade, 0, 255)
        return Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), "RGBA")
    _last = (None, None)
    def sharpen(self, cu, bar_rows):
        """unsharp mask over the whole card (not the black logo bar). Static frames are cached; blurs run on uint8 (fast)."""
        cu = np.ascontiguousarray(cu, dtype=np.uint8)
        key = hash(cu.data.tobytes())
        if self._last[0] == key: return self._last[1]
        b1 = cv2.GaussianBlur(cu, (0, 0), 1.6)
        h, w = cu.shape[:2]
        b2 = cv2.resize(cv2.GaussianBlur(cv2.resize(cu, (w // 4, h // 4), interpolation=cv2.INTER_AREA), (0, 0), 1.25), (w, h), interpolation=cv2.INTER_LINEAR)
        c = cu.astype(np.float32)
        out = c + SHARP * (c - b1) + 0.25 * (c - b2)
        out = np.clip(out, 0, 255).astype(np.uint8)
        out[:bar_rows] = cu[:bar_rows]
        self._last = (key, out)
        return out
