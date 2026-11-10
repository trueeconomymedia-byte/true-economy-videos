"""True Economy PRINTED-INK finish for Animated Shorts (full frame). Mirrors scripts/te_paper.py inkify()/sharpen():
the supplied card-paper PNG is the background AND the relief map; every ink pixel (text, bars, shapes) is multiplied by
the paper's own light/shade, drops out a little on the tooth's high points and on fine specks, then the ink gets
a light unsharp mask (radius 1.6 px at 2160 wide, scaled to the output; strength 1.0, plus a 0.25 broad pass). The bare paper
is left exactly as supplied, so the frame's average tone matches the paper. Static: identical texture every frame.
    from ink import Inker; ink = Inker(1080, 1920); frame_rgb = ink.compose(rgba_uint8)"""
import os, numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BASE = np.array([251, 248, 241], np.float32)

def paper_png(w, h):
    for name in ("True-Economy_card-paper_2160x3840.png", "True-Economy_card-paper_1080x1920.png"):
        p = os.path.join(REPO, "assets_public", name)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            if im.size != (w, h): im = im.resize((w, h), Image.LANCZOS)     # scaling only, never recoloured or blurred
            return np.asarray(im, np.float32)
    raise FileNotFoundError("assets_public/True-Economy_card-paper_*.png not found in the repo")

class Inker:
    def __init__(s, w=1080, h=1920, sharp=1.0):
        s.w, s.h, s.sharp = w, h, sharp
        s.paper = paper_png(w, h)
        L = s.paper.mean(2)
        rel = L - cv2.GaussianBlur(L, (0, 0), 6)                         # the tooth (fine relief) of the supplied sheet
        s.tooth = np.clip(rel / (rel.std() * 2 + 1e-6), -1, 1)[..., None]
        s.shade = 0.55 + 0.45 * (s.paper / BASE[None, None, :])          # the paper's own light/shade, applied to the ink
        r = np.random.default_rng(9)
        sp = np.clip(r.normal(128, 40, (h // 2, w // 2)), 0, 255).astype(np.uint8)
        s.spk = np.asarray(Image.fromarray(sp).resize((w, h), Image.BICUBIC), np.float32)[..., None] / 255 - 0.5
        s.drop = (1 - 0.10 * np.clip(s.tooth, 0, 1) - 0.22 * np.clip(s.spk * 2, 0, 1))
    def compose(s, rgba):
        a = rgba.astype(np.float32)
        al = np.clip(a[..., 3:4] / 255 * s.drop, 0, 1)
        rgb = np.clip(a[..., :3] * s.shade, 0, 255)
        out = s.paper * (1 - al) + rgb * al
        cu = np.clip(out, 0, 255).astype(np.uint8)
        r = 1.6 * s.w / 2160                       # the cards are sharpened at 2160 px wide: same look at any output size
        b1 = cv2.GaussianBlur(cu, (0, 0), r)
        b2 = cv2.resize(cv2.GaussianBlur(cv2.resize(cu, (s.w // 4, s.h // 4), interpolation=cv2.INTER_AREA), (0, 0), 1.25 * s.w / 2160), (s.w, s.h), interpolation=cv2.INTER_LINEAR)
        c = cu.astype(np.float32)
        sh = c + s.sharp * (c - b1) + 0.25 * (c - b2)
        m = cv2.GaussianBlur(np.ascontiguousarray(al[..., 0]), (0, 0), 2.0)[..., None]   # sharpen the ink; bare paper stays exactly as supplied
        m = np.clip(m * 3, 0, 1)
        return np.clip(sh * m + s.paper * (1 - m), 0, 255).astype(np.uint8)
