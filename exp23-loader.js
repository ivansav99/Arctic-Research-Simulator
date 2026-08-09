(()=>{
'use strict';
const BASE_SHA='eb04e98d1a9ca1835a5f626971cfcdcd77ada22114517db81a156ff8de9ff37e';
const FINAL_SHA='8ce4eac44538684a4256629951dc851f5df21b52e8ce6e589d09e8acce6e9a3f';
const PARTS=[0,1,2,3].map(i=>`runtime/exp23-final-0${i}.b64?v=23`);
const sha256=async text=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))).map(b=>b.toString(16).padStart(2,'0')).join('');
function applyFilePatch(base,patch,file='game.js'){
  const marker=`diff --git a/${file} b/${file}`;
  const start=patch.indexOf(marker);if(start<0)throw new Error(`Patch section missing: ${file}`);
  const next=patch.indexOf('\ndiff --git ',start+marker.length);
  const section=patch.slice(start,next<0?patch.length:next),p=section.split('\n'),src=base.split('\n'),out=[];
  let srcPos=0,i=0;
  while(i<p.length){
    const m=p[i].match(/^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/);
    if(!m){i++;continue;}
    const oldStart=Number(m[1])-1;
    while(srcPos<oldStart)out.push(src[srcPos++]);
    i++;
    while(i<p.length&&!p[i].startsWith('@@ ')&&!p[i].startsWith('diff --git ')){
      const line=p[i];
      if(line.startsWith(' ')){const val=line.slice(1);if(src[srcPos]!==val)throw new Error(`Patch context mismatch at ${srcPos+1}`);out.push(src[srcPos++]);}
      else if(line.startsWith('-')){const val=line.slice(1);if(src[srcPos]!==val)throw new Error(`Patch delete mismatch at ${srcPos+1}`);srcPos++;}
      else if(line.startsWith('+'))out.push(line.slice(1));
      else if(line.startsWith('\\ No newline')){}
      i++;
    }
  }
  while(srcPos<src.length)out.push(src[srcPos++]);
  return out.join('\n');
}
async function decodePatch(b64){
  const raw=atob(b64),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
  if(typeof DecompressionStream!=='function')throw new Error('Browser gzip decompression unavailable');
  const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  return await new Response(stream).text();
}
(async()=>{
  const [base,...parts]=await Promise.all([
    fetch('game.js?v=expedition-21-base',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('Base game load failed');return r.text();}),
    ...PARTS.map(url=>fetch(url,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`Patch part load failed: ${url}`);return r.text();}))
  ]);
  const baseHash=await sha256(base);if(baseHash!==BASE_SHA)throw new Error(`Base SHA mismatch ${baseHash}`);
  const patch=await decodePatch(parts.join('').replace(/\s+/g,''));
  const code=applyFilePatch(base,patch,'game.js');
  const finalHash=await sha256(code);if(finalHash!==FINAL_SHA)throw new Error(`Final SHA mismatch ${finalHash}`);
  (0,eval)(code);
  console.info('[ARS] Expedition 23 verified runtime build loaded');
})().catch(async error=>{
  console.error('[ARS] Expedition 23 loader failed; loading stable base',error);
  try{const code=await fetch('game.js?v=expedition-21-fallback',{cache:'no-store'}).then(r=>r.text());(0,eval)(code);}catch(fallbackError){console.error('[ARS] fallback failed',fallbackError);}
});
})();
