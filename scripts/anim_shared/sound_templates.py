"""True Economy Animated Shorts: SOUND TEMPLATES (user 23 Nov 2026: "automatically ... if I don't like it I'll ask you to
replace this certain sound template").

Every series keeps its own signature effects and reveal; what rotates is the MUSIC BED (key, tempo, chord order and the
piano pattern), so two videos never sound like the same template twice in a row. Same instruments throughout, so it
still sounds like one channel.

- TEMPLATES below = the named beds. A template the user dislikes is RETIRED in playbook/animated/sound_templates.json
  (move its name to that series' "retired" list, or to "retired_everywhere") and can be replaced by adding a new one here.
- playbook/animated/sound_templates.json = which templates each series may use, in rotation order.
- playbook/animated/sound_log.jsonl = one line per video: which template it used (so "I didn't like yesterday's sound"
  can be traced). The renderers write it; the daily task commits it with everything else.
- Rotation: the next template after the one this series used last; a re-render of the same slug keeps its template.
- Overrides for tests: TE_SOUND=<name> forces a template, TE_SOUND_NOLOG=1 does not write the log.
"""
import json, os, datetime
TEMPLATES = {
    # tr = semitones from the original A minor; prog = order of the four base chords (Am F C G shapes)
    "classic": {"label": "Classic (calm, sparse piano)",        "tr": 0,  "bpm": 96,  "prog": [0, 1, 2, 3], "motif": "sparse"},
    "bright":  {"label": "Bright (rolling piano, a bit faster)", "tr": 5,  "bpm": 108, "prog": [0, 1, 2, 3], "motif": "arp"},
    "deep":    {"label": "Deep (slow, low pads)",               "tr": -4, "bpm": 88,  "prog": [0, 3, 1, 3], "motif": "pads"},
    "steady":  {"label": "Steady (answering two-note piano)",   "tr": 2,  "bpm": 100, "prog": [0, 2, 3, 1], "motif": "call"},
}
BASE = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]   # Am F C G (MIDI)

def get(name, default="classic"):
    return dict(TEMPLATES.get(name) or TEMPLATES[default], name=name if name in TEMPLATES else default)

def make_mf(tpl):
    tr = tpl["tr"]; return lambda m: 440 * 2 ** ((m - 69 + tr) / 12)

def bed(tpl, add, padnote, epiano, softclick, DUR):
    """Write the music bed for this template onto the 'bed' bus (notes are given in A minor; mf transposes)."""
    mf = make_mf(tpl); beat = 60 / tpl["bpm"]; bar = 4 * beat; t = 0.0; ci = 0; motif = tpl["motif"]
    while t < DUR:
        ch = BASE[tpl["prog"][ci % 4]]
        for m in ch: add('bed', padnote(mf(m - 12), bar + 1.4), t, 0.05 if motif != "pads" else 0.065)
        add('bed', padnote(mf(ch[0] - 24), bar + 1.4) * 0.9, t, 0.07)
        if motif == "sparse":      # felt piano on beats 1, 3, 4 + soft 8th pulse (the original)
            for b, m in [(0, ch[-1] + 12), (2, ch[1] + 12), (3, ch[2] + 12)]:
                add('bed', epiano(mf(m), 2.2, 0.5), t + b * beat, 0.06, (-0.25 if b % 2 else 0.25))
            for e in range(8): add('bed', softclick(0.6 if e % 2 == 0 else 0.35), t + e * beat / 2, 0.05)
        elif motif == "arp":       # rolling 8th-note arpeggio + quarter pulse
            for e, m in enumerate([ch[0], ch[2], ch[3], ch[2], ch[1], ch[2], ch[3], ch[2]]):
                add('bed', epiano(mf(m), 1.6, 0.45), t + e * beat / 2, 0.045 if e % 2 else 0.06, (-0.3 if e % 2 else 0.3))
            for e in range(4): add('bed', softclick(0.5), t + e * beat, 0.035)
        elif motif == "pads":      # slow and low: one long low piano note a bar, half-time pulse
            add('bed', epiano(mf(ch[0]), 3.6, 0.6), t, 0.07, 0.0)
            add('bed', epiano(mf(ch[2]), 3.0, 0.45), t + 2 * beat, 0.045, 0.2)
            for e in range(2): add('bed', softclick(0.5), t + e * 2 * beat, 0.04)
        elif motif == "call":      # a two-note phrase that answers itself on beats 2 and 4
            for b, m in [(1, ch[-1] + 12), (1.5, ch[2] + 12), (3, ch[1] + 12), (3.5, ch[2] + 12)]:
                add('bed', epiano(mf(m), 1.8, 0.5), t + b * beat, 0.055, (0.3 if b < 2 else -0.3))
            for e in range(8): add('bed', softclick(0.55 if e % 4 == 0 else 0.3), t + e * beat / 2, 0.045)
        t += bar; ci += 1
    return mf

def _paths(root):
    p = os.path.join(root, "playbook", "animated"); return os.path.join(p, "sound_templates.json"), os.path.join(p, "sound_log.jsonl")

def pick(series, slug, root, default="classic"):
    """The template this video should use (rotation), and whether it is a new pick that should be logged."""
    forced = os.environ.get("TE_SOUND")
    if forced in TEMPLATES: return forced, False
    cfgp, logp = _paths(root)
    try: cfg = json.load(open(cfgp))
    except Exception: return default, False
    s = cfg.get("series", {}).get(series, {}); gone = set(s.get("retired", [])) | set(cfg.get("retired_everywhere", []))
    names = [n for n in s.get("templates", []) if n in TEMPLATES and n not in gone] or [default]
    last = None
    if os.path.exists(logp):
        for line in open(logp):
            try: e = json.loads(line)
            except Exception: continue
            if e.get("series") == series: last = e
    if last and last.get("slug") == slug and last.get("template") in names: return last["template"], False   # a re-render keeps its sound
    if last and last.get("template") in names: return names[(names.index(last["template"]) + 1) % len(names)], True
    return names[0], True

def apply(beats_path, series, slug, root, default="classic"):
    """Called by each series' renderer just before its sound is made: picks the template, writes it into the beats file
    and the sound log, and returns its name."""
    name, new = pick(series, slug, root, default)
    b = json.load(open(beats_path)); b["sound"] = name; json.dump(b, open(beats_path, "w"))
    if new and not os.environ.get("TE_SOUND_NOLOG"):
        with open(_paths(root)[1], "a") as f:
            f.write(json.dumps({"date": datetime.date.today().isoformat(), "series": series, "slug": slug, "template": name, "label": TEMPLATES[name]["label"]}) + "\n")
    print(f"sound template: {name} - {TEMPLATES[name]['label']}")
    return name
