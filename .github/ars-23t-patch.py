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
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 regex match, found {count}")
    p.write_text(updated)


# Approved vessel art: keep the two existing F/Vs and replace only the four larger classes.
replace_once(
    'expedition.js',
    """  const VESSEL_IMAGES = {
    coastal:'assets/vessels/fishing-trawler.webp',
    global:'assets/vessels/noaa-rv-brown.webp',
    icebreaker:'https://commons.wikimedia.org/wiki/Special:FilePath/Polarforskningssekretariatet%20IMG%202551%20Oden%20Hjorthfjellet.jpg',
    nuclear:'https://commons.wikimedia.org/wiki/Special:FilePath/50%20Let%20Pobedy.jpg'
  };""",
    """  const VESSEL_IMAGES = {
    coastal:'assets/vessels/coastal-rv.webp',
    global:'assets/vessels/global-rv.webp',
    icebreaker:'assets/vessels/icebreaker.webp',
    nuclear:'assets/vessels/nuclear-icebreaker.webp'
  };""",
    'vessel image mapping'
)

# Grey out unavailable grant offers, show why, and disable acceptance until capability is restored.
sub_once(
    'expedition.js',
    r"  function offerCard\(item\) \{.*?\n  \}\n  function activeGrantCard",
    """  function offerCard(item) {
    const specialty=item.anyScientist?'Any scientist aboard':item.specialties.map(id=>specialtyById[id]?.name).filter(Boolean).join(' / '),media=canonicalMissionMedia(item);
    const readiness=missionReadiness(item),missing=readiness.rows.find(row=>!row.ready),projection=missionFoodProjection(item),cap=grantLoad()>=grantCapacity(),foodUnsafe=projection.remaining<15,fuelUnsafe=!vessel().nuclearFuel&&projection.fuelRemaining<10,blocked=!readiness.ready;
    const label=blocked?`MISSING · ${missing?.label||'REQUIRED CAPABILITY'}`:cap?`ACTIVE GRANT LIMIT ${grantLoad()}/${grantCapacity()}`:foodUnsafe?`INSUFFICIENT FOOD · PROJECTED ${Math.max(0,Math.floor(projection.remaining))}%`:fuelUnsafe?`INSUFFICIENT FUEL · PROJECTED ${Math.max(0,Math.floor(projection.fuelRemaining))}%`:'ACCEPT RESEARCH GRANT';
    const missingNote=blocked?`<div class=\"arx-requirement\"><b>NOT READY</b><span>${escapeHtml(missing?.detail||missing?.label||'Purchase or restore the missing capability, then return to this grant.')}</span></div>${readinessMarkup(readiness)}`:'';
    return `<article class=\"arx-card offer research-offer ${blocked?'locked':''}\"><div class=\"arx-offer-thumb\"><img src=\"${escapeHtml(media?.src||MEDIA.fieldKit.src)}\" alt=\"${escapeHtml(media?.alt||item.title)}\"></div><div class=\"arx-card-head\"><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(specialty)}</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p>${missingNote}<div class=\"arx-grant-advance\"><span><small>PAYMENT ON COMPLETION</small><b>${cash(item.reward)}</b></span></div><h4 class=\"arx-mini-label\">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class=\"arx-mini-label\">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class=\"arx-stats\"><span>+${item.data} data</span><span>${item.minCrew||missionMinCrew(item)} people minimum</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span><span>~${projection.days} field days</span>${item.iceValueMultiplier>1?`<span>ICE DATA VALUE ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>Food on return ~${Math.max(0,Math.floor(projection.remaining))}%</span><span>Fuel on return ~${Math.max(0,Math.floor(projection.fuelRemaining))}%</span></div><button data-arx-action=\"accept\" data-id=\"${item.id}\" ${blocked||cap||foodUnsafe||fuelUnsafe?'disabled':''}>${escapeHtml(label)}</button></article>`;
  }
  function activeGrantCard""",
    'grant offer readiness'
)

# Active grants also visibly grey out when equipment/crew capability is lost.
replace_once(
    'expedition.js',
    "    const missing=!eligible(item), projection=missionFoodProjection(item);",
    "    const missing=!eligible(item), readiness=missionReadiness(item), projection=missionFoodProjection(item);",
    'active grant readiness variable'
)
replace_once(
    'expedition.js',
    'return `<article class="arx-card grant"><div class="arx-card-head">',
    'return `<article class="arx-card grant ${missing?\'locked\':\'\'}"><div class="arx-card-head">',
    'active grant locked class'
)
replace_once(
    'expedition.js',
    '<p>${escapeHtml(item.description)}</p><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}',
    '<p>${escapeHtml(item.description)}</p>${missing?readinessMarkup(readiness):\'\'}<h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}',
    'active grant missing explanation'
)

