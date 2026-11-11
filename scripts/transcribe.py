#!/usr/bin/env python3
"""True Economy: word-level transcript of a clip (for captions.py).
Usage: python3 transcribe.py CLIP OUT_words.json [--model small.en] [--prompt "60/40, S&P 500, Federal Reserve"]
Writes [{"w": word, "s": start_s, "e": end_s}, ...] and a draft phrase file OUT_words.draft.json
(2-5 words, <= 24 characters, split at punctuation and pauses) for the run to review and mark.
Needs: pip install --break-system-packages faster-whisper ; model download from huggingface.co (must be an allowed domain)."""
import sys, json, subprocess, tempfile, os
a=sys.argv[1:]
def opt(n,d):
    if n in a:
        i=a.index(n); v=a[i+1]; del a[i:i+2]; return v
    return d
model=opt('--model','small.en'); prompt=opt('--prompt','')
clip,out=a[0],a[1]
wav=os.path.join(tempfile.mkdtemp(),'a.wav')
subprocess.run(['ffmpeg','-v','error','-y','-i',clip,'-ac','1','-ar','16000',wav],check=True)
import wave, numpy as np
with wave.open(wav) as wf: audio=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768.0  # pass samples, not a path (avoids PyAV version issues)
from faster_whisper import WhisperModel
m=WhisperModel(model,device='cpu',compute_type='int8')
segs,_=m.transcribe(audio,word_timestamps=True,initial_prompt=prompt or None,vad_filter=True)
words=[]
for s in segs:
    for w in s.words:
        t=w.word.strip()
        if not t: continue
        if words and t[0] in '-&/%' and w.start-words[-1]['e']<0.3:   # rejoin split tokens: 60/40, S&P, 10-year
            words[-1]['w']+=t; words[-1]['e']=round(w.end,2); continue
        words.append({'w':t,'s':round(w.start,2),'e':round(w.end,2)})
json.dump(words,open(out,'w'),indent=0)
# draft phrases
ph=[];cur=[]
def flush():
    global cur
    if cur: ph.append({'text':' '.join(x['w'] for x in cur),'mark':'','start':cur[0]['s'],'end':cur[-1]['e']}); cur=[]
for i,w in enumerate(words):
    if cur and (len(' '.join(x['w'] for x in cur+[w]))>24 or len(cur)>=5 or w['s']-cur[-1]['e']>0.35): flush()
    cur.append(w)
    if w['w'][-1] in '.,?!;:': flush()
flush()
json.dump({'phrases':ph},open(out.replace('.json','')+'.draft.json','w'),indent=1)
print('words',len(words),'phrases',len(ph))
print(' '.join(x['w'] for x in words))
