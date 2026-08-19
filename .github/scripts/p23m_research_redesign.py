from pathlib import Path
import re

EXP=Path('expedition.js')
GAME=Path('game.js')
INDEX=Path('index.html')
exp=EXP.read_text()
game=GAME.read_text()
index=INDEX.read_text()

def once(text, old, new, label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected one match, got {n}')
    return text.replace(old,new,1)

def rex(text, pattern, replacement, label, flags=re.S):
    out,n=re.subn(pattern,replacement,text,count=1,flags=flags)
    if n!=1:
        raise SystemExit(f'{label}: expected one regex match, got {n}')
    return out

# ---------------------------------------------------------------------------
# Canonical imagery and equipment economics
# ---------------------------------------------------------------------------
media_anchor="    ek80: {src:'assets/equipment/ek80-scientific-echosounder.webp', alt:'Portable multi-frequency scientific echosounder transceivers and split-beam sensors', credit:'Original face-free equipment illustration', source:''},\n"
media_add=media_anchor+"    cameraTelephoto: {src:'assets/equipment/field-camera-telephoto.svg', alt:'Weather-sealed field camera with an extra-large telephoto lens', credit:'Original equipment illustration', source:''},\n    bongoDetailed: {src:'assets/equipment/bongo-net-detailed.svg', alt:'Detailed paired bongo plankton net system', credit:'Original equipment illustration', source:''},\n    ednaKit: {src:'assets/equipment/edna-filtration-kit.svg', alt:'Portable eDNA filtration pump, filter holders and sterile sample cartridges', credit:'Original equipment illustration', source:''},\n    fieldKit: {src:'assets/equipment/general-field-kit.svg', alt:'General Arctic field kit with GPS, notebook, sample bottles and hand tools', credit:'Original equipment illustration', source:''},\n    shoreDebris: {src:'assets/research/shoreline-debris-transect.svg', alt:'Arctic shoreline debris survey transect with tape, quadrats and field sheet', credit:'Original research illustration', source:''},\n"
exp=once(exp,media_anchor,media_add,'add canonical media')

exp=once(exp,"media:MEDIA.aerial}),\n    'service-toolkit'","media:MEDIA.cameraTelephoto}),\n    'service-toolkit'",'field optics camera')
exp=once(exp,"media:MEDIA.bongoNet}),\n    'vertical-plankton-net'","media:MEDIA.bongoDetailed}),\n    'vertical-plankton-net'",'bongo equipment media')
exp=once(exp,"media:MEDIA.local}),\n    'all-sky-camera'","media:MEDIA.ednaKit}),\n    'all-sky-camera'",'edna field kit media')
exp=once(exp,"'ice-core-system': equipment({id:'ice-core-system', name:'Sea-Ice Field System', price:80000,","'ice-core-system': equipment({id:'ice-core-system', name:'Sea-Ice Field System', price:32000,",'sea ice field system price')

old_drone="'large-drone': equipment({id:'large-drone', name:'Long-Range Survey Drone', price:650000, slotType:'heavy', slots:1, tier:3, deckTag:'UAS', helideckUse:1, specialties:['atmosphere','sea-ice-physics','marine-mammals'], crew:[{specialties:['atmosphere','sea-ice-physics','marine-mammals'], minCareer:'professor', count:1}], description:'Deck-launched aircraft for ice, wildlife and atmospheric corridor surveys.', specs:['Requires one helideck','Thermal and mapping payloads','Extends useful fog visibility by 10 km'], media:MEDIA.drone})"
new_drone="'large-drone': equipment({id:'large-drone', name:'Long-Range Fixed-Wing Survey UAS', price:650000, slotType:'heavy', slots:1, tier:3, deckTag:'FIXED-WING UAS', minVesselClass:'global', specialties:['atmosphere','sea-ice-physics','marine-mammals'], crew:[{specialties:['atmosphere','sea-ice-physics','marine-mammals'], minCareer:'professor', count:1}], description:'Large deck-launched fixed-wing research aircraft for long ice, wildlife and atmospheric corridor surveys.', specs:['Global-class R/V or larger','Deck launch and recovery cradle','Thermal, visible and mapping payloads','Extends useful fog visibility by 10 km'], media:MEDIA.drone})"
exp=once(exp,old_drone,new_drone,'fixed wing drone equipment')

old_possible="  function equipmentPossibleOnShip(item,ship=vessel()) {\n    if (!item) return false;\n    if (item.builtIn) return ship.standardEquipment.includes(item.id);\n    if ((item.tier||1)>vesselScienceTier(ship)) return false;\n    if (item.consumable) return true;\n    if ((item.helideckUse||0)>ship.helidecks) return false;\n    return (ship.slots[item.slotType]||0)>=(item.slots||0);\n  }"
new_possible="  function equipmentPossibleOnShip(item,ship=vessel()) {\n    if (!item) return false;\n    if (item.builtIn) return ship.standardEquipment.includes(item.id);\n    if ((item.tier||1)>vesselScienceTier(ship)) return false;\n    if(item.minVesselClass){const order=['fishing','trawler','coastal','global','icebreaker','nuclear'];if(order.indexOf(ship.id)<order.indexOf(item.minVesselClass))return false;}\n    if (item.consumable) return true;\n    if ((item.helideckUse||0)>ship.helidecks) return false;\n    return (ship.slots[item.slotType]||0)>=(item.slots||0);\n  }"
exp=once(exp,old_possible,new_possible,'minimum vessel class support')

# Fixed mission pictures: never shuffle unrelated grant imagery.
exp=once(exp,"media:MEDIA.local, description:'Run careful echosounder lines across a small harbor","media:MEDIA.hullSensor, description:'Run careful echosounder lines across a small harbor",'harbor sounding media')
exp=once(exp,"media:MEDIA.local, description:'Photograph and classify debris along a short beach transect","media:MEDIA.shoreDebris, description:'Photograph and classify debris along a short beach transect",'shore debris media')
exp=once(exp,"stationSpacingKm:3, media:MEDIA.local, description:'Use paired mesh sizes","stationSpacingKm:3, media:MEDIA.bongoDetailed, description:'Use paired mesh sizes",'bongo mission media')
exp=once(exp,"fjordPreferred:true, media:MEDIA.local, description:'Collect a plankton tow and sterile filtered-water samples","fjordPreferred:true, media:MEDIA.ednaKit, description:'Collect a plankton tow and sterile filtered-water samples",'edna mission media')
exp=once(exp,"equipment:['edna-lab'], data:30, reward:36000, supplies:10, workHours:52, media:MEDIA.local, coastal:true","equipment:['edna-lab'], data:30, reward:36000, supplies:10, workHours:52, media:MEDIA.ednaKit, coastal:true",'coastal ecosystem media')
exp=exp.replace("stationCounts:{icebreaker:5,nuclear:8}, stationSpacingKm:45, data:52, reward:84000, supplies:10, workHours:84, media:MEDIA.aerial","stationCounts:{global:4,icebreaker:5,nuclear:8}, stationSpacingKm:45, data:52, reward:84000, supplies:10, workHours:84, media:MEDIA.drone",1)
exp=exp.replace("stationCounts:{icebreaker:5,nuclear:9}","stationCounts:{global:4,icebreaker:5,nuclear:9}",1)

# Better publication tier language.
old_papers="  const PAPER_LEVELS = [\n    {id:'local',threshold:100,next:1000,label:'Local science newsletter',journal:'Svalbard Science Bulletin',award:30000,initialCitations:10,potential:90},\n    {id:'national',threshold:1000,next:10000,label:'National research journal',journal:'Nordic Polar Research Review',award:350000,initialCitations:130,potential:1400},\n    {id:'international',threshold:10000,next:null,label:'Prestigious international journal',journal:'International Journal of Polar Systems',award:4000000,initialCitations:1700,potential:18000}\n  ];"
new_papers="  const PAPER_LEVELS = [\n    {id:'local',threshold:100,next:1000,label:'Arctic Field Research Note',journal:'Svalbard Science Bulletin',award:30000,initialCitations:10,potential:90},\n    {id:'national',threshold:1000,next:10000,label:'Peer-Reviewed Research Article',journal:'Nordic Polar Research Review',award:350000,initialCitations:130,potential:1400},\n    {id:'international',threshold:10000,next:null,label:'Landmark International Paper',journal:'International Journal of Polar Systems',award:4000000,initialCitations:1700,potential:18000}\n  ];"
exp=once(exp,old_papers,new_papers,'paper tier names')
exp=once(exp,"<span>100 LOCAL</span><span>1,000 NATIONAL</span><span>10,000 INTERNATIONAL</span>","<span>100 FIELD NOTE</span><span>1,000 RESEARCH ARTICLE</span><span>10,000 LANDMARK PAPER</span>",'paper gauge labels')
exp=exp.replace("more data for a local science paper","more data for an Arctic Field Research Note",1)
exp=exp.replace("'International paper threshold reached · automatic submission'","'Landmark paper threshold reached · automatic submission'",1)

# Add more unmistakably postdoctoral programs.
postdoc_anchor="    mission({id:'postdoc-edna-foodweb', title:'Plankton Metabarcoding & Microbial Food-Web Survey', shortTitle:'PLANKTON DNA', specialties:['plankton','coastal-ecology'], equipment:['plankton-winch','edna-lab'], data:48, reward:60000, supplies:14, workHours:68, coastal:true, fjordPreferred:true, description:'Combine depth-resolved plankton collections with eDNA filtration to resolve community composition from metazoans to bacteria and viruses.', steps:['Plan sterile station sequence','Collect depth-resolved plankton','Filter paired water samples','Preserve DNA and microscopy fractions','Complete chain-of-custody metadata']}),\n"
postdoc_new=postdoc_anchor+"    mission({id:'postdoc-frontogenesis',postdocOpportunity:true,title:'Fjord Frontogenesis & Turbulent Exchange Experiment',shortTitle:'FRONT DYNAMICS',specialties:['physical','coastal-oceanography'],equipment:['medium-winch','coastal-suite'],transect:true,stationCounts:{coastal:5,global:7,icebreaker:9,nuclear:11},stationSpacingKm:8,data:58,reward:76000,supplies:15,workHours:78,coastal:true,fjordPreferred:true,media:MEDIA.winch,description:'Resolve lateral density gradients, ageostrophic exchange and frontal sharpening across a rapidly evolving Arctic fjord front.',steps:['Map the frontal density gradient','Repeat velocity sections across the front','Profile stratification and shear','Resolve cross-front exchange','Synthesize the frontal energy budget']}),\n    mission({id:'postdoc-acoustic-inversion',postdocOpportunity:true,title:'Coupled Acoustic Scattering & Plankton Community Inversion',shortTitle:'ACOUSTIC INVERSION',specialties:['fisheries','plankton'],equipment:['fish-acoustics','plankton-winch'],transect:true,stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10},stationSpacingKm:14,data:62,reward:82000,supplies:17,workHours:84,media:MEDIA.ek80,description:'Combine multi-frequency acoustic backscatter with depth-resolved net samples to invert scattering layers into biological size and community structure.',steps:['Calibrate the acoustic frequencies','Map vertically migrating scattering layers','Collect depth-matched net samples','Fit taxon-specific scattering models','Invert the section for community structure']}),\n    mission({id:'postdoc-carbon-edna',postdocOpportunity:true,title:'Mesoscale Carbon Export & eDNA Coupling Survey',shortTitle:'CARBON COUPLING',specialties:['biogeochemistry','plankton','coastal-ecology'],equipment:['edna-lab','plankton-winch','portable-water-lab'],transect:true,stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10},stationSpacingKm:12,data:66,reward:88000,supplies:19,workHours:88,coastal:true,media:MEDIA.ednaKit,description:'Couple particulate export, hydrographic structure and metabarcoding across a mesoscale feature to identify the organisms driving carbon transfer.',steps:['Map the hydrographic feature','Collect depth-resolved water and plankton','Filter paired eDNA replicates','Quantify particle and biomass gradients','Assemble the coupled carbon-community section']}),\n    mission({id:'postdoc-underice-biooptics',postdocOpportunity:true,title:'Under-Ice Bio-Optical Coupling Experiment',shortTitle:'UNDER-ICE OPTICS',specialties:['sea-ice-physics','sea-ice-ecology'],equipment:['ice-core-system','edna-lab'],data:60,reward:80000,supplies:18,workHours:82,iceAllowed:true,media:MEDIA.iceCorer,description:'Link snow and ice structure to transmitted light, under-ice biological communities and eDNA across a drifting floe.',steps:['Survey snow and ice thickness','Measure transmitted spectral light','Collect stratified ice cores','Filter under-ice eDNA samples','Relate optical habitat to community structure']}),\n"
exp=once(exp,postdoc_anchor,postdoc_new,'postdoc opportunity templates')

# ---------------------------------------------------------------------------
# Rewards: grad + postdoc x3; port grants x5 relative to popup work; advance pay.
# ---------------------------------------------------------------------------
old_scale="    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03), rewardScale=vesselRewardScale();"
new_scale="    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03), rewardScale=vesselRewardScale(),missionLevel=templateCareerLevel(template),careerRewardBoost=missionLevel<=2?3:1,sourceRewardBoost=kind==='grant'?(state.port?5:2):1;"
exp=once(exp,old_scale,new_scale,'reward scale variables')
old_reward="      data:Math.max(1,Math.round(template.data*scale*vesselScale*crewScale*iceValueMultiplier)), reward:Math.round(template.reward*scale*(kind === 'opportunity'||kind==='weather-opportunity' ? 1.6 : 2)*iceValueMultiplier*rewardScale),"
new_reward="      data:Math.max(1,Math.round(template.data*scale*vesselScale*crewScale*iceValueMultiplier)), reward:Math.round(template.reward*scale*careerRewardBoost*sourceRewardBoost*iceValueMultiplier*rewardScale),"
exp=once(exp,old_reward,new_reward,'reward formula')
exp=once(exp,"      sourcePortId:normalizedPortId(origin), recoveryTitle:","      upfront:kind==='grant'?Math.round(template.reward*scale*careerRewardBoost*sourceRewardBoost*iceValueMultiplier*rewardScale*.2):0, advancePaid:0, postdocOpportunity:!!template.postdocOpportunity,\n      sourcePortId:normalizedPortId(origin), recoveryTitle:",'target advance fields')

# Canonical media replaces the previous random unique-image shuffle.
exp=rex(exp,r"  const GRANT_MEDIA_POOL=.*?\n  function giveGrantUniqueMedia\(target,used,rng\)\{.*?\n  \}\n  function generateOffers",'''  const GRANT_MEDIA_POOL=[MEDIA.river,MEDIA.ice,MEDIA.storm,MEDIA.ctd,MEDIA.rov,MEDIA.radar,MEDIA.balloon,MEDIA.aerostat,MEDIA.drone,MEDIA.drifter,MEDIA.winch,MEDIA.handheldWater,MEDIA.iceCorer,MEDIA.miniRov,MEDIA.shallowAdcp,MEDIA.surfaceNet,MEDIA.verticalNet,MEDIA.bongoDetailed,MEDIA.ednaKit,MEDIA.fieldKit,MEDIA.shallowCorer,MEDIA.vessel].filter(Boolean);
  function canonicalMissionMedia(item){const template=TEMPLATES.find(template=>template.id===item?.templateId);return template?.media||item?.media||MEDIA.fieldKit||MEDIA.local;}
  function giveGrantUniqueMedia(target,used,rng){
    const template=TEMPLATES.find(item=>item.id===target.templateId),gear=[...(target.equipment||[]),...(target.consumables||[])].map(id=>EQUIPMENT[id]?.media).find(media=>media?.src),media=template?.media||gear||target.media||MEDIA.fieldKit||MEDIA.local;
    target.media=clone(media);if(used&&media?.src)used.add(media.src);return !!media?.src;
  }
  function generateOffers''','canonical grant media')

# Increase weight for complex postdoc rapid-response programs.
exp=once(exp,"if(teamLevel===2)weight+=level===2?18:level===1?2:0;","if(teamLevel===2)weight+=level===2?18:level===1?2:0;if(teamLevel===2&&template.postdocOpportunity)weight+=42;",'postdoc popup weighting')

# ---------------------------------------------------------------------------
# Grant cards: fixed media + named team + equipment + advance disclosure.
# ---------------------------------------------------------------------------
exp=rex(exp,r"  function offerCard\(item\) \{.*?\n  \}\n  function activeGrantCard",'''  function offerCard(item) {
    const specialty=item.anyScientist?'Any scientist aboard':item.specialties.map(id=>specialtyById[id]?.name).filter(Boolean).join(' / '),media=canonicalMissionMedia(item);
    const projection=missionFoodProjection(item), cap=grantLoad()>=grantCapacity(), foodUnsafe=projection.remaining<15, fuelUnsafe=!vessel().nuclearFuel&&projection.fuelRemaining<10;
    const label=cap?`ACTIVE GRANT LIMIT ${grantLoad()}/${grantCapacity()}`:foodUnsafe?`INSUFFICIENT FOOD · PROJECTED ${Math.max(0,Math.floor(projection.remaining))}%`:fuelUnsafe?`INSUFFICIENT FUEL · PROJECTED ${Math.max(0,Math.floor(projection.fuelRemaining))}%`:'ACCEPT RESEARCH GRANT';
    return `<article class="arx-card offer research-offer"><div class="arx-offer-thumb"><img src="${escapeHtml(media?.src||MEDIA.fieldKit.src)}" alt="${escapeHtml(media?.alt||item.title)}"></div><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(specialty)}</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p><div class="arx-grant-advance"><span><small>TOTAL SPONSOR AWARD</small><b>${cash(item.reward)}</b></span><span><small>PAID UPFRONT ON ACCEPTANCE</small><b>${cash(item.upfront||0)}</b></span></div><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class="arx-mini-label">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class="arx-stats"><span>+${item.data} data</span><span>${item.minCrew||missionMinCrew(item)} people minimum</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span><span>~${projection.days} field days</span>${item.iceValueMultiplier>1?`<span>ICE PREMIUM ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>Food on return ~${Math.max(0,Math.floor(projection.remaining))}%</span><span>Fuel on return ~${Math.max(0,Math.floor(projection.fuelRemaining))}%</span></div><button data-arx-action="accept" data-id="${item.id}" ${cap||foodUnsafe||fuelUnsafe?'disabled':''}>${label}</button></article>`;
  }
  function activeGrantCard''','grant offer details')

old_active="    const recovery=!!item.deploymentId;\n    return `<article class=\"arx-card grant\"><div class=\"arx-card-head\"><div><b>${escapeHtml(item.title)}</b><small>${recovery?'RETURN VISIT REQUIRED':missing?'CAPABILITY CURRENTLY MISSING':'READY'} · ${Math.round(item.workHours)} PERSON-HOURS</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p><div class=\"arx-stats\"><span>${item.data} data</span>${item.iceValueMultiplier>1?`<span>ICE PREMIUM ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>~${projection.days} field days</span><span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><button class=\"danger\" data-arx-action=\"drop-grant\" data-id=\"${item.id}\" ${recovery?'disabled':''}>${recovery?'RETURN VISIT CANNOT BE DROPPED':'DROP RESEARCH GRANT'}</button></article>`;"
new_active="    const recovery=!!item.deploymentId,teamPickup=item.missionMode==='staged-recovery';\n    return `<article class=\"arx-card grant\"><div class=\"arx-card-head\"><div><b>${escapeHtml(item.title)}</b><small>${recovery?'RETURN VISIT REQUIRED':missing?'CAPABILITY CURRENTLY MISSING':'READY'} · ${Math.round(item.workHours)} PERSON-HOURS</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p><h4 class=\"arx-mini-label\">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class=\"arx-mini-label\">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class=\"arx-stats\"><span>${item.data} data</span><span>Upfront paid ${cash(item.advancePaid||0)}</span>${item.iceValueMultiplier>1?`<span>ICE PREMIUM ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>~${projection.days} field days</span><span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><div class=\"arx-grant-actions\"><button data-arx-action=\"navigate-target\" data-id=\"${item.id}\">LOCATE / NAVIGATE</button><button class=\"danger\" data-arx-action=\"drop-grant\" data-id=\"${item.id}\" ${recovery&&!teamPickup?'disabled':''}>${recovery?(teamPickup?'DROP RETURN PICKUP':'DEPLOYED EQUIPMENT MUST BE RECOVERED'):'DROP RESEARCH GRANT'}</button></div></article>`;"
exp=once(exp,old_active,new_active,'active grant card')

exp=rex(exp,r"  function collectingGrantCard\(item\) \{.*?\n  \}\n",'''  function collectingGrantCard(item) {
    const teamPickup=item.recoveryMode==='staged-recovery';
    return `<article class="arx-card grant"><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${teamPickup?'FIELD TEAM ASHORE · RETURN VISIT PENDING':'INSTRUMENT COLLECTING · RETURN VISIT PENDING'}</small></div><em>${Math.max(0,Math.ceil(item.remainingDays||0))} d</em></div><p>${teamPickup?'The shore party is working independently. You can return for them when ready, or hand their pickup to local logistics and drop the return visit.':'Autonomous observations are underway. This research grant continues to occupy one scientist-led grant slot until recovery.'}</p>${teamPickup?`<button class="danger" data-arx-action="abandon-deployment" data-id="${item.id}">DROP RETURN PICKUP</button>`:'<button disabled>RECOVERY WINDOW NOT OPEN YET</button>'}</article>`;
  }
''','collecting pickup drop')

# ---------------------------------------------------------------------------
# One stable research card for explanation -> execution -> result.
# ---------------------------------------------------------------------------
exp=rex(exp,r"  function openTarget\(id,context=\{\}\) \{.*?\n  function operationEquipmentMarkup\(target\) \{",'''  function renderResearchWindow(target,{phase='ready',resultTitle='',resultBody='',resultStats=[]}={}) {
    const running=phase==='running',complete=phase==='complete',programFinished=complete&&target.status==='completed';
    const readiness=missionReadiness(target),projection=readiness.projection,station=currentStation(target),stationLabel=station?`${station.number} of ${target.stations.length}`:'Single station';
    const contextDistance=state.lastTargetContext?.id===target.id?state.lastTargetContext.distanceKm:null,navDistance=state.navigation?.id===target.id?state.navigation.distanceKm:null,distance=Number.isFinite(contextDistance)?contextDistance:Number.isFinite(navDistance)?navDistance:Infinity,atSite=target.anywhere||distance<=RESEARCH_INTERACTION_KM;
    const opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity',missing=readiness.rows.find(row=>!row.ready),participants=participantIdsFor(target),rate=workRate(target),workHours=Math.round(running?(activeOperation?.workHours||operationWorkHours(target)):remainingWorkHours(target));
    const progress=running?0:complete?100:0,steps=target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station'];
    const canNavigate=!target.anywhere&&!atSite&&!running&&!programFinished,canBegin=atSite&&readiness.ready&&!running&&!complete;
    const primaryLabel=running?'RESEARCH IN PROGRESS':complete?'RESEARCH COMPLETE':!atSite&&!target.anywhere?'SAIL TO SITE FIRST':readiness.ready?'BEGIN RESEARCH':`CANNOT BEGIN · ${missing?.label||'MISSING CAPABILITY'}`;
    const decline=opportunity?`<button class="ghost" data-arx-action="cancel-opportunity" data-id="${target.id}" ${running||complete?'disabled':''}>DECLINE</button>`:(target.kind==='grant'||target.kind==='contract')?`<button class="danger" data-arx-action="drop-grant" data-id="${target.id}" ${running||programFinished||(target.deploymentId&&target.missionMode!=='staged-recovery')?'disabled':''}>${target.missionMode==='staged-recovery'?'DROP RETURN PICKUP':'DROP GRANT'}</button>`:'<button class="ghost" disabled>NO DROP ACTION</button>';
    const media=canonicalMissionMedia(target),result=resultTitle||'Research result';
    const modal=root.querySelector('#arx-target-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-target-card arx-operation arx-research-unified ${complete?'arx-complete':''}"><button class="arx-close" data-arx-action="close-target" aria-label="Close research site" ${running?'disabled':''}>×</button><small>${target.weather?'LIVE WEATHER RESEARCH':opportunity?'DISCOVERED RESEARCH OPPORTUNITY':'ACTIVE RESEARCH GRANT'}</small><h2>${escapeHtml(target.title)}</h2>${mediaMarkup(target,'hero')}<p>${escapeHtml(target.description)}</p><div class="arx-target-facts arx-research-facts"><span><small>STATION</small><b>${stationLabel}</b></span><span><small>REMAINING WORK</small><b>${workHours} person-hours · team rate ${rate.toFixed(1)}×</b></span><span><small>TOTAL AWARD</small><b>${cash(target.reward||0)}</b></span><span><small>UPFRONT</small><b>${cash(target.upfront||0)}${target.advancePaid?' · PAID':''}</b></span><span><small>RESULT</small><b>${['mooring-deploy','staged-deploy','autonomous'].includes(target.missionMode)?'Data after telemetry / recovery':`+${target.data} data`}</b></span><span><small>DISTANCE</small><b>${target.anywhere?'REMOTE / ONBOARD':Number.isFinite(distance)?`${Math.round(distance)} km`:'OFF-SCREEN SITE'}</b></span></div><h3 class="arx-operation-subhead">RESPONSIBLE SCIENTISTS</h3>${operationScientistsMarkup(target)}<h3 class="arx-operation-subhead">EQUIPMENT USED</h3>${operationEquipmentMarkup(target)}<h3 class="arx-check-title">MISSION READINESS</h3>${readinessMarkup(readiness)}<div class="arx-operation-progress"><div><b id="arx-operation-percent">${progress}%</b><span>${workHours} person-hours · ~${projection.days} game days · ${participants.length||1} scientist${participants.length===1?'':'s'} assigned</span></div><i><em id="arx-operation-bar" style="width:${progress}%"></em></i></div><ol>${steps.map((step,index)=>`<li data-arx-step="${index}" class="${complete?'done':''}"><i>${complete?'✓':index+1}</i><b>${escapeHtml(step)}</b><span>${complete?'Complete':'Queued'}</span></li>`).join('')}</ol><div class="arx-operation-result-space">${complete?`<div class="arx-research-result"><small>${escapeHtml(result)}</small><p>${escapeHtml(resultBody)}</p>${resultStats.length?`<div class="arx-chance">${resultStats.map(item=>`<span>${escapeHtml(item.label)}<b>${escapeHtml(item.value)}</b></span>`).join('')}</div>`:''}</div>`:'<div class="arx-result-placeholder">Results will appear here without replacing this research card.</div>'}</div><div class="arx-research-actions">${decline}<button data-arx-action="navigate-target" data-id="${target.id}" ${canNavigate?'':'disabled'}>${complete&&!programFinished?'NAVIGATE TO NEXT STATION':'NAVIGATE TO SITE'}</button><button data-arx-action="complete-target" data-id="${target.id}" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button><button data-arx-action="acknowledge-research" ${complete?'':'disabled'}>OKAY</button></div></div>`;
    modal.classList.add('open');
  }
  function openTarget(id,context={}) {
    const target=state.targets.find(item=>item.id===id);if(!target)return false;
    if(activeOperation&&activeOperation.targetId!==id){toast('RESEARCH STATION ALREADY IN PROGRESS');return false;}
    const distance=context.distanceKm??(state.navigation?.id===id?state.navigation.distanceKm:Infinity);
    state.targets.forEach(item=>item.selected=item.id===id);state.lastTargetContext={...context,id,distanceKm:distance};
    renderResearchWindow(target,{phase:activeOperation?.targetId===id?'running':'ready'});renderSidebar();return true;
  }
  function operationEquipmentMarkup(target) {''','unified open target')

exp=rex(exp,r"  function operationEquipmentMarkup\(target\) \{.*?\n  \}\n  function operationScientistsMarkup",'''  function operationEquipmentMarkup(target) {
    const ids=[...(target.equipment||[]),...(target.consumables||[])],items=[...new Set(ids)].map(id=>EQUIPMENT[id]).filter(Boolean);
    if(!items.length)return `<div class="arx-operation-equipment"><div class="arx-operation-gear field-kit"><img src="${escapeHtml(MEDIA.fieldKit.src)}" alt="${escapeHtml(MEDIA.fieldKit.alt)}"><span>General Arctic Field Kit</span></div></div>`;
    return `<div class="arx-operation-equipment">${items.map(item=>`<div class="arx-operation-gear"><img src="${escapeHtml(item.media?.src||MEDIA.fieldKit.src)}" alt="${escapeHtml(item.media?.alt||item.name)}"><span>${escapeHtml(item.name)}</span></div>`).join('')}</div>`;
  }
  function operationScientistsMarkup''','field kit imagery')

exp=rex(exp,r"  function renderOperationShell\(target\) \{.*?\n  \}\n  function participantIdsFor",'''  function renderOperationShell(target) { renderResearchWindow(target,{phase:'running'}); }
  function participantIdsFor''','stable running window')

exp=rex(exp,r"  function completionModal\(target,title,body,stats=\[\]\) \{.*?\n  \}\n  function settleResearch",'''  function completionModal(target,title,body,stats=[]) { renderResearchWindow(target,{phase:'complete',resultTitle:title,resultBody:body,resultStats:stats}); }
  function settleResearch''','stable completion window')

# Visual duration now follows effective workload / team productivity instead of a narrow fixed range.
old_duration="    const workHours=operationWorkHours(target), days=effectiveDays(target,workHours), durationMs=clamp(5000+days*850,6000,11500);\n    activeOperation={targetId:id,startedAt:performance.now(),durationMs,workHours,days,stationIndex:target.stationIndex||0,participantIds:participantIdsFor(target),steps:target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station']};"
new_duration="    const workHours=operationWorkHours(target),days=effectiveDays(target,workHours),participantIds=participantIdsFor(target),productivity=Math.max(1,workRate(target)),challenge=1+(templateCareerLevel(target)-1)*.28,durationMs=clamp(2600+(workHours/productivity)*130*challenge,3400,22000);\n    activeOperation={targetId:id,startedAt:performance.now(),durationMs,workHours,days,stationIndex:target.stationIndex||0,participantIds,steps:target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station']};"
exp=once(exp,old_duration,new_duration,'team scaled progress duration')

# Advance payment and final balance.
old_settle="  function settleResearch(target,dataGain) {\n    addData(dataGain); adjustMoney(target.reward);\n    return [{label:'DATA ARCHIVED',value:`+${dataGain}`},{label:'SPONSOR PAYMENT',value:cash(target.reward)}];\n  }"
new_settle="  function settleResearch(target,dataGain) {\n    const advance=Math.max(0,Number(target.advancePaid)||0),balance=Math.max(0,(Number(target.reward)||0)-advance);addData(dataGain);adjustMoney(balance);\n    return [{label:'DATA ARCHIVED',value:`+${dataGain}`},{label:'TOTAL AWARD',value:cash(target.reward)},{label:'UPFRONT PAID',value:cash(advance)},{label:'FINAL PAYMENT',value:cash(balance)}];\n  }"
exp=once(exp,old_settle,new_settle,'settle grant balance')
exp=once(exp,"reward:target.reward,equipment:[...target.equipment]","reward:target.reward,upfront:target.upfront||0,advancePaid:target.advancePaid||0,equipment:[...target.equipment]",'deployment advance copy')
exp=once(exp,"media:clone(deployment.media),lat:deployment.lat,lon:deployment.lon,data:deployment.data,reward:deployment.reward,","media:clone(deployment.media),lat:deployment.lat,lon:deployment.lon,data:deployment.data,reward:deployment.reward,upfront:deployment.upfront||0,advancePaid:deployment.advancePaid||0,",'recovery advance copy')

# Accepting a grant releases its stated advance immediately.
accept_old="    state.targets.forEach(item=>item.selected=false); offer.selected=true; state.targets.push(offer);\n    state.offers=state.offers.filter(item=>item.id!==id); recordGrantUse(offer.templateId,offer); addLog(`Research grant accepted: ${offer.title}.`);\n    toast(`RESEARCH GRANT ACCEPTED · ${offer.shortTitle}`); changed();"
accept_new="    state.targets.forEach(item=>item.selected=false);offer.selected=true;if((offer.upfront||0)>0&&!offer.advancePaid){offer.advancePaid=offer.upfront;adjustMoney(offer.upfront);}state.targets.push(offer);\n    state.offers=state.offers.filter(item=>item.id!==id);recordGrantUse(offer.templateId,offer);addLog(`Research grant accepted: ${offer.title}.${offer.advancePaid?` Upfront sponsor payment ${cash(offer.advancePaid)}.`:''}`);\n    toast(`RESEARCH GRANT ACCEPTED · ${offer.shortTitle}${offer.advancePaid?` · +${cash(offer.advancePaid)} UPFRONT`:''}`);changed();"
exp=once(exp,accept_old,accept_new,'grant advance acceptance')

# Release as many non-chief scientists as desired; active grants simply become unready.
exp=once(exp,"    if (grantLoad()>Math.max(1,remaining.length)) { toast('DROP OR COMPLETE A RESEARCH GRANT BEFORE REDUCING THE SCIENCE TEAM'); return; }\n",'', 'remove crew grant-count release block')

# Team return visits can be dropped; mooring/equipment recovery remains protected.
exp=rex(exp,r"  function dropGrant\(id\) \{.*?\n  \}\n  function chooseVessel",'''  function abandonDeployment(id){const deployment=state.deployments.find(item=>item.id===id);if(!deployment||deployment.recoveryMode!=='staged-recovery')return;deployment.status='abandoned';if(deployment.recoveryTargetId)state.targets=state.targets.filter(item=>item.id!==deployment.recoveryTargetId);deployment.recoveryTargetId=null;addLog(`Return pickup dropped for ${deployment.title}; local logistics assumed responsibility for the field party.`);toast('RETURN PICKUP DROPPED · LOCAL LOGISTICS WILL RECOVER THE TEAM');changed();}
  function dropGrant(id) {
    const grant=state.targets.find(item=>item.id===id&&(item.kind==='grant'||item.kind==='contract'));if(!grant||activeOperation?.targetId===id)return;
    if(grant.deploymentId&&grant.missionMode!=='staged-recovery'){toast('THIS RETURN VISIT IS REQUIRED TO RECOVER DEPLOYED EQUIPMENT');return;}
    if(grant.deploymentId&&grant.missionMode==='staged-recovery'){const deployment=state.deployments.find(item=>item.id===grant.deploymentId);if(deployment){deployment.status='abandoned';deployment.recoveryTargetId=null;}addLog(`Return pickup dropped for ${grant.title}; local logistics assumed responsibility for the field party.`);}else state.droppedGrantTemplates.push(grant.templateId);
    state.targets=state.targets.filter(item=>item.id!==id);if(state.navigation?.id===id)state.navigation=null;if(state.lastTargetContext?.id===id)state.lastTargetContext=null;root?.querySelector('#arx-target-modal')?.classList.remove('open');toast(grant.missionMode==='staged-recovery'?'RETURN PICKUP DROPPED':'RESEARCH GRANT DROPPED');changed();
  }
  function chooseVessel''','droppable team pickup')

# Navigation prompt is now just the stable research card. No separate "navigate?" modal.
exp=rex(exp,r"  function openNavigationPrompt\(id=state.navigation\?\.id\) \{.*?\n  \}\n\n  function confirmDeparture",'''  function openNavigationPrompt(id=state.navigation?.id) {
    const target=state.targets.find(item=>item.id===id);if(!target)return false;const nav=state.navigation?.id===id?state.navigation:null;return openTarget(id,{distanceKm:nav?.distanceKm??Infinity,target});
  }

  function confirmDeparture''','remove navigation prompt window')

# Actions for stable card and return pickup.
exp=once(exp,"    else if (action==='drop-grant') dropGrant(id);","    else if (action==='drop-grant') dropGrant(id);\n    else if (action==='abandon-deployment') abandonDeployment(id);\n    else if (action==='navigate-target') { const target=state.targets.find(item=>item.id===id);root.querySelector('#arx-target-modal')?.classList.remove('open');if(target)callbacks.onNavigate?.(target); }",'research actions')
old_prof="    else if (action==='accept-professor-grant'&&state.remoteOffer) { state.targets.forEach(item=>item.selected=false);state.remoteOffer.selected=true;state.targets.push(state.remoteOffer);addLog(`Professor-originated grant accepted: ${state.remoteOffer.title}.`);state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed(); }"
new_prof="    else if (action==='accept-professor-grant'&&state.remoteOffer) { state.targets.forEach(item=>item.selected=false);state.remoteOffer.selected=true;if((state.remoteOffer.upfront||0)>0&&!state.remoteOffer.advancePaid){state.remoteOffer.advancePaid=state.remoteOffer.upfront;adjustMoney(state.remoteOffer.upfront);}state.targets.push(state.remoteOffer);addLog(`Professor-originated grant accepted: ${state.remoteOffer.title}.`);state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed(); }"
exp=once(exp,old_prof,new_prof,'professor grant advance')

# New compact styling for one-window research cards and grant team/equipment previews.
style_marker="    root.addEventListener('click',event=>{"
style_add="""    style.textContent+=`\n      .arx-research-unified{width:min(780px,100%)!important;max-height:calc(100vh - 24px)!important;overflow:auto!important}.arx-research-unified .arx-media.hero{height:180px;margin:10px 0 14px;border-radius:10px}.arx-research-facts{grid-template-columns:repeat(3,1fr)!important}.arx-research-actions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-top:12px}.arx-research-actions button,.arx-grant-actions button{width:100%;padding:9px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:7px;font-weight:900;letter-spacing:.06em}.arx-research-actions button:disabled{background:#315766;color:#7896a0}.arx-research-actions .ghost{border:1px solid rgba(166,230,244,.25);background:transparent;color:#a9d2dc}.arx-research-actions .danger,.arx-grant-actions .danger{border:1px solid rgba(249,115,103,.38);background:rgba(111,45,52,.6);color:#ffd0c9}.arx-operation-scientists,.arx-operation-equipment{display:flex;flex-wrap:wrap;gap:7px;margin:7px 0 11px}.arx-operation-scientists>div,.arx-operation-gear{display:flex;align-items:center;gap:7px;min-width:150px;padding:6px;border-radius:7px;background:rgba(30,79,96,.4)}.arx-operation-scientists img,.arx-operation-gear img{width:42px;height:42px;flex:0 0 42px;border-radius:7px;object-fit:cover;background:#123d51}.arx-operation-gear img{object-fit:contain}.arx-operation-scientists b,.arx-operation-scientists small,.arx-operation-gear span{display:block;font-size:7px}.arx-operation-scientists small{margin-top:2px;color:#8fb7c2}.arx-operation-subhead,.arx-mini-label{margin:9px 0 4px;color:#7dd3fc;font:900 8px system-ui;letter-spacing:.1em}.research-offer .arx-operation-scientists>div,.research-offer .arx-operation-gear{min-width:130px;padding:4px}.research-offer .arx-operation-scientists img,.research-offer .arx-operation-gear img{width:34px;height:34px;flex-basis:34px}.arx-grant-advance{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:8px 0}.arx-grant-advance span{padding:7px;border-radius:7px;background:rgba(246,211,101,.08)}.arx-grant-advance small,.arx-grant-advance b{display:block}.arx-grant-advance small{color:#8fb7c2;font-size:6px}.arx-grant-advance b{margin-top:3px;color:#fff1a8;font-size:10px}.arx-grant-actions{display:grid;grid-template-columns:1fr 1fr;gap:6px}.arx-result-placeholder{padding:9px;border:1px dashed rgba(166,230,244,.18);border-radius:7px;color:#789eaa;font-size:8px;text-align:center}.arx-research-result{padding:10px;border:1px solid rgba(142,240,207,.24);border-radius:8px;background:rgba(35,91,77,.16)}.arx-research-result>small{color:#8ef0cf;font-size:8px;font-weight:900;letter-spacing:.08em}.arx-research-result>p{color:#b9d7d9;font-size:9px}@media(max-width:760px){.arx-research-facts{grid-template-columns:1fr 1fr!important}.arx-research-actions{grid-template-columns:1fr 1fr}.arx-research-unified .arx-media.hero{height:145px}.arx-grant-advance{grid-template-columns:1fr}}\n    `;\n"""+style_marker
exp=once(exp,style_marker,style_add,'research card styles')

# ---------------------------------------------------------------------------
# GAME: no auto navigation popup, clickable research over port, port clearance,
# and off-screen arrows for every active research site.
# ---------------------------------------------------------------------------
old_wrapper="  if(research?.maybeSpawnOpportunity){const spawnOpportunity=research.maybeSpawnOpportunity.bind(research);research.maybeSpawnOpportunity=payload=>{const target=spawnOpportunity({...researchEnvironment(payload?.weather),...payload});if(target?.id)setTimeout(()=>{if(!currentPortCity)research?.openNavigationPrompt?.(target.id);},0);return target;};}"
new_wrapper="  if(research?.maybeSpawnOpportunity){const spawnOpportunity=research.maybeSpawnOpportunity.bind(research);research.maybeSpawnOpportunity=payload=>spawnOpportunity({...researchEnvironment(payload?.weather),...payload});}"
game=once(game,old_wrapper,new_wrapper,'remove opportunity auto popup')

old_pointer="  function handleMapPointer(clientX,clientY){const guidance=researchGuidanceAt(clientX,clientY);if(guidance){research?.openNavigationPrompt?.(guidance.targetId);return;}const portItem=nearbyCityAt(clientX,clientY);if(portItem){if(state.dockedPort===portItem.city.name&&currentPortCity){currentPortCity=portItem.city;research?.enterPort?.(portItem.city,{resume:true});}else startPortApproach(portItem);return;}const site=nearbyResearchTargetAt(clientX,clientY);if(site){research?.selectTarget?.(site.target.id);if(site.distance<=RESEARCH_INTERACTION_KM)research?.openTarget?.(site.target.id,{distanceKm:site.distance,atSite:true,target:site.target});else navigateToResearchTarget(site.target);return;}"
new_pointer="  function handleMapPointer(clientX,clientY){const guidance=researchGuidanceAt(clientX,clientY);if(guidance){const target=researchTargets().find(item=>item.id===guidance.targetId);if(target){const item=researchTargetWorld(target);research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,target});}return;}const site=nearbyResearchTargetAt(clientX,clientY);if(site){research?.selectTarget?.(site.target.id);research?.openTarget?.(site.target.id,{distanceKm:site.distance,atSite:site.distance<=RESEARCH_INTERACTION_KM,target:site.target});return;}const portItem=nearbyCityAt(clientX,clientY);if(portItem){if(state.dockedPort===portItem.city.name&&currentPortCity){currentPortCity=portItem.city;research?.enterPort?.(portItem.city,{resume:true});}else startPortApproach(portItem);return;}"
game=once(game,old_pointer,new_pointer,'research click priority and stable card')

# Prevent popup opportunities from spawning over a port marker.
port_anchor="    const site=polar(point.lat,point.lon),siteIce=iceTypeAt(site.x,site.y),siteProfile=iceNavigationProfileAt(site.x,site.y),template=context.template||{},iceAllowed=!!template.iceAllowed;\n"
port_new=port_anchor+"    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<38;}))return false;\n"
game=once(game,port_anchor,port_new,'opportunity port clearance')

# All off-screen targets receive guidance arrows, not only the selected grant.
game=rex(game,r"  function drawResearchGuidance\(\)\{.*?\n  function researchGuidanceAt\(x,y\)\{.*?\}\n",'''  function drawResearchGuidance(){
    const hits=[],cx=width/2,cy=height/2,targets=researchTargets().map(target=>({target,...researchTargetWorld(target)})).filter(item=>item.p.x<=35||item.p.x>=width-35||item.p.y<=95||item.p.y>=height-35).sort((a,b)=>(b.target.selected?1:0)-(a.target.selected?1:0)||a.distance-b.distance).slice(0,8);
    for(let index=0;index<targets.length;index++){const item=targets[index],target=item.target,p=item.p,dx=p.x-cx,dy=p.y-cy,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length,edge=Math.min(width*.38,height*.36),spread=(index%3-1)*11,x=cx+ux*edge-uy*spread,y=cy+uy*edge+ux*spread,a=Math.atan2(uy,ux),opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity',selected=!!(target.selected||target.active);hits.push({x,y,r:selected?33:27,targetId:target.id});ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.fillStyle=opportunity?'rgba(142,240,207,.97)':'rgba(246,211,101,.96)';ctx.strokeStyle='rgba(5,34,48,.92)';ctx.lineWidth=selected?3.5:2.5;ctx.beginPath();ctx.moveTo(selected?16:13,0);ctx.lineTo(-8,-8);ctx.lineTo(-4,0);ctx.lineTo(-8,8);ctx.closePath();ctx.fill();ctx.stroke();ctx.rotate(-a);ctx.font=`${selected?900:800} ${selected?9:8}px system-ui`;ctx.textAlign='center';ctx.strokeStyle='rgba(5,34,48,.96)';ctx.lineWidth=3;const title=(target.shortTitle||target.title||'RESEARCH').toUpperCase().slice(0,18),label=`${title} · ${Math.round(item.distance)} KM`;ctx.strokeText(label,0,24);ctx.fillStyle=opportunity?'#b9f7df':'#fff3aa';ctx.fillText(label,0,24);ctx.restore();}
    researchGuidanceHit=hits;
  }
  function researchGuidanceAt(x,y){const hits=Array.isArray(researchGuidanceHit)?researchGuidanceHit:researchGuidanceHit?[researchGuidanceHit]:[];return [...hits].reverse().find(hit=>Math.hypot(x-hit.x,y-hit.y)<=hit.r)||null;}
''','all research arrows')

# Cache bust the two runtime files.
index=re.sub(r'expedition\.js\?v=[^\"]+', 'expedition.js?v=expedition-23m-research-program', index, count=1)
index=re.sub(r'game\.js\?v=[^\"]+', 'game.js?v=expedition-23m-research-program', index, count=1)

EXP.write_text(exp)
GAME.write_text(game)
INDEX.write_text(index)
