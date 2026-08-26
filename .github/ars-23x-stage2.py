from pathlib import Path
import re


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(); count=text.count(old)
    if count != 1: raise SystemExit(f'{label}: expected 1 match, found {count}')
    p.write_text(text.replace(old,new,1))


def replace_regex(path, pattern, replacement, label):
    p=Path(path); text=p.read_text(); new_text,count=re.subn(pattern,replacement,text,count=1,flags=re.S)
    if count != 1: raise SystemExit(f'{label}: expected 1 regex match, found {count}')
    p.write_text(new_text)

# -------------------------------------------------------------------------
# Expedition state: keep opportunity history separate from grant history.
# -------------------------------------------------------------------------
replace_once(
 'expedition.js',
 "scientistRecords:{}, promotions:[], recentGrantTemplates:[], recentGrantSites:[], grantCooldowns:{}, grantMarketReady:{}, assistedByVessels:[], bridgeSupportNotice:null, lastPortId:null, lastProfessorGrantDay:-999, remoteOffer:null, helicopterFoodReminderShown:false",
 "scientistRecords:{}, promotions:[], recentGrantTemplates:[], recentGrantSites:[], recentOpportunityTemplates:[], lastOpportunitySpawnPosition:null, grantCooldowns:{}, grantMarketReady:{}, assistedByVessels:[], bridgeSupportNotice:null, lastPortId:null, lastProfessorGrantDay:-999, remoteOffer:null, helicopterFoodReminderShown:false",
 'opportunity state fields'
)
replace_once(
 'expedition.js',
 "state.observed=state.observed||[]; state.observedIndividuals=state.observedIndividuals||[]; state.homePortId=state.homePortId||'longyearbyen'; state.recentGrantTemplates=state.recentGrantTemplates||[]; state.recentGrantSites=state.recentGrantSites||[]; state.grantCooldowns=state.grantCooldowns||{};",
 "state.observed=state.observed||[]; state.observedIndividuals=state.observedIndividuals||[]; state.homePortId=state.homePortId||'longyearbyen'; state.recentGrantTemplates=state.recentGrantTemplates||[]; state.recentGrantSites=state.recentGrantSites||[]; state.recentOpportunityTemplates=state.recentOpportunityTemplates||[]; state.lastOpportunitySpawnPosition=state.lastOpportunitySpawnPosition||null; state.grantCooldowns=state.grantCooldowns||{};",
 'restore opportunity state'
)
replace_once(
 'expedition.js',
 "state.offers=(state.offers||[]).filter(Boolean).slice(0,9);\n    renderSidebar();",
 "state.offers=(state.offers||[]).filter(Boolean).slice(0,9);\n    const staleField=(state.targets||[]).filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!item.accepted&&item.status!=='completed');if(staleField.length>2){const keep=new Set(staleField.slice(-2).map(item=>item.id));state.targets=state.targets.filter(item=>!(item.kind==='opportunity'||item.kind==='weather-opportunity')||item.accepted||item.status==='completed'||keep.has(item.id));}\n    renderSidebar();",
 'prune old popup clutter on load'
)

