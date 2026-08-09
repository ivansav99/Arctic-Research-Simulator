(()=>{
'use strict';
const parts=[
  'exp23-runtime-parts/exp23-00.txt',
  'exp23-runtime-parts/exp23-01.txt',
  'exp23-runtime-parts/exp23-02.txt',
  'exp23-runtime-parts/exp23-03.txt',
  'exp23-runtime-parts/exp23-04.txt'
];
Promise.all(parts.map(path=>fetch(path+'?v=expedition-23',{cache:'no-store'}).then(response=>{
  if(!response.ok)throw new Error(`Failed to load ${path}: ${response.status}`);
  return response.text();
}))).then(chunks=>(0,eval)(chunks.join(''))).catch(error=>{
  console.error('[ARS] Expedition 23 runtime loader failed',error);
  fetch('game.js?v=expedition-21-emergency',{cache:'no-store'}).then(r=>r.text()).then(code=>(0,eval)(code));
});
})();
