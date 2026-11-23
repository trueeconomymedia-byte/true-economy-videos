#!/usr/bin/env python3
"""True Economy BRAIN - step 3: rank every series and share out the posting slots.
usage: python3 brain_rank.py [--now 2026-11-23T20:00Z] [--dry]      (--dry prints only, writes nothing)

One league table per posting schedule ("pool": animated = Animated Shorts, daily = Daily Post). All settings: config.json "rank".
SCORE (50 = a typical video of that schedule):
  typical  recency-weighted median of each video's index (value / the pool's own median on that platform, last `baseline_days`),
           combined over platforms. Shows the floor.
  watch    same for average watch time (TikTok + Instagram).
  hit      best index on any platform >= `hit_index` earns a bonus that counts in full for `hit_full_days`, then halves every
           `hit_halflife_days`. Shows the ceiling; fades if it is not repeated.
  Few videos = "unknown, not bad": the score is pulled towards `prior_score` until a series has `min_videos` matured videos.
GROUPS  new (< min_videos) | top (>= top_score) | middle | bottom (< bottom_score).
SLOTS   posts_per_day x window. `test_share` of them go to new + bottom series (new: `new_slots` each; bottom: 1 each, taking
        turns when there are more series than slots), the rest to top + middle by score. While no series has enough videos to be
        ranked, everyone gets one slot and the rest is shared by provisional score. Nobody above `cap_share` of the window.
        The window grows (7 -> 14 -> 21 -> 28 days) when a pool has more series than one week can hold.
SAFETY  Slots change automatically ONLY when the Buffer data is fresh and complete (see freshness()). Otherwise the previous
        slots stay and a `rank:confirm` decision is queued for the user. Resting, scrapping, relaunching or adding a series is
        never automatic: this script only queues proposals; scripts/brain_decide.py applies them after the user approves.
Writes playbook/brain/ranking.json (read by scripts/anim_plan.py and scripts/daily_plan.py), ranking.md (the report section),
ranking_history.jsonl (one line per ISO week) and rank_proposals.json."""
import json, os, sys, math, statistics as st, datetime as dt, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "playbook", "brain"); PB = os.path.join(ROOT, "playbook")
DEF = {"baseline_days": 35, "min_videos": 6, "recent_videos": 6, "older_weight": 0.5, "prior_score": 58,
       "hit_index": 10, "hit_full_days": 28, "hit_halflife_days": 7, "hit_points": 25, "typical_points": 20, "watch_points": 12,
       "top_score": 60, "bottom_score": 40, "test_share": 0.3, "cap_share": 0.43, "new_slots": 2, "bottom_weeks_to_flag": 3,
       "relaunch_videos": 3, "max_wait_weeks": 3, "fresh_hours": 36, "coverage_min": 0.9, "coverage_days": [1, 21],
       "pools": {"daily": {"posts_per_day": 1}}}          # animated posts_per_day = registry.json limits.max_posts_per_day
