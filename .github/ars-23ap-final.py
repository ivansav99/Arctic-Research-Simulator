from pathlib import Path
import re


def repl(s, old, new, label):
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    return s.replace(old,new,1)

p=Path('game.js')
s=p.read_text(encoding='utf-8')

old="""    const ANIMAL_SAMPLE_SOURCES={
      'BELUGA':'assets/audio/wildlife/beluga.mp3',
      'HUMPBACK':'assets/audio/wildlife/humpback.mp3',
      'WALRUS':'assets/audio/wildlife/walrus.mp3',
      'ARCTIC TERN':'assets/audio/wildlife/arctic-tern.mp3'
    };"""
new="""    const ANIMAL_SAMPLE_SOURCES={
      'BELUGA':'assets/audio/wildlife/beluga.mp3',
      'HUMPBACK':'assets/audio/wildlife/humpback.mp3',
      'BOWHEAD':'assets/audio/wildlife/bowhead.mp3',
      'WALRUS':'assets/audio/wildlife/walrus.mp3',
      'BEARDED SEAL':'assets/audio/wildlife/bearded-seal.mp3',
      'HARP SEAL':'assets/audio/wildlife/harp-seal.mp3',
      'ARCTIC TERN':'assets/audio/wildlife/arctic-tern.mp3',
      'COMMON EIDER':'assets/audio/wildlife/common-eider.mp3',
      'PINK-FOOTED GOOSE':'assets/audio/wildlife/pink-footed-goose.mp3',
      'BRENT GOOSE':'assets/audio/wildlife/brent-goose.mp3'
    };"""
s=repl(s,old,new,'animal source map')

old="const playAnimal=species=>{const c=ensure(),key=String(species||'').toUpperCase(),buffer=animalBuffers[key];if(!c||!ANIMAL_SAMPLE_SOURCES[key])return false;if(!buffer){loadAnimalSamples(c);return false;}const src=c.createBufferSource(),g=c.createGain();src.buffer=buffer;g.gain.value=.42;src.connect(g).connect(c.destination);const run=()=>src.start();if(c.state!=='running'){Promise.resolve(c.resume()).then(()=>{if(c.state==='running')run();}).catch(()=>{});}else run();return true;};"
new="const playAnimal=(species,{ambient=false}={})=>{const c=ensure(),key=String(species||'').toUpperCase(),buffer=animalBuffers[key];if(!c||!ANIMAL_SAMPLE_SOURCES[key])return false;if(!buffer){loadAnimalSamples(c);return false;}const src=c.createBufferSource(),g=c.createGain();src.buffer=buffer;g.gain.value=ambient?.12:1;src.connect(g).connect(c.destination);const run=()=>src.start();if(c.state!=='running'){Promise.resolve(c.resume()).then(()=>{if(c.state==='running')run();}).catch(()=>{});}else run();if(!ambient)nextAnimal=performance.now()+26000+Math.random()*16000;return true;};"
s=repl(s,old,new,'animal gain modes')

old="const nearbyAnimal=()=>{let best=null,bestDist=Infinity;try{forEachWildlifeVisual((entity,species,category,w)=>{const key=String(species||'').toUpperCase();if(!ANIMAL_SAMPLE_SOURCES[key])return;const p=worldToScreen(w.x,w.y);if(p.x<0||p.x>width||p.y<70||p.y>height)return;const d=Math.hypot(w.x-state.x,w.y-state.y);if(d<bestDist){bestDist=d;best=key;}});}catch(e){}return best;};"
new="const visibleAnimalSamples=()=>{const choices=[];try{forEachWildlifeVisual((entity,species,category,w)=>{const key=String(species||'').toUpperCase();if(!ANIMAL_SAMPLE_SOURCES[key])return;const p=worldToScreen(w.x,w.y);if(p.x<0||p.x>width||p.y<70||p.y>height)return;choices.push(key);});}catch(e){}return choices;};"
s=repl(s,old,new,'visible animal sample list')

old="if(!nextAnimal)nextAnimal=now+7000+Math.random()*7000;if(now>=nextAnimal){const species=nearbyAnimal();if(species&&playAnimal(species)){lastAnimal=now;nextAnimal=now+22000+Math.random()*22000;}else nextAnimal=now+6000+Math.random()*5000;}"
new="if(!nextAnimal)nextAnimal=now+9000+Math.random()*9000;if(now>=nextAnimal){const choices=visibleAnimalSamples(),species=choices.length?choices[Math.floor(Math.random()*choices.length)]:null;if(species&&playAnimal(species,{ambient:true})){lastAnimal=now;nextAnimal=now+20000+Math.random()*28000;}else nextAnimal=now+7000+Math.random()*7000;}"
s=repl(s,old,new,'random quiet visible wildlife ambience')
p.write_text(s,encoding='utf-8')

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s,n=re.subn(r"game\.js\?v=[^\"']+","game.js?v=expedition-23ap-approved-wildlife-audio",s,count=1)
if n!=1:
    raise SystemExit(f'game cache replacements={n}')
p.write_text(s,encoding='utf-8')

credits=Path('assets/audio/wildlife/CREDITS.md')
text=credits.read_text(encoding='utf-8') if credits.exists() else '# Wildlife audio credits\n'
marker='## Approved expansion — 23ap'
if marker not in text:
    text += """

## Approved expansion — 23ap

The player reviewed and approved these field recordings for the prototype. Short mono derivatives are normalized/trimmed for gameplay.

- `beluga.mp3` — alternative Beluga Whale exemplar from NOAA Fisheries, Northeast Fisheries Science Center Passive Acoustics Branch (`Dele-multisound-NOAA-Castellote-01-beluga-clip.mp3`).
- `bearded-seal.mp3` — Bearded Seal exemplar from NOAA Fisheries (`Erba-Multisound-Cornell-OrnithologyLab-01-bearded-seal-clip.mp3`).
- `harp-seal.mp3` — Harp Seal exemplar from NOAA Fisheries (`Pagr-call-NPI-Van-Parijs-02-harp-seal-clip.mp3`).
- `bowhead.mp3` — Bowhead Whale song; prototype source is UC San Diego Voices in the Sea, with Arctic WWF/K.M. Stafford recording retained as fallback provenance.
- `common-eider.mp3` — Common Eider field recording, British Library collection via Wikimedia Commons, CC BY-SA 4.0; trimmed/normalized derivative.
- `pink-footed-goose.mp3` — Pink-footed Geese field recording, British Library collection via Wikimedia Commons, CC BY-SA 4.0; trimmed/normalized derivative.
- `brent-goose.mp3` — Brent Goose field recording, British Library collection via Wikimedia Commons; trimmed/normalized derivative.

Existing approved files retained: `humpback.mp3`, `walrus.mp3`, and `arctic-tern.mp3`.

Before commercial App Store release, re-check redistribution/attribution terms for the NOAA, UCSD/WWF, and Brent Goose sources. Provenance is intentionally retained here for that audit.
"""
credits.write_text(text,encoding='utf-8')
