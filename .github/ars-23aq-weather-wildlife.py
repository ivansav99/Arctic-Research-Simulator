from pathlib import Path
import re


def replace_once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old,new,1)

# ---- game.js ----
p=Path('game.js')
s=p.read_text()
s=replace_once(s,
"    let ac=null,waveSource=null,waveGain=null,ambientWindGain=null,ambientPadGain=null,ambientPadOsc=[],lastCrack=0,lastAnimal=0,unlockChimed=false,unlockPromise=null,nextAnimal=0,animalLoading=false;const animalBuffers={};",
"    let ac=null,waveSource=null,waveGain=null,ambientWindGain=null,ambientPadGain=null,ambientPadOsc=[],lastCrack=0,lastAnimal=0,unlockChimed=false,unlockPromise=null,nextAnimal=0,nextFogHorn=0,lastFogEventId=null,animalLoading=false;const animalBuffers={};",
'game sound state')
s=replace_once(s,
"    // SEASONAL ARCTIC AMBIENCE: quiet by default; a low tonal bed and sparse seasonal details.\n    const setupAmbience=c=>{};",
"    // Weather ambience stays silent in normal conditions. During a gale, an airy filtered-noise bed fades in smoothly.\n    const setupAmbience=c=>{const seconds=6,b=c.createBuffer(1,c.sampleRate*seconds,c.sampleRate),d=b.getChannelData(0);for(let i=0;i<d.length;i++){const gust=.78+.22*Math.sin(i/9100)+.08*Math.sin(i/1730);d[i]=(Math.random()*2-1)*gust;}const src=c.createBufferSource(),hp=c.createBiquadFilter(),lp=c.createBiquadFilter();src.buffer=b;src.loop=true;hp.type='highpass';hp.frequency.value=260;lp.type='lowpass';lp.frequency.value=1750;ambientWindGain=c.createGain();ambientWindGain.gain.value=0;src.connect(hp).connect(lp).connect(ambientWindGain).connect(c.destination);src.start();};",
'weather ambience setup')
s=replace_once(s,
"      'PINK-FOOTED GOOSE':'assets/audio/wildlife/pink-footed-goose.mp3',\n      'BRENT GOOSE':'assets/audio/wildlife/brent-goose.mp3'",
"      'PINK-FOOTED GOOSE':'assets/audio/wildlife/pink-footed-goose.mp3',\n      'BRENT GOOSE':'assets/audio/wildlife/brent-goose.mp3',\n      'BARNACLE GOOSE':'assets/audio/wildlife/barnacle-goose.mp3',\n      'SNOW GOOSE':'assets/audio/wildlife/snow-goose.mp3',\n      'GRAY WHALE':'assets/audio/wildlife/gray-whale.mp3',\n      'RIBBON SEAL':'assets/audio/wildlife/ribbon-seal.mp3'",
'animal source expansion')
s=replace_once(s,
"    const playAnimal=(species,{ambient=false}={})=>{const c=ensure(),key=String(species||'').toUpperCase(),buffer=animalBuffers[key];if(!c||!ANIMAL_SAMPLE_SOURCES[key])return false;if(!buffer){loadAnimalSamples(c);return false;}const src=c.createBufferSource(),g=c.createGain();src.buffer=buffer;g.gain.value=ambient?.12:1;src.connect(g).connect(c.destination);const run=()=>src.start();if(c.state!=='running'){Promise.resolve(c.resume()).then(()=>{if(c.state==='running')run();}).catch(()=>{});}else run();if(!ambient)nextAnimal=performance.now()+26000+Math.random()*16000;return true;};",
"    const animalSampleKey=species=>String(species||'').toUpperCase().replace(/ SCHOOL$/,'').trim();\n    const hasAnimal=species=>!!ANIMAL_SAMPLE_SOURCES[animalSampleKey(species)];\n    const playAnimal=(species,{ambient=false}={})=>{const c=ensure(),key=animalSampleKey(species),buffer=animalBuffers[key];if(!c||!ANIMAL_SAMPLE_SOURCES[key])return false;if(!buffer){loadAnimalSamples(c);return false;}const src=c.createBufferSource(),g=c.createGain();src.buffer=buffer;g.gain.value=ambient?.06:.5;src.connect(g).connect(c.destination);const run=()=>src.start();if(c.state!=='running'){Promise.resolve(c.resume()).then(()=>{if(c.state==='running')run();}).catch(()=>{});}else run();if(!ambient)nextAnimal=performance.now()+26000+Math.random()*16000;return true;};",
'animal gains and lookup')
old_update="    const update=paused=>{if(!ac)return;const now=performance.now(),day=((state.seasonDay%365)+365)%365,season=day<91?'autumn':day<213?'winter':day<274?'spring':'summer';if(waveGain)waveGain.gain.setTargetAtTime((!paused&&state.commandActive&&state.moving&&!state.ramming)?0.045:0,ac.currentTime,.22);if(ambientPadGain)ambientPadGain.gain.setTargetAtTime(0,ac.currentTime,.2);if(!paused&&ac.state==='running'){if(!nextAnimal)nextAnimal=now+9000+Math.random()*9000;if(now>=nextAnimal){const choices=visibleAnimalSamples(),species=choices.length?choices[Math.floor(Math.random()*choices.length)]:null;if(species&&playAnimal(species,{ambient:true})){lastAnimal=now;nextAnimal=now+20000+Math.random()*28000;}else nextAnimal=now+7000+Math.random()*7000;}}if(!paused&&state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};\n    return{unlock,play,update,playAnimal};"
new_update="    const update=paused=>{if(!ac)return;const now=performance.now(),weather=currentWeather(),gale=!paused&&weather.type==='high-wind'&&weather.amount>.03,gust=.82+.18*Math.sin(now/1800)+.07*Math.sin(now/470),galeLevel=gale?Math.max(.018,Math.min(.072,(.018+weather.amount*.052)*gust)):0;if(waveGain)waveGain.gain.setTargetAtTime((!paused&&state.commandActive&&state.moving&&!state.ramming)?0.045:0,ac.currentTime,.22);if(ambientWindGain)ambientWindGain.gain.setTargetAtTime(galeLevel,ac.currentTime,.55);if(ambientPadGain)ambientPadGain.gain.setTargetAtTime(0,ac.currentTime,.2);if(!paused&&ac.state==='running'){if(weather.type==='fog'&&weather.amount>.12){if(lastFogEventId!==weather.eventId){lastFogEventId=weather.eventId;nextFogHorn=now+12000+Math.random()*18000;}if(now>=nextFogHorn){ferryHorn(0,2.55);nextFogHorn=now+35000+Math.random()*45000;}}else{lastFogEventId=null;nextFogHorn=0;}if(!nextAnimal)nextAnimal=now+9000+Math.random()*9000;if(now>=nextAnimal){const choices=visibleAnimalSamples(),species=choices.length?choices[Math.floor(Math.random()*choices.length)]:null;if(species&&playAnimal(species,{ambient:true})){lastAnimal=now;nextAnimal=now+20000+Math.random()*28000;}else nextAnimal=now+7000+Math.random()*7000;}}if(!paused&&state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};\n    return{unlock,play,update,playAnimal,hasAnimal};"
s=replace_once(s,old_update,new_update,'weather/fog update')
s=replace_once(s,
"    onToast:showToast,\n    onSound:type=>sound.play(type),",
"    onToast:showToast,\n    hasWildlifeSound:species=>sound.hasAnimal?.(species)===true,\n    onSound:(type,payload)=>type==='wildlife'?sound.playAnimal?.(payload?.species):sound.play(type),",
'research sound callbacks')
p.write_text(s)