def jl(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
def jf(p, d): return json.load(open(p)) if os.path.exists(p) else d
def wmedian(pairs):                                       # weighted median of (value, weight)
    pairs = sorted(pairs); tot = sum(w for _, w in pairs); acc = 0
    for v, w in pairs:
        acc += w
        if acc >= tot / 2: return v
def clip(x, a, b): return max(a, min(b, x))
def uk_day(iso):
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    try:
        from zoneinfo import ZoneInfo; t = t.astimezone(ZoneInfo("Europe/London"))
    except Exception: pass
    return t.date()

def load(now):
    cfg = jf(os.path.join(B, "config.json"), {}); R = {**DEF, **cfg.get("rank", {})}
    reg = jf(os.path.join(PB, "animated", "registry.json"), {"series": {}, "limits": {}}); ser = jf(os.path.join(PB, "series.json"), {"series": {}})
    state = jf(os.path.join(B, "series_state.json"), {})   # {series: {"status": "rested"|"relaunch", "since": date, "relaunch_from": date}}
    pools = {"animated": {"posts_per_day": reg.get("limits", {}).get("max_posts_per_day", 1), "series": {}},
             "daily": {"posts_per_day": R["pools"].get("daily", {}).get("posts_per_day", 1), "series": {}}}
    for sid, s in reg["series"].items(): pools["animated"]["series"][sid] = {"name": s["name"].split(" (")[0].split(":")[0], "since": s.get("since"), "paused": s.get("status") == "paused"}
    for sid, s in ser["series"].items(): pools["daily"]["series"][sid] = {"name": s.get("name", sid), "since": s.get("since"), "paused": s.get("status") == "paused"}
    for pool in pools.values():
        for sid, s in pool["series"].items():
            stt = state.get(sid, {}); s["rested"] = s["paused"] or stt.get("status") == "rested"; s["relaunch_from"] = stt.get("relaunch_from") if stt.get("status") == "relaunch" else None
    akeys = sorted(pools["animated"]["series"], key=len, reverse=True)
    def where(series):                                    # brain series name -> (pool, series id)
        if series.startswith("anim_"):
            rest = series[5:]
            for k in akeys:
                if rest == k or rest.startswith(k + "_"): return "animated", k
            return None
        return ("daily", series) if series in pools["daily"]["series"] else None
    posts = {r["post_id"]: r for r in jl(os.path.join(B, "posts.jsonl"))}; snaps = {}
    for r in jl(os.path.join(B, "metrics.jsonl")):
        if r["post_id"] not in snaps or r["snapshot_at"] >= snaps[r["post_id"]]["snapshot_at"]: snaps[r["post_id"]] = r
    PM = cfg.get("primary_metric", {"tiktok": "views", "instagram": "views", "facebook": "impressions"}); mat = cfg.get("maturity_days", 4)
    rows = []
    for pid, p in posts.items():
        w = where(p["series"]); s = snaps.get(pid)
        if not w or not s or not p.get("sent_at"): continue
        v = s.get(PM.get(p["platform"], "views"))
        if v is None: continue
        t = dt.datetime.fromisoformat(p["sent_at"].replace("Z", "+00:00"))
        rows.append({"pool": w[0], "sid": w[1], "platform": p["platform"], "day": uk_day(p["sent_at"]), "age": (now - t).total_seconds() / 86400,
                     "value": v, "watch": s.get("averageTimeWatched") or None, "mature": (now - t).days >= mat})
    return cfg, R, pools, rows, posts, snaps, PM

def freshness(now, R, pools, posts, snaps):
    """Fresh and complete = newest snapshot within fresh_hours, all three platforms present, and at least coverage_min of the
    posts the two logs say were published (1-21 days ago) have a metrics row on each of their channels."""
    why = []
    newest = max((s["snapshot_at"] for s in snaps.values()), default=None)
    age_h = (now - dt.datetime.fromisoformat(newest.replace("Z", "+00:00"))).total_seconds() / 3600 if newest else None
    if age_h is None or age_h > R["fresh_hours"]: why.append("the latest Buffer numbers are " + ("missing" if age_h is None else f"{age_h:.0f} hours old (limit {R['fresh_hours']})"))
    have = collections.defaultdict(set)                   # (pool, day) -> platforms with metrics
    akeys = set(pools["animated"]["series"])
    for pid, p in posts.items():
        if pid in snaps and p.get("sent_at"):
            pool = "animated" if p["series"].startswith("anim_") else ("daily" if p["series"] in pools["daily"]["series"] else None)
            if pool: have[(pool, uk_day(p["sent_at"]))].add(p["platform"])
    exp = got = 0; miss = []; lo, hi = R["coverage_days"]; today = now.date()
    for pool, path in (("animated", os.path.join(PB, "animated", "log.jsonl")), ("daily", os.path.join(PB, "log.jsonl"))):
        for r in jl(path):
            if pool == "animated" and r.get("status") not in ("posted", "scheduled"): continue
            try: d = dt.date.fromisoformat(r["date"])
            except Exception: continue
            if not (lo <= (today - d).days <= hi): continue
            for ch in r.get("channels") or ["tiktok", "instagram", "facebook"]:
                exp += 1
                if ch in have[(pool, d)]: got += 1
                else: miss.append(f"{pool} {d} {ch}")
    cov = got / exp if exp else 0
    if cov < R["coverage_min"]: why.append(f"only {cov:.0%} of the posts from the last {hi} days have numbers (need {R['coverage_min']:.0%}); missing e.g. {', '.join(miss[:4])}")
    for pl in ("tiktok", "instagram", "facebook"):
        if not any(s["platform"] == pl and (now - dt.datetime.fromisoformat(s["snapshot_at"].replace("Z", "+00:00"))).total_seconds() / 3600 <= R["fresh_hours"] for s in snaps.values()):
            why.append(f"no fresh {pl} numbers")
    return {"fresh": not why, "why": why, "snapshot_at": newest, "coverage": round(cov, 3), "expected": exp, "found": got}

def score_pool(pool, P, rows, R, now):
    rs = [r for r in rows if r["pool"] == pool and r["mature"]]
    recent = [r for r in rs if r["age"] <= R["baseline_days"]] or rs
    base = {}; wbase = {}
    for pl in {r["platform"] for r in rs}:
        v = [r["value"] for r in recent if r["platform"] == pl] or [r["value"] for r in rs if r["platform"] == pl]
        base[pl] = st.median(v) or 1
        w = [r["watch"] for r in recent if r["platform"] == pl and r["watch"]]
        if w: wbase[pl] = st.median(w)
    out = {}
    for sid, meta in P["series"].items():
        L = [r for r in rs if r["sid"] == sid]
        if meta.get("relaunch_from"): L = [r for r in L if r["day"].isoformat() >= meta["relaunch_from"]]     # a relaunch is judged on its new videos only
        days = sorted({r["day"] for r in L}, reverse=True); n = len(days)
        allv = sorted({r["day"] for r in rows if r["pool"] == pool and r["sid"] == sid})
        wt = {d: (1.0 if i < R["recent_videos"] else R["older_weight"]) for i, d in enumerate(days)}
        typ = {}; wat = {}
        for pl in base:
            a = [(r["value"] / base[pl], wt[r["day"]]) for r in L if r["platform"] == pl]
            if a: typ[pl] = wmedian(a)
            b = [(r["watch"] / wbase[pl], wt[r["day"]]) for r in L if r["platform"] == pl and r["watch"] and pl in wbase]
            if b: wat[pl] = wmedian(b)
        gm = lambda d: math.exp(sum(math.log(max(x, 0.02)) for x in d.values()) / len(d)) if d else None
        typical, watch = gm(typ), gm(wat)
        hit = None
        for r in L:
            ix = r["value"] / base[r["platform"]]
            if ix >= R["hit_index"]:
                fade = 1.0 if r["age"] <= R["hit_full_days"] else 0.5 ** ((r["age"] - R["hit_full_days"]) / R["hit_halflife_days"])
                pts = R["hit_points"] * clip(math.log10(ix) / 3, 0, 1) * fade
                if not hit or pts > hit["points"]: hit = {"points": round(pts, 1), "index": round(ix, 1), "platform": r["platform"], "day": r["day"].isoformat(), "value": r["value"], "fade": round(fade, 2)}
        raw = None
        if typical is not None:
            raw = 50 + R["typical_points"] * clip(math.log2(typical), -2, 2) + (R["watch_points"] * clip(math.log2(watch), -1, 1) if watch else 0) + (hit["points"] if hit else 0)
        k = min(n, R["min_videos"]) / R["min_videos"]
        score = R["prior_score"] if raw is None else raw * k + R["prior_score"] * (1 - k)
        group = "rested" if meta["rested"] else ("new" if n < R["min_videos"] else ("top" if score >= R["top_score"] else ("bottom" if score < R["bottom_score"] else "middle")))
        out[sid] = {"name": meta["name"], "group": group, "score": round(score, 1), "raw_score": None if raw is None else round(raw, 1), "videos": n, "videos_all": len(allv),
                    "typical_index": None if typical is None else round(typical, 2), "watch_index": None if watch is None else round(watch, 2),
                    "by_platform": {pl: {"index": round(typ[pl], 2), "n": sum(1 for r in L if r["platform"] == pl)} for pl in typ},
                    "hit": hit, "recent_hit": bool(hit and hit["fade"] >= 0.5), "last_posted": allv[-1].isoformat() if allv else None,
                    "relaunch": bool(meta.get("relaunch_from"))}
    return out, {"views": {k: round(v) for k, v in base.items()}, "watch": {k: round(v, 1) for k, v in wbase.items()}}

def share_slots(S, R, ppd):
    live = {k: v for k, v in S.items() if v["group"] != "rested"}
    week = 7 * ppd; window = 7
    while window < 28 and len(live) > 0.8 * week * (window // 7): window += 7
    total = ppd * window; cap = max(1, round(R["cap_share"] * total))
    test = [k for k, v in live.items() if v["group"] in ("new", "bottom")]; perf = [k for k, v in live.items() if v["group"] in ("top", "middle")]
    t_slots = total if not perf else (0 if not test else max(1, round(R["test_share"] * total))); p_slots = total - t_slots
    slots = {k: 0 for k in live}; left = t_slots
    new = sorted((k for k in test if live[k]["group"] == "new"), key=lambda k: -live[k]["score"])            # best provisional score first
    bottom = sorted((k for k in test if live[k]["group"] == "bottom"), key=lambda k: live[k]["last_posted"] or "")  # whoever waited longest first
    for rnd in range(R["new_slots"] if perf else 1):      # round 1: one slot each (new, then bottom); round 2: a second slot for each new series,
        for k in (new + bottom if rnd == 0 else new):     # so a new series is not crowded out by established ones. With no established series yet,
            if left and slots[k] < cap: slots[k] += 1; left -= 1   # the rest is shared by provisional score instead (below).
    def by_weight(keys, n):                               # hand out n slots by score weight, largest remainder, respecting the cap
        while n > 0:
            ok = [k for k in keys if slots[k] < cap]
            if not ok: break
            w = {k: 2 ** ((live[k]["score"] - 50) / 15) for k in ok}; tw = sum(w.values())
            k = max(ok, key=lambda k: (w[k] / tw * (n + sum(slots[x] for x in ok)) - slots[k], live[k]["score"]))
            slots[k] += 1; n -= 1
        return n
    left = by_weight([k for k in test if live[k]["group"] == "new"], left)
    if perf:
        for k in sorted(perf, key=lambda k: -live[k]["score"]):   # every top/middle series at least one, best first
            if p_slots and slots[k] < cap: slots[k] += 1; p_slots -= 1
        p_slots = by_weight(perf, p_slots + left); left = 0
    spare = by_weight(list(live), p_slots + left)
    waiting = [k for k in test if slots[k] == 0]          # more test series than test slots: they take turns
    max_live = len(perf) + max(1, t_slots) * R["max_wait_weeks"] // max(1, window // 7)
    return slots, {"window_days": window, "total_slots": total, "cap_per_series": cap, "test_slots": t_slots, "posts_per_day": ppd, "unused": spare, "waiting": waiting, "max_live": max_live, "live": len(live)}

def main():
    a = sys.argv[1:]; dry = "--dry" in a
    now = dt.datetime.fromisoformat(a[a.index("--now") + 1].replace("Z", "+00:00")) if "--now" in a else dt.datetime.now(dt.timezone.utc)
    cfg, R, pools, rows, posts, snaps, PM = load(now)
    fr = freshness(now, R, pools, posts, snaps)
    prev = jf(os.path.join(B, "ranking.json"), {}); hist = jl(os.path.join(B, "ranking_history.jsonl"))
    week = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"; hist = [h for h in hist if h["week"] != week]
    out = {"generated": now.strftime("%Y-%m-%dT%H:%MZ"), "week": week, "data": fr, "pools": {}}; props = []; md = []
    for pool, P in pools.items():
        S, base = score_pool(pool, P, rows, R, now); slots, info = share_slots(S, R, P["posts_per_day"])
        old = (prev.get("pools", {}).get(pool) or {})
        applied = fr["fresh"] or not old.get("series")      # nothing to keep on the very first run
        for sid, s in S.items():
            s["suggested_slots"] = slots.get(sid, 0)
            s["slots"] = s["suggested_slots"] if applied else (old["series"].get(sid, {}).get("slots", s["suggested_slots"]) if sid in old.get("series", {}) else s["suggested_slots"])
            streak = 0                                    # consecutive weekly runs in the bottom group, this week included
            if s["group"] == "bottom":
                streak = 1
                for h in sorted(hist, key=lambda h: h["week"], reverse=True):
                    if h.get("groups", {}).get(pool, {}).get(sid) == "bottom": streak += 1
                    else: break
            s["bottom_weeks"] = streak
            if streak >= R["bottom_weeks_to_flag"] and s["videos"] >= R["min_videos"] and not s["recent_hit"]:
                ev = {"score": s["score"], "videos": s["videos"], "typical_index": s["typical_index"], "watch_index": s["watch_index"], "bottom_weeks": streak, "by_platform": s["by_platform"]}
                if not s["relaunch"] and not any(d for d in jl(os.path.join(B, "decisions.jsonl")) if d["id"] == f"rank:relaunch:{sid}" and d["status"] == "approved"):
                    props.append({"id": f"rank:relaunch:{sid}", "kind": "rank_relaunch", "series": sid, "pool": pool, "big": True, "evidence": ev,
                                  "recommendation": f"Consider scrapping: {s['name']} has been in the bottom group {streak} weeks running. Second chance first: relaunch it with one fix (new opening or shorter length) and judge it on {R['relaunch_videos']} new videos"})
                else:
                    props.append({"id": f"rank:rest:{sid}", "kind": "rank_rest", "series": sid, "pool": pool, "big": True, "evidence": ev,
                                  "recommendation": f"Rest {s['name']} on the bench (bottom group {streak} weeks running, relaunch already tried). Design and ideas are kept"})
        if info["live"] > info["max_live"]:
            worst = min((k for k, v in S.items() if v["group"] in ("bottom", "middle", "top")), key=lambda k: S[k]["score"], default=None)
            if worst: props.append({"id": f"rank:rest:{worst}", "kind": "rank_rest", "series": worst, "pool": pool, "big": True, "evidence": {"live_series": info["live"], "room_for": info["max_live"], "score": S[worst]["score"], "videos": S[worst]["videos"]},
                                    "recommendation": f"The {pool} schedule has {info['live']} live series but room for about {info['max_live']} before each waits over {R['max_wait_weeks']} weeks. Rest the lowest-ranked one ({S[worst]['name']}) to make room"})
        changes = [f"{S[k]['name']}: {old['series'][k].get('slots')} -> {S[k]['suggested_slots']}" for k in S if k in old.get("series", {}) and old["series"][k].get("slots") != S[k]["suggested_slots"]]
        if not applied and changes:
            props.append({"id": f"rank:confirm:{pool}:{week}", "kind": "rank_confirm", "pool": pool, "big": True, "evidence": {"why_not_automatic": fr["why"], "changes": changes},
                          "recommendation": f"Buffer data was not fresh/complete, so the {pool} slots were NOT changed. Confirm to apply: " + "; ".join(changes)})
        out["pools"][pool] = {**info, "slots_applied": applied, "baseline": base, "series": S, "changes": changes}
        order = sorted(S, key=lambda k: (S[k]["group"] == "rested", -S[k]["score"]))
        md += [f"### {'Animated Shorts' if pool == 'animated' else 'Daily Post'}: {info['total_slots']} slots per {info['window_days']} days ({info['posts_per_day']} a day), {info['test_slots']} kept for testing, max {info['cap_per_series']} per series", "",
               "| # | Series | Group | Score | Videos | Typical | Watch | Hit | Slots |", "|---|---|---|---|---|---|---|---|---|"]
        for i, k in enumerate(order, 1):
            s = S[k]; h = f"{s['hit']['index']:g}x {s['hit']['platform']} {s['hit']['day'][5:]}" + ("" if s["hit"]["fade"] == 1 else f" (fading {s['hit']['fade']:.0%})") if s["hit"] else "-"
            md.append(f"| {i} | {s['name']} | {s['group']}{' (relaunch)' if s['relaunch'] else ''} | {s['score']:.0f} | {s['videos']} | {('%.2fx' % s['typical_index']) if s['typical_index'] else '-'} | {('%.2fx' % s['watch_index']) if s['watch_index'] else '-'} | {h} | {s['slots']}{'' if s['slots'] == s['suggested_slots'] else ' (suggested %d)' % s['suggested_slots']} |")
        md += ["", ("Slot changes applied automatically: " + ("; ".join(changes) or "none")) if applied else ("SLOTS NOT CHANGED (data check failed): " + "; ".join(fr["why"])), ""]
        if info["waiting"]: md += ["Taking turns for a testing slot (none this window): " + ", ".join(S[k]["name"] for k in info["waiting"]), ""]
    head = ["## Series ranking", f"_Generated {now:%Y-%m-%d %H:%M} UTC. Score 50 = a typical video of that schedule. Typical and Watch are multiples of that schedule's own median; a series with fewer than {R['min_videos']} matured videos is 'new' and its score is pulled towards {R['prior_score']} (unknown, not bad)._",
            f"_Buffer data check: {'fresh and complete' if fr['fresh'] else 'NOT fresh/complete - ' + '; '.join(fr['why'])} ({fr['found']} of {fr['expected']} expected post numbers found, newest snapshot {fr['snapshot_at']})._", ""]
    tail = ["### Needs your yes"] + ([f"- {p['recommendation']} (id `{p['id']}`; evidence {json.dumps(p['evidence'])})" for p in props] or ["- nothing this week"])
    text = "\n".join(head + md + tail) + "\n"
    if not dry:
        json.dump(out, open(os.path.join(B, "ranking.json"), "w"), indent=1)
        open(os.path.join(B, "ranking.md"), "w").write(text)
        json.dump(props, open(os.path.join(B, "rank_proposals.json"), "w"), indent=1)
        hist.append({"week": week, "generated": out["generated"], "fresh": fr["fresh"], "groups": {p: {k: v["group"] for k, v in d["series"].items()} for p, d in out["pools"].items()},
                     "scores": {p: {k: v["score"] for k, v in d["series"].items()} for p, d in out["pools"].items()}, "slots": {p: {k: v["slots"] for k, v in d["series"].items()} for p, d in out["pools"].items()}})
        open(os.path.join(B, "ranking_history.jsonl"), "w").write("".join(json.dumps(h) + "\n" for h in sorted(hist, key=lambda h: h["week"])))
    print(text)
if __name__ == "__main__": main()
