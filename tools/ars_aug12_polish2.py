from pathlib import Path

EXP=Path('expedition.js')
GAME=Path('game.js')
INDEX=Path('index.html')

def replace_once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old,new,1)

def replace_block(text, start, end, new, label):
    s=text.find(start)
    if s<0: raise SystemExit(f'{label}: start marker missing')
    e=text.find(end,s)
    if e<0: raise SystemExit(f'{label}: end marker missing')
    return text[:s]+new.rstrip()+"\n"+text[e:]

# ---------------- expedition.js ----------------
e=EXP.read_text()

e=replace_once(e,"  let devCareerOverride = null;\n","  let devCareerOverride = null;\n  let relocationPortCache = {key:null,ports:[]};\n",'relocation cache variable')

mission_helpers=r'''  function missionMinCrew(template) {
    const title=String(template?.title||'').toLowerCase();
    if ((template?.berthReserve||0)>0 && (template?.stationDelivery||template?.anyScientist||/deliver|transport|supply|field team|team deployment/.test(title))) return 1;
    const explicit=Number(template?.minCrew); if(Number.isFinite(explicit)&&explicit>0)return Math.max(1,Math.round(explicit));
    const level=templateCareerLevel(template),bounds={1:[1,3],2:[3,10],3:[10,20]}[level]||[1,3];
    const rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level).map(item=>Number(item.reward)||0).filter(value=>value>0);
    const low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low,reward=Math.max(low,Number(template?.reward)||low),t=high>low?clamp((reward-low)/(high-low),0,1):0;
    return Math.round(bounds[0]+(bounds[1]-bounds[0])*t);
  }
  function templateRelativeReward(template) {
    const level=templateCareerLevel(template),rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level&&!item.weather).map(item=>Number(item.reward)||0).filter(Boolean),low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low;
    return high>low?clamp(((Number(template?.reward)||low)-low)/(high-low),0,1):0;
  }
  function missionSpecialistRequirements(template) {
    if(Array.isArray(template?.specialistRequirements))return clone(template.specialistRequirements);
    if(template?.anyScientist)return [];
    const level=templateCareerLevel(template),specialties=[...new Set(template?.specialties||[])];
    if(level<2||specialties.length<2)return [];
    const relative=templateRelativeReward(template),seed=[...String(template?.id||template?.title||'')].reduce((sum,ch)=>(sum*31+ch.charCodeAt(0))>>>0,17),interdisciplinary=relative>=.42&&(seed%100)<(level>=3?62:42);
    if(!interdisciplinary)return [];
    const count=level>=3&&specialties.length>=3&&relative>=.7&&(seed%3!==1)?3:2,minCareer=level>=3?'professor':'postdoc';
    return specialties.slice(0,count).map(specialty=>({specialties:[specialty],minCareer,count:1}));
  }
  function expandedSpecialistNeeds(template) {
    const needs=[];for(const requirement of missionSpecialistRequirements(template))for(let i=0;i<(requirement.count||1);i++)needs.push(requirement);return needs;
  }
  function specialistAssignment(template) {
    const needs=expandedSpecialistNeeds(template);if(!needs.length)return {missing:0,ids:[]};let best=[];
    const walk=(index,used,ids)=>{if(index>=needs.length){if(ids.length>best.length)best=[...ids];return;}walk(index+1,used,ids);const need=needs[index];for(const scientist of state.scientists){if(used.has(scientist.id)||careerLevel(scientist.career)<careerLevel(need.minCareer)||!(need.specialties||[]).includes(scientist.specialty))continue;used.add(scientist.id);ids.push(scientist.id);walk(index+1,used,ids);ids.pop();used.delete(scientist.id);}};walk(0,new Set(),[]);return {missing:Math.max(0,needs.length-best.length),ids:best};
  }
  function specialistRequirementsMet(template) { return specialistAssignment(template).missing===0; }
  function missionFitsCurrentVessel(template,ship=vessel()) { return missionMinCrew(template)+Math.max(0,Number(template?.berthReserve)||0)<=ship.berths; }
  function vesselRewardScale(ship=vessel()) {
    const starter=VESSELS.fishing,baseCapital=Math.max(1,vesselPurchasePrice(starter)||120000),capital=Math.max(baseCapital,vesselPurchasePrice(ship)||ship.marketPrice||baseCapital);
    const operatingCost=s=>Math.max(1,(s.nuclearFuel?0:s.fuelCapacity*s.fuelUnitCost)+s.foodCapacity*s.foodUnitCost+s.supplyCapacity*250),baseOperating=operatingCost(starter),operating=operatingCost(ship);
    const capitalIndex=1+Math.max(0,Math.log10(capital/baseCapital))*1.35,operatingIndex=1+Math.max(0,Math.log10(operating/baseOperating))*.9;
    return clamp(capitalIndex*.7+operatingIndex*.3,1,12);
  }
  function wildlifeObservationData(ship=vessel()) { return ({fishing:2,trawler:4,coastal:8,global:16,icebreaker:32,nuclear:64}[ship.id]||2); }
'''
e=replace_block(e,'  function missionMinCrew(template) {','  function payroll() {',mission_helpers,'mission helper block')

