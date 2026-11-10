#!/usr/bin/env python3
"""Animated Shorts: which series and episodes are ALLOWED today (the hard limits; scoring is done by the task).
Usage: python3 scripts/anim_plan.py [YYYY-MM-DD]   (default: today in Europe/London)
Reads playbook/animated/registry.json and playbook/animated/log.jsonl (lines with status "posted" or "scheduled" count).
Prints JSON: {date, posted_today, can_post_today, series: {id: {status, posts_last_7, posted_yesterday, allowed, why,
             episodes: {id: {last, days_since, posts_last_7, allowed, why}}}}}"""
import json, os, sys, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "playbook", "animated")

def today_uk():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/London")).date()
    except Exception:
        return dt.date.today()

def main():
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else today_uk()
    reg = json.load(open(os.path.join(P, "registry.json"))); lim = reg["limits"]
    log = []
    lp = os.path.join(P, "log.jsonl")
    if os.path.exists(lp):
        for line in open(lp):
            line = line.strip()
            if line:
                r = json.loads(line)
                if r.get("status") in ("posted", "scheduled"): log.append(r)
    for r in log: r["_d"] = dt.date.fromisoformat(r["date"])
    win = lim["window_days"]
    in_win = lambda r: 0 <= (day - r["_d"]).days < win          # today and the previous 6 days
    posted_today = [r for r in log if r["_d"] == day]
    out = {"date": day.isoformat(), "posted_today": len(posted_today),
           "can_post_today": len(posted_today) < lim["max_posts_per_day"], "series": {}}
    for sid, s in reg["series"].items():
        sl = [r for r in log if r.get("style") == sid]
        n7 = sum(1 for r in sl if in_win(r)); yday = any(r["_d"] == day - dt.timedelta(days=1) for r in sl)
        allowed, why = True, "ok"
        if s["status"] == "paused": allowed, why = False, "paused"
        elif n7 >= lim["per_series_max_in_7_days"]: allowed, why = False, f"{n7} posts in the last {win} days (max {lim['per_series_max_in_7_days']})"
        elif lim.get("per_series_no_consecutive_days") and yday: allowed, why = False, "posted yesterday (never consecutive days)"
        elif not out["can_post_today"]: allowed, why = False, "an animated Short is already scheduled today"
        eps = {}
        for eid, e in s["episodes"].items():
            el = [r for r in sl if r.get("episode") == eid]
            last = max((r["_d"] for r in el), default=None)
            ds = (day - last).days if last else None
            e7 = sum(1 for r in el if in_win(r))
            ea, ew = allowed, why
            if ea and ds is not None and ds < e["gap_days"]: ea, ew = False, f"last {last} ({ds} days ago, gap {e['gap_days']})"
            if ea and e7 >= e["max_in_7_days"]: ea, ew = False, f"{e7} in the last {win} days (max {e['max_in_7_days']})"
            eps[eid] = {"last": last.isoformat() if last else None, "days_since": ds, "posts_last_7": e7, "allowed": ea, "why": ew,
                        "priority": e["priority"], "min_score": e.get("min_score", lim["min_score_to_post"])}
        trial = s["status"] == "trial"
        out["series"][sid] = {"status": s["status"], "posts_last_7": n7, "posted_yesterday": yday, "allowed": allowed, "why": why,
                              "trial_boost": 15 if trial and n7 == 0 else 0, "episodes": eps}
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
