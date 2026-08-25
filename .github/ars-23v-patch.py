from pathlib import Path
import re


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    p.write_text(text.replace(old, new, 1))


def sub_once(path, pattern, replacement, label, flags=re.S):
    p = Path(path)
    text = p.read_text()
    updated, count = re.subn(pattern, lambda m: replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 regex match, found {count}")
    p.write_text(updated)


# 1) Use known-good photographs for the two shipyard entries that were rendering blank.
replace_once(
    'expedition.js',
    "  const VESSEL_IMAGES = {\n    coastal:'assets/vessels/coastal-rv.webp',\n    global:'assets/vessels/global-rv.webp',\n    icebreaker:'assets/vessels/icebreaker.webp',\n    nuclear:'assets/vessels/nuclear-icebreaker.webp'\n  };",
    "  const VESSEL_IMAGES = {\n    coastal:'assets/vessels/coastal-rv.webp',\n    global:'assets/vessels/noaa-rv-brown.webp',\n    icebreaker:'https://commons.wikimedia.org/wiki/Special:FilePath/Polarforskningssekretariatet%20IMG%202551%20Oden%20Hjorthfjellet.jpg',\n    nuclear:'assets/vessels/nuclear-icebreaker.webp'\n  };",
    'shipyard photos'
)

# 2) Professor promotion: citations only, no paper-count gate.
replace_once(
    'expedition.js',
    "postdoc: {id:'postdoc', name:'Postdoctoral Researcher', short:'Postdoc', level:2, minCitations:100, salary:800, quality:1.12, productivity:1.35, color:'#7dd3fc', next:'professor', promotion:{papers:10,citations:1000}},",
    "postdoc: {id:'postdoc', name:'Postdoctoral Researcher', short:'Postdoc', level:2, minCitations:100, salary:800, quality:1.12, productivity:1.35, color:'#7dd3fc', next:'professor', promotion:{papers:0,citations:2000}},",
    'professor promotion metadata'
)
replace_once(
    'expedition.js',
    "    if (player?.career==='postdoc' && state.papers.length>=10 && state.citations>=1000) {\n      player.career='professor'; recordScientist(player); promotionQueue.push({name:'Chief Scientist',career:'professor',papers:state.papers.length,missions:player.missions||0,message:'Ten published papers and 1,000 citations have earned professor status. Global research vessels, icebreakers and heavy equipment are unlocked. Professors lead the highest-complexity programs and can originate new grants while at sea.'}); addLog('Chief Scientist promoted to professor · global vessels, icebreakers and heavy equipment unlocked.'); refreshProgressionOpportunities('career-promotion');\n    }",
    "    if (player?.career==='postdoc' && state.citations>=2000) {\n      player.career='professor'; recordScientist(player); promotionQueue.push({name:'Chief Scientist',career:'professor',papers:state.papers.length,missions:player.missions||0,message:'Reaching 2,000 citations has earned professor status. There is no minimum publication-count requirement. Global research vessels, icebreakers and heavy equipment are unlocked. Professors lead the highest-complexity programs and can originate new grants while at sea.'}); addLog('Chief Scientist promoted to professor at 2,000 citations · global vessels, icebreakers and heavy equipment unlocked.'); refreshProgressionOpportunities('career-promotion');\n    }",
    'professor promotion gate'
)

# 3) Correct grant progression logic: a career unlocks work up to that level,
# while the existing weighting still strongly favors the player's current level.
replace_once(
    'expedition.js',
    "const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);",
    "const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)<=careerFloor&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);",
    'grant career pool'
)

# Pass the desired long-range window into deterministic site fallback.
replace_once(
    'expedition.js',
    "const spacing=options.nearby?18:targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
    "const spacing=options.nearby?18:targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:window,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
    'grant distance window context'
)

# Official grants need a valid research site, not an unrealistically straight,
# obstacle-free great-circle line. The player can route around coasts and ice.
replace_once(
    'game.js',
    "    const dx=site.x-state.x,dy=site.y-state.y,length=Math.hypot(dx,dy),steps=Math.max(24,Math.ceil(length/2)),origin=context.origin&&polar(context.origin.lat,context.origin.lon),outX=origin?state.x-origin.x:0,outY=origin?state.y-origin.y:0,outLength=Math.hypot(outX,outY);\n    if(outLength>4&&(dx*outX+dy*outY)/(Math.max(1,length)*outLength)<.05)return false;\n    for(let step=1;step<=steps;step++){const x=state.x+dx*step/steps,y=state.y+dy*step/steps;if(unpolar(x,y).lat<MIN_LAT+.04||isLand(x,y)||!iceNavigationProfileAt(x,y).allowed)return false;}\n    return true;",
    "    if(context.kind==='grant'||context.kind==='contract')return true;\n    const dx=site.x-state.x,dy=site.y-state.y,length=Math.hypot(dx,dy),steps=Math.max(24,Math.ceil(length/2)),origin=context.origin&&polar(context.origin.lat,context.origin.lon),outX=origin?state.x-origin.x:0,outY=origin?state.y-origin.y:0,outLength=Math.hypot(outX,outY);\n    if(outLength>4&&(dx*outX+dy*outY)/(Math.max(1,length)*outLength)<.05)return false;\n    for(let step=1;step<=steps;step++){const x=state.x+dx*step/steps,y=state.y+dy*step/steps;if(unpolar(x,y).lat<MIN_LAT+.04||isLand(x,y)||!iceNavigationProfileAt(x,y).allowed)return false;}\n    return true;",
    'grant route validation'
)

# Long-range deterministic fallback for grants. This preserves the large-vessel
# distance scaling while making sponsor boards reliable instead of depending on
# a lucky random point landing on suitable water.
sub_once(
    'game.js',
    r"  function findResearchSite\(context=\{\}\)\{.*?\n  \}\n  function researchEnvironment",
    """  function findResearchSite(context={}){
    const template=context.template||{};
    if(template.glacier){
      const origin=context.origin||unpolar(state.x,state.y),sites=[...GLACIER_SITES].sort((a,b)=>Math.hypot(polar(a.lat,a.lon).x-state.x,polar(a.lat,a.lon).y-state.y)-Math.hypot(polar(b.lat,b.lon).x-state.x,polar(b.lat,b.lon).y-state.y));
      for(const glacier of sites){const center=polar(glacier.lat,glacier.lon);for(let radius=2;radius<=28;radius+=2)for(let i=0;i<36;i++){const a=i*Math.PI/18,pt=unpolar(center.x+Math.cos(a)*radius,center.y+Math.sin(a)*radius);pt.siteName=glacier.name;if(isResearchSiteSuitable(pt,context))return pt;}}
    }
    const origin=context.origin&&polar(context.origin.lat,context.origin.lon),outX=origin?state.x-origin.x:0,outY=origin?state.y-origin.y:0,outLength=Math.hypot(outX,outY),base=outLength>4?Math.atan2(outY,outX):state.commandActive?Math.atan2(state.ty-state.y,state.tx-state.x):state.angle-Math.PI/2;
    const shore=!!(template.shore||template.terrestrial),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,opportunityStart=({fishing:20,trawler:60,coastal:105,global:185,icebreaker:265,nuclear:345}[vesselIceId()]||20)+(careerLevel-1)*20,official=context.kind==='grant'||context.kind==='contract',window=context.distanceWindow;
    let distances;
    if(official&&Number.isFinite(window?.min)&&Number.isFinite(window?.max)){
      const span=Math.max(0,window.max-window.min);distances=[0,.16,.33,.5,.67,.84,1].map(f=>Math.round(window.min+span*f));
    }else if(shore)distances=[12,20,30,45,60,80];
    else if(context.kind==='opportunity'||context.kind==='weather-opportunity')distances=[opportunityStart,opportunityStart+30,opportunityStart+70,opportunityStart+120,opportunityStart+180];
    else distances=[45,65,85,105,130,165,210];
    const offsets=[0,-10,10,-20,20,-30,30,-45,45,-60,60,-75,75,-90,90,-105,105,-120,120,-135,135,-150,150,-165,165,180];
    for(const distance of distances)for(const degrees of offsets){const angle=base+degrees*Math.PI/180,point=unpolar(state.x+Math.cos(angle)*distance,state.y+Math.sin(angle)*distance);if(isResearchSiteSuitable(point,context))return point;}
    return null;
  }
  function researchEnvironment""",
    'long-range grant fallback'
)

# 4) Remove fast ice completely for now: no shoreline band, no fast-ice type,
# no fast-ice collision. Other pack/marginal/cracked ice remains unchanged.
replace_once(
    'game.js',
    "  function fastIceGrowth(){const d=state.seasonDay;if(d<91||d>=274)return 0;if(d<=182)return.5-.5*Math.cos(Math.PI*(d-91)/91);return.5+.5*Math.cos(Math.PI*(d-182)/92);}",
    "  function fastIceGrowth(){return 0;} // Fast ice temporarily disabled.",
    'disable fast ice'
)

# 5) Wildlife: if even one observable animal/school is currently visible on
# the map, do not spawn another encounter. Otherwise add only one at a time,
# with a local cap of two rather than the previous burst toward five.
replace_once(
    'game.js',
    "  function updateWildlifeEncounters(dt){wildlifeEncounterClock+=dt;if(wildlifeEncounterClock<.6)return;wildlifeEncounterClock=0;retireDistantEncounters();const local=localWildlifeCount();if(local<3){spawnWildlifeEncounter();spawnWildlifeEncounter();}else if(local<5)spawnWildlifeEncounter();}",
    "  function visibleWildlifeCount(){let total=0;forEachWildlifeVisual((entity,species,category,w)=>{if(!wildlifeClearOfPorts(w.x,w.y))return;const p=worldToScreen(w.x,w.y);if(p.x>=-35&&p.x<=width+35&&p.y>=72&&p.y<=height+35)total++;});return total;}\n  function updateWildlifeEncounters(dt){wildlifeEncounterClock+=dt;if(wildlifeEncounterClock<.9)return;wildlifeEncounterClock=0;retireDistantEncounters();if(visibleWildlifeCount()>=1)return;if(localWildlifeCount()>=2)return;spawnWildlifeEncounter();}",
    'wildlife spawn cap'
)

# Cache bust the modified scripts for the live Pages build.
replace_once(
    'index.html',
    'expedition-23u-field-opportunity-audio',
    'expedition-23v-grants-wildlife-no-fast-ice',
    'cache version first occurrence'
)
# The version appears multiple times; update all remaining occurrences safely.
p=Path('index.html');text=p.read_text();p.write_text(text.replace('expedition-23u-field-opportunity-audio','expedition-23v-grants-wildlife-no-fast-ice'))

print('ARS 23v patch applied')
