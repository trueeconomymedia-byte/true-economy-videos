#!/usr/bin/env python3
"""BAR GRAIN (user-approved option, 21 Nov 2026): soft, compression-safe film grain INSIDE solid-coloured bars of a static card video.
Only the bars move (grain); text, paper, banner and the other bars stay still. First frame ~ last frame (seamless loop).
Why it survives platform re-encodes: brightness-only (no colour noise), soft/clumpy (gaussian-blurred), +-10 levels, and a NEW pattern only every 3rd frame (10/s).
Tested at a harsh 1.5 Mbps re-encode: no blocking or flicker.
usage: python3 -I bar_grain.py IN.mp4 OUT.mp4 AUDIO.wav "x,y,w,h;x,y,w,h" [amp=10] [hold=3] [sigma=2.2]
  IN.mp4  = the finished static 4K card video (video_card.py output, 2160x3840); rects = bars in CARD CANVAS units (948x1300; 4K px = 132+2x, 620+2y).
  Pick which bars get grain (usually the focal / current-period bars; light context bars stay still). Re-encode result with crf 24 as usual."""
import sys, subprocess, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
inp, outp, audio, rs = sys.argv[1:5]
amp = float(sys.argv[5]) if len(sys.argv) > 5 else 10.0
HOLD = int(sys.argv[6]) if len(sys.argv) > 6 else 3
sig = float(sys.argv[7]) if len(sys.argv) > 7 else 2.2
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", inp, "-frames:v", "1", "/tmp/_bg_base.png"], check=True)
base = np.array(Image.open("/tmp/_bg_base.png").convert("RGB")).astype(np.float32); H4, W4 = base.shape[:2]
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", inp]))
N = round(dur * 30)
boxes = []
for r in rs.split(";"):
    x, y, w, h = [float(v) for v in r.split(",")]
    boxes.append((int(132 + 2 * x) + 2, int(620 + 2 * y) + 2, int(132 + 2 * (x + w)) - 2, int(620 + 2 * (y + h)) - 2))
rng = np.random.default_rng(11)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W4}x{H4}", "-r", "30", "-i", "-", "-i", audio,
                      "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", outp], stdin=subprocess.PIPE)
for f in range(N):
    if f % HOLD == 0:
        noise = []
        for (x0, y0, x1, y1) in boxes:
            g = gaussian_filter(rng.standard_normal((y1 - y0, x1 - x0)).astype(np.float32), sig); g /= g.std(); noise.append(g * amp)
    fr = base.copy()
    for (x0, y0, x1, y1), g in zip(boxes, noise): fr[y0:y1, x0:x1] += g[..., None]
    p.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("done", N, "frames")