e=replace_once(e,"  function grantCapacity() { return Math.max(1,state.scientists.length); }","  function grantCapacity() { const level=playerCareerLevel();if(level<2)return Math.max(1,state.scientists.length);const postdocs=state.scientists.filter(item=>item.career==='postdoc').length,professors=state.scientists.filter(item=>item.career==='professor').length;return Math.max(2,postdocs*2+professors*3); }",'grant capacity')

fleet_block=r'''  function vesselsForPort(port=state.port) {
    if (isRussianPort(port)) return [VESSELS.nuclear];
    return ['fishing','trawler','coastal','global','icebreaker'].map(id=>VESSELS[id]);
  }
  function vesselForSaleHere(id,port=state.port) {
    if (id==='nuclear') return isRussianPort(port);
    return !isRussianPort(port)&&['fishing','trawler','coastal','global','icebreaker'].includes(id);
  }
'''
e=replace_block(e,'  function vesselsForPort(port=state.port) {','  function vesselScienceTier(ship=vessel()) {',fleet_block,'fleet market block')

e=replace_once(e,"message:'Congratulations, you finally earned your PhD degree! Two published papers and 100 citations have earned postdoc status. You may now hire postdocs (one per 100 citations), purchase medium-duty science systems, commission a coastal-class research vessel, relocate your expedition to ports around the Arctic, and receive much more sophisticated postdoc-level research programs.'","message:`Congratulations, you finally earned your PhD degree! You reached postdoc status with ${state.papers.length} published papers and ${Math.floor(state.citations)} citations. You may now hire postdocs (one per 100 citations), purchase medium-duty science systems, commission a coastal-class research vessel, relocate your expedition to ports around the Arctic, and receive much more sophisticated postdoc-level research programs.`",'dynamic PhD message')

eligible_old="""  function eligible(template, weather=null) {\n    if (!hasSpecialty(template)) return false;\n    if ((template.equipment || []).some(id => !equipmentOperational(id))) return false;\n    if (state.scientists.length<missionMinCrew(template)) return false;\n    if (template.weather && weather && template.weather !== weather.type) return false;\n    return true;\n  }"""
eligible_new="""  function eligible(template, weather=null) {\n    if (!hasSpecialty(template)) return false;\n    if (!missionFitsCurrentVessel(template)) return false;\n    if (!specialistRequirementsMet(template)) return false;\n    if ((template.equipment || []).some(id => !equipmentOperational(id))) return false;\n    if (state.scientists.length<missionMinCrew(template)) return false;\n    if (template.weather && weather && template.weather !== weather.type) return false;\n    return true;\n  }"""
e=replace_once(e,eligible_old,eligible_new,'eligible function')

# Slightly stronger range separation as vessels grow.
e=replace_once(e,"const ranges={fishing:[5,48],trawler:[8,110],coastal:[18,260],global:[35,520],icebreaker:[55,880],nuclear:[70,1200]}","const ranges={fishing:[5,48],trawler:[10,125],coastal:[28,330],global:[65,700],icebreaker:[95,1050],nuclear:[125,1450]}",'distance ranges')

# Build targets: prevent impossible berth combinations, carry specialist requirements/lifetimes, and scale cash with vessel economics.
e=replace_once(e,"  function buildTarget(template, origin, rng, kind='grant', options={}) {\n    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03);","  function buildTarget(template, origin, rng, kind='grant', options={}) {\n    if(!missionFitsCurrentVessel(template))return null;\n    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03), rewardScale=vesselRewardScale();",'build target header')
e=replace_once(e,"equipment:[...(template.equipment || [])], consumables:[...(template.consumables || [])], minCrew:missionMinCrew(template),","equipment:[...(template.equipment || [])], consumables:[...(template.consumables || [])], minCrew:missionMinCrew(template), specialistRequirements:missionSpecialistRequirements(template),",'target specialist requirements')
e=replace_once(e,"reward:Math.round(template.reward*scale*(kind === 'opportunity' ? 1.6 : 2)*iceValueMultiplier),","reward:Math.round(template.reward*scale*(kind === 'opportunity'||kind==='weather-opportunity' ? 1.6 : 2)*iceValueMultiplier*rewardScale),",'target reward scaling')
e=replace_once(e,"anywhere:!!template.anywhere, stationDelivery:!!template.stationDelivery, berthReserve:template.berthReserve||0, shore:!!template.shore, glacier:!!template.glacier, terrestrial:!!template.terrestrial, fjordPreferred:!!template.fjordPreferred, siteName:point.siteName||null, iceValueMultiplier, status:'active', kind, selected:false,","anywhere:!!template.anywhere, stationDelivery:!!template.stationDelivery, berthReserve:template.berthReserve||0, shore:!!template.shore, glacier:!!template.glacier, terrestrial:!!template.terrestrial, fjordPreferred:!!template.fjordPreferred, siteName:point.siteName||null, iceValueMultiplier, status:'active', kind, selected:false, discoveredAtDay:state.elapsedDays, expiresAtDay:kind==='weather-opportunity'?state.elapsedDays+2.25:kind==='opportunity'?state.elapsedDays+3+rng()*2:null, weatherEventId:options.weatherEventId||null,",'target lifetime fields')