# ---- expedition.js ----
p=Path('expedition.js')
s=p.read_text()
s=replace_once(s,
"    const tone=item.photoTone==='dark'?'dark':'';\n    const modal=root?.querySelector('#arx-wildlife-modal'); if(!modal)return false;",
"    const tone=item.photoTone==='dark'?'dark':'',hasSound=callbacks.hasWildlifeSound?.(key)===true;\n    const modal=root?.querySelector('#arx-wildlife-modal'); if(!modal)return false;",
'wildlife has-sound flag')
s=replace_once(s,
"<img src=\"${escapeHtml(item.photo)}\" alt=\"${escapeHtml(item.displayName)}\"><span>${firstIndividual?",
"<img src=\"${escapeHtml(item.photo)}\" alt=\"${escapeHtml(item.displayName)}\">${hasSound?`<button class=\"arx-photo-sound\" data-arx-action=\"replay-wildlife-sound\" data-arx-species=\"${escapeHtml(key)}\" aria-label=\"Replay ${escapeHtml(item.displayName)} sound\" title=\"Replay animal sound\">🔊</button>`:''}<span>${firstIndividual?",
'wildlife photo sound button')
s=replace_once(s,
"    else if (action==='close-wildlife') { root.querySelector('#arx-wildlife-modal').classList.remove('open'); if(!showPendingWildlifeArticle())setTimeout(maybeAutoPublish,0); }",
"    else if (action==='replay-wildlife-sound') callbacks.onSound?.('wildlife',{species:button.dataset.arxSpecies});\n    else if (action==='close-wildlife') { root.querySelector('#arx-wildlife-modal').classList.remove('open'); if(!showPendingWildlifeArticle())setTimeout(maybeAutoPublish,0); }",
'wildlife replay action')
s=replace_once(s,
".arx-photo span{position:absolute;left:10px;bottom:10px;padding:6px 8px;border-radius:5px;background:rgba(3,26,39,.85);color:#f6d365;font-size:7px;font-weight:900}.arx-species",
".arx-photo span{position:absolute;left:10px;bottom:10px;padding:6px 8px;border-radius:5px;background:rgba(3,26,39,.85);color:#f6d365;font-size:7px;font-weight:900}.arx-photo .arx-photo-sound{position:absolute;z-index:3;right:10px;top:10px;width:42px!important;height:42px!important;padding:0!important;border:1px solid rgba(235,250,252,.65)!important;border-radius:50%!important;background:rgba(3,26,39,.78)!important;color:#f4fbfc!important;font-size:18px!important;line-height:1!important;box-shadow:0 4px 14px rgba(0,0,0,.28);cursor:pointer;backdrop-filter:blur(5px)}.arx-photo .arx-photo-sound:active{transform:scale(.94)}.arx-species",
'wildlife sound button style')
p.write_text(s)