# -------------------------------------------------------------------------
# Distance model. Keep pointIsSpaced untouched immediately after this block.
# -------------------------------------------------------------------------
replace_regex(
 'expedition.js',
 r"  function researchDistanceWindow\(template,kind,options=\{\}\) \{.*?\n  \}\n  function targetSpacingKm\(\) \{ return state\.currentVessel==='fishing'\?12:state\.currentVessel==='trawler'\?18:32; \}",
 """  function researchDistanceWindow(template,kind,options={}) {
    const vesselId=state.currentVessel,official=kind==='grant'||kind==='contract';
    const grantRanges={fishing:[25,150],trawler:[260,720],coastal:[950,1700],global:[1200,2300],icebreaker:[1400,2700],nuclear:[1600,3100]};
    const opportunityRanges={fishing:[25,100],trawler:[70,230],coastal:[170,480],global:[260,700],icebreaker:[320,850],nuclear:[380,1000]};
    const nearbyRanges={fishing:[20,70],trawler:[55,150],coastal:[120,300],global:[180,420],icebreaker:[220,520],nuclear:[260,620]};
    const range=(options.nearby?nearbyRanges:official?grantRanges:opportunityRanges)[vesselId]||(official?grantRanges.fishing:opportunityRanges.fishing);
    const career=playerCareerLevel(),careerBonus=official?0:(career>=3?60:career===2?25:0),explicit=Math.max(0,Number(template.minDistance)||0);
    let min=Math.max(range[0]+careerBonus,explicit),max=Math.max(min+20,range[1]+careerBonus);
    if(official&&Number.isFinite(template.distanceRange)&&vesselId==='fishing')max=Math.min(max,min+Math.max(80,template.distanceRange*3));
    return{min,max};
  }
  function targetSpacingKm() { return {fishing:25,trawler:65,coastal:140,global:220,icebreaker:280,nuclear:340}[state.currentVessel]||25; }""",
 'distance and spacing model'
)
# anywhere must mean flexible placement, never exactly the origin/port.
replace_once(
 'expedition.js',
 "let point=template.anywhere ? {...origin} : template.fixedDestination ? {...template.fixedDestination} : null;",
 "let point=template.fixedDestination ? {...template.fixedDestination} : null;",
 'anywhere placement semantics'
)
replace_once(
 'expedition.js',
 "const spacing=options.nearby?18:targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
 "const spacing=options.nearby?Math.max(35,targetSpacingKm()*.7):targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:window,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
 'target context distance window'
)
replace_once(
 'expedition.js',
 "for (let attempt=0; attempt<96; attempt++) {",
 "for (let attempt=0; attempt<((kind==='grant'||kind==='contract')?240:120); attempt++) {",
 'target search attempts'
)

# Grant boards: unlocked levels are <= Chief level; weight still favors current level.
replace_once(
 'expedition.js',
 "const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))",
 "const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)<=careerFloor&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))",
 'grant career filter'
)

