from pathlib import Path
import re

def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text()
    count=text.count(old)
    if count!=1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    p.write_text(text.replace(old,new,1))

def sub_once(path, pattern, replacement, label, flags=re.S):
    p=Path(path)
    text=p.read_text()
    updated,count=re.subn(pattern, lambda m: replacement, text, count=1, flags=flags)
    if count!=1:
        raise SystemExit(f"{label}: expected 1 regex match, found {count}")
    p.write_text(updated)

# Persist field-opportunity spacing/variety history.
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
    'opportunity restore defaults'
)

# Distances now reflect actual expedition capability rather than local starter-scale missions.
sub_once(
    'expedition.js',
    r"  function researchDistanceWindow\(template,kind,options=\{\}\) \{.*?\n  \}\n  function targetSpacingKm\(\) \{.*?\n  \}",
    """  function researchDistanceWindow(template,kind,options={}) {
    const vesselId=state.currentVessel,official=kind==='grant'||kind==='contract',field=kind==='opportunity'||kind==='weather-opportunity',career=playerCareerLevel();
    const grantRanges={fishing:[30,105],trawler:[240,650],coastal:[900,1600],global:[1100,2000],icebreaker:[1300,2350],nuclear:[1500,2800]};
    const fieldRanges={fishing:[25,90],trawler:[110,300],coastal:[240,680],global:[360,920],icebreaker:[470,1180],nuclear:[580,1450]};
    const base=(official?grantRanges:fieldRanges)[vesselId]||(official?grantRanges.fishing:fieldRanges.fishing);
    let min=base[0],max=base[1];
    const careerBonus=career>=3?120:career===2?55:0;min+=careerBonus;max+=careerBonus;
    if(Number.isFinite(template.minDistance))min=Math.max(min,template.minDistance);
    if(options.nearby&&field){min=Math.max(35,min*.72);max=Math.max(min+40,max*.82);}
    if(vesselId==='fishing'&&Number.isFinite(template.distanceRange))max=Math.min(max,min+Math.max(35,template.distanceRange*2.2));
    if(vesselId==='trawler'&&Number.isFinite(template.distanceRange))max=Math.min(max,min+Math.max(120,template.distanceRange*4));
    return{min:Math.max(5,min),max:Math.max(min+20,max)};
  }
  function targetSpacingKm() {
    return {fishing:18,trawler:45,coastal:110,global:180,icebreaker:240,nuclear:300}[state.currentVessel]||18;
  }""",
    'research distance scaling'
)

# "Anywhere" means flexible geography, not exactly at the player/port.
replace_once(
    'expedition.js',
    "    let point=template.anywhere ? {...origin} : template.fixedDestination ? {...template.fixedDestination} : null;",
    "    let point=template.fixedDestination ? {...template.fixedDestination} : null;",
    'flexible target origin'
)
replace_once(
    'expedition.js',
    "      if ((!template.anywhere&&!pointIsSpaced(point,avoidPoints,spacing)) || (!template.anywhere&&validator&&!validator(point,context()))) point=null;",
    "      if (!pointIsSpaced(point,avoidPoints,spacing) || (validator&&!validator(point,context()))) point=null;",
    'fixed target validation'
)

# Prune port-overlap legacy opportunities and old saves with >2 live popups.
sub_once(
    'expedition.js',
    r"  function getMapTargets\(\) \{.*?\n  \}\n  function selectTarget",
    """  function getMapTargets() {
    const remove=new Set();
    if(callbacks.researchSitePortClear){
      for(const item of state.targets)if((item.kind==='opportunity'||item.kind==='weather-opportunity')&&!callbacks.researchSitePortClear(item))remove.add(item.id);
    }
    const field=state.targets.filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!remove.has(item.id));
    if(field.length>2){
      const ranked=[...field].sort((a,b)=>Number(!!(b.accepted||b.selected||b.active))-Number(!!(a.accepted||a.selected||a.active))||state.targets.indexOf(b)-state.targets.indexOf(a));
      const keep=new Set(ranked.slice(0,2).map(item=>item.id));
      for(const item of field)if(!keep.has(item.id))remove.add(item.id);
    }
    if(remove.size){
      state.targets=state.targets.filter(item=>!remove.has(item.id));
      if(state.navigation&&remove.has(state.navigation.id))state.navigation=null;
      if(state.lastTargetContext&&remove.has(state.lastTargetContext.id))state.lastTargetContext=null;
    }
    return state.targets.map(item=>({...item,mapEligible:eligible(item,item.weather?{type:item.weather}:null)}));
  }
  function selectTarget""",
    'map target pruning'
)