# ---- cache bust ----
p=Path('index.html')
s=p.read_text()
s=re.sub(r'expedition\.js\?v=[^\"\']+', 'expedition.js?v=expedition-23aq-weather-wildlife-audio', s, count=1)
s=re.sub(r'game\.js\?v=[^\"\']+', 'game.js?v=expedition-23aq-weather-wildlife-audio', s, count=1)
p.write_text(s)

# ---- credits ----
p=Path('assets/audio/wildlife/CREDITS.md')
s=p.read_text().rstrip()+"""

## Weather + wildlife expansion — 23aq

- `bowhead.mp3` — **Bowhead Whale song** from NOAA Alaska Fisheries Science Center's *Acoustic Studies Sound Board of Marine Mammals in Alaska* (`assets/bowhead-song.mp3`). This replaces the earlier narrated prototype clip so gameplay contains no spoken identification.
- `gray-whale.mp3` — **Gray Whale pops/calls** from the same NOAA Alaska Fisheries Science Center sound board (`assets/gray-whale-pops.mp3`).
- `ribbon-seal.mp3` — **Ribbon Seal vocalization** from the same NOAA Alaska Fisheries Science Center sound board (`assets/ribbon-seal.mp3`).
- `barnacle-goose.mp3` — **Barnacle Goose** field recording `Branta leucopsis - Barnacle Goose XC466464.mp3`, via Wikimedia Commons / Xeno-canto. Retain source-page attribution/license metadata for release audit.
- `snow-goose.mp3` — **Snow Goose** field recording `Artis, blauwe en witte sneeuwgans - SoundCloud - Beeld en Geluid.ogg`, via Wikimedia Commons / Netherlands Institute for Sound & Vision. Retain source-page attribution/license metadata for release audit.

NOAA sound-board landing page: https://www.fisheries.noaa.gov/resource/outreach-and-education/acoustic-studies-sound-board-marine-mammals-alaska
Legacy interactive sound board: https://apps-afsc.fisheries.noaa.gov/Audio/Alaska-Marine-Mammal-Acoustic-Studies/index.html
Wikimedia source pages should be re-checked for the exact current license/attribution text before a commercial store release.
"""+"\n"
p.write_text(s)

