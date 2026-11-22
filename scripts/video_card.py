#!/usr/bin/env python3
"""Entry point used by the Daily Post and Markets Daily tasks (same command as always: python3 -I video_card.py chart.svg out.mp4 <bg>).
Picks the card look from playbook/style.json ("daily_card_style": "flat" = default since 22 Nov 2026, the Animated Shorts paper background with no banner / cut-paper edge;
"legacy" = the previous look: black banner + torn paper + topic background, scripts/video_card_legacy.py). Env CARD_STYLE=flat|legacy overrides the file.
Stock Market Today does not use this script (video_mkts.py)."""
import os, sys, json, runpy
here = os.path.dirname(os.path.abspath(__file__))
style = os.environ.get("CARD_STYLE", "")
if not style:
    for p in (os.path.join(here, "..", "playbook", "style.json"), "/tmp/tev/playbook/style.json"):
        if os.path.exists(p):
            try: style = json.load(open(p)).get("daily_card_style", ""); break
            except Exception: pass
style = style if style in ("flat", "legacy") else "flat"
target = os.path.join(here, "video_card_flat.py" if style == "flat" else "video_card_legacy.py")
if not os.path.exists(target): target = os.path.join("/tmp/tev/scripts", os.path.basename(target))
print("card style:", style, flush=True)
runpy.run_path(target, run_name="__main__")
