#!/usr/bin/env python3
"""True Economy BRAIN - step 2: analyse the store and write playbook/brain/scorecard.md + proposals.json.
usage: python3 brain_analyze.py [--now 2026-11-15T20:00Z] [--rank]      (--rank prints the weakest eligible series, for 'which series should a new idea replace?')
Rules (config.json): metrics are compared per platform against that platform's own median (index = value / median);
a verdict needs >= min_posts matured posts, >= min_consistency on one side of the median and (TikTok) watch time agreeing."""
import json, os, sys, statistics as st, datetime as dt, collections
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "playbook", "brain")
cfg = json.load(open(os.path.join(B, "config.json")))
def jl(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
posts = {r["post_id"]: r for r in jl(os.path.join(B, "posts.jsonl"))}
snaps = {}
for r in jl(os.path.join(B, "metrics.jsonl")):                    # latest snapshot per post wins
    if r["post_id"] not in snaps or r["snapshot_at"] >= snaps[r["post_id"]]["snapshot_at"]: snaps[r["post_id"]] = r
args = sys.argv[1:]
now = dt.datetime.fromisoformat(args[args.index("--now") + 1].replace("Z", "+00:00")) if "--now" in args else dt.datetime.now(dt.timezone.utc)
mat = dt.timedelta(days=cfg["maturity_days"])
PM = cfg["primary_metric"]; WIN = {"strong": cfg["strong_index"], "weak": cfg["weak_index"]}
rows = []
for pid, p in posts.items():
    s = snaps.get(pid)
    if not s or p["series"] == "documentary_link": continue
    t = dt.datetime.fromisoformat(p["sent_at"].replace("Z", "+00:00"))
    v = s.get(PM.get(p["platform"], "views"))
    if v is None: continue
    rows.append({**p, "value": v, "watch": s.get("averageTimeWatched"), "eng": s.get("engagementRate"), "mature": (now - t) >= mat})
M = [r for r in rows if r["mature"]]
base = {pl: st.median(r["value"] for r in M if r["platform"] == pl) for pl in PM if any(r["platform"] == pl for r in M)}
wbase = st.median([r["watch"] for r in M if r["platform"] == "tiktok" and r["watch"]] or [0])
for r in M:
    r["idx"] = r["value"] / base[r["platform"]] if base.get(r["platform"]) else None
    r["widx"] = (r["watch"] / wbase) if (r["watch"] and wbase) else None
def cell(L):
    ix = [r["idx"] for r in L]; n = len(ix); med = st.median(ix)
    side = max(sum(i > 1 for i in ix), sum(i < 1 for i in ix)) / n
    w = [r["widx"] for r in L if r["widx"]]; wm = st.median(w) if w else None
    return {"n": n, "med": med, "cons": side, "watch": wm}
def verdict(c, pl):
    if c["n"] < cfg["min_posts_for_verdict"]: return "not enough data"
    ok = c["cons"] >= cfg["min_consistency"]
    wagree = (c["watch"] is None) or pl != "tiktok" or ((c["watch"] >= 1) == (c["med"] >= 1))
    if c["med"] >= WIN["strong"] and ok and wagree: return "STRONG"
    if c["med"] <= WIN["weak"] and ok and wagree: return "WEAK"
    return "mixed / average"
out = ["# Brain scorecard", f"_Generated {now:%Y-%m-%d %H:%M} UTC. Posts older than {cfg['maturity_days']} days count as matured: {len(M)} of {len(rows)} measured posts._", "",
       "## Platform baselines (median primary metric of matured posts; index 1.00 = typical for that platform)"]
for pl, b in base.items(): out.append(f"- {pl}: median {PM[pl]} = {b:.0f} (n={sum(r['platform']==pl for r in M)})" + (f", median TikTok watch time {wbase:.1f}s" if pl == "tiktok" else ""))
out += ["", "## Series x platform (index vs platform median; automated series only)", "", "| Series | Platform | n | Median index | Same-side share | Watch idx (TikTok) | Verdict |", "|---|---|---|---|---|---|---|"]
props = []; summ = {}
G = collections.defaultdict(list)
for r in M:
    if r["series"] != "manual_pre_automation": G[(r["series"], r["platform"])].append(r)
for (ser, pl), L in sorted(G.items()):
    c = cell(L); v = verdict(c, pl)
    out.append(f"| {ser} | {pl} | {c['n']} | {c['med']:.2f} | {c['cons']:.0%} | {('%.2f' % c['watch']) if c['watch'] else '-'} | {v} |")
    summ.setdefault(ser, {})[pl] = (c, v)
    if v in ("STRONG", "WEAK") and c["n"] >= cfg["min_posts_for_big_change"] and abs(c["med"] - 1) >= cfg["big_change_effect_min"]:
        props.append({"id": f"{ser}:{pl}:{v.lower()}", "kind": "series_platform_" + v.lower(), "series": ser, "platform": pl, "big": True,
                      "evidence": {"n": c["n"], "median_index": round(c["med"], 2), "same_side_share": round(c["cons"], 2), "watch_index": c["watch"]},
                      "recommendation": ("Keep/expand " if v == "STRONG" else "Consider stopping / replacing ") + f"{ser} on {pl}"})
# series ranking: TikTok-weighted overall score = median of per-platform median indices (platforms with n>=min)
rank = []
for ser, d in summ.items():
    meds = [c["med"] for pl, (c, v) in d.items() if c["n"] >= cfg["min_posts_for_verdict"]]
    n = sum(c["n"] for pl, (c, v) in d.items())
    rank.append((ser, st.median(meds) if meds else None, n, bool(meds)))
out += ["", "## Series ranking (median of per-platform indices; only series with a verdict-eligible platform)"]
for ser, sc, n, ok in sorted(rank, key=lambda x: (x[1] is None, -(x[1] or 0))):
    out.append(f"- {ser}: " + (f"{sc:.2f} ({n} posts)" if ok else f"not enough data ({n} matured posts across platforms)"))
# caption features per platform
out += ["", "## Caption features (index vs platform median; a feature needs >= 6 posts on each side)", "", "| Platform | Feature | With: n / median idx | Without: n / median idx | Reading |", "|---|---|---|---|---|"]
def bucket(r):
    ch = r["features"]["chars"]; return "short <300" if ch < 300 else ("medium 300-700" if ch < 700 else "long >700")
feats = {"starts with a number/money": lambda r: r["features"]["number_first"], "hook is a question": lambda r: r["features"]["question"],
         "has a call to action": lambda r: r["features"]["cta"], "uses emoji": lambda r: r["features"]["emoji"], "2+ hashtags": lambda r: r["features"]["hashtags"] >= 2}
for pl in base:
    P = [r for r in M if r["platform"] == pl]
    for name, f in feats.items():
        a = [r["idx"] for r in P if f(r)]; b = [r["idx"] for r in P if not f(r)]
        if len(a) >= 6 and len(b) >= 6:
            ma, mb = st.median(a), st.median(b); rd = "better with" if ma > mb * 1.25 else ("better without" if mb > ma * 1.25 else "no clear difference"); rd = rd if min(len(a), len(b)) >= cfg["min_caption_posts_per_side_for_proposal"] or rd == "no clear difference" else rd + " (suggestive only, small sample)"
            out.append(f"| {pl} | {name} | {len(a)} / {ma:.2f} | {len(b)} / {mb:.2f} | {rd} |")
            if rd.startswith("better") and "suggestive" not in rd and min(len(a), len(b)) >= cfg["min_caption_posts_per_side_for_proposal"]: props.append({"id": f"caption:{pl}:{name}", "kind": "caption_style", "platform": pl, "big": False, "evidence": {"with_n": len(a), "with_median": round(ma, 2), "without_n": len(b), "without_median": round(mb, 2)}, "recommendation": f"{pl}: captions {rd} '{name}' perform better (soft guidance, within brand limits)"})
        else: out.append(f"| {pl} | {name} | {len(a)} / - | {len(b)} / - | not enough data |")
base_manual = [r for r in M if r["series"] == "manual_pre_automation" and r["platform"] == "tiktok"]
if base_manual: out += ["", f"_Baseline: {len(base_manual)} hand-posted TikToks before 26 Oct had median index {st.median(r['idx'] for r in base_manual):.2f} on the same scale._"]
out += ["", "## Proposals this run", ""] + ([f"- [{'BIG - needs approval' if p['big'] else 'auto-allowed'}] {p['recommendation']} - evidence {json.dumps(p['evidence'])}" for p in props] or ["- none: not enough data for any change yet"])
open(os.path.join(B, "scorecard.md"), "w").write("\n".join(out) + "\n")
json.dump(props, open(os.path.join(B, "proposals.json"), "w"), indent=1)
if "--rank" in args:
    print("Weakest eligible series first:"); [print(f"  {ser}: {sc:.2f} ({n} posts)") for ser, sc, n, ok in sorted([x for x in rank if x[3]], key=lambda x: x[1])]
print("\n".join(out))