# Hard acceptance guard: an aspirational grant may be displayed but cannot be accepted until ready.
replace_once(
    'expedition.js',
    """  function acceptOffer(id) {
    const offer=state.offers.find(item=>item.id===id); if (!offer) return;
    if (grantLoad()>=grantCapacity()) { toast(`ACTIVE RESEARCH GRANT LIMIT · ${grantLoad()}/${grantCapacity()}`); return; }""",
    """  function acceptOffer(id) {
    const offer=state.offers.find(item=>item.id===id); if (!offer) return;
    const readiness=missionReadiness(offer),missing=readiness.rows.find(row=>!row.ready);
    if(!readiness.ready){toast(`GRANT NOT READY · ${String(missing?.label||'MISSING CAPABILITY').toUpperCase()}`);return;}
    if (grantLoad()>=grantCapacity()) { toast(`ACTIVE RESEARCH GRANT LIMIT · ${grantLoad()}/${grantCapacity()}`); return; }""",
    'grant acceptance readiness guard'
)

# Clicking a distant guidance arrow should preview the grant and offer DROP / NAVIGATE actions.
replace_once(
    'expedition.js',
    "if(!target.anywhere&&distance>RESEARCH_INTERACTION_KM){callbacks.onNavigate?.(target);renderSidebar();return true;}",
    "if(!context.preview&&!target.anywhere&&distance>RESEARCH_INTERACTION_KM){callbacks.onNavigate?.(target);renderSidebar();return true;}",
    'target preview mode'
)
replace_once(
    'expedition.js',
    "const workActions=complete?'<button data-arx-action=\"acknowledge-research\">OKAY</button>':`${decline}<button data-arx-action=\"complete-target\" data-id=\"${target.id}\" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button>`;",
    "const workActions=complete?'<button data-arx-action=\"acknowledge-research\">OKAY</button>':!atSite&&!target.anywhere?`${decline}<button data-arx-action=\"navigate-target\" data-id=\"${target.id}\">NAVIGATE TO SITE</button>`:`${decline}<button data-arx-action=\"complete-target\" data-id=\"${target.id}\" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button>`;",
    'preview navigation action'
)

# Remove legacy invalid pop-up opportunities from saves as soon as map targets are requested.
replace_once(
    'expedition.js',
    "  function getMapTargets() { return state.targets.map(item=>({...item,mapEligible:eligible(item,item.weather?{type:item.weather}:null)})); }",
    """  function getMapTargets() {
    if(callbacks.researchSitePortClear){
      const removed=new Set(state.targets.filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!callbacks.researchSitePortClear(item)).map(item=>item.id));
      if(removed.size){state.targets=state.targets.filter(item=>!removed.has(item.id));if(state.navigation&&removed.has(state.navigation.id))state.navigation=null;if(state.lastTargetContext&&removed.has(state.lastTargetContext.id))state.lastTargetContext=null;}
    }
    return state.targets.map(item=>({...item,mapEligible:eligible(item,item.weather?{type:item.weather}:null)}));
  }""",
    'prune port-overlap opportunities'
)

# Shipyard attention only for an affordable vessel that is actually a step upward.
replace_once(
    'expedition.js',
    "    const fleetAttention=vesselsForPort().some(vesselPurchaseReady);",
    "    const vesselRanks={fishing:0,trawler:1,coastal:2,global:3,icebreaker:4,nuclear:5},currentRank=vesselRanks[state.currentVessel]??0;\n    const fleetAttention=vesselsForPort().some(item=>(vesselRanks[item.id]??-1)>currentRank&&vesselPurchaseReady(item));",
    'shipyard attention ranking'
)

# Make locked research cards visibly desaturated in addition to the existing opacity treatment.
replace_once(
    'expedition.js',
    ".research-offer .arx-operation-scientists>div,.research-offer .arx-operation-gear{min-width:130px;padding:4px}",
    ".research-offer.locked{filter:saturate(.28);border-color:rgba(148,163,184,.3)!important}.arx-card.grant.locked{filter:saturate(.32);border-color:rgba(148,163,184,.28)!important}.research-offer .arx-operation-scientists>div,.research-offer .arx-operation-gear{min-width:130px;padding:4px}",
    'locked grant styling'
)

