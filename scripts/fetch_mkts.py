#!/usr/bin/env python3
"""Pulls real market data from Yahoo's chart feed and writes the numeric part of /tmp/mkts.json (base) -> usage: python3 fetch_mkts.py out_base.json
Prints a summary. The model then adds big/big_cap/footer/source after checking the news."""
import json, sys, urllib.request, datetime as dt
UA = {"User-Agent": "Mozilla/5.0"}
def get(sym, interval, rng):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval={interval}&range={rng}"
    for host in ("query1", "query2"):
        try:
            req = urllib.request.Request(u.replace("query1", host), headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=25))["chart"]["result"][0]
        except Exception as e:
            err = e
    raise err
def local_date(ts, off): return dt.datetime.fromtimestamp(ts + off, dt.timezone.utc).date()
sp = get("%5EGSPC", "5m", "2d"); m = sp["meta"]; off = m["gmtoffset"]
bars = [(t, c) for t, c in zip(sp["timestamp"], sp["indicators"]["quote"][0]["close"]) if c is not None]
sess = local_date(bars[-1][0], off)
day = [(t, c) for t, c in bars if local_date(t, off) == sess]
reg = m["currentTradingPeriod"]["regular"]; t0, t1 = reg["start"], reg["end"]
if (day[-1][0] - t0) < 3600: sys.exit("S&P session looks incomplete or not today")
prev = round(m["previousClose"], 2); close = round(m["regularMarketPrice"], 2)
pts = [[round(min(1, max(0, (t - t0) / (t1 - t0))), 4), round(c, 2)] for t, c in day]
pts[-1][1] = close
pct = (close / prev - 1) * 100
world = []
for name, sym, code, country in [("Nasdaq", "%5EIXIC", "US", "United States"), ("Dow", "%5EDJI", "US", "United States"),
        ("FTSE 100", "%5EFTSE", "UK", "United Kingdom"), ("Nikkei 225", "%5EN225", "JP", "Japan"),
        ("Kospi", "%5EKS11", "KR", "South Korea"), ("Hang Seng", "%5EHSI", "HK", "Hong Kong")]:
    try:
        r = get(sym, "1d", "10d"); mm = r["meta"]
        rows = [(t, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None]
        idx = [i for i, (t, _) in enumerate(rows) if local_date(t, mm["gmtoffset"]) == sess]
        if not idx or idx[-1] == 0:
            # daily bar for today can be missing (None): fall back to meta price vs previous close
            r5 = get(sym, "5m", "1d"); m5 = r5["meta"]
            if local_date(m5["regularMarketTime"], m5["gmtoffset"]) != sess or not m5.get("previousClose"):
                print("SKIP (no session on", sess, "):", name); continue
            c_a, c_b = m5["previousClose"], m5["regularMarketPrice"]
            world.append([name, round((c_b / c_a - 1) * 100, 2), code, country]); print(name, world[-1][1], "(5m fallback)"); continue
        (t_a, c_a), (t_b, c_b) = rows[idx[-1] - 1], rows[idx[-1]]
        world.append([name, round((c_b / c_a - 1) * 100, 2), code, country]); print(name, world[-1][1])
    except Exception as e:
        print("SKIP", name, e)
wd = lambda d: d.strftime("%A")
prev_day = [local_date(t, off) for t, _ in bars if local_date(t, off) < sess]
pd_ = prev_day[-1] if prev_day else sess - dt.timedelta(days=1)
sgn = lambda v: ("+" if v >= 0 else "−") + f"{abs(v):.2f}%"
base = {"date": f"{wd(sess)} {sess.day} {sess.strftime('%B %Y')}", "sp_pts": pts, "sp_ref": prev,
        "sp_ref_lab": f"{wd(pd_)}’s close {prev:,.0f}", "sp_lab_end": [f"Close {close:,.0f}", sgn(pct)],
        "prev_lab": "9:30am", "today_lab": "4pm" if (t1 - t0) > 6 * 3600 else "Early close",
        "chart_note": "S&P 500 every 5 minutes · US Eastern time", "world": world, "out": "/tmp/mkts.svg",
        "session_date": str(sess), "sp_close": close, "sp_prev": prev, "sp_pct": round(pct, 2)}
json.dump(base, open(sys.argv[1], "w"), ensure_ascii=False)
print("S&P", prev, "->", close, f"{pct:.2f}%", "bars", len(pts), "session", sess)
