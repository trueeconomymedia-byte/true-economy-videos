#!/usr/bin/env python3
"""True Economy BRAIN - step 1: ingest Buffer posts (with metrics) into the repo store.
usage: python3 brain_ingest.py <buffer_list_posts_output.json> [more.json ...]
Accepts the saved list_posts result file(s) (either the raw tool-result file [{type,text}] or plain JSON with edges).
Appends a metrics SNAPSHOT per post to playbook/brain/metrics.jsonl and upserts playbook/brain/posts.jsonl (post registry:
platform, series, features of the caption). Series mapping order: video URL prefix -> series_overrides.json (by date/time) ->
playbook/log.jsonl (Daily Post, by UK date) -> markets_log.jsonl (Markets Daily) -> 'unmapped'."""
import json, re, sys, os, datetime as dt
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "playbook", "brain")
P = os.path.join(B, "..")
def jl(path):
    return [json.loads(l) for l in open(path) if l.strip()] if os.path.exists(path) else []
def load_edges(path):
    raw = json.load(open(path))
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "text" in raw[0] and "type" in raw[0]:
        raw = json.loads(raw[0]["text"])
    return [e["node"] if "node" in e else e for e in (raw.get("edges") or raw.get("posts") or [])]
def uk_date(iso):                                  # sent time is UTC; UK = UTC (winter) / +1 (summer): use London rule
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    y = t.year
    last_sun = lambda m: max(d for d in (dt.datetime(y, m, x, 1, tzinfo=dt.timezone.utc) for x in range(25, 32 if m in (3, 10) else 30)) if d.weekday() == 6)
    bst = last_sun(3) <= t < last_sun(10)
    return (t + dt.timedelta(hours=1 if bst else 0))
def features(text):
    t = (text or "").strip(); first = re.split(r"(?<=[.!?])\s|\n", t)[0] if t else ""
    return {"chars": len(t), "hashtags": len(re.findall(r"#\w+", t)), "question": bool(re.search(r"\?", first)),
            "number_first": bool(re.match(r"^\W*(?:[\$£€]?\d|\d)", first)) or bool(re.search(r"[\$£€]\s?\d", first)),
            "cta": bool(re.search(r"\b(follow|subscribe|comment|share|save)\b", t, re.I)), "emoji": bool(re.search(r"[\U0001F300-\U0001FAFF]", t)),
            "hook": first[:90]}
def series_for(node, logs, mlogs, over):
    s = json.dumps(node.get("assets") or [])
    m = re.search(r"videos/([a-z_]+?)-[^/\"\\]*?\d{4}-\d{2}-\d{2}\.mp4", s)
    if m and m.group(1) not in ("markets", "stock", "how"): return m.group(1), "video_url"
    if re.search(r"videos/markets-", s): return "markets_daily", "video_url"
    if re.search(r"videos/stock-market-today", s): return "stock_market_today", "video_url"
    sa = node.get("sentAt") or node.get("dueAt") or ""
    if not sa: return "unmapped", "none"
    t = uk_date(sa); d = t.strftime("%Y-%m-%d")
    for o in over:                                  # manual backfill rules: {"date","hour_from","hour_to","series"}
        if o["date"] == d and o.get("hour_from", 0) <= t.hour < o.get("hour_to", 24) and (not o.get("match") or re.search(o["match"], node.get("text") or "", re.I)):
            return o["series"], "override"
    if d < "2026-10-26": return "manual_pre_automation", "rule"      # posted by hand before the automated tasks existed (baseline only)
    late = t.hour >= 22 or t.hour < 3
    if late:
        dd = (t - dt.timedelta(days=1 if t.hour < 3 else 0)).strftime("%Y-%m-%d")
        for r in mlogs:
            if r.get("date") == dd and r.get("status") == "posted": return "markets_daily", "markets_log"
    for r in logs:
        if r.get("date") == d: return r["series"], "log"
    return "unmapped", "none"
def main(files):
    over = json.load(open(os.path.join(B, "series_overrides.json"))) if os.path.exists(os.path.join(B, "series_overrides.json")) else []
    logs, mlogs = jl(os.path.join(P, "log.jsonl")), jl(os.path.join(P, "markets_log.jsonl"))
    posts = {r["post_id"]: r for r in jl(os.path.join(B, "posts.jsonl"))}
    snap_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"); nm = 0
    with open(os.path.join(B, "metrics.jsonl"), "a") as mf:
        for f in files:
            for n in load_edges(f):
                if n.get("status") != "sent" or not (n.get("text") or "").strip(): continue
                pid = n["id"]; sa = n.get("sentAt") or ""
                ser, src = series_for(n, logs, mlogs, over)
                posts[pid] = {"post_id": pid, "platform": n["channelService"], "sent_at": sa, "series": ser, "series_source": src,
                              "text_start": (n.get("text") or "")[:100].replace("\n", " "), "features": features(n.get("text"))}
                mt = {x["type"]: x["value"] for x in (n.get("metrics") or [])}
                if mt: mf.write(json.dumps({"post_id": pid, "snapshot_at": snap_at, "sent_at": sa, "platform": n["channelService"], **mt}) + "\n"); nm += 1
    with open(os.path.join(B, "posts.jsonl"), "w") as pf:
        for r in sorted(posts.values(), key=lambda r: r["sent_at"]): pf.write(json.dumps(r) + "\n")
    print(f"posts registry: {len(posts)}; metric snapshots appended: {nm}")
if __name__ == "__main__": main(sys.argv[1:])