# Port grants: after postdoc, stop offering graduate-tier work; fresh purchases/hiring already call fresh generation.
e=replace_once(e,"const available=TEMPLATES.filter(item=>!item.weather&&eligible(item)&&!activeTemplates.has(item.id)","const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&eligible(item)&&!activeTemplates.has(item.id)",'port career floor')
e=replace_once(e,"const teamLevel=Math.max(1,...state.scientists.map(item=>careerLevel(item.career))),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length","const teamLevel=playerCareerLevel(),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length",'offer team level')
e=replace_once(e,"if(!state.offers.length){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback)state.offers.push(fallback);}","if(!state.offers.length&&playerCareerLevel()<2){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback)state.offers.push(fallback);}",'postdoc fallback removal')

# Trade-down UI should show cash returned, not a zero commission.
e=replace_once(e,"listPrice=vesselPurchasePrice(item),due=Math.max(0,listPrice-credit),grantBlocked=","listPrice=vesselPurchasePrice(item),net=listPrice-credit,due=Math.max(0,net),refund=Math.max(0,-net),grantBlocked=",'trade net calculation')
e=replace_once(e,"text:`Cash after trade credit: need ${cash(due)}`","text:refund>0?`Trade credit exceeds list price · receive ${cash(refund)}`:`Cash after trade credit: need ${cash(due)}`",'trade check label')
e=replace_once(e,"reason=active?'EQUIPPED':disabled?'REQUIREMENTS NOT MET':`TRADE IN & COMMISSION · ${cash(due)}`","reason=active?'EQUIPPED':disabled?'REQUIREMENTS NOT MET':refund>0?`TRADE IN & RECEIVE ${cash(refund)}`:`TRADE IN & COMMISSION · ${cash(due)}`",'trade action label')
e=replace_once(e,"item.id==='nuclear'?'Sold only in Murmansk':'Conventional vessels sold in Longyearbyen'","item.id==='nuclear'?'Sold in Russian Arctic ports':'Conventional vessels sold at non-Russian Arctic ports'",'shipyard sales text')

# Equipment categories.
cat_block=r'''  function equipmentCategory(item) {
    const text=`${item?.id||''} ${item?.name||''} ${(item?.specialties||[]).join(' ')}`.toLowerCase();
    if(item?.consumable)return 'Consumables & Sample Supplies';
    if(/drone|aerostat|atmos|weather|radar|radiometer|lidar|starlink|satellite/.test(text))return 'Atmosphere, Remote Sensing & Communications';
    if(/mooring|glider|float|auv|rov|autonomous|drifter/.test(text))return 'Autonomous Platforms & Moorings';
    if(/plankton|fish|fisher|edna|biology|ecology|mammal|hydrophone|net/.test(text))return 'Biology & Ecology';
    if(/ice|snow|sediment|core|magnet|geophys|seafloor/.test(text))return 'Sea Ice, Seafloor & Geophysics';
    if(/ctd|adcp|xbt|winch|current|salin|echo|sonar|hydrograph|water/.test(text))return 'Oceanography & Hydrography';
    return 'General Science Systems';
  }
  function categorizedEquipmentMarkup(items) {
    const order=['Oceanography & Hydrography','Biology & Ecology','Sea Ice, Seafloor & Geophysics','Atmosphere, Remote Sensing & Communications','Autonomous Platforms & Moorings','Consumables & Sample Supplies','General Science Systems'],groups=new Map();
    for(const item of items){const category=equipmentCategory(item);if(!groups.has(category))groups.set(category,[]);groups.get(category).push(item);}
    return order.filter(category=>groups.has(category)).map(category=>`<section class="arx-equipment-category"><h3 style="margin-top:18px">${escapeHtml(category)}</h3><div class="arx-grid arx-store-list">${groups.get(category).map(equipmentCard).join('')}</div></section>`).join('');
  }
  function equipmentCatalogMarkup(ship=vessel()) {
    const items=equipmentForVessel(ship), aboard=items.filter(item=>isInstalled(item.id)||(item.consumable&&(state.inventory[item.id]||0)>0)), available=items.filter(item=>!aboard.includes(item)), usage=slotUsage();
    return `<div class="arx-slot-banner"><b>SCIENCE DECK</b><span>${slotSummary(ship,usage)} · helidecks ${helideckUsage()}/${ship.helidecks}</span><small>Trade-in value is 100% of purchase price, so swapping equipment is encouraged.</small></div><h3>Already aboard</h3><div class="arx-grid arx-store-list">${aboard.map(equipmentCard).join('')||'<div class="arx-empty"><b>No portable science equipment aboard.</b></div>'}</div><div class="arx-empty-slots">${emptySlotMarkup(ship)}</div><h3 style="margin-top:22px">Available equipment by category</h3>${categorizedEquipmentMarkup(available)||'<div class="arx-empty"><b>No further compatible equipment at this port.</b></div>'}`;
  }
'''
e=replace_block(e,'  function equipmentCatalogMarkup(ship=vessel()) {','  function missionFoodProjection(item) {',cat_block,'equipment categories')