# Missing equipment links jump straight to the relevant Equipment shop item.
sub_once(
    'expedition.js',
    r"  function offerCard\(item\) \{.*?\n  \}\n  function activeGrantCard",
    """  function missingMissionEquipmentIds(target) {
    const missing=[],seen=new Set();
    const visit=id=>{if(!id||seen.has(id))return;seen.add(id);const item=EQUIPMENT[id];if(!item)return;for(const required of item.requiresEquipment||[])visit(required);const aboard=item.consumable?(state.inventory[id]||0)>0:isInstalled(id);if(!aboard)missing.push(id);};
    [...new Set([...(target.equipment||[]),...(target.consumables||[])])].forEach(visit);
    return missing;
  }
  function missingEquipmentShopMarkup(target) {
    const ids=missingMissionEquipmentIds(target);if(!ids.length)return'';
    return `<div class="arx-missing-equipment-links">${ids.map(id=>`<button data-arx-action="shop-equipment" data-id="${escapeHtml(id)}">EQUIPMENT SHOP · ${escapeHtml(EQUIPMENT[id]?.name||id)}</button>`).join('')}</div>`;
  }
  function offerCard(item) {
    const specialty=item.anyScientist?'Any scientist aboard':item.specialties.map(id=>specialtyById[id]?.name).filter(Boolean).join(' / '),media=canonicalMissionMedia(item);
    const readiness=missionReadiness(item),missing=readiness.rows.find(row=>!row.ready),projection=missionFoodProjection(item),cap=grantLoad()>=grantCapacity(),foodUnsafe=projection.remaining<15,fuelUnsafe=!vessel().nuclearFuel&&projection.fuelRemaining<10,blocked=!readiness.ready;
    const label=blocked?`MISSING · ${missing?.label||'REQUIRED CAPABILITY'}`:cap?`ACTIVE GRANT LIMIT ${grantLoad()}/${grantCapacity()}`:foodUnsafe?`INSUFFICIENT FOOD · PROJECTED ${Math.max(0,Math.floor(projection.remaining))}%`:fuelUnsafe?`INSUFFICIENT FUEL · PROJECTED ${Math.max(0,Math.floor(projection.fuelRemaining))}%`:'ACCEPT RESEARCH GRANT';
    const missingNote=blocked?`<div class="arx-requirement"><b>NOT READY</b><span>${escapeHtml(missing?.detail||missing?.label||'Purchase or restore the missing capability, then return to this grant.')}</span></div>${readinessMarkup(readiness)}${missingEquipmentShopMarkup(item)}`:'';
    return `<article class="arx-card offer research-offer ${blocked?'locked':''}"><div class="arx-offer-thumb"><img src="${escapeHtml(media?.src||MEDIA.fieldKit.src)}" alt="${escapeHtml(media?.alt||item.title)}"></div><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(specialty)}</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p>${missingNote}<div class="arx-grant-advance"><span><small>PAYMENT ON COMPLETION</small><b>${cash(item.reward)}</b></span></div><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class="arx-mini-label">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class="arx-stats"><span>+${item.data} data</span><span>${item.minCrew||missionMinCrew(item)} people minimum</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span><span>~${projection.days} field days</span>${item.iceValueMultiplier>1?`<span>ICE DATA VALUE ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>Food on return ~${Math.max(0,Math.floor(projection.remaining))}%</span><span>Fuel on return ~${Math.max(0,Math.floor(projection.fuelRemaining))}%</span></div><button data-arx-action="accept" data-id="${item.id}" ${blocked||cap||foodUnsafe||fuelUnsafe?'disabled':''}>${escapeHtml(label)}</button></article>`;
  }
  function activeGrantCard""",
    'clickable missing equipment'
)
replace_once(
    'expedition.js',
    "    else if (action==='sell-equipment') sellEquipment(id);\n    else if (action==='accept') acceptOffer(id);",
    "    else if (action==='sell-equipment') sellEquipment(id);\n    else if (action==='shop-equipment') { if(!state.port){toast('EQUIPMENT SHOP AVAILABLE IN PORT');return;} activePortTab='equipment';portScrollTop=0;openStoreDetail=id;renderPort(); }\n    else if (action==='accept') acceptOffer(id);",
    'equipment shop action'
)

