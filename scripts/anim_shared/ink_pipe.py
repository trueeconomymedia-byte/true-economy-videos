#!/usr/bin/env python3
"""Streams RGBA PNG frames (4-byte big-endian length + PNG bytes on stdin) through the printed-ink finish (ink.py)
and encodes them with ffmpeg. Usage: ink_pipe.py OUT.mp4 [W H FPS]. A zero-length record ends the stream."""
import sys, os, struct, subprocess, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ink import Inker
out = sys.argv[1]; W, H, FPS = (int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]) if len(sys.argv) > 4 else (1080, 1920, "30")
ink = Inker(W, H)
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", FPS, "-i", "-",
                       "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
inp = sys.stdin.buffer; n = 0
while True:
    hdr = inp.read(4)
    if len(hdr) < 4: break
    ln = struct.unpack(">I", hdr)[0]
    if ln == 0: break
    buf = inp.read(ln)
    bgra = cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_UNCHANGED)
    rgba = cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGBA)
    ff.stdin.write(ink.compose(rgba).tobytes()); n += 1
ff.stdin.close(); code = ff.wait()
print(f"ink_pipe: {n} frames, ffmpeg exit {code}", file=sys.stderr); sys.exit(code)
