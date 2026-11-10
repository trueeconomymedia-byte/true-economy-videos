"""True Economy Shorts FRAME (user-approved 10 Nov 2026, the user's own pick (version A)): the full-bleed paper layout around the card.
Applies to every scheduled card Short EXCEPT Stock Market Today (that series keeps its own old plain-white style: make_mkts.py / video_mkts.py never import this).

What it draws (all STATIC, identical every frame):
  * darker, slightly faded back paper above the banner and below the card (same paper family, neutral greige, no colour tint)
  * the black banner PRINTED on the paper: ink lets the paper tooth and tiny specks show through, slightly uneven top and bottom edges,
    ink pooling just inside the edge, the E knocked out of the ink (shows paper), E sits 5 px right of the old logo position
  * the banner's top edge is the top edge of the sheet: a very small bright torn-paper rim, with a tight soft shadow falling on the back paper above it
  * the card's bottom edge: a straight sheet edge with a fine, smooth deckle (NOT fibery), a hairline light fringe and a soft shadow on the back paper below
  * card + banner positions never move (banner top y=296, bottom 474, card bottom 3360)
usage (in video_card.py / video_flow.py / video_card_seq.py):
    import te_frame as TF
    fr = TF.FRAME.copy()            # instead of the moving background
    ... draw the card into fr[y0:y1, x0:x1] as before ...
    TF.finish(fr)                   # re-draws the banner rows and the bottom edge on top of the card
Tunables are the constants in build(); do not change without the user's approval."""
import os
import numpy as np, cv2
from PIL import Image
import te_paper as TP

W, H = 2160, 3840
Y0, BAR_B, Y1 = 296, 474, 3360
E_CX, E_CY, E_H = 184, 385, 70          # E centre (old position cx=179, +5 px right per user), height 70 px

def _jit(rng, s, amp):
    n = cv2.GaussianBlur(rng.standard_normal((1, W)).astype(np.float32), (0, 0), s)
    return n / n.std() * amp

def _e_alpha():
    ad = next(d for d in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), "/tmp/tev/scripts/assets", "/tmp/assets") if os.path.exists(os.path.join(d, "te_E.png")))
    m = Image.open(os.path.join(ad, "te_E.png")).convert("L")
    w = int(round(E_H * m.width / m.height))
    m = m.resize((w * 4, E_H * 4), Image.LANCZOS).resize((w, E_H), Image.LANCZOS)
    a = (np.asarray(m, np.float32) / 255)
    ex, ey = E_CX - w // 2, E_CY - E_H // 2
    full = np.zeros((H, W, 1), np.float32); full[ey:ey + E_H, ex:ex + w, 0] = a
    return full

