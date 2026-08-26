from pathlib import Path


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text()
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    p.write_text(text.replace(old,new,1))

# 1. Use the four approved vessel drawings; keep both F/V photos untouched.
replace_once(
    'expedition.js',
    """  const VESSEL_IMAGES = {
    coastal:'assets/vessels/fishing-trawler.webp',
    global:'assets/vessels/noaa-rv-brown.webp',
    icebreaker:'https://commons.wikimedia.org/wiki/Special:FilePath/Polarforskningssekretariatet%20IMG%202551%20Oden%20Hjorthfjellet.jpg',
    nuclear:'https://commons.wikimedia.org/wiki/Special:FilePath/50%20Let%20Pobedy.jpg'
  };""",
    """  const VESSEL_IMAGES = {
    coastal:'assets/vessels/coastal-rv.webp?v=23x',
    global:'assets/vessels/global-rv.webp?v=23x',
    icebreaker:'assets/vessels/icebreaker.webp?v=23x',
    nuclear:'assets/vessels/nuclear-icebreaker.webp?v=23x'
  };""",
    'approved vessel image mapping'
)

# 2. Make WebAudio unlock visibly/audibly verifiable on the first user gesture.
replace_once(
    'game.js',
    "    let ac=null,waveSource=null,waveGain=null,lastCrack=0,lastAnimal=0;",
    "    let ac=null,waveSource=null,waveGain=null,lastCrack=0,lastAnimal=0,unlockChimed=false;",
    'sound unlock state'
)
replace_once(
    'game.js',
    "    const unlock=()=>{const c=ensure();if(c?.state==='suspended')c.resume();};",
    "    const unlock=()=>{const c=ensure();if(!c)return;const confirm=()=>{if(unlockChimed||c.state!=='running')return;unlockChimed=true;tone(660,.10,.10,0,'sine');tone(880,.14,.09,.10,'sine');};if(c.state==='suspended'){const resumed=c.resume();if(resumed&&typeof resumed.then==='function')resumed.then(confirm).catch(()=>{});else confirm();}else confirm();};",
    'sound unlock implementation'
)
replace_once(
    'game.js',
    """  document.addEventListener('pointerdown',()=>sound.unlock(),{capture:true,passive:true});
  document.addEventListener('keydown',()=>sound.unlock(),{capture:true});""",
    """  document.addEventListener('pointerdown',()=>sound.unlock(),{capture:true,passive:true});
  document.addEventListener('touchstart',()=>sound.unlock(),{capture:true,passive:true});
  document.addEventListener('click',()=>sound.unlock(),{capture:true,passive:true});
  document.addEventListener('keydown',()=>sound.unlock(),{capture:true});""",
    'global audio unlock events'
)

# 3. The minimap itself is clipped round already; replace the square main-map
# viewport marker with a true circular footprint and fill the circular canvas.
replace_once(
    'game.js',
    "const c=size/2,radius=size*.45,geometry=miniMapGeometry(),worldRadius=geometry.worldRadius;",
    "const c=size/2,radius=size*.5-2,geometry=miniMapGeometry(),worldRadius=geometry.worldRadius;",
    'minimap circle radius'
)
replace_once(
    'game.js',
    "const viewW=Math.min(radius*2,width/scale/worldRadius*radius),viewH=Math.min(radius*2,height/scale/worldRadius*radius);mini.strokeStyle='rgba(255,243,164,.68)';mini.lineWidth=.8;mini.strokeRect(p.x-viewW/2,p.y-viewH/2,viewW,viewH);",
    "const viewRadius=Math.min(radius-3,Math.max(4,Math.min(width,height)/(2*scale*worldRadius)*radius));mini.strokeStyle='rgba(255,243,164,.72)';mini.lineWidth=1;mini.beginPath();mini.arc(p.x,p.y,viewRadius,0,Math.PI*2);mini.stroke();",
    'round visible-map footprint'
)

# 4. Publication language and mobile Research attention: Article = gold.
replace_once(
    'expedition.js',
    "${level&&!level.next?'AUTO-PUBLISH READY':'PUBLISH PAPER'}",
    "${level&&!level.next?'AUTO-PUBLISH READY':level?`PUBLISH ${level.label.toUpperCase()}`:'PUBLISH LETTER'}",
    'publication button wording'
)
replace_once(
    'expedition.js',
    "const researchToggle=root.querySelector('#arx-mobile-toggle'); researchToggle?.classList.toggle('attention',!!level&&!!level.next&&state.publicationCooldown<=0);",
    "const researchToggle=root.querySelector('#arx-mobile-toggle');const articleReady=state.data>=1000&&state.publicationCooldown<=0;researchToggle?.classList.toggle('attention',false);researchToggle?.classList.toggle('article-ready',articleReady);",
    'article-ready research button'
)
replace_once(
    'expedition.js',
    "#arx-mobile-toggle.attention{border-color:#8ef0cf!important;background:rgba(28,105,85,.96)!important;color:#ecfff8!important;box-shadow:0 0 0 2px rgba(142,240,207,.14),0 0 22px rgba(142,240,207,.48)!important}",
    "#arx-mobile-toggle.attention{border-color:#8ef0cf!important;background:rgba(28,105,85,.96)!important;color:#ecfff8!important;box-shadow:0 0 0 2px rgba(142,240,207,.14),0 0 22px rgba(142,240,207,.48)!important}#arx-mobile-toggle.article-ready{border-color:#f6d365!important;background:rgba(125,91,22,.97)!important;color:#fff6c7!important;box-shadow:0 0 0 2px rgba(246,211,101,.18),0 0 24px rgba(246,211,101,.55)!important}.arx-store-details[data-arx-store-details^=\"vessel-\"] .arx-media img{object-fit:contain!important;padding:6px;background:#0b3043}",
    'article gold and vessel shop fit CSS'
)

# Cache-bust only after all exact replacements succeed.
p=Path('index.html')
text=p.read_text()
old='expedition-23s-progression-pass'
if old not in text:
    raise SystemExit('stage1 cache version not found')
p.write_text(text.replace(old,'expedition-23x-stage1-safe'))

print('ARS 23x stage 1 applied')