# Main map: stronger labelled graticule.
sub_once(
    'game.js',
    r"  function drawGraticule\(\)\{.*?\}\n  function drawCurrentArrows",
    """  function drawGraticule(){
    const pole=worldToScreen(0,0);ctx.save();ctx.strokeStyle='rgba(223,249,251,.36)';ctx.lineWidth=1;ctx.setLineDash([4,6]);ctx.font='700 8px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';
    [60,65,70,75,80,85].forEach(lat=>{const r=terrainLatitudeRadius(lat)*scale;ctx.beginPath();ctx.arc(pole.x,pole.y,r,0,Math.PI*2);ctx.stroke();if(lat===70||lat===80){const w=polar(lat,15),p=worldToScreen(w.x,w.y);if(p.x>28&&p.x<width-28&&p.y>92&&p.y<height-28){ctx.setLineDash([]);ctx.strokeStyle='rgba(5,34,48,.82)';ctx.lineWidth=3;ctx.strokeText(`${lat}°N`,p.x,p.y);ctx.fillStyle='rgba(235,252,253,.9)';ctx.fillText(`${lat}°N`,p.x,p.y);ctx.strokeStyle='rgba(223,249,251,.36)';ctx.lineWidth=1;ctx.setLineDash([4,6]);}}});
    for(let lon=-180;lon<180;lon+=30){const e=polar(MIN_LAT,lon),b=worldToScreen(e.x,e.y);ctx.beginPath();ctx.moveTo(pole.x,pole.y);ctx.lineTo(b.x,b.y);ctx.stroke();if(lon%60===0&&b.x>32&&b.x<width-32&&b.y>96&&b.y<height-28){const label=lon===0?'0°':`${Math.abs(lon)}°${lon<0?'W':'E'}`;ctx.setLineDash([]);ctx.strokeStyle='rgba(5,34,48,.82)';ctx.lineWidth=3;ctx.strokeText(label,b.x,b.y);ctx.fillStyle='rgba(235,252,253,.9)';ctx.fillText(label,b.x,b.y);ctx.strokeStyle='rgba(223,249,251,.36)';ctx.lineWidth=1;ctx.setLineDash([4,6]);}}
    ctx.setLineDash([]);ctx.restore();
  }
  function drawCurrentArrows""",
    'main map graticule'
)

# Strong port exclusion for spontaneous opportunities. Grants retain their smaller local-work exclusion.
replace_once(
    'game.js',
    "    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<portBuffer;}))return false;",
    "    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&!researchSitePortClear(point))return false;",
    'opportunity port exclusion'
)
replace_once(
    'game.js',
    "  function isResearchSiteSuitable(point,context={}){",
    """  function researchSitePortClear(point){
    if(!Number.isFinite(point?.lat)||!Number.isFinite(point?.lon))return false;const site=polar(point.lat,point.lon),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,base=({fishing:60,trawler:90,coastal:130,global:210,icebreaker:290,nuclear:380}[vesselIceId()]||60),buffer=Math.max(60,base+(careerLevel-1)*20);return cityLabels.every(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)>=buffer;});
  }
  function isResearchSiteSuitable(point,context={}){""",
    'port clear helper'
)

# Main-map grant markers: eligibility overrides official yellow styling.
replace_once(
    'game.js',
    "ctx.fillStyle=official?'#f6d365':eligible?'#8ef0cf':'#8a9da2';",
    "ctx.fillStyle=!eligible?'#8a9da2':official?'#f6d365':'#8ef0cf';",
    'main map target eligibility color'
)
replace_once(
    'game.js',
    "if(official||eligible){ctx.strokeStyle=official?'rgba(246,211,101,.88)':'rgba(142,240,207,.82)';ctx.shadowColor=official?'#f6d365':'#8ef0cf';ctx.shadowBlur=10+pulse*7;ctx.lineWidth=1.8;ctx.beginPath();ctx.arc(p.x,p.y,outer,0,Math.PI*2);ctx.stroke();ctx.shadowBlur=0;}",
    "if(eligible){ctx.strokeStyle=official?'rgba(246,211,101,.88)':'rgba(142,240,207,.82)';ctx.shadowColor=official?'#f6d365':'#8ef0cf';ctx.shadowBlur=10+pulse*7;ctx.lineWidth=1.8;ctx.beginPath();ctx.arc(p.x,p.y,outer,0,Math.PI*2);ctx.stroke();ctx.shadowBlur=0;}else{ctx.strokeStyle='rgba(138,157,162,.72)';ctx.shadowBlur=0;ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(p.x,p.y,outer,0,Math.PI*2);ctx.stroke();}",
    'main map target eligibility ring'
)