def build():
    # ---- paper texture for the whole frame (same recipe as the card paper, +sharpened) ----
    v, _ = TP._fine(W, H); v = TP._hp(v, W, H)
    rc = TP._hp(TP._crisp(W, H), W, H)
    pp = np.clip(TP.BASE[None, None, :] + 0.66 * (v + 0.55 * rc)[..., None] * TP.TINT, 0, 255)
    b1 = cv2.GaussianBlur(pp, (0, 0), 1.6); b2 = cv2.GaussianBlur(pp, (0, 0), 5.0)
    pap = np.clip(pp + 0.9 * (pp - b1) + 0.25 * (pp - b2), 0, 255); del pp, b1, b2
    ink0 = np.clip(23 + 0.80 * v[..., None] + np.array([1, 0, -1], np.float32), 0, 255)   # printed soft black (matches the reference)
    pt = lambda dx, dy: np.roll(np.roll(pap, dx, 1), dy, 0)
    P, P2, P3 = pt(211, 67), pt(700, 300), pt(500, 260); del pap
    lum = P.mean(2); t = lum - cv2.GaussianBlur(lum, (0, 0), 6); t = t / t.std()
    tooth = np.clip(0.5 + 0.5 * t, 0, 1)
    rng = np.random.default_rng(7)
    gn = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.9); gn /= gn.std()
    spk = np.clip((gn - 1.6) * 0.9, 0, 1); del gn, lum, t
    ys = np.arange(H, dtype=np.float32)[:, None]
    # ---- banner ink (straight-ish edges with a slight wobble, ink pooling inside the edges, E knocked out) ----
    bb = BAR_B + _jit(rng, 20, 0.5) + _jit(rng, 1.6, 0.8)
    edge_t = Y0 + _jit(rng, 20, 0.5) + _jit(rng, 1.6, 0.8)
    r0 = Y0 - 16
    mb = np.clip(bb - ys + 0.5, 0, 1)
    al = (np.clip(1 - 0.10 * tooth - 0.22 * spk * 2, 0, 1) * mb)[..., None]
    eb = np.clip(1 - np.minimum(bb - ys, ys - edge_t) / 6, 0, 1)[..., None]
    ink = ink0 * (1 - 0.18 * eb * mb[..., None])
    bar = P * (1 - al) + ink * al
    aE = _e_alpha()
    bar = bar * (1 - aE * mb[..., None]) + P * (aE * mb[..., None])
    del ink, ink0, eb, al
    edge_b = Y1 + _jit(rng, 18, 1.2) + _jit(rng, 3.0, 1.3)
    wrim = np.clip(2.6 + _jit(rng, 2.0, 1.3) + _jit(rng, 7, 1.0), 0.4, 6.0)
    # ---- back paper (neutral greige, 6% darker than the card; fade toward the frame edges) ----
    TN = 0.925; TT = np.array([TN, TN * 0.995, TN * 0.985], np.float32)
    FADE = 0.12
    fr = np.zeros((H, W, 3), np.float32)
    # top back paper
    bt = P3[:Y0] * TT * (1 - FADE * np.clip((Y0 - ys[:Y0]) / (H - Y1), 0, 1) ** 1.4)[..., None]
    fr[:Y0] = bt
    # banner + sheet top edge (torn rim, tight shadow on the back paper)
    t0, t1 = Y0 - 80, Y0 + 40
    ysr = ys[t0:t1]
    d = np.clip(edge_t[:, :] - wrim - ysr, 0, None)
    base_sh = bt_rows(P3, TT, t0, t1, ys) * (1 - (0.30 * np.exp(-d / 9.0) + 0.12 * np.exp(-d / 2.5)) * (ysr < edge_t))[..., None]
    mt = np.clip(ysr - edge_t + 0.5, 0, 1)
    gs = np.where((ysr >= r0)[..., None], bar[t0:t1], P[t0:t1])
    topc = base_sh * (1 - mt[..., None]) + gs * mt[..., None]
    rim_m = np.clip(ysr - (edge_t - wrim) + 0.5, 0, 1) * np.clip(edge_t - ysr + 0.5, 0, 1)
    rim_a = (rim_m * np.clip(0.95 - 0.45 * spk[t0:t1] - 0.25 * tooth[t0:t1], 0, 1))[..., None]
    topc = topc * (1 - rim_a) + (P[t0:t1] * 1.03) * rim_a
    fr[t0:t1] = topc
    fr[t1:BAR_B + 12] = np.where((ys[t1:BAR_B + 12] >= r0)[..., None], bar[t1:BAR_B + 12], P[t1:BAR_B + 12])
    fr[BAR_B + 12:Y1 - 10] = P[BAR_B + 12:Y1 - 10]          # placeholder; the card is drawn over these rows
    # a touch of extra sharpening on the printed banner + top edge only
    rg = fr[:Y0 + 220].copy(); rg[BAR_B + 12:] = P[BAR_B + 12:Y0 + 220]
    bl = cv2.GaussianBlur(rg, (0, 0), 1.5)
    fr[:BAR_B + 12] = np.clip(rg + 0.55 * (rg - bl), 0, 255)[:BAR_B + 12]
    # ---- bottom: straight sheet edge with a fine deckle, hairline fringe, soft shadow on the faded back paper ----
    b0 = Y1 - 10
    yb = ys[b0:]
    dsh = np.clip(yb - Y1, 0, None)
    base = P2[b0:] * TT * (1 - 0.16 * np.exp(-dsh / 10.0))[..., None] * (1 - FADE * np.clip(dsh / (H - Y1), 0, 1) ** 1.4)[..., None]
    mbm = np.clip(edge_b - yb + 0.5, 0, 1)
    comp = base * (1 - mbm[..., None]) + P2[b0:] * mbm[..., None]
    comp = comp * (1 + np.exp(-((yb - edge_b + 1.2) / 1.1) ** 2) * 0.04)[..., None]
    dd = np.clip(yb - edge_b, 0, None)
    comp = comp * (1 - 0.10 * np.exp(-dd / 9.0) * (yb > edge_b))[..., None]
    fr[b0:] = comp
    return np.clip(fr, 0, 255).astype(np.uint8)

def bt_rows(P3, TT, t0, t1, ys):
    return P3[t0:t1] * TT * (1 - 0.12 * np.clip((Y0 - ys[t0:t1]) / (H - Y1), 0, 1) ** 1.4)[..., None]

FRAME = build()

def bg_frame(t=0):
    return FRAME.copy()

def finish(fr):
    """call AFTER the card has been drawn/sharpened into fr: puts the printed banner (with its torn rim, E and edges) and the card's bottom edge on top"""
    fr[:BAR_B + 12] = FRAME[:BAR_B + 12]
    fr[Y1 - 10:] = FRAME[Y1 - 10:]
    return fr