# Throttle field opportunities, require meaningful movement, and rotate template types.
sub_once(
    'expedition.js',
    r"  function maybeSpawnOpportunity\(payload=\{\}\) \{.*?\n  \}\n\n  function publishPaper",
    """  function activeFieldOpportunityCount(){return state.targets.filter(item=>item.kind==='opportunity'||item.kind==='weather-opportunity').length;}
  function opportunityMovementRequiredKm(){return{fishing:35,trawler:75,coastal:140,global:210,icebreaker:280,nuclear:350}[state.currentVessel]||35;}
  function rememberOpportunitySpawn(target,position){
    const templateId=target?.templateId||target?.id;if(templateId)state.recentOpportunityTemplates=[templateId,...(state.recentOpportunityTemplates||[]).filter(id=>id!==templateId)].slice(0,4);
    if(Number.isFinite(position?.lat)&&Number.isFinite(position?.lon))state.lastOpportunitySpawnPosition={lat:position.lat,lon:position.lon};
  }
  function enoughMovementForOpportunity(position){
    if(!state.lastOpportunitySpawnPosition)return true;
    return geoDistance(state.lastOpportunitySpawnPosition,position)>=opportunityMovementRequiredKm();
  }
  function maybeSpawnOpportunity(payload={}) {
    if(!payload.position)return null;
    if(maybeOfferProfessorGrant(payload))return null;
    const opportunityCap=2,weather=payload.weather;
    if(weather?.type&&weather.type!=='clear'&&weather.eventId&&!state.weatherEventsSeen.includes(weather.eventId)){
      const openSlots=Math.max(0,opportunityCap-activeFieldOpportunityCount()),careerFloor=playerCareerLevel(),weatherTemplates=TEMPLATES.filter(item=>item.weather===weather.type&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&templateSupportedByVessel(item)),basic=careerFloor<2?weatherTemplates.find(item=>item.anyScientist):null,advanced=weatherTemplates.filter(item=>!item.anyScientist&&eligible(item,weather)),spawned=[];
      for(const template of [basic,...advanced].filter(Boolean).filter((item,index,array)=>array.findIndex(other=>other.id===item.id)===index).slice(0,openSlots)){
        const rng=seeded(`${weather.eventId}-${template.id}`),target=buildTarget(template,payload.position,rng,'weather-opportunity',{weatherEventId:weather.eventId,iceThickness:Number(payload.iceThickness)||0});
        if(target){target.selected=false;state.targets.push(target);rememberOpportunitySpawn(target,payload.position);spawned.push(target);}
      }
      state.weatherEventsSeen.push(weather.eventId);
      if(spawned.length){toast(`WEATHER RESEARCH AVAILABLE · ${spawned.map(item=>item.shortTitle).join(' + ')}`);changed({port:false});return spawned[0];}
      return null;
    }
    if(activeFieldOpportunityCount()>=opportunityCap||!enoughMovementForOpportunity(payload.position))return null;
    const coastal=payload.fjord||payload.fjordScore>.38||payload.coastal||payload.coastDistanceKm<30,iceEdge=!!payload.iceEdge||payload.ice==='marginal'||payload.ice==='fast',iceThickness=Math.max(0,Number(payload.iceThickness)||0),deepIce=payload.ice==='packed'||payload.ice==='cracked'||payload.ice==='fast',inIce=iceEdge||deepIce,teamLevel=Math.max(1,...state.scientists.map(item=>careerLevel(item.career))),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length;
    const rng=seeded(`${payload.position.lat.toFixed(2)}-${payload.position.lon.toFixed(2)}-${state.portVisits}-${state.completed.length}-${Math.floor(state.elapsedDays*4)}`),unlockCredit=teamLevel>=3?8:teamLevel>=2?3:0,recent=(state.recentOpportunityTemplates||[]).slice(0,3);
    const basePossible=TEMPLATES.filter(item=>!item.weather&&templateSupportedByVessel(item)&&(playerCareerLevel()<2||templateCareerLevel(item)>=playerCareerLevel())&&(item.unlockAfter||0)<=state.completed.length+unlockCredit);
    let possible=basePossible.filter(item=>!recent.includes(item.id));
    if(!possible.length)possible=basePossible.filter(item=>!recent.slice(0,2).includes(item.id));
    if(!possible.length)possible=basePossible.filter(item=>item.id!==recent[0]);
    if(inIce){const icePossible=possible.filter(item=>item.iceAllowed);if(icePossible.length)possible=icePossible;}
    if(!possible.length){
      if(playerCareerLevel()>=2)return null;
      const fallback=compatibleFallbackTemplate();fallback.anywhere=false;fallback.minDistance=35;fallback.distanceRange=80;const target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:false,iceThickness});
      if(!target)return null;target.selected=false;state.targets.push(target);rememberOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;
    }
    const weighted=possible.flatMap(template=>{let weight=1,level=templateCareerLevel(template);if(coastal&&(template.coastal||template.fjordPreferred||template.tier==='local'))weight+=payload.fjord?5:3;if(iceEdge&&template.iceAllowed)weight+=18;if(deepIce&&template.iceAllowed)weight+=30+iceThickness*18;if(inIce&&!template.iceAllowed)weight=1;if(teamLevel===2)weight+=level===2?18:level===1?1:0;if(teamLevel===2&&template.postdocOpportunity)weight+=34;if(teamLevel>=3)weight+=level===3?42:level===2?12:1;if(level===2)weight+=postdocCount*4+professorCount*3;if(level===3)weight+=professorCount*12;if(payload.ramming&&template.iceAllowed)weight+=25;if(!coastal&&template.tier!=='local')weight+=3;return Array(Math.max(1,Math.round(weight))).fill(template);});
    const ready=weighted.filter(item=>eligible(item)),aspirational=weighted.filter(item=>teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item));let pool;
    if(!ready.length&&aspirational.length)pool=aspirational;
    else if(!ready.length)return null;
    else if(aspirational.length&&rng()<.25)pool=aspirational;
    else pool=ready;
    const template=pool[Math.floor(rng()*pool.length)];let target=buildTarget(template,payload.position,rng,'opportunity',{nearby:false,iceThickness});
    if(!target)return null;
    target.selected=false;state.targets.push(target);rememberOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;
  }

  function publishPaper""",
    'field opportunity behavior'
)

