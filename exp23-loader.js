(()=>{
'use strict';
const BUILD='expedition-24';
const PARTS=[0,1,2,3].map(i=>`runtime/exp23-final-0${i}.b64?v=24`);
const svgData=svg=>'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(svg);
window.AR_ICEBREAKER_ART_DATA={
  icebreaker:svgData(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 256"><defs><filter id="s"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#031923" flood-opacity=".65"/></filter><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f34f3d"/><stop offset="1" stop-color="#a91818"/></linearGradient></defs><g filter="url(#s)"><path d="M64 5C86 20 99 49 102 94l5 104-17 45H38l-17-45 5-104C29 49 42 20 64 5Z" fill="#162e3a"/><path d="M64 12C82 28 92 54 94 96l4 96-14 39H44l-14-39 4-96C36 54 46 28 64 12Z" fill="url(#h)"/><path d="M64 21C75 34 82 57 83 91l3 85H42l3-85c1-34 8-57 19-70Z" fill="#f7fbfc"/><path d="M43 107h42l1 46H42Z" fill="#e9f1f3"/><rect x="48" y="76" width="32" height="19" rx="3" fill="#315b6c"/><g fill="#8bd3ec"><rect x="51" y="80" width="8" height="7" rx="1"/><rect x="61" y="80" width="8" height="7" rx="1"/><rect x="71" y="80" width="6" height="7" rx="1"/></g><path d="M52 63h24l5 13H47Z" fill="#dde9ed"/><rect x="61" y="46" width="6" height="19" fill="#253f4a"/><path d="M64 45 78 54" stroke="#253f4a" stroke-width="3"/><circle cx="64" cy="202" r="20" fill="#dce9ec" stroke="#f2c84b" stroke-width="3"/><path d="M55 193v18m18-18v18M55 202h18" stroke="#f2c84b" stroke-width="4" stroke-linecap="round"/><path d="M37 101 25 117m66-16 12 16" stroke="#f7fbfc" stroke-width="4" stroke-linecap="round"/><path d="M42 159h44" stroke="#a7bec6" stroke-width="3"/><path d="M64 12 55 38h18Z" fill="#f7fbfc" opacity=".85"/></g></svg>`),
  nuclear:svgData(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 256"><defs><filter id="s"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#031923" flood-opacity=".7"/></filter><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ef4037"/><stop offset=".58" stop-color="#c51f24"/><stop offset="1" stop-color="#761219"/></linearGradient></defs><g filter="url(#s)"><path d="M64 3C90 20 105 50 108 92l7 106-20 48H33l-20-48 7-106C23 50 38 20 64 3Z" fill="#102d3a"/><path d="M64 10C86 27 97 54 100 96l6 98-17 40H39l-17-40 6-98C31 54 42 27 64 10Z" fill="url(#h)"/><path d="M64 18C79 35 87 61 88 101l2 66H38l2-66c1-40 9-66 24-83Z" fill="#f6fafb"/><path d="M41 101h46l2 58H39Z" fill="#edf4f6"/><path d="M47 62h34l8 38H39Z" fill="#dfeaec"/><rect x="48" y="75" width="32" height="18" rx="3" fill="#254a5c"/><g fill="#9ce0f5"><rect x="51" y="79" width="7" height="7"/><rect x="60" y="79" width="7" height="7"/><rect x="69" y="79" width="8" height="7"/></g><rect x="61" y="38" width="7" height="25" fill="#233c49"/><path d="M64 38 82 49" stroke="#233c49" stroke-width="4"/><circle cx="64" cy="204" r="24" fill="#dce9ec" stroke="#ffd34d" stroke-width="4"/><path d="M53 193v22m22-22v22M53 204h22" stroke="#ffd34d" stroke-width="5" stroke-linecap="round"/><path d="M38 171h52" stroke="#a5bcc5" stroke-width="3"/><path d="M34 112 20 126m74-14 14 14" stroke="#f7fbfc" stroke-width="5" stroke-linecap="round"/><path d="M64 10 52 42h24Z" fill="#fff" opacity=".9"/><path d="M29 95 18 108m81-13 11 13" stroke="#f7d24a" stroke-width="3"/></g></svg>`)
};
function showFatal(error){
  console.error('[ARS] Expedition 24 failed to load',error);
  const box=document.createElement('div');
  box.style.cssText='position:fixed;z-index:99999;left:16px;right:16px;top:16px;padding:14px 16px;background:#5b1117;color:#fff;border:2px solid #ff8f92;border-radius:10px;font:700 14px/1.4 system-ui,sans-serif;box-shadow:0 6px 30px #0008';
  box.textContent='ARS Expedition 24 failed to load. Hard-refresh the page. '+(error?.message||error);
  document.body.appendChild(box);
}
function findSeq(src,seq,guess){
  if(!seq.length)return Math.max(0,Math.min(src.length,guess));
  const matchesAt=i=>{if(i<0||i+seq.length>src.length)return false;for(let j=0;j<seq.length;j++)if(src[i+j]!==seq[j])return false;return true;};
  for(let d=0;d<=300;d++){if(matchesAt(guess+d))return guess+d;if(d&&matchesAt(guess-d))return guess-d;}
  for(let i=0;i<=src.length-seq.length;i++)if(matchesAt(i))return i;
  return -1;
}
function applyFilePatch(base,patch,file='game.js'){
  const marker=`diff --git a/${file} b/${file}`;
  const start=patch.indexOf(marker);if(start<0)throw new Error(`Patch section missing: ${file}`);
  const next=patch.indexOf('\ndiff --git ',start+marker.length);
  const lines=patch.slice(start,next<0?patch.length:next).split('\n');
  let src=base.replace(/\r\n/g,'\n').split('\n'),offset=0,i=0,hunks=0;
  while(i<lines.length){
    const m=lines[i].match(/^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/);
    if(!m){i++;continue;}
    const oldStart=Number(m[1])-1,oldSeq=[],newSeq=[];i++;
    while(i<lines.length&&!lines[i].startsWith('@@ ')&&!lines[i].startsWith('diff --git ')){
      const line=lines[i];
      if(line.startsWith(' ')){oldSeq.push(line.slice(1));newSeq.push(line.slice(1));}
      else if(line.startsWith('-'))oldSeq.push(line.slice(1));
      else if(line.startsWith('+'))newSeq.push(line.slice(1));
      i++;
    }
    const guess=oldStart+offset,pos=findSeq(src,oldSeq,guess);
    if(pos<0)throw new Error(`Patch hunk ${hunks+1} did not match near line ${oldStart+1}`);
    src.splice(pos,oldSeq.length,...newSeq);offset+=newSeq.length-oldSeq.length;hunks++;
  }
  if(!hunks)throw new Error('No Expedition 23 game hunks found');
  return src.join('\n');
}
async function decodePatch(b64){
  if(typeof DecompressionStream!=='function')throw new Error('This browser lacks DecompressionStream');
  const raw=atob(b64),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
  return await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
}
(async()=>{
  const [base,...parts]=await Promise.all([
    fetch('game.js?v=expedition-24-base',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`Base game HTTP ${r.status}`);return r.text();}),
    ...PARTS.map(url=>fetch(url,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`Patch HTTP ${r.status}: ${url}`);return r.text();}))
  ]);
  const patch=await decodePatch(parts.join('').replace(/\s+/g,''));
  let code=applyFilePatch(base,patch,'game.js');
  const artRE=/icebreaker:atlasSprite\(127,6,38,64\),\s*nuclear:atlasSprite\(127,6,38,64\)/;
  if(!artRE.test(code))throw new Error('Icebreaker sprite hook not found');
  code=code.replace(artRE,"icebreaker:{image:loadSprite(window.AR_ICEBREAKER_ART_DATA.icebreaker),sx:0,sy:0,sw:128,sh:256},\n      nuclear:{image:loadSprite(window.AR_ICEBREAKER_ART_DATA.nuclear),sx:0,sy:0,sw:128,sh:256}");
  code=code.replace("const GAME_VERSION='expedition-23'","const GAME_VERSION='expedition-24'");
  for(const token of ["GAME_VERSION='expedition-24'",'getIceTexturePattern','carveIcebreakerTrack','AR_ICEBREAKER_ART_DATA.icebreaker'])if(!code.includes(token))throw new Error(`Build verification failed: ${token}`);
  document.documentElement.dataset.arsVersion=BUILD;
  (0,eval)(code+'\n//# sourceURL=ars-expedition-24.js');
  console.info('[ARS] Expedition 24 loaded: textured sea ice + distinct icebreaker art');
})().catch(showFatal);
})();
