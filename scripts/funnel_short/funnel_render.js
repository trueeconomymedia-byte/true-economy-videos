// True Economy funnel Short renderer.
// node funnel_render.js <data.json> <outdir> <slug>
// Writes: <slug>-funnel-auto.mp4 (cold open: full chart first, for Buffer), <slug>-funnel-youtube.mp4 (starts on the hook),
//         <slug>-thumb-tease.png, <slug>-thumb-answer.png, <slug>-beats-auto.json, <slug>-beats-youtube.json (silent videos;
//         funnel_short.py adds the sound).
const {chromium}=require('playwright');const {spawn}=require('child_process');
const fs=require('fs'),path=require('path');
const [,,dataPath,outdir,slug]=process.argv;
const HERE=__dirname, ASSETS=path.join(HERE,'..','assets'), INKDIR=path.join(HERE,'..','anim_shared');
const D=JSON.parse(fs.readFileSync(dataPath,'utf8'));
const b64=(p,mime)=>`data:${mime};base64,`+fs.readFileSync(p).toString('base64');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 // the shared Animated Shorts background (identical for every series)
 const {tex1,tex2}=await require('../anim_shared/background.js').textures(p);
 // optional logo: data.logo path, else scripts/assets/logos/<company-slug>.(png|svg)
 let logo=null;const cs=String(D.logo_key||'none').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
 for(const c of [D.logo,path.join(ASSETS,'logos',cs+'.png'),path.join(ASSETS,'logos',cs+'.svg')]){
  if(c&&fs.existsSync(c)){logo=b64(c,c.endsWith('.svg')?'image/svg+xml':'image/png');break}}
 const url='file://'+path.join(HERE,'funnel.html');
 const VARS=(process.env.FUNNEL_VARIANTS||'auto,youtube').split(',');
 for(const [variant,cold] of [['auto',1],['youtube',0]].filter(v=>VARS.includes(v[0]))){
  await p.goto(url);await p.waitForTimeout(300);
  // fonts must be loaded BEFORE building: the headline marker and the title fit are measured from the real glyphs
  await p.evaluate(async()=>{await document.fonts.load('700 86px Lora');await document.fonts.load('800 54px Inter');await document.fonts.load('600 28px Inter');await document.fonts.ready});
  const INK=!!D.ink;   // printed-ink finish on the supplied card paper (scripts/anim_shared/ink.py)
  await p.evaluate(d=>BUILD(d),{...D,tex1,tex2,logo,cold,...(INK?{bg_image:'none'}:{})});
  if(INK)await p.evaluate(()=>{for(const e of [document.documentElement,document.body,document.getElementById('stage')])e.style.background='transparent'});
  await p.waitForTimeout(300);
  const beats=await p.evaluate(()=>BEATS);
  fs.writeFileSync(path.join(outdir,`${slug}-beats-${variant}.json`),JSON.stringify(beats));
  if(variant==='auto'){
   for(const [fn,nm] of [['tease','thumb-tease'],['answer','thumb-answer']]){
    await p.evaluate(f=>window[f](),fn);const out=path.join(outdir,`${slug}-${nm}.png`);
    if(!INK){await p.screenshot({path:out});continue}
    const raw=out+'.rgba.png';await p.screenshot({path:raw,omitBackground:true});
    require('child_process').execFileSync('python3',['-c',`import sys;sys.path.insert(0,'${INKDIR}');import numpy as np;from PIL import Image;from ink import Inker;a=np.asarray(Image.open('${raw}').convert('RGBA'));Image.fromarray(Inker(1080,1920).compose(a)).save('${out}')`]);fs.unlinkSync(raw);}
  }
  const N=Math.round(beats.total*30), tmp=path.join(outdir,`${slug}-${variant}-silent.tmp.mp4`);
  const ff=INK?spawn('python3',[path.join(INKDIR,'ink_pipe.py'),tmp],{stdio:['pipe','inherit','inherit']})
   :spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','17','-preset','veryfast','-pix_fmt','yuv420p',tmp],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<N;f++){await p.evaluate(t=>setTime(t),f/30);
   let buf=INK?await p.screenshot({type:'png',omitBackground:true}):await p.screenshot({type:'jpeg',quality:92});
   if(INK){const h=Buffer.alloc(4);h.writeUInt32BE(buf.length);buf=Buffer.concat([h,buf]);}
   if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
  if(INK)ff.stdin.write(Buffer.alloc(4));
  ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));
  if(code!==0){console.error('ffmpeg failed',variant);process.exit(1)}
  fs.renameSync(tmp,path.join(outdir,`${slug}-${variant}-silent.mp4`));
  console.log('rendered',variant,beats.total.toFixed(2)+'s',logo?'with logo':'no logo');
 }
 await b.close();
})();