# Offscreen grant arrows grey out when capability is lost, but stay clickable.
sub_once(
    'game.js',
    r"  function drawResearchGuidance\(\)\{.*?\n  \}\n  function researchGuidanceAt",
    """  function drawResearchGuidance(){
    const hits=[],cx=width/2,cy=height/2,targets=researchTargets().filter(target=>target.kind==='grant'||target.kind==='contract'||target.kind==='recovery').map(target=>({target,...researchTargetWorld(target)})).filter(item=>item.p.x<=35||item.p.x>=width-35||item.p.y<=95||item.p.y>=height-35).sort((a,b)=>(b.target.selected?1:0)-(a.target.selected?1:0)||a.distance-b.distance).slice(0,8);
    for(let index=0;index<targets.length;index++){const item=targets[index],target=item.target,p=item.p,dx=p.x-cx,dy=p.y-cy,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length,edge=Math.min(width*.38,height*.36),spread=(index%3-1)*11,x=cx+ux*edge-uy*spread,y=cy+uy*edge+ux*spread,a=Math.atan2(uy,ux),opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity',selected=!!(target.selected||target.active),eligible=target.mapEligible!==false;hits.push({x,y,r:selected?33:27,targetId:target.id});ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.fillStyle=!eligible?'rgba(138,157,162,.97)':opportunity?'rgba(142,240,207,.97)':'rgba(246,211,101,.96)';ctx.strokeStyle='rgba(5,34,48,.92)';ctx.lineWidth=selected?3.5:2.5;ctx.beginPath();ctx.moveTo(selected?16:13,0);ctx.lineTo(-8,-8);ctx.lineTo(-4,0);ctx.lineTo(-8,8);ctx.closePath();ctx.fill();ctx.stroke();ctx.rotate(-a);ctx.font=`${selected?900:800} ${selected?9:8}px system-ui`;ctx.textAlign='center';ctx.strokeStyle='rgba(5,34,48,.96)';ctx.lineWidth=3;const title=(target.shortTitle||target.title||'RESEARCH').toUpperCase().slice(0,18),label=`${title} · ${Math.round(item.distance)} KM`;ctx.strokeText(label,0,24);ctx.fillStyle=!eligible?'#b7c4c7':opportunity?'#b9f7df':'#fff3aa';ctx.fillText(label,0,24);ctx.restore();}
    researchGuidanceHit=hits;
  }
  function researchGuidanceAt""",
    'guidance arrow eligibility color'
)

# Clicking an offscreen guidance arrow opens the grant card instead of immediately changing course.
replace_once(
    'game.js',
    "if(item.distance<=RESEARCH_INTERACTION_KM){research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:true,target});}else navigateToResearchTarget(target);",
    "if(item.distance<=RESEARCH_INTERACTION_KM){research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:true,target});}else{research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:false,target,preview:true});}",
    'guidance arrow preview click'
)

# Minimap: grey unavailable grants and change the current main-map footprint from rectangle to circle.
replace_once(
    'game.js',
    "mini.fillStyle=official?'#f6d365':eligible?'#8ef0cf':'#83979c';",
    "mini.fillStyle=!eligible?'#83979c':official?'#f6d365':'#8ef0cf';",
    'minimap target eligibility color'
)
replace_once(
    'game.js',
    "if(official&&d>radius-5){mini.strokeStyle='rgba(246,211,101,.9)';mini.lineWidth=1;mini.beginPath();mini.arc(dot.x,dot.y,6,0,Math.PI*2);mini.stroke();}",
    "if(official&&d>radius-5){mini.strokeStyle=eligible?'rgba(246,211,101,.9)':'rgba(131,151,156,.9)';mini.lineWidth=1;mini.beginPath();mini.arc(dot.x,dot.y,6,0,Math.PI*2);mini.stroke();}",
    'minimap offscreen target ring color'
)
replace_once(
    'game.js',
    "mini.strokeRect(p.x-viewW/2,p.y-viewH/2,viewW,viewH);",
    "const viewRadius=Math.min(radius,Math.max(9,Math.hypot(viewW,viewH)/2));mini.beginPath();mini.arc(p.x,p.y,viewRadius,0,Math.PI*2);mini.stroke();",
    'minimap circular view footprint'
)