# Mission readiness includes explicit interdisciplinary specialist rows and names the player for any-scientist jobs.
readiness_block=r'''  function missionReadiness(target) {
    const projection=missionFoodProjection(target), rows=[],player=playerScientist();
    const teamReady=hasSpecialty(target);
    rows.push({label:'Qualified science team',ready:teamReady,detail:target.anyScientist?`${player?.name||'You'} · Chief Scientist qualifies`:target.specialties.map(id=>specialtyById[id]?.name||id).join(' / ')});
    const requirements=missionSpecialistRequirements(target);
    if(requirements.length){const assignment=specialistAssignment(target),names=requirements.map(requirement=>`${CAREERS[requirement.minCareer]?.name||requirement.minCareer}: ${(requirement.specialties||[]).map(id=>specialtyById[id]?.name||id).join(' / ')}`);rows.push({label:`Interdisciplinary specialists · ${requirements.length}`,ready:assignment.missing===0,detail:assignment.missing?`${assignment.missing} specialist position${assignment.missing===1?'':'s'} still missing · ${names.join(' + ')}`:names.join(' + ')});}
    const minCrew=target.minCrew||missionMinCrew(target);
    rows.push({label:'Minimum expedition team',ready:state.scientists.length>=minCrew,detail:`${state.scientists.length} aboard · ${minCrew} required`});
    if (target.berthReserve) {
      const free=Math.max(0,vessel().berths-state.scientists.length);
      rows.push({label:'Berths for visiting field team',ready:free>=target.berthReserve,detail:`${free} free · ${target.berthReserve} required`});
    }
    for (const id of target.equipment||[]) {
      const item=EQUIPMENT[id], ready=equipmentOperational(id);
      rows.push({label:item?.name||id,ready,detail:ready?'Aboard and operable':isInstalled(id)||state.inventory[id]?'Aboard, but the required operator or support system is missing':'Not aboard'});
    }
    rows.push({label:'Food reserve',ready:projection.remaining>=5,detail:`Projected ${Math.round(projection.remaining)}% after mission`});
    if(!vessel().nuclearFuel)rows.push({label:'Fuel reserve',ready:projection.fuelRemaining>=3,detail:`Projected ${Math.round(projection.fuelRemaining)}% after mission`});
    return {ready:rows.every(row=>row.ready),rows,projection};
  }
'''
e=replace_block(e,'  function missionReadiness(target) {','  function readinessMarkup',readiness_block,'mission readiness')

# Prefer the player as the named participant when literally anyone can do the task; include matched interdisciplinary specialists otherwise.
participant_block=r'''  function participantIdsFor(target) {
    const player=playerScientist();if(target?.anyScientist)return player?[player.id]:[];
    const specialistIds=specialistAssignment(target).ids||[],ids=[...specialistIds];
    const candidates=state.scientists.filter(item=>(target.specialties||[]).includes(item.specialty)).sort((a,b)=>careerLevel(b.career)-careerLevel(a.career));
    for(const item of candidates)if(!ids.includes(item.id))ids.push(item.id);
    return ids.length?ids:(player?[player.id]:[]);
  }
'''
e=replace_block(e,'  function participantIdsFor(target) {','  function workRate',participant_block,'participant selection')

# Vessel compatibility + aspirational crew/specialist opportunities.
support_block=r'''  function templateSupportedByVessel(template) {
    if (template.transect&&stationCountFor(template)<2) return false;
    if (!missionFitsCurrentVessel(template)) return false;
    return (template.equipment||[]).every(id=>equipmentPossibleOnShip(EQUIPMENT[id],vessel()));
  }
  function teamCouldDoWithEquipment(template) {
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&!eligible(template)&&(template.equipment||[]).some(id=>!equipmentOperational(id));
  }
  function teamCouldDoWithMoreCrew(template) {
    const specialistGap=specialistAssignment(template).missing;
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&(template.equipment||[]).every(id=>equipmentOperational(id))&&((state.scientists.length<missionMinCrew(template))||(specialistGap>0&&specialistGap<=1));
  }
'''
e=replace_block(e,'  function templateSupportedByVessel(template) {','  function maybeOfferProfessorGrant',support_block,'template support block')