# Publication button text and mobile research attention: no green Letter alert, gold Article alert.
replace_once(
    'expedition.js',
    "    const papers=[...state.papers].reverse().slice(0,3), navOpportunity=nav?.target&&(nav.target.kind==='opportunity'||nav.target.kind==='weather-opportunity');",
    "    const papers=[...state.papers].reverse().slice(0,3), navOpportunity=nav?.target&&(nav.target.kind==='opportunity'||nav.target.kind==='weather-opportunity'), publishLabel=!level?'PUBLISH LETTER':level.id==='local'?'PUBLISH LETTER':level.id==='national'?'PUBLISH ARTICLE':'AUTO-PUBLISH BOOK';",
    'publication label variable'
)
replace_once(
    'expedition.js',
    "${level&&!level.next?'AUTO-PUBLISH READY':'PUBLISH PAPER'}",
    "${publishLabel}",
    'publication button label'
)
replace_once(
    'expedition.js',
    "    const researchToggle=root.querySelector('#arx-mobile-toggle'); researchToggle?.classList.toggle('attention',!!level&&!!level.next&&state.publicationCooldown<=0);",
    "    const researchToggle=root.querySelector('#arx-mobile-toggle'),articleReady=level?.id==='national'&&state.publicationCooldown<=0;researchToggle?.classList.remove('attention');researchToggle?.classList.toggle('article-ready',articleReady);",
    'article research attention'
)