# -------------------------------------------------------------------------
# Grant readiness: unavailable calls stay visible/grey but cannot be accepted.
# Missing equipment links directly to the matching shop card.
# -------------------------------------------------------------------------
replace_regex(
 'expedition.js',
 r"  function offerCard\(item\) \{.*?\n  \}\n  function portVesselDashboardMarkup",
 """  function missingMissionEquipment(target) {
    return [...new Set([...(target.equipment||[]),...(target.consumables||[])])].filter(id=>EQUIPMENT[id]&&!equipmentOperational(id));
  }
  function offerCard(item) {
    const specialty=item.anyScientist?'Any scientist aboard':item.specialties.map(id=>specialtyById[id]?.name).filter(Boolean).join(' / '),media=canonicalMissionMedia(item);
    const projection=missionFoodProjection(item),cap=grantLoad()>=grantCapacity(),foodUnsafe=projection.remaining<15,fuelUnsafe=!vessel().nuclearFuel&&projection.fuelRemaining<10,ready=eligible(item),missingGear=missingMissionEquipment(item),readiness=missionReadiness(item);
    const blocked=!ready||cap||foodUnsafe||fuelUnsafe;
    const label=cap?`ACTIVE GRANT LIMIT ${grantLoad()}/${grantCapacity()}`:foodUnsafe?`INSUFFICIENT FOOD · PROJECTED ${Math.max(0,Math.floor(projection.remaining))}%`:fuelUnsafe?`INSUFFICIENT FUEL · PROJECTED ${Math.max(0,Math.floor(projection.fuelRemaining))}%`:!ready?'GRANT NOT READY':'ACCEPT RESEARCH GRANT';
    const gearLinks=missingGear.length?`<div class="arx-grant-shop-links"><small>MISSING EQUIPMENT · CLICK TO SHOP</small>${missingGear.map(id=>`<button data-arx-action="shop-equipment" data-id="${id}">EQUIPMENT SHOP · ${escapeHtml(EQUIPMENT[id]?.name||id)}</button>`).join('')}</div>`:'';
    return `<article class="arx-card offer research-offer ${ready?'':'unready'}"><div class="arx-offer-thumb"><img src="${escapeHtml(media?.src||MEDIA.fieldKit.src)}" alt="${escapeHtml(media?.alt||item.title)}"></div><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(specialty)}</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p><div class="arx-grant-advance"><span><small>PAYMENT ON COMPLETION</small><b>${cash(item.reward)}</b></span></div><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class="arx-mini-label">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}${!ready?`<h4 class="arx-mini-label">WHY THIS GRANT IS LOCKED</h4>${readinessMarkup(readiness)}${gearLinks}`:''}<div class="arx-stats"><span>+${item.data} data</span><span>${item.minCrew||missionMinCrew(item)} people minimum</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span><span>~${projection.days} field days</span>${item.iceValueMultiplier>1?`<span>ICE DATA VALUE ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>Food on return ~${Math.max(0,Math.floor(projection.remaining))}%</span><span>Fuel on return ~${Math.max(0,Math.floor(projection.fuelRemaining))}%</span></div><button data-arx-action="accept" data-id="${item.id}" ${blocked?'disabled':''}>${label}</button></article>`;
  }
  function portVesselDashboardMarkup""",
 'locked grant card'
)
# Direct shop jump action.
replace_once(
 'expedition.js',
 "else if (action==='equipment') buyEquipment(id);\n    else if (action==='sell-equipment') sellEquipment(id);\n    else if (action==='accept') acceptOffer(id);",
 "else if (action==='equipment') buyEquipment(id);\n    else if (action==='sell-equipment') sellEquipment(id);\n    else if (action==='shop-equipment') { if(!state.port){toast('RETURN TO PORT TO PURCHASE EQUIPMENT');}else{activePortTab='equipment';openStoreDetail=`equipment-${id}`;portScrollTop=0;renderPort();requestAnimationFrame(()=>root?.querySelector(`[data-arx-store-details=\\\"equipment-${id}\\\"]`)?.scrollIntoView({block:'start',behavior:'smooth'}));} }\n    else if (action==='accept') acceptOffer(id);",
 'shop equipment action'
)
# Hard acceptance guard behind the disabled UI.
replace_once(
 'expedition.js',
 "const offer=state.offers.find(item=>item.id===id); if (!offer) return;\n    if (grantLoad()>=grantCapacity())",
 "const offer=state.offers.find(item=>item.id===id); if (!offer) return;\n    if(!eligible(offer)){const missing=missingMissionEquipment(offer);toast(missing.length?`GRANT NOT READY · NEED ${EQUIPMENT[missing[0]]?.name||missing[0]}`:'GRANT NOT READY · CHECK CREW AND EQUIPMENT');return;}\n    if (grantLoad()>=grantCapacity())",
 'hard grant readiness guard'
)
# Grey styling while keeping shop buttons fully usable.
replace_once(
 'expedition.js',
 ".research-offer .arx-operation-scientists img,.research-offer .arx-operation-gear img{width:34px;height:34px;flex-basis:34px}",
 ".research-offer .arx-operation-scientists img,.research-offer .arx-operation-gear img{width:34px;height:34px;flex-basis:34px}.research-offer.unready{border-color:rgba(150,166,171,.32)!important;background:rgba(45,58,64,.46)!important}.research-offer.unready>.arx-offer-thumb,.research-offer.unready>.arx-card-head,.research-offer.unready>p,.research-offer.unready>.arx-grant-advance,.research-offer.unready>.arx-stats{filter:grayscale(.75);opacity:.7}.arx-grant-shop-links{display:grid;gap:6px;margin:8px 0 11px}.arx-grant-shop-links>small{color:#c5d1d4;font-size:7px;font-weight:900;letter-spacing:.08em}.arx-grant-shop-links button{background:#78919a!important;color:#f7fbfc!important}",
 'locked grant CSS'
)