# Random/weather opportunities: finite lifespan, no auto-selection/arrows, current-career work only after PhD.
e=replace_once(e,"const weatherTemplates=TEMPLATES.filter(item=>item.weather===weather.type), basic=weatherTemplates.find(item=>item.anyScientist), advanced=weatherTemplates.filter(item=>!item.anyScientist&&eligible(item,weather));","const careerFloor=playerCareerLevel(),weatherTemplates=TEMPLATES.filter(item=>item.weather===weather.type&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&templateSupportedByVessel(item)), basic=careerFloor<2?weatherTemplates.find(item=>item.anyScientist):null, advanced=weatherTemplates.filter(item=>!item.anyScientist&&eligible(item,weather));",'weather career filtering')
e=replace_once(e,"target=buildTarget(template,payload.position,rng,'weather-opportunity');\n        if (target) { target.selected=spawned.length===0; state.targets.push(target); spawned.push(target); }","target=buildTarget(template,payload.position,rng,'weather-opportunity',{weatherEventId:weather.eventId});\n        if (target) { target.selected=false; state.targets.push(target); spawned.push(target); }",'weather target selection')
e=replace_once(e,"const opportunityCap=inIce?12:8;","const opportunityCap=4;",'opportunity cap')
e=replace_once(e,"let possible=TEMPLATES.filter(item=>!item.weather&&templateSupportedByVessel(item)&&(item.unlockAfter||0)<=state.completed.length+unlockCredit&&!recent.has(item.id));","let possible=TEMPLATES.filter(item=>!item.weather&&templateSupportedByVessel(item)&&(playerCareerLevel()<2||templateCareerLevel(item)>=playerCareerLevel())&&(item.unlockAfter||0)<=state.completed.length+unlockCredit&&!recent.has(item.id));",'random opportunity career floor')
e=replace_once(e,"    if(!state.targets.some(item=>item.selected))target.selected=true;\n    state.targets.push(target);","    target.selected=false;\n    state.targets.push(target);",'random opportunity auto selection')

# Expire random opportunities; weather opportunities also vanish when their weather event is no longer active.
needle="    state.recentGrantSites=(state.recentGrantSites||[]).filter(site=>state.elapsedDays-(site.day||0)<90).slice(0,18);\n"
insert=needle+"    const activeWeather=environment?.weather||null,expiredOpportunityIds=new Set();\n    state.targets=state.targets.filter(target=>{if(target.kind!=='opportunity'&&target.kind!=='weather-opportunity')return true;const timedOut=Number.isFinite(target.expiresAtDay)&&state.elapsedDays>=target.expiresAtDay,weatherGone=target.kind==='weather-opportunity'&&activeWeather&&(activeWeather.type==='clear'||(target.weatherEventId&&activeWeather.eventId!==target.weatherEventId));if(timedOut||weatherGone){expiredOpportunityIds.add(target.id);return false;}return true;});\n    if(state.navigation?.id&&expiredOpportunityIds.has(state.navigation.id))state.navigation=null;\n"
e=replace_once(e,needle,insert,'opportunity expiry')

# Wildlife observations give progressively more data on larger vessels.
e=replace_once(e,"if (firstIndividual) { state.observedIndividuals.push(individualId); addData(2); addLog(`Observed ${species} at ${formatLatLon(info.lat,info.lon)} · +2 data.`); }","if (firstIndividual) { const wildlifeData=wildlifeObservationData(); state.observedIndividuals.push(individualId); addData(wildlifeData); addLog(`Observed ${species} at ${formatLatLon(info.lat,info.lon)} · +${wildlifeData} data.`); }",'wildlife data reward')
e=replace_once(e,"${firstIndividual?'<p class=\"arx-observation-note\">New individual observation · +2 data added to the expedition archive.</p>':'<p class=\"arx-observation-note\">This individual was already logged; no duplicate data awarded.</p>'}","${firstIndividual?`<p class=\"arx-observation-note\">New individual observation · +${wildlifeObservationData()} data added to the expedition archive.</p>`:'<p class=\"arx-observation-note\">This individual was already logged; no duplicate data awarded.</p>'}",'wildlife modal data text')

# Cache expensive relocation access calculations, and close the old modal before teleporting so we do not nest port renders.
e=replace_once(e,"  function relocationPorts() { return (callbacks.getRelocationPorts?.()||[]).map(item=>({...item,id:item.id||slug(item.name)})); }","  function relocationPorts(force=false) { const key=`${state.currentVessel}:${Math.floor((state.elapsedDays||0)*2)}`;if(!force&&relocationPortCache.key===key)return relocationPortCache.ports;const ports=(callbacks.getRelocationPorts?.()||[]).map(item=>({...item,id:item.id||slug(item.name)}));relocationPortCache={key,ports};return ports; }",'relocation cache')
e=replace_once(e,"    const oldMoney=state.money; adjustMoney(-RELOCATION_COST); state.homePortId=id;\n    const moved=callbacks.relocateToPort?.(id);","    const oldMoney=state.money; adjustMoney(-RELOCATION_COST); state.homePortId=id;\n    closePort(); relocationPortCache={key:null,ports:[]};\n    const moved=callbacks.relocateToPort?.(id);",'relocation modal close')