# Clickable missing-equipment button styling + gold Article alert.
replace_once(
    'expedition.js',
    "#arx-mobile-toggle.attention{border-color:#8ef0cf!important;background:rgba(28,105,85,.96)!important;color:#ecfff8!important;box-shadow:0 0 0 2px rgba(142,240,207,.14),0 0 22px rgba(142,240,207,.48)!important}",
    "#arx-mobile-toggle.attention{border-color:#8ef0cf!important;background:rgba(28,105,85,.96)!important;color:#ecfff8!important;box-shadow:0 0 0 2px rgba(142,240,207,.14),0 0 22px rgba(142,240,207,.48)!important}#arx-mobile-toggle.article-ready{border-color:#f6d365!important;background:rgba(112,78,10,.96)!important;color:#fff4bd!important;box-shadow:0 0 0 2px rgba(246,211,101,.2),0 0 24px rgba(246,211,101,.58)!important}",
    'gold article attention style'
)
replace_once(
    'expedition.js',
    ".research-offer.locked{filter:saturate(.28);border-color:rgba(148,163,184,.3)!important}.arx-card.grant.locked",
    ".research-offer.locked{filter:saturate(.28);border-color:rgba(148,163,184,.3)!important}.arx-missing-equipment-links{display:grid;gap:6px;margin:8px 0}.arx-missing-equipment-links button{border:1px solid rgba(125,211,252,.4)!important;background:rgba(24,76,98,.78)!important;color:#bcefff!important;text-align:left!important;cursor:pointer!important}.arx-card.grant.locked",
    'equipment link style'
)

# Allow auto-opening a site while the sidebar is open.
replace_once(
    'expedition.js',
    "    isBusy:()=>!!activeOperation||!!root?.querySelector('.arx-modal.open')||!!root?.querySelector('.arx-sidebar.open')",
    "    canAutoOpenTarget:()=>!activeOperation&&!root?.querySelector('.arx-modal.open'),\n    isBusy:()=>!!activeOperation||!!root?.querySelector('.arx-modal.open')||!!root?.querySelector('.arx-sidebar.open')",
    'target auto-open API'
)

# Port buffers: field popups stay well away; grants on larger vessels are never generated in/near port.
sub_once(
    'game.js',
    r"  function researchSitePortClear\(point\)\{.*?\n  \}",
    """  function researchSitePortClear(point){
    if(!Number.isFinite(point?.lat)||!Number.isFinite(point?.lon))return false;
    const site=polar(point.lat,point.lon),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,base=({fishing:70,trawler:160,coastal:360,global:540,icebreaker:700,nuclear:900}[vesselIceId()]||70),buffer=base+(careerLevel-1)*45;
    return cityLabels.every(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)>=buffer;});
  }""",
    'field port exclusion'
)
replace_once(
    'game.js',
    "    if((context.kind==='grant'||context.kind==='contract')&&Number.isFinite(context.origin?.lat)&&Number.isFinite(context.origin?.lon)){const origin=polar(context.origin.lat,context.origin.lon);if(Math.hypot(origin.x-site.x,origin.y-site.y)<20)return false;}",
    "    if(context.kind==='grant'||context.kind==='contract'){const grantPortBuffer={fishing:35,trawler:220,coastal:700,global:850,icebreaker:1000,nuclear:1200}[vesselIceId()]||35;if(cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<grantPortBuffer;}))return false;}",
    'grant port exclusion'
)

# Research markers are easier to tap and arrivals use the actual target distance.
replace_once('game.js',"  const RESEARCH_INTERACTION_KM=10,","  const RESEARCH_INTERACTION_KM=14,",'research interaction radius')
replace_once(
    'game.js',
    "if(d<=27&&d<best){best=d;hit={target,distance:item.distance};}",
    "if(d<=36&&d<best){best=d;hit={target,distance:item.distance};}",
    'research marker tap radius'
)
sub_once(
    'game.js',
    r"  function updateResearchNavigation\(\)\{.*?\n  \}\n  function drawResearchGuidance",
    """  function updateResearchNavigation(){
    if(pendingResearchTargetId){
      const pending=researchTargets().find(item=>item.id===pendingResearchTargetId);
      if(!pending){pendingResearchTargetId=null;pendingResearchArrival=null;}
      else if(pendingResearchArrival&&(research?.canAutoOpenTarget?.()??!research?.isBusy?.())){
        const waypointRemaining=Math.hypot(state.x-pendingResearchArrival.x,state.y-pendingResearchArrival.y),siteItem=researchTargetWorld(pending),arrived=siteItem.distance<=RESEARCH_INTERACTION_KM*1.35||waypointRemaining<=RESEARCH_INTERACTION_KM||(!state.commandActive&&siteItem.distance<=RESEARCH_INTERACTION_KM*2);
        if(arrived){pendingResearchTargetId=null;pendingResearchArrival=null;state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;research?.openTarget?.(pending.id,{distanceKm:siteItem.distance,atSite:true,target:pending});}
      }
    }
    const target=selectedResearchTarget();if(!target){research?.updateNavigation?.(null);return;}const item=researchTargetWorld(target),dx=item.w.x-state.x,dy=item.w.y-state.y,bearing=(Math.atan2(dx,dy)*180/Math.PI+360)%360;research?.updateNavigation?.({id:target.id,target,distanceKm:item.distance,bearingDeg:bearing});
  }
  function drawResearchGuidance""",
    'research arrival reliability'
)

