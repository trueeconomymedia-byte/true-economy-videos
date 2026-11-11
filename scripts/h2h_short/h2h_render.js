// True Economy "Head to head" renderer. node h2h_render.js <build.json> <outdir> <slug>
// Writes <slug>-youtube-silent.mp4 (the one video for every platform), <slug>-beats-youtube.json,
// <slug>-thumb-tease.png, <slug>-thumb-answer.png. Frames go through the shared printed-ink finish (anim_shared/ink_pipe.py).
const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');
const fs=require('fs'),path=require('path');
const [,,dataPath,outdir,slug]=process.argv;
const INKDIR=path.join(__dirname,'..','anim_shared');
const D=JSON.parse(fs.readFileSync(dataPath,'utf8'));
const inkPng=(raw,out)=>{execFileSync('python3',['-c',`import sys;sys.path.insert(0,${JSON.stringify(INKDIR)});import numpy as np;from PIL import Image;from ink import Inker;a=np.asarray(Image.open(${JSON.stringify(raw)}).convert('RGBA'));Image.fromarray(Inker(1080,1920).compose(a)).save(${JSON.stringify(out)})`]);fs.unlinkSync(raw)};
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>{console.error('page error:',e.message);process.exit(1)});
 const VARS=(process.env.H2H_VARIANTS||'youtube').split(',');   // no cold open (user, 11 Nov 2026): the cover is picked by thumbnailOffset
 for(const [variant,cold] of [['auto',1],['youtube',0]].filter(v=>VARS.includes(v[0]))){
  await p.goto('file://'+path.join(__dirname,'h2h.html'));
  await p.evaluate(async()=>{await document.fonts.load('700 86px Lora');await document.fonts.load('800 54px Inter');await document.fonts.load('600 28px Inter');await document.fonts.ready});
  await p.evaluate(d=>BUILD(d),{...D,cold});
  const beats=await p.evaluate(()=>BEATS);
  fs.writeFileSync(path.join(outdir,`${slug}-beats-${variant}.json`),JSON.stringify(beats));
  if(variant==='youtube'){for(const [fn,nm] of [['tease','thumb-tease'],['answer','thumb-answer']]){
   await p.evaluate(f=>window[f](),fn);const out=path.join(outdir,`${slug}-${nm}.png`),raw=out+'.rgba.png';
   await p.screenshot({path:raw,omitBackground:true});inkPng(raw,out)}}
  const N=Math.round(beats.total*30),tmp=path.join(outdir,`${slug}-${variant}-silent.tmp.mp4`);
  const ff=spawn('python3',[path.join(INKDIR,'ink_pipe.py'),tmp],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<N;f++){await p.evaluate(t=>setTime(t),f/30);let buf=await p.screenshot({type:'png',omitBackground:true});
   const h=Buffer.alloc(4);h.writeUInt32BE(buf.length);buf=Buffer.concat([h,buf]);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
  ff.stdin.write(Buffer.alloc(4));ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));
  if(code!==0){console.error('encode failed',variant);process.exit(1)}
  fs.renameSync(tmp,path.join(outdir,`${slug}-${variant}-silent.mp4`));
  console.log('rendered',variant,beats.total.toFixed(2)+'s');
 }
 await b.close();
})();