# -------------------------------------------------------------------------
# Spontaneous opportunities: max 2, movement gate, spacing and type rotation.
# -------------------------------------------------------------------------
replace_regex(
 'expedition.js',
 r"  function maybeSpawnOpportunity\(payload=\{\}\) \{.*?\n  \}\n\n  function publishPaper",
 """  function liveFieldOpportunities(){return state.targets.filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!item.accepted&&item.status!=='completed');}
  function opportunityMoveGateKm(){return{fishing:45,trawler:90,coastal:150,global:220,icebreaker:270,nuclear:330}[state.currentVessel]||45;}
  function recordOpportunitySpawn(target,position){if(!target)return;state.recentOpportunityTemplates=[target.templateId,...(state.recentOpportunityTemplates||[]).filter(id=>id!==target.templateId)].slice(0,3);if(position&&Number.isFinite(position.lat)&&Number.isFinite(position.lon))state.lastOpportunitySpawnPosition={lat:position.lat,lon:position.lon};}
  function maybeSpawnOpportunity(payload={}) {
    if(!payload.position)return null;
    if(maybeOfferProfessorGrant(payload))return null;
    const live=liveFieldOpportunities();if(live.length>=2)return null;
    const previous=state.lastOpportunitySpawnPosition,moveRequired=opportunityMoveGateKm();if(previous&&geoDistance(previous,payload.position)<moveRequired)return null;
    const recentList=state.recentOpportunityTemplates||[],recent=new Set(recentList),activeTypes=new Set(live.map(item=>item.templateId));
    const weather=payload.weather;
    if(weather?.type&&weather.type!=='clear'&&weather.eventId&&!state.weatherEventsSeen.includes(weather.eventId)){
      const careerFloor=playerCareerLevel(),weatherTemplates=TEMPLATES.filter(item=>item.weather===weather.type&&templateCareerLevel(item)<=careerFloor&&templateSupportedByVessel(item)&&!activeTypes.has(item.id)),basic=careerFloor<2?weatherTemplates.find(item=>item.anyScientist&&!recent.has(item.id)):null,advanced=weatherTemplates.filter(item=>!item.anyScientist&&eligible(item,weather)&&!recent.has(item.id));
      const template=advanced[0]||basic||weatherTemplates.find(item=>eligible(item,weather));
      state.weatherEventsSeen.push(weather.eventId);
      if(!template)return null;
      const rng=seeded(`${weather.eventId}-${template.id}`),target=buildTarget(template,payload.position,rng,'weather-opportunity',{weatherEventId:weather.eventId,iceThickness:Number(payload.iceThickness)||0,nearby:!!(payload.iceEdge||payload.iceThickness)});
      if(!target)return null;target.selected=false;state.targets.push(target);recordOpportunitySpawn(target,payload.position);toast(`WEATHER RESEARCH AVAILABLE · ${target.shortTitle}`);changed({port:false});return target;
    }
    const coastal=payload.fjord||payload.fjordScore>.38||payload.coastal||payload.coastDistanceKm<30,iceEdge=!!payload.iceEdge||payload.ice==='marginal'||payload.ice==='fast',iceThickness=Math.max(0,Number(payload.iceThickness)||0),deepIce=payload.ice==='packed'||payload.ice==='cracked'||payload.ice==='fast',inIce=iceEdge||deepIce,teamLevel=Math.max(1,...state.scientists.map(item=>careerLevel(item.career))),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length,careerFloor=playerCareerLevel(),unlockCredit=teamLevel>=3?8:teamLevel>=2?3:0;
    const basePossible=TEMPLATES.filter(item=>!item.weather&&templateSupportedByVessel(item)&&templateCareerLevel(item)<=careerFloor&&(item.unlockAfter||0)<=state.completed.length+unlockCredit&&!activeTypes.has(item.id));
    let possible=basePossible.filter(item=>!recent.has(item.id));if(!possible.length&&recentList.length)possible=basePossible.filter(item=>item.id!==recentList[0]);if(!possible.length)possible=basePossible;
    if(inIce){const icePossible=possible.filter(item=>item.iceAllowed);if(icePossible.length)possible=icePossible;}
    const allowGenericFallback=careerFloor===1&&state.currentVessel==='fishing';
    if(!possible.length){if(!allowGenericFallback)return null;const fallback=compatibleFallbackTemplate();if(recent.has(fallback.id))return null;const rng=seeded(`fallback-${payload.position.lat.toFixed(2)}-${payload.position.lon.toFixed(2)}-${Math.floor(state.elapsedDays*4)}`),target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:false,iceThickness});if(!target)return null;target.selected=false;state.targets.push(target);recordOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;}
    const weighted=possible.flatMap(template=>{let weight=1,level=templateCareerLevel(template);if(coastal&&(template.coastal||template.fjordPreferred||template.tier==='local'))weight+=payload.fjord?8:4;if(iceEdge&&template.iceAllowed)weight+=12;if(deepIce&&template.iceAllowed)weight+=20+iceThickness*10;if(inIce&&!template.iceAllowed)weight=1;if(teamLevel===2)weight+=level===2?18:level===1?3:0;if(teamLevel===2&&template.postdocOpportunity)weight+=30;if(teamLevel>=3)weight+=level===3?36:level===2?12:2;if(level===2)weight+=postdocCount*4+professorCount*3;if(level===3)weight+=professorCount*10;if(!coastal&&template.tier!=='local')weight+=3;return Array(Math.max(1,Math.round(weight))).fill(template);});
    const ready=weighted.filter(item=>eligible(item)),aspirational=weighted.filter(item=>teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item));let pool;if(!ready.length&&aspirational.length)pool=aspirational;else if(!ready.length)return null;else if(aspirational.length&&Math.random()<.25)pool=aspirational;else pool=ready;
    const rng=seeded(`${payload.position.lat.toFixed(2)}-${payload.position.lon.toFixed(2)}-${state.portVisits}-${state.completed.length}-${Math.floor(state.elapsedDays*4)}`),template=pool[Math.floor(rng()*pool.length)],target=buildTarget(template,payload.position,rng,'opportunity',{nearby:false,iceThickness});
    if(!target)return null;target.selected=false;state.targets.push(target);recordOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;
  }

  function publishPaper""",
 'opportunity spawn policy'
)