# Make minimap graticule more visible and label it when expanded.
replace_once('game.js', "mini.strokeStyle='rgba(255,255,255,.2)';mini.lineWidth=.7;", "mini.strokeStyle='rgba(255,255,255,.34)';mini.lineWidth=.8;", 'minimap latitude grid visibility')
replace_once('game.js', "mini.strokeStyle='rgba(255,255,255,.18)';mini.lineWidth=.65;", "mini.strokeStyle='rgba(255,255,255,.3)';mini.lineWidth=.75;", 'minimap longitude grid visibility')
replace_once(
    'game.js',
    "}}if(!miniTerrain)land.forEach(shape=>{pathPolygon(mini,shape.pts,project);",
    "}}if(minimapExpanded){mini.save();mini.font='700 7px system-ui';mini.textAlign='center';mini.textBaseline='middle';for(const lat of[70,80]){const w=polar(lat,15),p=project(w.x,w.y);if(Math.hypot(p.x-c,p.y-c)<radius-8){mini.strokeStyle='rgba(5,34,48,.8)';mini.lineWidth=2.5;mini.strokeText(`${lat}°N`,p.x,p.y);mini.fillStyle='rgba(238,253,255,.88)';mini.fillText(`${lat}°N`,p.x,p.y);}}for(const lon of[-120,-60,0,60,120]){const w=polar(MIN_LAT+1,lon),p=project(w.x,w.y);if(Math.hypot(p.x-c,p.y-c)<radius-8){const label=lon===0?'0°':`${Math.abs(lon)}°${lon<0?'W':'E'}`;mini.strokeStyle='rgba(5,34,48,.8)';mini.lineWidth=2.5;mini.strokeText(label,p.x,p.y);mini.fillStyle='rgba(238,253,255,.88)';mini.fillText(label,p.x,p.y);}}mini.restore();}if(!miniTerrain)land.forEach(shape=>{pathPolygon(mini,shape.pts,project);",
    'minimap graticule labels'
)

# Keep NPC research vessels visually consistent with the new fleet art.
replace_once(
    'game.js',
    "{id:'rv-nansen-fjord',name:'R/V Nansen Fjord',classId:'coastal',kind:'research',typeLabel:'Coastal-class research vessel',speed:10.5,mission:'Fram Strait hydrography and plankton stations',captainName:'Dr. Hana Suzuki',captainRole:'Chief Scientist',captainPortrait:'assets/scientists/hana-suzuki.webp',image:'assets/vessels/noaa-rv-brown.webp'",
    "{id:'rv-nansen-fjord',name:'R/V Nansen Fjord',classId:'coastal',kind:'research',typeLabel:'Coastal-class research vessel',speed:10.5,mission:'Fram Strait hydrography and plankton stations',captainName:'Dr. Hana Suzuki',captainRole:'Chief Scientist',captainPortrait:'assets/scientists/hana-suzuki.webp',image:'assets/vessels/coastal-rv.webp'",
    'coastal npc vessel art'
)
replace_once(
    'game.js',
    "{id:'rv-meridian-ice',name:'R/V Meridian Ice',classId:'global',kind:'research',typeLabel:'Global-class research vessel',speed:13,mission:'Pan-Arctic mooring service expedition',captainName:'Prof. Elena Morozova',captainRole:'Chief Scientist',captainPortrait:'assets/scientists/elena-morozova.webp',image:'assets/vessels/noaa-rv-brown.webp'",
    "{id:'rv-meridian-ice',name:'R/V Meridian Ice',classId:'global',kind:'research',typeLabel:'Global-class research vessel',speed:13,mission:'Pan-Arctic mooring service expedition',captainName:'Prof. Elena Morozova',captainRole:'Chief Scientist',captainPortrait:'assets/scientists/elena-morozova.webp',image:'assets/vessels/global-rv.webp'",
    'global npc vessel art'
)

# Let expedition.js prune legacy port-overlapping opportunities.
replace_once(
    'game.js',
    "    isResearchSiteSuitable,\n    findResearchSite,",
    "    isResearchSiteSuitable,\n    researchSitePortClear,\n    findResearchSite,",
    'port-clear callback'
)

# Cache bust without changing GAME_VERSION, so current playtest saves are preserved.
p = Path('index.html')
text = p.read_text()
old = 'expedition-23s-progression-pass'
if old not in text:
    raise SystemExit('index cache version: old marker not found')
p.write_text(text.replace(old, 'expedition-23t-grants-vessels-map'))

print('ARS 23t patch applied successfully')