# Make the viewport footprint truly circular instead of the diagonal-sized pseudo-square footprint.
replace_once(
    'game.js',
    "const viewRadius=Math.min(radius,Math.max(9,Math.hypot(viewW,viewH)/2));",
    "const viewRadius=Math.min(radius,Math.max(9,Math.min(viewW,viewH)/2));",
    'minimap circular viewport'
)

# Rebuild WebAudio output with an audible master bus and confirmation chime after unlock.
sub_once(
    'game.js',
    r"  const sound=\(\(\)=>\{.*?\n  \}\)\(\);",
    """  const sound=(()=>{
    let ac=null,masterGain=null,waveSource=null,waveGain=null,lastCrack=0,unlockChimed=false,unlockPromise=null;
    const output=()=>masterGain||ac?.destination;
    const ensure=()=>{
      if(ac&&ac.state!=='closed')return ac;
      try{
        const AudioCtor=window.AudioContext||window.webkitAudioContext;if(!AudioCtor)throw new Error('WebAudio unavailable');
        ac=new AudioCtor({latencyHint:'interactive'});masterGain=ac.createGain();masterGain.gain.value=1.3;const compressor=ac.createDynamicsCompressor();compressor.threshold.value=-20;compressor.knee.value=18;compressor.ratio.value=4;compressor.attack.value=.004;compressor.release.value=.18;masterGain.connect(compressor).connect(ac.destination);
        const seconds=5,buffer=ac.createBuffer(1,ac.sampleRate*seconds,ac.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*(.38+.28*Math.sin(i/6200));waveSource=ac.createBufferSource();waveSource.buffer=buffer;waveSource.loop=true;const filter=ac.createBiquadFilter();filter.type='lowpass';filter.frequency.value=430;waveGain=ac.createGain();waveGain.gain.value=0;waveSource.connect(filter).connect(waveGain).connect(masterGain);waveSource.start();
      }catch(error){console.warn('ARS AUDIO INITIALIZATION FAILED',error);ac=null;masterGain=null;waveSource=null;waveGain=null;}
      return ac;
    };
    const tone=(freq=440,duration=.15,gain=.08,when=0,type='sine')=>{const c=ensure();if(!c||c.state!=='running')return;const o=c.createOscillator(),g=c.createGain(),start=c.currentTime+when;o.type=type;o.frequency.setValueAtTime(freq,start);g.gain.setValueAtTime(.0001,start);g.gain.exponentialRampToValueAtTime(Math.min(.45,gain*2.15),start+.012);g.gain.exponentialRampToValueAtTime(.0001,start+duration);o.connect(g).connect(output());o.start(start);o.stop(start+duration+.03);};
    const burst=(duration=.3,gain=.06,low=300,high=2200,when=0)=>{const c=ensure();if(!c||c.state!=='running')return;const b=c.createBuffer(1,Math.ceil(c.sampleRate*duration),c.sampleRate),d=b.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*(1-i/d.length);const src=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain();src.buffer=b;f.type='bandpass';f.frequency.value=(low+high)/2;f.Q.value=.7;g.gain.value=Math.min(.4,gain*1.9);src.connect(f).connect(g).connect(output());src.start(c.currentTime+when);};
    const ferryHorn=(when=0,duration=2.55)=>{const c=ensure();if(!c||c.state!=='running')return;const start=c.currentTime+when,filter=c.createBiquadFilter(),hornGain=c.createGain();filter.type='lowpass';filter.frequency.setValueAtTime(760,start);filter.Q.value=.55;hornGain.gain.setValueAtTime(.0001,start);hornGain.gain.exponentialRampToValueAtTime(.18,start+.18);hornGain.gain.setValueAtTime(.18,start+duration*.72);hornGain.gain.exponentialRampToValueAtTime(.0001,start+duration);filter.connect(hornGain).connect(output());for(const[freq,level,type,detune]of[[92,.95,'sine',-3],[138,.62,'triangle',2],[184,.38,'sine',-2],[276,.18,'triangle',3]]){const o=c.createOscillator(),g=c.createGain();o.type=type;o.detune.value=detune;o.frequency.setValueAtTime(freq*.985,start);o.frequency.linearRampToValueAtTime(freq,start+.22);g.gain.value=level;o.connect(g).connect(filter);o.start(start);o.stop(start+duration+.04);}burst(.22,.05,90,700,when);};
    const playNow=type=>{switch(type){case'cash':case'cash-in':case'cash-out':burst(.05,.075,1500,5200);tone(1480,.085,.08,.015,'square');tone(2080,.17,.07,.045,'sine');break;case'data':tone(980,.08,.065,0,'square');tone(1260,.08,.05,.07,'square');break;case'paper-accepted':for(let i=0;i<7;i++)burst(.35,.055,500,3500,i*.07);tone(523,.5,.11,.05);tone(659,.5,.09,.12);tone(784,.6,.09,.2);break;case'paper-rejected':tone(430,.5,.095);tone(350,.6,.085,.15);tone(270,.75,.08,.3);break;case'port':for(const offset of[0,.86])ferryHorn(offset,2.35);break;case'depart':ferryHorn(0,1.65);break;case'ice':burst(.24,.09,80,900);tone(135,.22,.055,.01,'sawtooth');break;case'whale':tone(145,.85,.085,0,'sine');tone(118,.75,.07,.18,'sine');break;case'bird':tone(1650,.08,.045,0,'sine');tone(2100,.07,.04,.09,'sine');break;case'seal':tone(310,.12,.055,0,'square');tone(250,.18,.045,.1,'triangle');break;case'mammal':tone(420,.1,.045);tone(520,.1,.04,.09);break;case'fish':burst(.08,.035,900,3200);break;default:tone(720,.08,.035);}};
    const unlock=()=>{const c=ensure();if(!c)return Promise.resolve(false);if(unlockPromise)return unlockPromise;unlockPromise=Promise.resolve(c.state==='running'?undefined:c.resume()).then(()=>{const ok=c.state==='running';if(ok&&!unlockChimed){unlockChimed=true;tone(660,.1,.075,0,'sine');tone(880,.16,.07,.08,'sine');}return ok;}).catch(error=>{console.warn('ARS AUDIO UNLOCK FAILED',error);return false;}).finally(()=>{unlockPromise=null;});return unlockPromise;};
    const play=type=>{const c=ensure();if(!c)return;if(c.state!=='running'){unlock().then(ok=>{if(ok)playNow(type);});return;}playNow(type);};
    const update=paused=>{if(!ac||ac.state!=='running')return;const moving=!paused&&state.started&&!state.gameOver,waveTarget=moving?(state.moving?.025:.012):0;if(waveGain)waveGain.gain.setTargetAtTime(waveTarget,ac.currentTime,.35);const now=performance.now();if(!paused&&state.ramming&&now-lastCrack>900){lastCrack=now;playNow('ice');}};
    return{unlock,play,update};
  })();""",
    'audio engine'
)