# Cache-bust stage 2.
p=Path('index.html'); text=p.read_text(); old='expedition-23x-stage1-safe'
if old not in text: raise SystemExit('stage2 cache version not found')
p.write_text(text.replace(old,'expedition-23x-safe-reimplementation'))

# -------------------------------------------------------------------------
# Map interaction and research-site placement.
# -------------------------------------------------------------------------
replace_once('game.js','function nearbyResearchTargetAt(clientX,clientY){let match=null,best=27;','function nearbyResearchTargetAt(clientX,clientY){let match=null,best=36;','research target hit radius')
replace_once(
 'game.js',
 "else if(pendingResearchArrival&&!research?.isBusy?.()){const remaining=Math.hypot(state.x-pendingResearchArrival.x,state.y-pendingResearchArrival.y);if(remaining<=RESEARCH_INTERACTION_KM){pendingResearchTargetId=null;pendingResearchArrival=null;state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;research?.openTarget?.(pending.id,{distanceKm:remaining,atSite:true,target:pending});}}",
 "else if(pendingResearchArrival&&!research?.isBusy?.()){const remaining=Math.hypot(state.x-pendingResearchArrival.x,state.y-pendingResearchArrival.y),actual=researchTargetWorld(pending).distance;if(remaining<=RESEARCH_INTERACTION_KM||actual<=RESEARCH_INTERACTION_KM){pendingResearchTargetId=null;pendingResearchArrival=null;state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;research?.selectTarget?.(pending.id);research?.openTarget?.(pending.id,{distanceKm:Math.min(actual,remaining),atSite:true,target:pending});}}",
 'reliable target arrival open'
)

