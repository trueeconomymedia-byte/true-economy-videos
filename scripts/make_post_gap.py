import sys; sys.path.insert(0, "/tmp")
from te_lib import *
OUT = sys.argv[1]
GA, JA, GG, JG = 5.4713, 4.3420, 0.013, 0.007     # IMF WEO Oct 2026: GDP 2026 ($tn) and real growth 2026
yrs = list(range(2026, 2047))
G = [GA * (1 + GG) ** (y - 2026) for y in yrs]; J = [JA * (1 + JG) ** (y - 2026) for y in yrs]
gap0, gap1 = G[0] - J[0], G[-1] - J[-1]
c = Card(); c.title("Germany's lead over", "Japan grows to $2.1tn", mark="$2.1tn", accent="none")
c.subtitle("If both keep their 2026 IMF growth rates · GDP in 2026 US$ · illustrative")
KH = 150
px0, px1 = 64, 700                      # plot x range (right side = end labels)
ptop = c.top + 20; pbot = c.bottom - KH - 70
ymin, ymax = 3.0, 8.0; sy = (pbot - ptop) / (ymax - ymin)
X = lambda y: px0 + (y - 2026) / 20 * (px1 - px0)
Y = lambda v: pbot - (v - ymin) * sy
with c.group("body"):
    for v in (3, 4, 5, 6, 7, 8):
        c.line(px0, Y(v), px1 + 10 if v == 3 else 948, Y(v), INK if v == 3 else "#CFC8B8", 2 if v == 3 else 1.5)
        c.text(px0 - 12, Y(v) + 6, f"${v}tn", 16, GREY, "sb", "r")
    for y in (2026, 2036, 2046):
        c.text(X(y), pbot + 30, str(y), 20, GREY, "sb", "m")
    c.text(px0 + 8, pbot + 62, "Chart starts at $3tn, not zero", 16, GREY, "sb")
    # red wedge = the gap, drawn first, lines on top
    c.polygon([(X(y), Y(g)) for y, g in zip(yrs, G)] + [(X(y), Y(j)) for y, j in reversed(list(zip(yrs, J)))], RED)
    c.polyline([(X(y), Y(j)) for y, j in zip(yrs, J)], BLUE_L, 8)
    c.polyline([(X(y), Y(g)) for y, g in zip(yrs, G)], BLUE, 8)
    c.circle(X(2026), Y(G[0]), 9, BLUE); c.circle(X(2026), Y(J[0]), 9, BLUE_L)
    c.circle(X(2046), Y(G[-1]), 9, BLUE); c.circle(X(2046), Y(J[-1]), 9, BLUE_L)
with c.group("toplabels"):
    ex = px1 + 26
    for code, nm, v, yy, col in (("DE", "Germany", G[-1], Y(G[-1]), BLUE), ("JP", "Japan", J[-1], Y(J[-1]), BLUE_L)):
        c.flag(ex + 14, yy - 30, 14, code); c.text(ex + 36, yy - 24, nm, 24, INK, "b")
        c.text(ex, yy + 14, f"${v:.2f}tn", 32, INK, "b"); c.text(ex, yy + 38, "in 2046", 16, GREY, "sb")
    # start values
    c.text(X(2026) + 4, Y(G[0]) - 48, f"${G[0]:.2f}tn", 28, INK, "b")
    c.text(X(2026) + 4, Y(J[0]) + 44, f"${J[0]:.2f}tn", 28, INK, "b")
    c.text(X(2026) + 14, Y(J[0]) - 12 - 0, "", 1)
    # gap callouts
    c.text(X(2036), Y((G[10] + J[10]) / 2) - 70, f"gap ${G[10]-J[10]:.2f}tn in 2036", 20, RED, "b", "m") if False else None
    mid = (Y(G[-1]) + Y(J[-1])) / 2
    xm = X(2037); ym = (Y(G[11]) + Y(J[11])) / 2
    c.text(xm, ym - 10, "Germany's lead", 30, "#FFFFFF", "b", "m")
    c.text(xm, ym + 28, f"${gap0:.2f}tn now", 26, "#FFFFFF", "b", "m")
    c.text(xm, ym + 60, f"${gap1:.2f}tn in 2046", 26, "#FFFFFF", "b", "m")
    c.text(X(2035), Y(G[9]) - 26, "+1.3% a year", 20, INK, "b", "m")
    c.text(X(2035), Y(J[9]) + 40, "+0.7% a year", 20, INK, "b", "m")
ky = c.bottom - KH
with c.group("kpis"):
    c.rect(0, ky, 948, KH - 16, YEL, 1, 6)
    t1 = f"The gap grows by ${gap1-gap0:.2f}tn in 20 years"
    c.text(474, ky + 62, t1, fit("b", t1, 40, 900), INK, "b", "m")
    t2 = "Germany grows 1.3% a year, Japan 0.7%: the lead widens"
    c.text(474, ky + 104, t2, fit("sb", t2, 26, 900), INK, "sb", "m")
c.footer("Faster growth turns $1.13tn into $2.09tn"); c.source("Source: IMF WEO Oct 2026 · projection illustrative: 2026 growth held constant, exchange rates fixed")
c.save(OUT)
