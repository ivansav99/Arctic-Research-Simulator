from pathlib import Path
import re


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    p.write_text(text.replace(old, new, 1))


def sub_once(path, pattern, new, label, flags=re.S):
    p = Path(path)
    text = p.read_text()
    text2, count = re.subn(pattern, new, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 regex match, found {count}')
    p.write_text(text2)


# One shared citation budget across all hired scientists.
sub_once(
    'expedition.js',
    r"  function hiredCareerCount\(id\) \{[^\n]*\}\n  function careerHireStatus\(id\) \{.*?\n  \}\n",
    """  function hiredCareerCount(id) { return state.scientists.filter(item=>!item.isPlayer&&item.career===id).length; }
  const CAREER_CITATION_COST={grad:10,postdoc:100,professor:1000};
  function citationCapacityUsed() {
    return state.scientists.filter(item=>!item.isPlayer).reduce((sum,item)=>sum+(CAREER_CITATION_COST[item.career]||0),0);
  }
  function careerHireStatus(id) {
    const cost=CAREER_CITATION_COST[id]||Infinity,total=Math.floor(state.citations),used=citationCapacityUsed(),playerReady=id==='grad'||playerCareerLevel()>=careerLevel(id);
    const stage=id==='grad'?'Graduate Student':id==='postdoc'?'Postdoc':'Professor';
    const gate=!playerReady?`Chief Scientist must become a ${id==='postdoc'?'postdoc':'professor'} first`:null;
    return {ready:playerReady&&used+cost<=total,label:gate||`Citation budget ${used}/${total} used · ${stage} requires ${cost.toLocaleString()} citations`};
  }
""",
    'shared citation budget'
)

# Progressively push spontaneous opportunities farther out as vessel/career improves.
sub_once(
    'expedition.js',
    r"  function researchDistanceWindow\(template,kind,options=\{\}\) \{.*?\n  \}\n  function targetSpacingKm",
    """  function researchDistanceWindow(template,kind,options={}) {
    if(options.nearby){const max=options.iceThickness>=2?70:90;return{min:10,max};}
    const ranges={fishing:[5,48],trawler:[10,125],coastal:[28,330],global:[65,700],icebreaker:[95,1050],nuclear:[125,1450]}, range=ranges[state.currentVessel]||ranges.fishing;
    const progress=clamp(state.completed.length/12,0,1),localMax=state.currentVessel==='fishing'?28+progress*34:state.currentVessel==='trawler'?80+progress*55:range[1];
    const career=playerCareerLevel(),careerBonus=career>=3?45:career===2?20:0;
    const opportunityFloor={fishing:18,trawler:55,coastal:100,global:180,icebreaker:260,nuclear:340}[state.currentVessel]||18;
    const explicit=template.minDistance??0,official=kind==='grant'||kind==='contract';
    const baseMin=kind==='opportunity'||kind==='weather-opportunity'?Math.max(explicit,opportunityFloor+careerBonus):Math.max(explicit,range[0]+careerBonus);
    const min=official&&!template.anywhere?Math.max(22,baseMin):baseMin;
    const requestedMax=min+(template.distanceRange??((kind==='opportunity'||kind==='weather-opportunity')?range[1]*.55:range[1]-range[0]));
    return {min:Math.min(min,localMax-2),max:Math.max(min+2,Math.min(requestedMax,localMax))};
  }
  function targetSpacingKm""",
    'progression distance window'
)

# Rewards increase materially with career level and platform capability.
sub_once(
    'expedition.js',
    r"  function missionRewardAmount\(template,kind,distanceKm,rng,actualWorkHours=template\.workHours\) \{.*?\n  \}\n",
    """  function missionRewardAmount(template,kind,distanceKm,rng,actualWorkHours=template.workHours) {
    const official=kind==='grant'||kind==='contract',base=official?[40000,60000]:[10000,15000];
    const score=clamp(missionRewardScore(template,distanceKm,kind,actualWorkHours)+(rng()-.5)*.05,0,1);
    const careerFactor=playerCareerLevel()>=3?2.4:playerCareerLevel()===2?1.55:1;
    const vesselFactor={fishing:1,trawler:1.25,coastal:1.8,global:3,icebreaker:4.5,nuclear:6}[state.currentVessel]||1;
    const templateFactor=1+Math.max(0,templateCareerLevel(template)-1)*.18;
    const value=(base[0]+(base[1]-base[0])*score)*careerFactor*vesselFactor*templateFactor;
    return Math.round(value/500)*500;
  }
""",
    'progression reward scaling'
)

# Grant board scales with same-career peers and deliberately covers onboard specialties.
sub_once(
    'expedition.js',
    r"  function generateOffers\(port,\{fresh=false\}=\{\}\) \{.*?\n  \}\n\n  function mediaMarkup",
    """  function generateOffers(port,{fresh=false}={}) {
    if(!port)return; const portId=normalizedPortId(port),cycle=`${portId}:${state.portVisits}`; if(!fresh&&state.grantOfferCycle===cycle)return; state.grantOfferCycle=cycle;
    const rng=seeded(`${portId}-${state.portVisits}-grants-v6-${playerScientist()?.career||'grad'}-${state.currentVessel}`),activeTemplates=new Set(activeGrants().map(item=>item.templateId));
    const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);
    const teamLevel=playerCareerLevel(),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length,weighted=[];
    for(const template of available){const level=templateCareerLevel(template);let weight=teamLevel===1?(level===1?7:1):teamLevel===2?(level===2?12:level===1?1:2):(level===3?15:level===2?5:1);if(level===2)weight+=postdocCount*4+professorCount*2;if(level===3)weight+=professorCount*5;if(template.fjordPreferred&&teamLevel===1)weight+=2;for(let i=0;i<weight;i++)weighted.push(template);}
    for(let i=weighted.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[weighted[i],weighted[j]]=[weighted[j],weighted[i]];} const pool=[],seen=new Set(); for(const item of weighted)if(!seen.has(item.id)){seen.add(item.id);pool.push(item);}
    if(state.completed.length===0&&teamLevel===1){const harbor=pool.find(item=>item.id==='harbor-soundings');if(harbor){pool.splice(pool.indexOf(harbor),1);pool.unshift(harbor);}}
    const chiefCareer=playerScientist()?.career||'grad',sameLevel=state.scientists.filter(item=>item.career===chiefCareer),offerLimit=Math.min(12,Math.max(3,2+sameLevel.length*2));
    const priority=[],priorityIds=new Set();
    for(const scientist of [...sameLevel,...state.scientists.filter(item=>item.career!==chiefCareer)]){
      const match=pool.find(template=>!priorityIds.has(template.id)&&(template.specialties||[]).includes(scientist.specialty));
      if(match){priority.push(match);priorityIds.add(match.id);}
    }
    const ordered=[...priority,...pool.filter(item=>!priorityIds.has(item.id))];
    state.offers=[];const usedPictures=new Set();let attempts=0;
    for(const template of ordered){if(state.offers.length>=offerLimit||attempts>=offerLimit*4)break;attempts++;const target=buildTarget(template,port,rng,'grant');if(!target)continue;if(!giveGrantUniqueMedia(target,usedPictures,rng))continue;state.offers.push(target);}
    if(!state.offers.length){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback){giveGrantUniqueMedia(fallback,usedPictures,rng);state.offers.push(fallback);}}
  }

  function mediaMarkup""",
    'team-scaled grant board'
)

# If the team can see an opportunity but lacks equipment/crew, keep it as an aspirational gray ?.
replace_once(
    'expedition.js',
    """    let pool;
    if(!ready.length){const fallback=compatibleFallbackTemplate(),target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:inIce,iceThickness});if(!target)return null;target.selected=false;state.targets.push(target);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed();return target;}
    if (aspirational.length&&rng()<.30) pool=aspirational; else pool=ready;""",
    """    let pool;
    if(!ready.length&&aspirational.length) pool=aspirational;
    else if(!ready.length){const fallback=compatibleFallbackTemplate(),target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:inIce,iceThickness});if(!target)return null;target.selected=false;state.targets.push(target);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed();return target;}
    else if (aspirational.length&&rng()<.30) pool=aspirational; else pool=ready;""",
    'aspirational popup fallback'
)

# Central refresh hook for career, vessel, team and equipment progression.
p = Path('expedition.js')
text = p.read_text()
pattern = r"(  function scheduleGrantRefresh\(delay=120\)\{.*?\n  \}\n)"
m = re.search(pattern, text, flags=re.S)
if not m:
    raise SystemExit('progression refresh helper: scheduleGrantRefresh not found')
helper = """  function refreshProgressionOpportunities(reason='progression') {
    const removed=new Set(state.targets.filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!item.accepted&&item.status!=='completed').map(item=>item.id));
    if(removed.size){state.targets=state.targets.filter(item=>!removed.has(item.id));if(state.navigation&&removed.has(state.navigation.id))state.navigation=null;if(state.lastTargetContext&&removed.has(state.lastTargetContext.id))state.lastTargetContext=null;}
    state.grantOfferCycle=null;
    if(state.port){generateCandidates(state.port);refreshGrantOffersNow({render:true});}
    callbacks.onProgressionChanged?.({reason});
  }
"""
p.write_text(text[:m.end()] + helper + text[m.end():])

replace_once(
    'expedition.js',
    "addLog('Chief Scientist promoted to postdoc · coastal R/V and medium equipment unlocked.');",
    "addLog('Chief Scientist promoted to postdoc · coastal R/V and medium equipment unlocked.'); refreshProgressionOpportunities('career-promotion');",
    'postdoc promotion refresh'
)
replace_once(
    'expedition.js',
    "addLog('Chief Scientist promoted to professor · global vessels, icebreakers and heavy equipment unlocked.');",
    "addLog('Chief Scientist promoted to professor · global vessels, icebreakers and heavy equipment unlocked.'); refreshProgressionOpportunities('career-promotion');",
    'professor promotion refresh'
)

# Preserve compatible science equipment across hull changes and sell only excess/incompatible systems.
sub_once(
    'expedition.js',
    r"  function vesselTradeInValue\(ship=vessel\(\)\) \{.*?\n  \}\n",
    """  function equipmentFitsIds(ship,ids) {
    const used=slotUsage(ids);return SLOT_TYPES.every(type=>used[type]<=(ship.slots[type]||0))&&helideckUsage(ids)<=ship.helidecks;
  }
  function vesselTransferPlan(next) {
    const kept=[],sold=[];
    for(const id of state.installedEquipment){const item=EQUIPMENT[id];if(item&&equipmentPossibleOnShip(item,next)&&equipmentFitsIds(next,[...kept,id]))kept.push(id);else sold.push(id);}
    const keptInventory={},soldInventory={};
    for(const [id,count] of Object.entries(state.inventory||{})){const item=EQUIPMENT[id];if(item&&equipmentPossibleOnShip(item,next))keptInventory[id]=count;else soldInventory[id]=count;}
    const installedCredit=sold.reduce((sum,id)=>sum+Math.round((EQUIPMENT[id]?.price||0)*EQUIPMENT_RESALE_RATE),0);
    const inventoryCredit=Object.entries(soldInventory).reduce((sum,[id,count])=>{const item=EQUIPMENT[id];return sum+(item?Math.round(item.price/Math.max(1,item.units||1)*count*EQUIPMENT_RESALE_RATE):0);},0);
    return {kept,sold,keptInventory,soldInventory,resaleCredit:installedCredit+inventoryCredit};
  }
  function vesselTradeInValue(ship=vessel(),next=null) {
    const hull=Math.round(vesselPurchasePrice(ship)*VESSEL_TRADE_IN_RATE);
    if(next)return hull+vesselTransferPlan(next).resaleCredit;
    const installed=state.installedEquipment.reduce((sum,id)=>sum+Math.round((EQUIPMENT[id]?.price||0)*EQUIPMENT_RESALE_RATE),0);
    const inventory=Object.entries(state.inventory).reduce((sum,[id,count])=>{const item=EQUIPMENT[id]; return sum+(item?Math.round(item.price/Math.max(1,item.units||1)*count*EQUIPMENT_RESALE_RATE):0);},0);
    return hull+installed+inventory;
  }
  function vesselCommissioningCost(ship){return fullResupplyCost(ship);}
""",
    'vessel equipment transfer plan'
)

sub_once(
    'expedition.js',
    r"  function vesselPurchaseReady\(item\) \{.*?\n  \}\n  function vesselCard\(item\) \{.*?\n  \}\n",
    """  function vesselPurchaseReady(item) {
    if(!item||item.id===state.currentVessel)return false;
    if(!vesselMarketUnlock(item.id)||!vesselForSaleHere(item.id))return false;
    const preview=crewPreviewForVessel(item),gate=gateStatus(item,preview.kept),blockedAsset=deployedTradeAsset(),credit=vesselTradeInValue(vessel(),item),commissioning=vesselCommissioningCost(item),due=Math.max(0,vesselPurchasePrice(item)+commissioning-credit),grantBlocked=grantLoad()>Math.max(1,preview.kept.length);
    return !blockedAsset&&gate.ready&&!grantBlocked&&state.money>=due;
  }
  function vesselCard(item) {
    const active=state.currentVessel===item.id,unlocked=vesselMarketUnlock(item.id),forSale=vesselForSaleHere(item.id),preview=crewPreviewForVessel(item),gate=gateStatus(item,preview.kept),blockedAsset=deployedTradeAsset(),transfer=vesselTransferPlan(item),credit=vesselTradeInValue(vessel(),item),listPrice=vesselPurchasePrice(item),commissioning=vesselCommissioningCost(item),net=listPrice+commissioning-credit,due=Math.max(0,net),refund=Math.max(0,-net),grantBlocked=grantLoad()>Math.max(1,preview.kept.length),fuel=item.nuclearFuel?'REACTOR · ∞':formatCapacity(item.fuelCapacity,'L');
    const careerNeed=item.id==='coastal'?'Postdoc Chief Scientist':(['global','icebreaker','nuclear'].includes(item.id)?'Professor Chief Scientist':'No career gate');
    const transferText=active?'Current equipment remains aboard':transfer.sold.length?`${transfer.kept.length} systems transfer · ${transfer.sold.length} excess systems sold`:`${transfer.kept.length} installed systems transfer automatically`;
    const checks=[{ok:active||unlocked,text:active?'Currently equipped vessel':unlocked?`${careerNeed} requirement met`:careerNeed},{ok:active||forSale,text:forSale?'Sold at this port':item.id==='nuclear'?'Sold in Russian Arctic ports':'Conventional vessels sold at non-Russian Arctic ports'},{ok:active||!blockedAsset,text:blockedAsset?`Recover ${EQUIPMENT[blockedAsset]?.name||'deployed equipment'}`:'No deployed trade-blocking equipment'},{ok:active||gate.ready,text:gate.label},{ok:active||!grantBlocked,text:grantBlocked?'Reduce active grants before downsizing crew':'Active grants fit retained crew'},{ok:true,text:transferText},{ok:active||state.money>=due,text:refund>0?`Trade-in credit exceeds fully supplied purchase cost by ${cash(refund)}`:`Available cash ${cash(state.money)} · total due ${cash(due)}`}];
    const disabled=active||checks.some(check=>!check.ok),image=item.image||'assets/vessels/base-vessel.png',reason=active?'EQUIPPED':disabled?'PURCHASE UNAVAILABLE':refund>0?`PURCHASE FULLY SUPPLIED · RECEIVE ${cash(refund)} CREDIT`:`PURCHASE FULLY SUPPLIED · ${cash(due)}`,badge=active?'EQUIPPED':(listPrice?cash(listPrice):'STARTER VESSEL'),tradeName=vessel().shipName||vessel().name;
    return `<details class=\"arx-card arx-store-details ${active?'selected':''}\" data-arx-store-details=\"vessel-${item.id}\"><summary><span><b>${escapeHtml(item.shipName||item.name)}</b><small>${escapeHtml(item.name)} · ${item.className} · ${item.berths} BERTHS</small></span><em class=\"${disabled&&!active?'price-locked':''}\">${badge}</em></summary><div class=\"arx-detail-split\"><figure class=\"arx-media compact\"><img src=\"${escapeHtml(image)}\" alt=\"Side view of ${escapeHtml(item.shipName||item.name)}\"></figure><div><p>${escapeHtml(item.description)}</p><ul class=\"arx-spec-list arx-vessel-specs\"><li>${item.cruiseKnots} kn cruise · ${item.maxKnots} kn maximum</li><li>${escapeHtml(vesselIceCapabilityText(item))}</li><li>${fuel} fuel · ${item.foodEnduranceDays} d provisions</li><li>${item.helidecks} helideck${item.helidecks===1?'':'s'}</li><li>${slotSummary(item,{light:0,medium:0,heavy:0})}</li><li>${item.berths} total berths</li></ul><div class=\"arx-vessel-purchase-breakdown\"><span><small>HULL PRICE</small><b>${cash(listPrice)}</b></span><span><small>FULL FUEL / FOOD / LAB STORES</small><b>+ ${cash(commissioning)}</b></span><span><small>TRADE-IN + EXCESS SALE · ${escapeHtml(tradeName)}</small><b>− ${cash(credit)}</b></span><span><small>TOTAL DUE</small><b>${refund?`CREDIT ${cash(refund)}`:cash(due)}</b></span></div><div class=\"arx-requirement-checklist\">${checks.map(check=>`<div class=\"${check.ok?'ready':'missing'}\"><i>${check.ok?'✓':'!'}</i><span>${escapeHtml(check.text)}</span></div>`).join('')}</div><button data-arx-action=\"vessel\" data-id=\"${item.id}\" ${disabled?'disabled':''}>${reason}</button></div></div></details>`;
  }
""",
    'fully supplied vessel purchase cards'
)

sub_once(
    'expedition.js',
    r"  function chooseVessel\(id\) \{.*?\n  \}\n  function buyEquipment",
    """  function chooseVessel(id) {
    const next=VESSELS[id],previous=vessel(); if(!next||id===state.currentVessel||!vesselForSaleHere(id)||!vesselMarketUnlock(id))return;
    const blockedAsset=deployedTradeAsset();if(blockedAsset){toast(`RECOVER ${EQUIPMENT[blockedAsset]?.name||'DEPLOYED EQUIPMENT'} BEFORE TRADING HULLS`);return;}
    const preview=crewPreviewForVessel(next),gate=gateStatus(next,preview.kept),transfer=vesselTransferPlan(next),credit=vesselTradeInValue(previous,next),listPrice=vesselPurchasePrice(next),commissioning=vesselCommissioningCost(next),due=Math.max(0,listPrice+commissioning-credit);
    if(!gate.ready||grantLoad()>Math.max(1,preview.kept.length)||state.money<due)return;
    adjustMoney(credit-listPrice-commissioning);
    for(const scientist of preview.removed){recordScientist(scientist);const returned={...scientist,id:`candidate-${state.portVisits}-downsize-${scientist.profileId||slug(scientist.name)}`};delete returned.hiredAt;if(!state.candidates.some(item=>item.profileId===returned.profileId))state.candidates.push(returned);}
    state.scientists=preview.kept;state.installedEquipment=transfer.kept;state.inventory=transfer.keptInventory;state.ownedVessels=[id];pendingCandidateId=null;
    state.currentVessel=id;state.supplies=next.supplyCapacity;callbacks.setResources?.({fuel:100,food:100});
    const equipmentNote=transfer.sold.length?` ${transfer.kept.length} installed systems transferred; ${transfer.sold.length} excess systems sold automatically.`:` ${transfer.kept.length} installed systems transferred automatically.`;
    addLog(`${previous.shipName||previous.name} traded toward ${next.shipName||next.name}. New vessel commissioned with full fuel, food and lab stores for ${cash(commissioning)}.${equipmentNote}${preview.removed.length?` ${preview.removed.map(item=>item.name).join(', ')} remained ashore.`:''}`);
    callbacks.onVesselChanged?.(getVesselModifiers());refreshProgressionOpportunities('vessel-change');changed();
  }
  function buyEquipment""",
    'vessel purchase transfer execution'
)

replace_once(
    'expedition.js',
    "    scheduleGrantRefresh(); addLog(`${item.name} joined as ${career.name}.`); changed();",
    "    refreshProgressionOpportunities('team-change'); addLog(`${item.name} joined as ${career.name}.`); changed();",
    'hire refresh'
)
replace_once(
    'expedition.js',
    "    scheduleGrantRefresh(); changed();\n  }\n  function sellEquipment",
    "    if(item.consumable)scheduleGrantRefresh();else refreshProgressionOpportunities('equipment-change'); changed();\n  }\n  function sellEquipment",
    'equipment purchase refresh'
)

replace_once(
    'expedition.js',
    """if(tab==='crew')return `<p class=\"arx-help\">Salaries are deducted daily for everyone aboard, including you. Additional scientists require citation capacity: 10 per graduate student, 100 per postdoc, and 1,000 per professor.</p><div class=\"arx-vessel-columns\"><section><h3>Available to hire</h3>""",
    """if(tab==='crew')return `<p class=\"arx-help\">Salaries are deducted daily for everyone aboard, including you. All hired scientists share one citation budget: 10 per graduate student, 100 per postdoc, and 1,000 per professor.</p><div class=\"arx-vessel-columns\"><section><h3>Available to hire · ${citationCapacityUsed()}/${Math.floor(state.citations)} citations used</h3>""",
    'crew citation header'
)
replace_once(
    'expedition.js',
    """<span><small>AWARD</small><b>${cash(target.reward||0)}</b></span><span><small>RESULT</small><b>${['mooring-deploy','staged-deploy','autonomous'].includes(target.missionMode)?'Data after telemetry / recovery':`+${target.data} data`}</b></span>""",
    """<span><small>CASH AWARD</small><b>${cash(target.reward||0)}</b></span><span><small>DATA AWARD</small><b>${['mooring-deploy','staged-deploy','autonomous'].includes(target.missionMode)?'Data after telemetry / recovery':`+${target.data} data`}</b></span>""",
    'explicit opportunity awards'
)
replace_once(
    'expedition.js',
    ".arx-vessel-purchase-breakdown{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:10px 0}",
    ".arx-vessel-purchase-breakdown{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:10px 0}",
    'vessel purchase breakdown columns'
)

# Audio: unlock from the first interaction anywhere, not only the map canvas.
replace_once(
    'game.js',
    "    const play=(type)=>{if(!ac)return;switch(type){",
    "    const play=(type)=>{const c=ensure();if(!c)return;if(c.state==='suspended')c.resume();switch(type){",
    'sound play ensures context'
)
replace_once(
    'game.js',
    """    return{unlock,play,update};
  })();

  // Simplified but geographically ordered coastlines""",
    """    return{unlock,play,update};
  })();
  document.addEventListener('pointerdown',()=>sound.unlock(),{capture:true,passive:true});
  document.addEventListener('keydown',()=>sound.unlock(),{capture:true});

  // Simplified but geographically ordered coastlines""",
    'global sound unlock'
)

# Expanded minimap gets its own pannable center; collapsing returns to the vessel.
replace_once(
    'game.js',
    "let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,pendingResearchArrival=null,startFlowPending=false,npcUpdateAccumulator=0,researchGuidanceHit=null,minimapExpanded=false;",
    "let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,pendingResearchArrival=null,startFlowPending=false,npcUpdateAccumulator=0,researchGuidanceHit=null,minimapExpanded=false,miniViewX=state.x,miniViewY=state.y,miniPan=null;",
    'minimap pan state'
)
replace_once(
    'game.js',
    "  function miniMapGeometry(){const zoom=Math.max(.7,minimapExpanded?(miniZoomLevel||zoomLevel||1):(zoomLevel||1)),base=minimapExpanded?1100:1040;return{worldRadius:base/zoom,centerX:state.x,centerY:state.y};}",
    "  function miniMapGeometry(){const zoom=Math.max(.7,minimapExpanded?(miniZoomLevel||zoomLevel||1):(zoomLevel||1)),base=minimapExpanded?1100:1040;return{worldRadius:base/zoom,centerX:minimapExpanded?miniViewX:state.x,centerY:minimapExpanded?miniViewY:state.y};}",
    'minimap independent center'
)
replace_once(
    'game.js',
    "  function openMinimap(){if(!minimapPanel||minimapExpanded)return;minimapExpanded=true;miniZoomLevel=zoomLevel;syncMiniZoomControls();minimapPanel.classList.add('expanded');document.body.classList.add('nav-chart-open');miniLastDraw=0;drawMiniMap();}\n  function closeMinimap(){if(!minimapPanel)return;minimapExpanded=false;minimapPanel.classList.remove('expanded');document.body.classList.remove('nav-chart-open');drawMiniMap();}",
    "  function openMinimap(){if(!minimapPanel||minimapExpanded)return;minimapExpanded=true;miniViewX=state.x;miniViewY=state.y;miniPan=null;miniZoomLevel=zoomLevel;syncMiniZoomControls();minimapPanel.classList.add('expanded');document.body.classList.add('nav-chart-open');miniLastDraw=0;drawMiniMap();}\n  function closeMinimap(){if(!minimapPanel)return;minimapExpanded=false;miniViewX=state.x;miniViewY=state.y;miniPan=null;minimapPanel.classList.remove('expanded');document.body.classList.remove('nav-chart-open');drawMiniMap();}",
    'minimap recenter behavior'
)
replace_once(
    'game.js',
    "  miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();e.preventDefault();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});if(!minimapExpanded)openMinimap();});",
    """  miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();e.preventDefault();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});if(!minimapExpanded){openMinimap();return;}miniCanvas.setPointerCapture?.(e.pointerId);miniPan={id:e.pointerId,startX:e.clientX,startY:e.clientY,centerX:miniViewX,centerY:miniViewY,moved:false};});
  miniCanvas.addEventListener('pointermove',e=>{if(!minimapExpanded||!miniPan||miniPan.id!==e.pointerId)return;e.preventDefault();const radius=Math.max(1,miniCanvas.clientWidth*.45),geometry=miniMapGeometry(),dx=e.clientX-miniPan.startX,dy=e.clientY-miniPan.startY;if(Math.hypot(dx,dy)>6)miniPan.moved=true;miniViewX=miniPan.centerX-dx/radius*geometry.worldRadius;miniViewY=miniPan.centerY-dy/radius*geometry.worldRadius;const limit=TERRAIN_EXTENT_KM*.96,r=Math.hypot(miniViewX,miniViewY);if(r>limit){miniViewX*=limit/r;miniViewY*=limit/r;}miniLastDraw=0;drawMiniMap();});
  function finishMiniPan(e,cancelled=false){if(!miniPan||miniPan.id!==e.pointerId)return;const wasTap=!miniPan.moved&&!cancelled;miniPan=null;if(wasTap)navigateFromMiniMap(e);}
  miniCanvas.addEventListener('pointerup',e=>finishMiniPan(e,false));
  miniCanvas.addEventListener('pointercancel',e=>finishMiniPan(e,true));""",
    'minimap drag pan events'
)

# Do not generate spontaneous opportunities while docked, and keep them well away from ports as capability increases.
replace_once(
    'game.js',
    "    if(researchOpportunityClock>=opportunityInterval){researchOpportunityClock=0;research?.maybeSpawnOpportunity?.(opportunityEnv);}",
    "    if(!currentPortCity&&researchOpportunityClock>=opportunityInterval){researchOpportunityClock=0;research?.maybeSpawnOpportunity?.(opportunityEnv);}",
    'no dockside popup spawning'
)
replace_once(
    'game.js',
    "    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<38;}))return false;",
    "    const researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,portBuffer=({fishing:28,trawler:65,coastal:110,global:180,icebreaker:260,nuclear:340}[vesselIceId()]||28)+(careerLevel-1)*15;\n    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<portBuffer;}))return false;",
    'dynamic opportunity port buffer'
)
replace_once(
    'game.js',
    "    const shore=!!(template.shore||template.terrestrial),distances=shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[28,45,65,85,110,140]:[45,65,85,105,130,165,210]),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150];",
    "    const shore=!!(template.shore||template.terrestrial),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,opportunityStart=({fishing:20,trawler:60,coastal:105,global:185,icebreaker:265,nuclear:345}[vesselIceId()]||20)+(careerLevel-1)*20,distances=shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[opportunityStart,opportunityStart+30,opportunityStart+70,opportunityStart+120,opportunityStart+180]:[45,65,85,105,130,165,210]),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150];",
    'progression fallback opportunity distances'
)

# Wildlife observations scale with research platform and career stage.
replace_once(
    'game.js',
    "  function handleMapPointer(clientX,clientY){",
    """  function wildlifeObservationDataValue(){const researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerFactor=chief?.career==='professor'?2.2:chief?.career==='postdoc'?1.55:1,vesselBase={fishing:2,trawler:3,coastal:5,global:9,icebreaker:14,nuclear:20}[vesselIceId()]||2;return Math.max(2,Math.round(vesselBase*careerFactor));}
  function handleMapPointer(clientX,clientY){""",
    'wildlife data scaling helper'
)
replace_once(
    'game.js',
    "dataValue:2})===true;",
    "dataValue:wildlifeObservationDataValue()})===true;",
    'wildlife scaled award'
)

# Immediately re-seed spontaneous opportunities when progression changes at sea.
replace_once(
    'game.js',
    "    onCharacterReady:beginExpedition,\n    onToast:showToast,",
    "    onCharacterReady:beginExpedition,\n    onProgressionChanged:()=>{researchOpportunityClock=999;if(!currentPortCity){researchOpportunityClock=0;setTimeout(()=>research?.maybeSpawnOpportunity?.(researchEnvironment(currentWeather())),0);}},\n    onToast:showToast,",
    'progression callback'
)

# Cache bust the new playtest build.
p = Path('index.html')
text = p.read_text()
if 'expedition-23r-playtest-fixes' not in text:
    raise SystemExit('index cache tag: 23r marker not found')
p.write_text(text.replace('expedition-23r-playtest-fixes', 'expedition-23s-progression-pass'))

print('ARS 23s patch applied')
