from pathlib import Path
import re

GAME=Path('game.js'); EXP=Path('expedition.js'); INDEX=Path('index.html')
game=GAME.read_text(); exp=EXP.read_text(); index=INDEX.read_text()

def once(text, old, new, label):
    n=text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, got {n}')
    return text.replace(old,new,1)

# Grants: remove an undefined reward scaler that aborts every buildTarget() call.
exp = once(
    exp,
    "    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03), rewardScale=vesselRewardScale();",
    "    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03);",
    'remove undefined vessel reward scaler'
)
exp = once(
    exp,
    "reward:Math.round(template.reward*scale*(kind === 'opportunity'||kind==='weather-opportunity' ? 1.6 : 2)*iceValueMultiplier*rewardScale)",
    "reward:Math.round(template.reward*scale*(kind === 'opportunity'||kind==='weather-opportunity' ? 1.6 : 2)*iceValueMultiplier)",
    'restore grant reward formula'
)
if 'vesselRewardScale' in exp:
    raise SystemExit('vesselRewardScale reference still present')

# Port approach: stop exhaustively evaluating 10,080 candidates on every click.
# Search outward from the port in the direction of the ship and return on the
# first unobstructed usable approach. Broader fallback scans are progressively
# coarser, preserving hard-port/ice cases without blocking the UI for seconds.
port_pat = re.compile(r"  function findPortApproach\(city\)\{.*?\n  \}\n  function resetDistantWildlifeFromPort", re.S)
m=port_pat.search(game)
if not m:
    raise SystemExit('findPortApproach block not found')
port_new = r'''  function findPortApproach(city){
    const center=polar(city.lat,city.lon),toward=Math.atan2(state.y-center.y,state.x-center.x);
    let fallback=null,fallbackScore=Infinity;
    const scan=(startRadius,maxRadius,radiusStep,angles)=>{
      const turn=Math.PI*2/angles,offsets=[0];
      for(let step=1;step<=Math.floor(angles/2);step++){offsets.push(step);if(step<angles/2)offsets.push(-step);}
      for(let radius=startRadius;radius<=maxRadius;radius+=radiusStep)for(const offset of offsets){
        const a=toward+offset*turn,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);
        if(pos.lat<MIN_LAT||isLand(x,y))continue;
        const profile=iceNavigationProfileAt(x,y);if(!profile.allowed)continue;
        const shipDistance=Math.hypot(x-state.x,y-state.y),score=radius+shipDistance*.025;
        if(score<fallbackScore){fallback={x,y,shoreDistance:radius};fallbackScore=score;}
        if(clearDisplacement(state.x,state.y,x,y))return{x,y,shoreDistance:radius};
      }
      return null;
    };
    return scan(3,72,3,24)||scan(78,180,6,24)||scan(192,420,12,18)||fallback;
  }
  function resetDistantWildlifeFromPort'''
game = game[:m.start()] + port_new + game[m.end():]
if 'radius<=420;radius+=3)for(let i=0;i<72' in game:
    raise SystemExit('exhaustive port scan still present')

# Keep the arrival handoff nearly immediate once the ship reaches its approach.
game = once(
    game,
    "pendingPortEntryTimer=setTimeout(()=>{if(state.dockedPort===city.name&&currentPortCity===city)finishPortEntry(city);},140);",
    "pendingPortEntryTimer=setTimeout(()=>{if(state.dockedPort===city.name&&currentPortCity===city)finishPortEntry(city);},24);",
    'shorten port entry handoff'
)

# Force mobile Safari/PWA clients to fetch the corrected runtime files.
index = once(index,'expedition.js?v=expedition-23j-overscan','expedition.js?v=expedition-23k-port-grants','expedition cache bust')
index = once(index,'game.js?v=expedition-23j-overscan','game.js?v=expedition-23k-port-grants','game cache bust')

GAME.write_text(game); EXP.write_text(exp); INDEX.write_text(index)