# Shipyard heading recognizes all Russian and all non-Russian dealers.
e=replace_once(e,"${normalizedPortId()==='murmansk'?'Murmansk Nuclear Shipyard':normalizedPortId()==='longyearbyen'?'Longyearbyen Vessel Broker':'No vessel dealer at this port'}","${isRussianPort()?'Russian Nuclear Shipyard':normalizedPortId()==='longyearbyen'?'Longyearbyen Vessel Broker':'Arctic Vessel Broker'}",'shipyard heading')

# Selecting a random pop-up no longer clears the accepted grant selection that drives navigation guidance.
e=replace_once(e,"  function selectTarget(id) { state.targets.forEach(item=>item.selected=item.id===id); renderSidebar(); }","  function selectTarget(id) { const chosen=state.targets.find(item=>item.id===id),random=chosen&&(chosen.kind==='opportunity'||chosen.kind==='weather-opportunity');state.targets.forEach(item=>{const isRandom=item.kind==='opportunity'||item.kind==='weather-opportunity';if(random){if(isRandom)item.selected=item.id===id;}else item.selected=item.id===id;}); renderSidebar(); }",'target selection separation')

EXP.write_text(e)

# ---------------- game.js ----------------
g=GAME.read_text()

# Fish use the same observation filter as all other wildlife and never draw names.
fish_block=r'''  function drawFishSchools(){
    if(zoomLevel<.4)return;
    const now=performance.now()/420;ctx.save();
    for(const school of fishSchools){
      if(!wildlifeObservationAvailable(ensureWildlifeId(school)))continue;
      const ice=iceTypeAt(school.x,school.y);if(ice==='packed'||ice==='cracked'||ice==='fast'||isLand(school.x,school.y)||!wildlifeClearOfPorts(school.x,school.y))continue;
      const p=worldToScreen(school.x,school.y);if(p.x<-65||p.x>width+65||p.y<70||p.y>height+50)continue;
      const style=FISH_STYLES[school.species],visibleCount=Math.min(school.count,zoomLevel<.65?8:school.count);
      ctx.save();ctx.translate(p.x,p.y);ctx.rotate(school.angle);ctx.globalAlpha=.58;
      for(let i=0;i<visibleCount;i++){
        const row=Math.floor(i/5),col=i%5,ox=(col-2)*8+Math.sin(i*3.1+school.phase)*2,oy=(row-(visibleCount/5-1)/2)*7+Math.cos(i*2.7+school.phase)*2,wag=Math.sin(now+i*1.9+school.phase)*1.2,s=style.size*(.82+(i%3)*.1);
        ctx.fillStyle=style.color;ctx.strokeStyle='rgba(222,246,244,.68)';ctx.lineWidth=.7;ctx.beginPath();ctx.ellipse(ox,oy,s,s*.38,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(ox-s,oy);ctx.lineTo(ox-s-3,oy-2.8+wag);ctx.lineTo(ox-s-3,oy+2.8+wag);ctx.closePath();ctx.fill();
      }
      ctx.restore();
    }
    ctx.restore();
  }
'''
g=replace_block(g,'  function drawFishSchools(){','  function drawMap(){',fish_block,'fish drawing')

# Re-populate wildlife quickly after observations, but stop around five nearby unobserved encounters.
g=replace_once(g,"  function updateWildlifeEncounters(dt){wildlifeEncounterClock+=dt;if(wildlifeEncounterClock<1.35)return;wildlifeEncounterClock=0;retireDistantEncounters();const local=localWildlifeCount();if(local<7)spawnWildlifeEncounter();if(local<4)spawnWildlifeEncounter();}","  function updateWildlifeEncounters(dt){wildlifeEncounterClock+=dt;if(wildlifeEncounterClock<.6)return;wildlifeEncounterClock=0;retireDistantEncounters();const local=localWildlifeCount();if(local<3){spawnWildlifeEncounter();spawnWildlifeEncounter();}else if(local<5)spawnWildlifeEncounter();}",'wildlife spawn cadence')
g=replace_once(g,"observedWildlifeFallback.add(animal.individualId);research.openWildlife","observedWildlifeFallback.add(animal.individualId);wildlifeEncounterClock=1;research.openWildlife",'wildlife immediate replacement')