# Replace site-suitability function as a unit. Official grants do not require a
# straight unobstructed line from port; players can navigate around land/ice.
replace_regex(
 'game.js',
 r"  function isResearchSiteSuitable\(point,context=\{\}\)\{.*?\n  \}\n  function findResearchSite",
 """  function isResearchSiteSuitable(point,context={}){
    if(!Number.isFinite(point?.lat)||!Number.isFinite(point?.lon)||point.lat<MIN_LAT+.08)return false;
    const site=polar(point.lat,point.lon),siteIce=iceTypeAt(site.x,site.y),siteProfile=iceNavigationProfileAt(site.x,site.y),template=context.template||{},iceAllowed=!!template.iceAllowed,official=context.kind==='grant'||context.kind==='contract';
    const researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,fieldBuffer=({fishing:35,trawler:90,coastal:170,global:250,icebreaker:320,nuclear:380}[vesselIceId()]||35)+(careerLevel-1)*20,grantBuffer=({fishing:45,trawler:120,coastal:220,global:300,icebreaker:350,nuclear:400}[vesselIceId()]||45);
    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<fieldBuffer;}))return false;
    if(official&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<grantBuffer;}))return false;
    if(context.distanceWindow&&Number.isFinite(context.origin?.lat)&&Number.isFinite(context.origin?.lon)){const d=Math.hypot(site.x-polar(context.origin.lat,context.origin.lon).x,site.y-polar(context.origin.lat,context.origin.lon).y);if(d<context.distanceWindow.min-2||d>context.distanceWindow.max+2)return false;}
    if(isLand(site.x,site.y)||!siteProfile.allowed)return false;
    if((siteIce==='packed'||siteIce==='cracked'||siteIce==='fast')&&!iceAllowed)return false;
    const clearance=coastDistance(site.x,site.y,120),shore=!!(template.shore||template.terrestrial),coastal=!!template.coastal;
    if(shore&&(clearance<.5||clearance>7))return false;if(coastal&&!shore&&(clearance<3||clearance>85))return false;if(!coastal&&!shore&&!iceAllowed&&clearance<8)return false;
    if(template.glacier){let best=Infinity;for(const g of GLACIER_SITES){const w=polar(g.lat,g.lon);best=Math.min(best,Math.hypot(site.x-w.x,site.y-w.y));}if(best>28)return false;}
    if(official)return true;
    const dx=site.x-state.x,dy=site.y-state.y,length=Math.hypot(dx,dy),steps=Math.max(24,Math.ceil(length/2)),origin=context.origin&&polar(context.origin.lat,context.origin.lon),outX=origin?state.x-origin.x:0,outY=origin?state.y-origin.y:0,outLength=Math.hypot(outX,outY);
    if(outLength>4&&(dx*outX+dy*outY)/(Math.max(1,length)*outLength)<.05)return false;
    for(let step=1;step<=steps;step++){const x=state.x+dx*step/steps,y=state.y+dy*step/steps;if(unpolar(x,y).lat<MIN_LAT+.04||isLand(x,y)||!iceNavigationProfileAt(x,y).allowed)return false;}
    return true;
  }
  function findResearchSite""",
 'research site suitability'
)
# Make fallback site search honor the requested distance window instead of only
# searching within ~210 km.
replace_once(
 'game.js',
 "const shore=!!(template.shore||template.terrestrial),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,opportunityStart=({fishing:20,trawler:60,coastal:105,global:185,icebreaker:265,nuclear:345}[vesselIceId()]||20)+(careerLevel-1)*20,distances=shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[opportunityStart,opportunityStart+30,opportunityStart+70,opportunityStart+120,opportunityStart+180]:[45,65,85,105,130,165,210]),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150];",
 "const shore=!!(template.shore||template.terrestrial),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,opportunityStart=({fishing:25,trawler:70,coastal:170,global:260,icebreaker:320,nuclear:380}[vesselIceId()]||25)+(careerLevel-1)*20,window=context.distanceWindow,windowDistances=window?[window.min,window.min+(window.max-window.min)*.2,window.min+(window.max-window.min)*.4,window.min+(window.max-window.min)*.6,window.min+(window.max-window.min)*.8,window.max]:null,distances=windowDistances||(shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[opportunityStart,opportunityStart+50,opportunityStart+110,opportunityStart+190,opportunityStart+280]:[45,65,85,105,130,165,210])),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150,180];",
 'fallback site distance search'
)

print('ARS 23x stage 2 applied')