# ---- review page ----
items=[
('Beluga','beluga.mp3'),('Humpback Whale','humpback.mp3'),('Bowhead Whale','bowhead.mp3'),('Gray Whale','gray-whale.mp3'),('Walrus','walrus.mp3'),('Bearded Seal','bearded-seal.mp3'),('Harp Seal','harp-seal.mp3'),('Ribbon Seal','ribbon-seal.mp3'),('Arctic Tern','arctic-tern.mp3'),('Common Eider','common-eider.mp3'),('Pink-footed Goose','pink-footed-goose.mp3'),('Brent Goose','brent-goose.mp3'),('Barnacle Goose','barnacle-goose.mp3'),('Snow Goose','snow-goose.mp3')]
cards=''.join(f'<article><b>{name}</b><audio controls preload="none" src="assets/audio/wildlife/{fn}"></audio><small>{fn}</small></article>' for name,fn in items)
review=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARS wildlife audio review</title><style>body{{margin:0;padding:24px;background:#071d29;color:#eefbff;font:15px system-ui}}main{{max-width:760px;margin:auto}}h1{{font:800 30px Georgia,serif}}p,small{{color:#9fc5d0}}.tools{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}}button{{padding:12px 16px;border:0;border-radius:9px;background:#f6d365;color:#17323b;font-weight:900}}section{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}}article{{padding:14px;border:1px solid #2f6072;border-radius:10px;background:#0b3041}}article b,article small{{display:block}}audio{{width:100%;margin:10px 0}}</style></head><body><main><h1>Arctic Research · Audio Review</h1><p>Every wildlife recording currently implemented in the game. The two buttons below reproduce the synthesized weather/event effects.</p><div class="tools"><button id="wind">TEST GALE WIND · 5 SEC</button><button id="horn">TEST FOG / PORT HORN</button></div><section>{cards}</section><p><a style="color:#7dd3fc" href="assets/audio/wildlife/CREDITS.md">Recording credits / provenance</a></p></main><script>(()=>{{let ac=null;const ctx=()=>ac||(ac=new (window.AudioContext||window.webkitAudioContext)());function burst(c,d=.22,g=.028){{const b=c.createBuffer(1,Math.ceil(c.sampleRate*d),c.sampleRate),x=b.getChannelData(0);for(let i=0;i<x.length;i++)x[i]=(Math.random()*2-1)*(1-i/x.length);const s=c.createBufferSource(),f=c.createBiquadFilter(),v=c.createGain();s.buffer=b;f.type='bandpass';f.frequency.value=395;f.Q.value=.7;v.gain.value=g;s.connect(f).connect(v).connect(c.destination);s.start();}}function horn(){{const c=ctx(),start=c.currentTime,filter=c.createBiquadFilter(),master=c.createGain();filter.type='lowpass';filter.frequency.value=760;filter.Q.value=.55;master.gain.setValueAtTime(.0001,start);master.gain.exponentialRampToValueAtTime(.12,start+.18);master.gain.setValueAtTime(.12,start+1.84);master.gain.exponentialRampToValueAtTime(.0001,start+2.55);filter.connect(master).connect(c.destination);for(const[f,l,t,d]of[[92,.95,'sine',-3],[138,.62,'triangle',2],[184,.38,'sine',-2],[276,.18,'triangle',3]]){{const o=c.createOscillator(),g=c.createGain();o.type=t;o.detune.value=d;o.frequency.setValueAtTime(f*.985,start);o.frequency.linearRampToValueAtTime(f,start+.22);g.gain.value=l;o.connect(g).connect(filter);o.start(start);o.stop(start+2.59);}}burst(c);}}function wind(){{const c=ctx(),seconds=5,b=c.createBuffer(1,c.sampleRate*seconds,c.sampleRate),d=b.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*(.78+.22*Math.sin(i/9100)+.08*Math.sin(i/1730));const s=c.createBufferSource(),hp=c.createBiquadFilter(),lp=c.createBiquadFilter(),g=c.createGain();s.buffer=b;hp.type='highpass';hp.frequency.value=260;lp.type='lowpass';lp.frequency.value=1750;g.gain.value=.055;s.connect(hp).connect(lp).connect(g).connect(c.destination);s.start();}}document.querySelector('#horn').onclick=horn;document.querySelector('#wind').onclick=wind;}})();</script></body></html>'''
Path('wildlife-audio-review.html').write_text(review)

print('23aq code patch prepared')
