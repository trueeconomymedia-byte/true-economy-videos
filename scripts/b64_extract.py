#!/usr/bin/env python3
"""Decode the base64 file content from a saved Drive download_file_content result. usage: b64_extract.py saved_result_file out.mp3"""
import sys, json, base64, re
raw = open(sys.argv[1], "rb").read().decode("utf-8", "ignore")
best = ""
def walk(o):
    global best
    if isinstance(o, str):
        if len(o) > len(best) and re.fullmatch(r"(data:[^,]*,)?[A-Za-z0-9+/_=\s-]+", o): best = o
        try: walk(json.loads(o))
        except Exception: pass
    elif isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
try: walk(json.loads(raw))
except Exception: pass
if len(best) < 1000:
    m = max(re.findall(r"[A-Za-z0-9+/_=-]{1000,}", raw), key=len, default="")
    best = m
best = re.sub(r"^data:[^,]*,", "", best).strip()
best = best.replace("-", "+").replace("_", "/")
best += "=" * (-len(best) % 4)
data = base64.b64decode(best)
open(sys.argv[2], "wb").write(data)
print("wrote", sys.argv[2], len(data), "bytes", "ID3/MP3 ok" if data[:3] == b"ID3" or data[:2] == b"\xff\xfb" else "WARNING: header", data[:4])