# Better wildlife silhouettes for land mammals, especially Svalbard reindeer.
wildlife_icons=r'''  function drawReindeerIcon(name){
    const svalbard=String(name).includes('SVALBARD');ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.fillStyle=svalbard?'#9b7652':'#8b6547';ctx.strokeStyle='rgba(244,251,244,.94)';ctx.lineWidth=1.15;
    ctx.beginPath();ctx.ellipse(-2,2,10.5,6.2,-.08,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(5,-1);ctx.quadraticCurveTo(7,-7,9,-10);ctx.lineTo(12,-8);ctx.lineTo(8,2);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.ellipse(11,-10,4.6,3.2,-.25,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.fillStyle='#6e523d';ctx.beginPath();ctx.ellipse(14,-10,2.1,1.3,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle=svalbard?'#9b7652':'#8b6547';ctx.beginPath();ctx.moveTo(9,-12);ctx.lineTo(7,-16);ctx.lineTo(11,-13);ctx.closePath();ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(12,-13);ctx.lineTo(15,-16);ctx.lineTo(14,-12);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.strokeStyle='#6e523d';ctx.lineWidth=2.15;for(const x of[-8,-1,4]){ctx.beginPath();ctx.moveTo(x,6);ctx.lineTo(x+(x===-8?-1:1),13);ctx.stroke();}ctx.lineWidth=1.7;ctx.strokeStyle='#e3cfaa';
    ctx.beginPath();ctx.moveTo(9,-13);ctx.lineTo(7,-20);ctx.moveTo(7,-18);ctx.lineTo(3,-20);ctx.moveTo(7,-17);ctx.lineTo(10,-21);ctx.moveTo(12,-13);ctx.lineTo(15,-20);ctx.moveTo(15,-18);ctx.lineTo(19,-20);ctx.moveTo(15,-17);ctx.lineTo(12,-21);ctx.stroke();ctx.restore();
  }
  function drawFoxIcon(){ctx.save();ctx.fillStyle='#d8e4dc';ctx.strokeStyle='rgba(245,252,248,.95)';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(-1,2,8,4.6,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.arc(7,-1,3.8,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(5,-4);ctx.lineTo(6,-9);ctx.lineTo(8,-4);ctx.moveTo(8,-4);ctx.lineTo(11,-8);ctx.lineTo(11,-2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(-8,1);ctx.quadraticCurveTo(-16,-6,-18,1);ctx.quadraticCurveTo(-14,7,-8,5);ctx.fill();ctx.stroke();ctx.restore();}
  function drawWildlifeIcons(){
    const weather=currentWeather();ctx.save();
    forEachWildlifeVisual((entity,species,category,w)=>{
      if(!wildlifeClearOfPorts(w.x,w.y))return;const fog=wildlifeFogFactor(w.x,w.y,weather);if(fog<=.03)return;const p=worldToScreen(w.x,w.y);if(p.x<-40||p.x>width+40||p.y<70||p.y>height+40)return;
      const sprite=wildlifeSpriteFor(species,category),size=wildlifeSpriteSize(species,category);ctx.save();ctx.translate(p.x,p.y);ctx.globalAlpha=.96*fog;
      if(spriteReady(sprite)&&size){drawMarkerBackdrop(size.r,markerSurfaceTone(w.x,w.y));ctx.shadowColor='rgba(0,20,30,.22)';ctx.shadowBlur=8;ctx.shadowOffsetY=2;if(category==='whale')ctx.rotate((entity.angle||0)+Math.PI/2);drawSpriteCentered(sprite,size.w,size.h);}
      else if(category==='mammal'){drawMarkerBackdrop(17,markerSurfaceTone(w.x,w.y));const mammalName=String(species||'').toUpperCase();if(mammalName.includes('REINDEER')||mammalName.includes('CARIBOU'))drawReindeerIcon(mammalName);else if(mammalName.includes('FOX'))drawFoxIcon();}
      else if(category==='bird'){ctx.strokeStyle='#eef9fa';ctx.lineWidth=2.2;ctx.beginPath();ctx.moveTo(-9,2);ctx.quadraticCurveTo(-3,-6,0,0);ctx.quadraticCurveTo(3,-6,9,2);ctx.stroke();}
      else if(category==='fish'){}
      else{ctx.fillStyle='#d7e8df';ctx.beginPath();ctx.arc(0,0,7,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(239,252,252,.9)';ctx.stroke();}
      ctx.restore();
    });ctx.restore();
  }
'''
g=replace_block(g,'  function drawWildlifeIcons(){','  function wildlifeFogFactor',wildlife_icons,'wildlife icon block')

