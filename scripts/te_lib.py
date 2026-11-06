#!/usr/bin/env python3
"""True Economy card library. Every card post is built on this so branding and the template stay identical.
Canvas 948x1300 = the safe zone (fills edge to edge) of the white card (title included) of the user's Canva card. Pure flat vector: paths only, text outlined, no opacity.

    from te_lib import *
    c = Card()
    c.title("How Nvidia makes", "money?", mark="Nvidia")         # serif title, yellow marker behind `mark`
    c.subtitle("Where each quarter's revenue goes · quarter to 26 July 2026")
    # c.top = first free y under the subtitle (KPI row / chart starts here), c.bottom = last y for the chart (footer sits below)
    with c.group("body"):          # static groups (title/body/anything) are drawn first, never move in the video
        c.rect(x, y, w, h, BLUE); c.text(x, y, "label", 20, INK, "sb"); c.ribbon(...); c.flag(cx, cy, r, "US")
    with c.group("labels"):        # group "labels" (or any name starting "top") is drawn ABOVE the animation layer
        ...
    c.footer("62¢ of every $1 of revenue became profit"); c.source("Source: ...")
    c.save("/mnt/user-data/outputs/<slug>.svg", anim={...})        # writes <slug>.svg (+ .anim.json for the video script)
Rules: keep b1=66 (headline touches the top), source line at H-4, footer at H-40 (Facebook feed crops top and bottom). Groups must be flat (no nested <g>)."""
import json, re, math
from fontTools.ttLib import TTFont
from fontTools.t1Lib import T1Font
from fontTools.agl import UV2AGL
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import NullPen

W, H = 948, 1300
RED, BLUE, YEL = "#E23B3B", "#3362CE", "#FFF205"           # True Economy red / blue / yellow
GREEN = "#6CBF3F"
BLUE_D, BLUE_L, BLUE_XL = "#3362CE", "#A4BBE8", "#A4BBE8"
INK, GREY, PALE = "#111111", "#555555", "#EEEEEC"
X0, CW = 0, 948                                             # left margin, content width (right edge = 948)
IF = "/usr/share/fonts/opentype/inter/Inter-%s.otf"

class _F:
    def __init__(s, path, t1=False):
        s.t1 = t1
        if t1:
            f = T1Font(path); f.parse(); s.gs = f.getGlyphSet(); s.upem = 1000
        else:
            f = TTFont(path); s.f = f; s.gs = f.getGlyphSet(); s.cm = f.getBestCmap(); s.upem = f['head'].unitsPerEm
    def name(s, ch): return UV2AGL.get(ord(ch)) if s.t1 else s.cm.get(ord(ch))
    def adv(s, n):
        if n is None or n not in s.gs: return 0
        if s.t1:
            g = s.gs[n]; g.draw(NullPen()); return g.width
        return s.f['hmtx'][n][0]
fonts = {"b": _F(IF % "Bold"), "sb": _F(IF % "SemiBold"), "m": _F(IF % "Medium"), "xb": _F(IF % "ExtraBold"),
         "cb": _F("/usr/share/fonts/X11/Type1/c0632bt_.pfb", True)}     # cb = Charter bold (serif titles)
def width(fk, t, size):
    f = fonts[fk]; return sum(f.adv(f.name(c)) for c in t) * size / f.upem
def fit(fk, t, size, maxw):
    """largest size <= size so that t fits in maxw"""
    return min(size, maxw / max(width(fk, t, 1), 1e-6))