# More browser gesture paths for mobile/Safari audio.
replace_once(
    'game.js',
    "  document.addEventListener('pointerdown',()=>sound.unlock(),{capture:true,passive:true});\n  document.addEventListener('keydown',()=>sound.unlock(),{capture:true});",
    "  document.addEventListener('pointerdown',()=>sound.unlock(),{capture:true,passive:true});\n  document.addEventListener('click',()=>sound.unlock(),{capture:true,passive:true});\n  document.addEventListener('touchend',()=>sound.unlock(),{capture:true,passive:true});\n  document.addEventListener('keydown',()=>sound.unlock(),{capture:true});",
    'audio unlock gestures'
)

# Force a circular expanded chart at every CSS cascade layer.
style=Path('style.css')
css=style.read_text()
marker='/* ARS expedition-23u circular navigation chart */'
if marker not in css:
    css += "\n\n"+marker+"\n#minimap,.minimap.expanded #minimap{border-radius:50%!important;clip-path:circle(50% at 50% 50%)!important;overflow:hidden!important}\n"
style.write_text(css)

# Cache bust all core assets for this pass.
index=Path('index.html')
html=index.read_text()
html=html.replace('expedition-23t-grants-vessels-map','expedition-23u-field-opportunity-audio')
index.write_text(html)
