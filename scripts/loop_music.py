#!/usr/bin/env python3
"""Find the best seamless loop (6-10 s) in a music track and render it.
usage: python3 loop_music.py track.mp3 out_loop.wav [out_info.json] [--min 6] [--max 10] [--fps 30]
Loop length is a whole number of video frames (1/fps s) so the video can be cut to exactly the same length.
Prints/saves JSON: file, start, length, score, tempo, energy, brightness, mode_minor_score."""
import sys, json, subprocess, argparse, os, tempfile
import numpy as np
from scipy.signal import stft, find_peaks
from scipy.io import wavfile

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("info", nargs="?")
ap.add_argument("--min", type=float, default=6.0); ap.add_argument("--max", type=float, default=10.0)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--at", help="start_s,length_s: render this loop without searching")
a = ap.parse_args()
SR = 44100

def decode(path):
    with tempfile.TemporaryDirectory() as t:
        w = os.path.join(t, "d.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "2", "-ar", str(SR), "-c:a", "pcm_f32le", w], check=True)
        sr, d = wavfile.read(w)
    return d.astype(np.float32)

x = decode(a.src)                     # (n, 2)
mono = x.mean(axis=1)
n = len(mono)
HOP = 1024
f, t, Z = stft(mono, fs=SR, nperseg=2048, noverlap=2048 - HOP, boundary=None, padded=False)
mag = np.abs(Z)                       # (freq, frames)
fps_f = SR / HOP                      # feature frames per second (~43)
# 40 log-spaced bands 40 Hz - 12 kHz
edges = np.geomspace(40, 12000, 41)
bands = np.stack([mag[(f >= edges[i]) & (f < edges[i + 1])].sum(axis=0) for i in range(40)])
L = np.log1p(bands * 20)              # log-compressed band energies
Lc = L - L.mean(axis=0, keepdims=True)  # remove per-frame level (shape only)
nrm = np.linalg.norm(Lc, axis=0) + 1e-6
Fn = Lc / nrm
rms = np.sqrt((mag ** 2).mean(axis=0))

# ---- tempo / beats from spectral flux autocorrelation
flux = np.maximum(0, np.diff(L, axis=1)).sum(axis=0)
flux = np.concatenate([[0], flux]); flux = flux - np.convolve(flux, np.ones(21) / 21, "same")
flux[flux < 0] = 0
ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
lo, hi = int(fps_f * 60 / 180), int(fps_f * 60 / 60)      # 60-180 bpm
lag = lo + int(np.argmax(ac[lo:hi]))
# refine, and fold to 80-160 bpm if needed
bpm = 60 * fps_f / lag
while bpm < 80: bpm *= 2
while bpm > 160: bpm /= 2
beat = 60.0 / bpm                                          # seconds
# beat phase: best offset of a comb on the flux
fb = beat * fps_f
offs = np.arange(0, fb, 0.25)
phase = max(offs, key=lambda o: sum(flux[int(i)] for i in np.arange(o, len(flux) - 1, fb)))
phase_s = phase / fps_f

# ---- candidates
W = int(0.5 * fps_f)                                       # comparison window 0.5 s
dur = n / SR
starts = np.arange(phase_s + beat * 2, min(dur * 0.6, dur - a.max - 1), beat)   # beat-aligned starts
starts = [s for s in starts if s > 0.3 and rms[int(s * fps_f)] > 0.35 * np.median(rms)]
lens = np.arange(int(round(a.min * a.fps)), int(round(a.max * a.fps)) + 1) / a.fps
best = None
for s in starts:
    si = int(round(s * fps_f))
    if si - W < 0: continue
    for Ls in lens:
        ei = int(round((s + Ls) * fps_f))
        if ei + W >= Fn.shape[1]: continue
        pre = (Fn[:, si - W:si] * Fn[:, ei - W:ei]).sum(0).mean()      # what leads into the join vs the start
        post = (Fn[:, si:si + W] * Fn[:, ei:ei + W]).sum(0).mean()     # what follows the join vs the start
        lev = abs(np.log(rms[ei - W:ei].mean() + 1e-6) - np.log(rms[si - W:si].mean() + 1e-6))
        bars = Ls / (4 * beat)
        grid = abs(bars - round(bars)) * 4 * beat if round(bars) >= 1 else 4 * beat   # distance (s) from a whole number of bars
        beats = Ls / beat; gridb = abs(beats - round(beats)) * beat
        score = 0.5 * pre + 0.5 * post - 0.4 * lev - 0.6 * min(grid, 1.0) * 0.5 - 0.6 * min(gridb, 0.5)
        if best is None or score > best[0]:
            best = (score, s, Ls, pre, post, lev, gridb)
if a.at:
    s, Ls = [float(v) for v in a.at.split(",")]; score = pre = post = lev = gridb = 0.0
else:
    if best is None:
        sys.exit("no usable loop found")
    score, s, Ls, pre, post, lev, gridb = best

# ---- render with equal-power crossfade of the tail into the audio that precedes the start
nL = int(round(Ls * SR)); s0 = int(round(s * SR))
X = int(0.06 * SR)
seg = x[s0:s0 + nL].copy()
if s0 - X >= 0 and len(seg) == nL:
    ph = np.linspace(0, np.pi / 2, X)[:, None]
    seg[-X:] = seg[-X:] * np.cos(ph) + x[s0 - X:s0] * np.sin(ph)
seg *= 10 ** (-1.0 / 20)                    # 1 dB headroom
fi = int(0.004 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None] ** 0.5  # tiny anti-click only; loop join already blended
wavfile.write(a.out, SR, (np.clip(seg, -1, 1) * 32767).astype(np.int16))

# ---- simple descriptors (for matching a track to the day's mood)
cent = float((f[:, None] * mag).sum() / (mag.sum() + 1e-9))
chroma = np.zeros(12)
for k in range(1, len(f)):
    if 60 < f[k] < 2000:
        pc = int(round(12 * np.log2(f[k] / 440.0) + 9)) % 12
        chroma[pc] += mag[k].sum()
maj = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
mnr = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
cm = max(np.corrcoef(np.roll(maj, r), chroma)[0, 1] for r in range(12))
cn = max(np.corrcoef(np.roll(mnr, r), chroma)[0, 1] for r in range(12))
info = {"file": os.path.basename(a.src), "start_s": round(float(s), 3), "length_s": round(float(Ls), 4),
        "frames": int(round(Ls * a.fps)), "score": round(float(score), 3), "tempo_bpm": round(float(bpm), 1),
        "energy": round(float(rms.mean()), 3), "brightness_hz": round(cent), "minor_minus_major": round(float(cn - cm), 3),
        "join_similarity": round(float((pre + post) / 2), 3), "beat_grid_miss_s": round(float(gridb), 3)}
print(json.dumps(info))
if a.info: json.dump(info, open(a.info, "w"))