def solid(hexc, op, bg=(250, 250, 250)):
    if op == 1: return hexc
    c = [int(hexc[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(op * c[i] + (1 - op) * bg[i]) for i in range(3))
def money(v, cur="$"):
    return f"{cur}{v:,.1f}B" if v >= 1 else f"{cur}{v*1000:,.0f}M"

class Card:
    def __init__(s):
        s.groups = {}; s.cur = None; s.top = 0; s.bottom = H - 80; s.anim = {}
    # --- groups
    class _G:
        def __init__(g, c, n): g.c, g.n = c, n
        def __enter__(g): g.prev = g.c.cur; g.c.cur = g.n; g.c.groups.setdefault(g.n, []); return g
        def __exit__(g, *a): g.c.cur = g.prev
    def group(s, name): return Card._G(s, name)
    def _o(s, x):
        assert s.cur, "draw inside `with c.group(name):`"
        s.groups[s.cur].append(x)
    # --- primitives
    def text(s, x, y, t, size, fill=INK, fk="b", anchor="l"):
        f = fonts[fk]; w = width(fk, t, size)
        if anchor == "r": x -= w
        elif anchor == "m": x -= w / 2
        k = size / f.upem; pen = SVGPathPen(f.gs); cx = x
        for ch in t:
            n = f.name(ch)
            if n in f.gs: f.gs[n].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
            cx += f.adv(n) * k
        s._o(f'<path d="{pen.getCommands()}" fill="{fill}"/>')
    def rect(s, x, y, w, h, fill, op=1, r=0):
        fill = solid(fill, op)
        if r:
            s._o(f'<path d="M{x+r:.1f},{y:.1f} H{x+w-r:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+r:.1f} V{y+h-r:.1f} Q{x+w:.1f},{y+h:.1f} {x+w-r:.1f},{y+h:.1f} H{x+r:.1f} Q{x:.1f},{y+h:.1f} {x:.1f},{y+h-r:.1f} V{y+r:.1f} Q{x:.1f},{y:.1f} {x+r:.1f},{y:.1f} Z" fill="{fill}"/>')
        else:
            s._o(f'<path d="M{x:.1f},{y:.1f} H{x+w:.1f} V{y+h:.1f} H{x:.1f} Z" fill="{fill}"/>')
    def circle(s, cx, cy, r, fill, stroke=None, sw=0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        s._o(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{st}/>')
    def line(s, x1, y1, x2, y2, stroke, sw=2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s._o(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    def polyline(s, pts, stroke, sw=6, fill="none"):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        s._o(f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')
    def polygon(s, pts, fill):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts); s._o(f'<polygon points="{p}" fill="{fill}"/>')
    def path(s, d, fill="none", stroke=None, sw=0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        s._o(f'<path d="{d}" fill="{fill}"{st}/>')
    def ribbon(s, xs, ys0, ys1, xd, yd0, yd1, fill, op, animate=True):
        """flow ribbon (Sankey band). animate=True registers it so the video can run money streaks along it."""
        if animate: s.anim.setdefault("flow", []).append([xs, ys0, ys1, xd, yd0, yd1, fill])
        xm = (xs + xd) / 2
        s._o(f'<path d="M{xs:.1f},{ys0:.1f} C{xm:.1f},{ys0:.1f} {xm:.1f},{yd0:.1f} {xd:.1f},{yd0:.1f} L{xd:.1f},{yd1:.1f} '
             f'C{xm:.1f},{yd1:.1f} {xm:.1f},{ys1:.1f} {xs:.1f},{ys1:.1f} Z" fill="{solid(fill, op)}"/>')
    def pulse(s, x, y, w, h, rgb, cycles=None, r=6):
        """register a rectangle that gently flashes in the video (tile flash like Stock Market Today). rgb = (r,g,b)."""
        s.anim.setdefault("pulse", []).append([x, y, w, h, list(rgb), cycles, r])
    _uid = 0
    def flag(s, cx, cy, r, code):
        """round flag icon. Known: US UK JP KR HK FR DE IT IE NL BE ES PL RU CH CN IN BR CA SE NO DK AU(approx none). Unknown code -> grey disc with the code."""
        Card._uid += 1; u = f"f{Card._uid}"; x0_, y0_, w_ = cx - r, cy - r, 2 * r
        o = [f'<clipPath id="{u}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath><g clip-path="url(#{u})">']
        def band(cols, vertical):
            n = len(cols)
            for i, c in enumerate(cols):
                if vertical: o.append(f'<rect x="{x0_ + i*w_/n:.1f}" y="{y0_}" width="{w_/n+0.5:.1f}" height="{w_}" fill="{c}"/>')
                else: o.append(f'<rect x="{x0_}" y="{y0_ + i*w_/n:.1f}" width="{w_}" height="{w_/n+0.5:.1f}" fill="{c}"/>')
        tri = {"FR": (["#1F3C88", "#FFFFFF", "#D22F27"], True), "IT": (["#2E8B57", "#FFFFFF", "#D22F27"], True),
               "IE": (["#169B62", "#FFFFFF", "#FF883E"], True), "BE": (["#111111", "#FAE042", "#D22F27"], True),
               "DE": (["#111111", "#DD0000", "#FFCE00"], False), "NL": (["#AE1C28", "#FFFFFF", "#21468B"], False),
               "RU": (["#FFFFFF", "#1C57A5", "#D52B1E"], False), "PL": (["#FFFFFF", "#DC143C"], False),
               "ES": (["#AA151B", "#F1BF00", "#AA151B"], False), "SE": (["#006AA7"], False), "NO": (["#BA0C2F"], False),
               "DK": (["#C8102E"], False), "CH": (["#D52B1E"], False), "CA": (["#D52B1E", "#FFFFFF", "#D52B1E"], True)}
        if code == "US":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#FFFFFF"/>')
            for i in range(0, 7, 2): o.append(f'<rect x="{x0_}" y="{y0_+i*w_/7:.1f}" width="{w_}" height="{w_/7:.1f}" fill="#D22F27"/>')
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_*0.55:.1f}" height="{w_*4/7:.1f}" fill="#1F3C88"/>')
        elif code == "JP":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#FFFFFF"/><circle cx="{cx}" cy="{cy}" r="{r*0.42:.1f}" fill="#D7243A"/>')
        elif code == "KR":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#FFFFFF"/>'); rr = r * 0.42
            o.append(f'<path d="M{cx-rr:.1f},{cy} A{rr:.1f},{rr:.1f} 0 0 1 {cx+rr:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 1 {cx:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 0 {cx-rr:.1f},{cy} Z" fill="#D7243A"/>')
            o.append(f'<path d="M{cx+rr:.1f},{cy} A{rr:.1f},{rr:.1f} 0 0 1 {cx-rr:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 1 {cx:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 0 {cx+rr:.1f},{cy} Z" fill="#1F4E9E"/>')
        elif code == "UK":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#1F3C88"/>')
            d1 = f"M{x0_},{y0_} L{x0_+w_},{y0_+w_} M{x0_+w_},{y0_} L{x0_},{y0_+w_}"; d2 = f"M{cx},{y0_} V{y0_+w_} M{x0_},{cy} H{x0_+w_}"
            o.append(f'<path d="{d1}" stroke="#FFFFFF" stroke-width="{w_*0.2:.1f}"/><path d="{d1}" stroke="#D22F27" stroke-width="{w_*0.07:.1f}"/>')
            o.append(f'<path d="{d2}" stroke="#FFFFFF" stroke-width="{w_*0.34:.1f}"/><path d="{d2}" stroke="#D22F27" stroke-width="{w_*0.2:.1f}"/>')
        elif code == "HK":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#DE2910"/>')
            for k in range(5): o.append(f'<ellipse cx="{cx}" cy="{cy-r*0.3:.1f}" rx="{r*0.17:.1f}" ry="{r*0.3:.1f}" fill="#FFFFFF" transform="rotate({k*72} {cx} {cy})"/>')
        elif code == "CN":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#DE2910"/>')
            pts = []; sx, sy, R = cx - r * 0.45, cy - r * 0.4, r * 0.34
            for i in range(10):
                a = -math.pi / 2 + i * math.pi / 5; rr = R if i % 2 == 0 else R * 0.4
                pts.append(f"{sx+rr*math.cos(a):.1f},{sy+rr*math.sin(a):.1f}")
            o.append(f'<polygon points="{" ".join(pts)}" fill="#FFDE00"/>')
        elif code == "IN":
            band(["#FF9933", "#FFFFFF", "#138808"], False); o.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.2:.1f}" fill="none" stroke="#000080" stroke-width="2"/>')
        elif code == "BR":
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#009C3B"/>')
            o.append(f'<polygon points="{cx},{cy-r*0.7:.1f} {cx+r*0.85:.1f},{cy} {cx},{cy+r*0.7:.1f} {cx-r*0.85:.1f},{cy}" fill="#FFDF00"/><circle cx="{cx}" cy="{cy}" r="{r*0.33:.1f}" fill="#002776"/>')
        elif code in tri:
            cols, vert = tri[code]
            if code in ("SE", "NO", "DK", "CH"):   # cross flags
                o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="{cols[0]}"/>')
                cc = {"SE": "#FECC00", "NO": "#FFFFFF", "DK": "#FFFFFF", "CH": "#FFFFFF"}[code]
                o.append(f'<path d="M{cx-r*0.25:.1f},{y0_} V{y0_+w_} M{x0_},{cy} H{x0_+w_}" stroke="{cc}" stroke-width="{w_*0.18:.1f}"/>' if code != "CH" else f'<path d="M{cx},{cy-r*0.55:.1f} V{cy+r*0.55:.1f} M{cx-r*0.55:.1f},{cy} H{cx+r*0.55:.1f}" stroke="#FFFFFF" stroke-width="{w_*0.2:.1f}"/>')
            else: band(cols, vert)
        else:
            o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#DDDDDD"/>')
        o.append('</g>')
        if code not in ("US","UK","JP","KR","HK","CN","IN","BR") and code not in tri:
            s._o("".join(o)); s.text(cx, cy + r * 0.28, code, r * 0.8, INK, "b", "m")
        else:
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#00000022" stroke-width="1.5"/>'); s._o("".join(o))
    def alluvial(s, cols, series, x_left, x_right, y_top, y_bottom, colors, flags=None, node_w=16, gap=4, fmt=None,
                 label_cols=(0, -1), animate=True, op=0.9, small=14):
        """Wave / bump-ribbon chart: ranked stacks at each time column joined by smooth S-curve ribbons whose width = value.
        cols = ["1980","2000","2025"]; series = {"US":[2.9,10.3,30.6], ...} (None = absent in that column); colors = {"US": "#3362CE", ...};
        flags = {"US":"US"}; fmt = lambda v: f"${v:.1f}T". Stacks are bottom-aligned, largest on top, same scale for every column.
        Draw inside `with c.group("body")`; labels are drawn in the same group. Returns {name:[(x,y0,y1),...]} node geometry."""
        n = len(cols); xs = [x_left + (x_right - x_left - node_w) * i / (n - 1) for i in range(n)]
        fmt = fmt or (lambda v: f"{v:g}")
        tot = [sum((v[i] or 0) for v in series.values()) for i in range(n)]
        cnt = [sum(1 for v in series.values() if v[i]) for i in range(n)]
        k = min((y_bottom - y_top - gap * (cnt[i] - 1)) / tot[i] for i in range(n) if tot[i])
        geo = {nm: [None] * n for nm in series}
        for i in range(n):
            order = sorted([nm for nm in series if series[nm][i]], key=lambda nm: -series[nm][i])
            y = y_bottom - (sum(series[nm][i] for nm in order) * k + gap * (len(order) - 1))
            for nm in order:
                h = series[nm][i] * k; geo[nm][i] = (xs[i], y, y + h); y += h + gap
        for i in range(n - 1):                      # ribbons first (under the nodes)
            for nm in series:
                a, b = geo[nm][i], geo[nm][i + 1]
                if a and b: s.ribbon(a[0] + node_w, a[1], a[2], b[0], b[1], b[2], colors[nm], op, animate)
        for nm in series:                           # nodes
            for g in geo[nm]:
                if g: s.rect(g[0], g[1], node_w, g[2] - g[1], colors[nm])
        for ci in label_cols:                       # labels at first / last column, fanned upward so they never collide
            i = ci % n; left = (i == 0)
            items = sorted([[(geo[nm][i][1] + geo[nm][i][2]) / 2, nm] for nm in series if geo[nm][i]], key=lambda t: -t[0])
            prev = None
            for it in items:                        # bottom-up: each label sits at least `need` px above the one below
                nm = it[1]; big = (geo[nm][i][2] - geo[nm][i][1]) > 44; need = 46 if big else 24
                cy = it[0] if prev is None else min(it[0], prev - need)
                cy = min(cy, y_bottom - 6) if prev is None else cy
                it.append(cy); it.append(big); prev = cy
            for cy0, nm, cy, big in items:
                v = series[nm][i]; fs = 26 if big else small + 4
                x = xs[i] - 10 if left else xs[i] + node_w + 10; an = "r" if left else "l"
                if flags and nm in flags:
                    s.flag(x + (-14 if left else 14), cy, 14 if big else 10, flags[nm]); x += -34 if left else 34
                if big:
                    s.text(x, cy - 2, nm, fs, INK, "b", an); s.text(x, cy + fs * 0.85, fmt(v), fs * 0.72, GREY, "sb", an)
                else:                                # small node: one line "name  value"
                    vt = fmt(v); wv = width("sb", vt, fs * 0.8)
                    if left: s.text(x, cy + 6, vt, fs * 0.8, GREY, "sb", "r"); s.text(x - wv - 8, cy + 6, nm, fs, INK, "b", "r")
                    else: s.text(x, cy + 6, nm, fs, INK, "b", "l"); s.text(x + width("b", nm, fs) + 8, cy + 6, vt, fs * 0.8, GREY, "sb", "l")
        for i in range(1, n - 1):                   # middle columns: value only, on the node
            for nm in series:
                g = geo[nm][i]
                if g and (g[2] - g[1]) > 22: s.text(g[0] + node_w + 8, (g[1] + g[2]) / 2 + 6, fmt(series[nm][i]), 17, INK, "sb")
        for i, cl in enumerate(cols):               # column headings
            s.text(xs[i] + (node_w if i == 0 else 0) / 2 + (0 if i < n - 1 else node_w), y_top - 14, cl, 34, INK, "cb", "l" if i == 0 else ("r" if i == n - 1 else "m"))
        return geo

    # --- template pieces (fixed positions: do not move)
    def title(s, line1, line2=None, mark=None):
        """Serif title ALWAYS on two lines, with the black bar on its left (new template). `mark` = substring that gets the yellow marker.
        If only line1 is given it is split into two balanced lines automatically. Choose wording so both lines are of similar length. b1=66 is fixed."""
        if not line2:
            ws = line1.split(); best = None
            for i in range(1, len(ws)):
                a_, b_ = " ".join(ws[:i]), " ".join(ws[i:]); d_ = abs(width("cb", a_, 1) - width("cb", b_, 1))
                if best is None or d_ < best[0]: best = (d_, a_, b_)
            assert best, "title needs at least two words (or give line1 and line2)"
            _, line1, line2 = best
        TX = 38
        size = min(92.0, (948 - TX) / width("cb", line1, 1), (948 - TX) / width("cb", line2, 1))
        b1 = 66; pitch = size * 0.93
        with s.group("title"):
            s.rect(X0, b1 - size * 0.70, 12, size * 0.70 + pitch, INK)
            if mark:
                for ln, by in ((line1, b1), (line2, b1 + pitch)):
                    if ln and mark in ln:
                        i = ln.index(mark); wp = width("cb", ln[:i], size); wn = width("cb", mark, size)
                        s.rect(X0 + TX + wp - 6, by - size * 0.76, wn + 12, size * 0.93, YEL)
            s.text(X0 + TX, b1, line1, size, INK, "cb")
            s.text(X0 + TX, b1 + pitch, line2, size, INK, "cb")
        s._ty = b1 + pitch
    def subtitle(s, t):
        with s.group("title"): s.text(X0, s._ty + 52, t, 24, GREY, "m")
        s.top = s._ty + 52 + 70           # first y below the subtitle for KPI row / chart
    def footer(s, t):
        with s.group("footer"): s.text(X0, H - 40, t, fit("b", t, 30, CW), INK, "b")
    def source(s, t):
        with s.group("source"): s.text(X0, H - 4, t, fit("m", t, 15, CW), GREY, "m")
    def kpi_row(s, items, y=None, hi=3):
        """4 KPI boxes: items = [(label, value_text, sub_text)...]; box index `hi` is yellow. Returns bottom y."""
        y = s.top if y is None else y; n = len(items); gap = 14; bw = (CW - gap * (n - 1)) / n
        with s.group("kpis"):
            for i, (lab, val, sub) in enumerate(items):
                bx = X0 + i * (bw + gap); col = YEL if i == hi else PALE
                s.text(bx + bw / 2, y, lab, 19, INK, "sb", "m"); s.rect(bx, y + 14, bw, 92, col, 1, 4)
                s.text(bx + bw / 2, y + 62, val, fit("b", val, 34, bw - 16), INK, "b", "m")
                s.text(bx + bw / 2, y + 90, sub, 16, INK if col == YEL else BLUE_D, "sb", "m")
        return y + 14 + 92
    def svg(s):
        body = ""
        for n, items in s.groups.items(): body += f'<g id="{n}">' + "\n".join(items) + "\n</g>\n"
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W*2}" height="{H*2}">\n' + body + "</svg>\n"
    def save(s, path, anim=None):
        a = dict(s.anim); a.update(anim or {})
        open(path, "w").write(s.svg())
        json.dump(a, open(path.replace(".svg", ".anim.json"), "w"))
        if "flow" in a: json.dump(a["flow"], open(path.replace(".svg", ".ribbons.json"), "w"))
        print("wrote", path, "anim:", list(a))
