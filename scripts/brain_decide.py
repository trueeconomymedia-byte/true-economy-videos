#!/usr/bin/env python3
"""True Economy BRAIN - approvals. usage:
  python3 brain_decide.py add <proposals.json>           queue every BIG proposal not yet pending/decided (weekly task)
  python3 brain_decide.py list                           show pending decisions
  python3 brain_decide.py approve <id> ["note"]          user approved: mark approved and append a dated entry to playbook/feedback.md (newest wins) / routing.json
  python3 brain_decide.py decline <id> ["note"]          user declined: remembered, the same proposal is not re-raised for 8 weeks
The brain NEVER applies a big change itself: only this command, run after the user says approve."""
import json, os, sys, datetime as dt
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "playbook", "brain"); FB = os.path.join(B, "..", "feedback.md")
DJ = os.path.join(B, "decisions.jsonl"); RT = os.path.join(B, "routing.json")
dec = [json.loads(l) for l in open(DJ) if l.strip()] if os.path.exists(DJ) else []
def save():
    open(DJ, "w").write("".join(json.dumps(d) + "\n" for d in dec))
today = dt.date.today().isoformat(); a = sys.argv[1:]
if not a: sys.exit(__doc__)
if a[0] == "add":
    new = 0
    for p in json.load(open(a[1])):
        if not p.get("big"): continue
        old = [d for d in dec if d["id"] == p["id"]]
        if old and (old[-1]["status"] == "pending" or (old[-1]["status"] == "declined" and (dt.date.fromisoformat(today) - dt.date.fromisoformat(old[-1]["date"])).days < 56) or old[-1]["status"] == "approved"): continue
        dec.append({"id": p["id"], "date": today, "status": "pending", "recommendation": p["recommendation"], "evidence": p["evidence"], "series": p.get("series"), "platform": p.get("platform"), "kind": p["kind"]}); new += 1
    save(); print("queued", new)
elif a[0] == "list":
    for d in dec:
        if d["status"] == "pending": print(d["id"], "|", d["recommendation"], "|", json.dumps(d["evidence"]))
elif a[0] in ("approve", "decline"):
    i = a[1]; note = a[2] if len(a) > 2 else ""
    hit = [d for d in dec if d["id"] == i and d["status"] == "pending"]
    if not hit: sys.exit("no pending decision " + i)
    d = hit[0]; d["status"] = "approved" if a[0] == "approve" else "declined"; d["date"] = today; d["note"] = note
    if a[0] == "approve":
        with open(FB, "a") as f:
            f.write(f"\n## {today} BRAIN DECISION {d['id']} (user approved, backed by data: {json.dumps(d['evidence'])})\n- {d['recommendation']}. {note}\n")
        if d["kind"] == "series_platform_weak" and d.get("series") and d.get("platform"):
            rt = json.load(open(RT)) if os.path.exists(RT) else {"skip_platforms": {}}
            rt["skip_platforms"].setdefault(d["series"], [])
            if d["platform"] not in rt["skip_platforms"][d["series"]]: rt["skip_platforms"][d["series"]].append(d["platform"])
            json.dump(rt, open(RT, "w"), indent=1)
    save(); print(d["status"], d["id"])