# Known NPC vessel classes use the exact player sprite family, with a tint; unusual craft retain polished custom silhouettes.
npc_block=r'''  function npcTint(npc){const tones=['#d96f5f','#5e9fbd','#d2aa52','#6ba384','#9a7fb5','#b97855'];const seed=[...String(npc.id||npc.name||'ship')].reduce((sum,ch)=>sum+ch.charCodeAt(0),0);return tones[seed%tones.length];}
  function drawNpcIcon(npc){
    const cls=String(npc.classId||'').toLowerCase(),sprite=SPRITES.vessels[cls];ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
    if(spriteReady(sprite)){
      const dims=cls==='nuclear'?[30,51]:cls==='icebreaker'?[29,49]:cls==='global'?[28,47]:cls==='coastal'?[25,44]:[23,42];drawSpriteCentered(sprite,dims[0],dims[1]);ctx.globalCompositeOperation='source-atop';ctx.globalAlpha=.3;ctx.fillStyle=npcTint(npc);ctx.fillRect(-dims[0]/2,-dims[1]/2,dims[0],dims[1]);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.restore();return;
    }
    if(npc.kind==='canoe'){ctx.fillStyle='#78442d';ctx.strokeStyle='#f3e6c8';ctx.lineWidth=1.4;ctx.beginPath();ctx.moveTo(0,-14);ctx.quadraticCurveTo(8,0,0,15);ctx.quadraticCurveTo(-8,0,0,-14);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(-9,-8);ctx.lineTo(9,9);ctx.stroke();ctx.restore();return;}
    if(npc.kind==='sailing'){ctx.strokeStyle='#f6fbfb';ctx.lineWidth=1.4;ctx.fillStyle='#784f38';ctx.beginPath();ctx.ellipse(0,5,6,14,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#f5f0d8';ctx.beginPath();ctx.moveTo(0,-19);ctx.lineTo(0,6);ctx.lineTo(14,4);ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle='#f0d86c';ctx.fillRect(-1.1,-20,2.2,29);ctx.restore();return;}
    drawNpcHull(34,14,npcTint(npc),'#eaf8fa');ctx.fillStyle='#eef7f5';ctx.fillRect(-5,-10,10,10);ctx.fillStyle='#24566b';ctx.fillRect(-3.5,-8,7,3);ctx.restore();
  }
'''
g=replace_block(g,'  function drawNpcIcon(npc){','  function drawNpcVessels(){',npc_block,'npc icon block')

# Only accepted port grants/recoveries drive persistent directional guidance. Random pop-ups remain map question marks only.
g=replace_once(g,"  function selectedResearchTarget(){return researchTargets().find(target=>target.selected||target.active)||null;}","  function selectedResearchTarget(){return researchTargets().find(target=>(target.kind==='grant'||target.kind==='contract'||target.kind==='recovery')&&(target.selected||target.active))||null;}",'official guidance selection')

# Port approach no longer rejects a port because its immediate shoreline is fast ice or imperfect coastline geometry; find the closest reachable stand-off water point.
port_block=r'''  function findPortApproach(city){
    const center=polar(city.lat,city.lon);let reachable=null,reachableScore=Infinity,fallback=null,fallbackScore=Infinity;
    for(let radius=3;radius<=420;radius+=3)for(let i=0;i<72;i++){
      const a=i*Math.PI/36,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);if(pos.lat<MIN_LAT||isLand(x,y))continue;const profile=iceNavigationProfileAt(x,y);if(!profile.allowed)continue;
      const shipDistance=Math.hypot(x-state.x,y-state.y),score=radius+shipDistance*.025;if(score<fallbackScore){fallback={x,y,shoreDistance:radius};fallbackScore=score;}
      if(clearDisplacement(state.x,state.y,x,y)&&score<reachableScore){reachable={x,y,shoreDistance:radius};reachableScore=score;}
    }
    return reachable||fallback;
  }
'''
g=replace_block(g,'  function findPortApproach(city){','  function resetDistantWildlifeFromPort',port_block,'port approach')

# Close/backward clicks used to deliberately abort if the heading change exceeded ~100 degrees near the target. Turn through it instead and finish the maneuver.
old_turn="""if(dist<Math.max(14,arrivalRadius*4)&&Math.abs(da)>Math.PI*.55){state.commandActive=false;state.moving=false;state.ramming=false;state.tx=state.x;state.ty=state.y;ui.speed.textContent=(Math.hypot(flow.vx,flow.vy)/KNOT_TO_WORLD_SPEED).toFixed(1)+' KN DRIFT';if(state.portDestination)enterPort(state.portDestination);}else{state.angle+=da*Math.min(1,dt*4.2);state.moving=through>.02;ui.speed.textContent=through<.02?'0.0 KN':(through/KNOT_TO_WORLD_SPEED).toFixed(1)+(state.ramming?' KN ICE':' KN');}"""
new_turn="""{const turnRate=dist<Math.max(30,arrivalRadius*8)?9:4.8;state.angle+=da*Math.min(1,dt*turnRate);state.moving=through>.02;ui.speed.textContent=through<.02?'0.0 KN':(through/KNOT_TO_WORLD_SPEED).toFixed(1)+(state.ramming?' KN ICE':' KN');}"""
g=replace_once(g,old_turn,new_turn,'close turn abort')

# Force new browser script versions.
GAME.write_text(g)

idx=INDEX.read_text()
idx=idx.replace('expedition.js?v=expedition-22g-gameplay','expedition.js?v=expedition-22j-progression')
idx=idx.replace('game.js?v=expedition-22i-renderfix','game.js?v=expedition-22j-progression')
if 'expedition-22j-progression' not in idx: raise SystemExit('cache-bust replacement failed')
INDEX.write_text(idx)
