#!/usr/bin/env python3
"""Daily Post: today's series order from the brain ranking (playbook/brain/ranking.json, written weekly by scripts/brain_rank.py).
Usage: python3 scripts/daily_plan.py [YYYY-MM-DD]   (default: today in Europe/London)
Prints JSON {date, ranking_on, order: [{series, name, group, score, slots, posted_in_window, slots_left, days_since, allowed, why}], rule}.
The task works DOWN `order` and posts the first series that has a fully verified topic today. Every rule in playbook/series.json
still applies (never the same series as yesterday, how_company only on a newer quarter, trend only when trending, the
monthly us_vs_uk special, 56-day topic repeat). gap_days is the longest gap: a series the ranking gives more slots may run sooner. If rank.enabled is false in playbook/brain/config.json this prints ranking_on=false
and the task uses the fixed rotation in series.json as before."""
import json, os, sys, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PB = os.path.join(ROOT, "playbook"); B = os.path.join(PB, "brain")
def today_uk():
    try:
        from zoneinfo import ZoneInfo; return dt.datetime.now(ZoneInfo("Europe/London")).date()
    except Exception: return dt.date.today()
def main():
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else today_uk()
    ser = json.load(open(os.path.join(PB, "series.json")))["series"]
    try:
        on = json.load(open(os.path.join(B, "config.json"))).get("rank", {}).get("enabled"); rk = json.load(open(os.path.join(B, "ranking.json")))["pools"]["daily"] if on else None
    except Exception: rk = None
    if not rk: print(json.dumps({"date": day.isoformat(), "ranking_on": False, "rule": "use the rotation in playbook/series.json"}, indent=1)); return
    log = [json.loads(l) for l in open(os.path.join(PB, "log.jsonl")) if l.strip()]
    for r in log: r["_d"] = dt.date.fromisoformat(r["date"])
    win = rk["window_days"]; ppd = rk.get("posts_per_day", 1); cap = rk["cap_per_series"]; order = []
    today_n = sum(1 for r in log if r["_d"] == day)
    for sid, v in rk["series"].items():
        if sid not in ser: continue
        L = [r for r in log if r.get("series") == sid]; n = sum(1 for r in L if 0 <= (day - r["_d"]).days < win)
        last = max((r["_d"] for r in L), default=None); ds = (day - last).days if last else None
        gap = min(ser[sid].get("gap_days", 0), max(2, win // max(1, v["slots"])))      # the ranking may shorten a series' variety gap (never below 2 days); topic rules are untouched
        ok, why = True, "ok"
        if v["group"] == "rested" or ser[sid].get("status") == "paused": ok, why = False, "rested / paused"
        elif today_n >= ppd: ok, why = False, "today's Daily Post slots are already used"
        elif ds == 0: ok, why = False, "already posted today"
        elif ppd == 1 and ds == 1: ok, why = False, "posted yesterday (never the same series two days running)"
        elif ds is not None and ds < gap: ok, why = False, f"last posted {ds} days ago (gap {gap})"
        elif n >= cap: ok, why = False, f"{n} posts in the last {win} days (max {cap})"
        left = max(0, v["slots"] - n)
        order.append({"series": sid, "name": v["name"], "group": v["group"], "score": v["score"], "slots": v["slots"], "posted_in_window": n, "slots_left": left,
                      "days_since": ds, "kind": ser[sid].get("kind"), "allowed": ok, "why": why, "_k": (not ok, left == 0, -((ds if ds is not None else win) / (win / max(1, v["slots"]))), -v["score"])})   # most overdue for its own pace first
    order.sort(key=lambda o: o.pop("_k"))
    print(json.dumps({"date": day.isoformat(), "ranking_on": True, "window_days": win, "order": order,
                      "rule": "Work down `order`: first allowed series with slots_left > 0 and a fully verified topic today. A series with slots_left = 0 is used only if none above it can be verified. Never post an unverified number; say in the final message which series was first in the order and which was used."}, indent=1))
if __name__ == "__main__": main()
