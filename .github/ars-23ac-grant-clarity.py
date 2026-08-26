from pathlib import Path
import re

p=Path('expedition.js')
s=p.read_text()

def sub_once(pattern,repl,label,flags=re.S):
    global s
    s2,n=re.subn(pattern,repl,s,count=1,flags=flags)
    if n!=1: raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s2

def rep_once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s.replace(old,new,1)

# Fresh vessel-art URLs so repaired binaries are not served from stale browser cache.
s=s.replace("?v=23x'","?v=23ac'")

# Purchase diagnostics: capacity before crew, with exact slot/helideck numbers.
sub_once(r"  function equipmentPurchaseStatus\(item,ship=vessel\(\)\) \{.*?\n  \}\n  function slotSummary",'''  function equipmentPurchaseStatus(item,ship=vessel()) {
    if (!item) return {ready:false,reason:'Equipment unavailable'};
    const inventory=state.inventory[item.id]||0,maxUnits=item.maxUnits??Infinity,loadUnits=item.consumable?Math.min(item.units||1,Math.max(0,maxUnits-inventory)):0,purchaseCost=item.consumable?Math.round(item.price*loadUnits/Math.max(1,item.units||1)):item.price,storageRoom=!item.consumable||loadUnits>0;
    const possible=equipmentPossibleOnShip(item,ship),capacity=item.consumable?storageRoom:(item.builtIn||equipmentFits(ship,item.id));
    const usage=slotUsage(),slotType=item.slotType||'science',slotUsed=usage[slotType]||0,slotTotal=ship.slots?.[slotType]||0,slotsNeeded=item.slots||0,deckUsed=helideckUsage();
    const playerTierReady=(item.tier||1)<=playerCareerLevel(),crewReady=crewRequirementsMet(equipmentCrewRequirements(item)),prerequisites=(item.requiresEquipment||[]).every(id=>equipmentOperational(id));
    const support=playerTierReady&&crewReady&&prerequisites,affordable=state.money>=purchaseCost; let reason='Ready to purchase';
    if (!possible) reason='Not supported by this vessel class';
    else if (!playerTierReady) reason=`Chief Scientist must reach ${item.tier===3?'professor':'postdoc'} level first`;
    else if (!storageRoom) reason=`Expendable storage full · ${inventory}/${maxUnits} units aboard`;
    else if (!capacity) {
      if((item.helideckUse||0)>0&&deckUsed+(item.helideckUse||0)>ship.helidecks) reason=`No helideck capacity · ${deckUsed}/${ship.helidecks} positions in use · needs ${item.helideckUse}`;
      else reason=`No ${slotType} equipment capacity · ${slotUsed}/${slotTotal} slots used · needs ${slotsNeeded}`;
    }
    else if (!crewReady) reason=`Crew requirement not met · ${equipmentCrewRequirements(item).map(need=>`${need.count||1} × ${CAREERS[need.minCareer]?.short||need.minCareer} · ${(need.specialties||[]).map(id=>specialtyById[id]?.name||id).join(' / ')}`).join(' + ')||'qualified operator required'}`;
    else if (!prerequisites) reason=`Requires ${item.requiresEquipment.map(id=>EQUIPMENT[id]?.name||id).join(' + ')}`;
    else if (!affordable) reason='Insufficient funds';
    return {ready:possible&&capacity&&support&&affordable,possible,capacity,crewReady,prerequisites,support,affordable,storageRoom,maxUnits,inventory,loadUnits,purchaseCost,reason,slotType,slotUsed,slotTotal,slotsNeeded,deckUsed};
  }
  function slotSummary''','equipment purchase status')

# Make equipment cards report the actual blocker rather than always blaming crew.
rep_once("    const status=ready?'OPERATIONAL WITH CURRENT CREW':item.consumable&&inventory<=0?(supportReady?'CURRENT CREW READY · NO UNITS ABOARD':`CURRENT CREW CANNOT OPERATE · ${tier} SUPPORT NEEDED`):installed?`NOT OPERABLE · ${tier}-LEVEL SUPPORT NEEDED`:supportReady?'CURRENT CREW CAN OPERATE':'CURRENT CREW CANNOT OPERATE';",
"    const status=ready?'OPERATIONAL WITH CURRENT CREW':item.consumable&&inventory<=0?(purchase.ready?'READY TO LOAD · NO UNITS ABOARD':purchase.reason.toUpperCase()):installed?equipmentReadinessDetail(item.id).toUpperCase():purchase.ready?'READY TO PURCHASE & INSTALL':purchase.reason.toUpperCase();",
'equipment card status')

# Precise mission equipment diagnostics, and only shop-link equipment that is physically absent.
insert='''  function equipmentPhysicallyAboard(id) {
    const item=EQUIPMENT[id];if(!item)return false;
    return item.consumable?(state.inventory[id]||0)>0:isInstalled(id);
  }
  function equipmentReadinessDetail(id) {
    const item=EQUIPMENT[id];if(!item)return 'Equipment unavailable';
    if(!equipmentPhysicallyAboard(id))return 'Not aboard';
    if(item.deploymentAsset&&state.deployments.some(deployment=>deployment.recoveryRequired&&deployment.status!=='recovered'&&(deployment.equipment||[]).includes(id)))return 'Aboard, but currently deployed and awaiting recovery';
    if(id==='deep-mooring-payload'&&state.deployments.some(deployment=>deployment.recoveryRequired&&deployment.status!=='recovered'))return 'Aboard, but committed to an unrecovered mooring';
    if((item.helideckUse||0)>vessel().helidecks)return `Aboard, but this vessel lacks ${item.helideckUse} required helideck position${item.helideckUse===1?'':'s'}`;
    const missingSupport=(item.requiresEquipment||[]).filter(required=>!equipmentOperational(required));
    if(missingSupport.length)return `Aboard, but support system missing: ${missingSupport.map(required=>EQUIPMENT[required]?.name||required).join(' + ')}`;
    if(!crewRequirementsMet(equipmentCrewRequirements(item)))return `Aboard, but crew requirement not met: ${equipmentCrewRequirements(item).map(need=>`${need.count||1} × ${CAREERS[need.minCareer]?.short||need.minCareer} · ${(need.specialties||[]).map(key=>specialtyById[key]?.name||key).join(' / ')}`).join(' + ')}`;
    return 'Aboard and operable';
  }
'''
marker='  function missionReadiness(target) {'
if s.count(marker)!=1: raise SystemExit('missionReadiness marker')
s=s.replace(marker,insert+marker,1)
rep_once("      rows.push({label:item?.name||id,ready,detail:ready?'Aboard and operable':isInstalled(id)||state.inventory[id]?'Aboard, but the required operator or support system is missing':'Not aboard'});",
"      rows.push({label:item?.name||id,ready,detail:equipmentReadinessDetail(id)});",
'mission equipment detail')
rep_once("    return [...new Set([...(target.equipment||[]),...(target.consumables||[])])].filter(id=>EQUIPMENT[id]&&!equipmentOperational(id));",
"    return [...new Set([...(target.equipment||[]),...(target.consumables||[])])].filter(id=>EQUIPMENT[id]&&!equipmentPhysicallyAboard(id));",
'missing equipment shop links')

# Geographic names must map to their real Arctic region.
anchor_helpers='''  const GEOGRAPHIC_RESEARCH_ANCHORS=[
    {pattern:/\\bbeaufort gyre\\b/i,name:'Beaufort Gyre',lat:75.5,lon:-145,radiusKm:260},
    {pattern:/\\bfram strait\\b/i,name:'Fram Strait',lat:79.5,lon:-1.5,radiusKm:150},
    {pattern:/\\blomonosov ridge\\b/i,name:'Lomonosov Ridge',lat:86.2,lon:140,radiusKm:200},
    {pattern:/\\bsvalbard\\b/i,name:'Svalbard shelf',lat:78.5,lon:15,radiusKm:170}
  ];
  function geographicAnchorFor(template){
    if(template?.fixedDestination)return {lat:template.fixedDestination.lat,lon:template.fixedDestination.lon,radiusKm:35,name:template.shortTitle||template.title||'Research region'};
    const text=`${template?.title||''} ${template?.shortTitle||''}`;const match=GEOGRAPHIC_RESEARCH_ANCHORS.find(item=>item.pattern.test(text));
    return match?{lat:match.lat,lon:match.lon,radiusKm:match.radiusKm,name:match.name}:null;
  }
'''
marker='  function buildTarget(template, origin, rng, kind=\'grant\', options={}) {'
if s.count(marker)!=1: raise SystemExit('buildTarget marker')
s=s.replace(marker,anchor_helpers+marker,1)
rep_once("    const window=template.anywhere?{min:0,max:0}:researchDistanceWindow(template,kind,options);\n    const validator=callbacks.isResearchSiteSuitable;\n    const avoidPoints=[...state.targets,...state.offers,...(state.recentGrantSites||[])].filter(item=>item.status!=='completed');\n    let point=template.anywhere?{lat:origin.lat,lon:origin.lon}:(template.fixedDestination ? {...template.fixedDestination} : null);\n    let distance=0, bearing=0;\n    const spacing=options.nearby?Math.max(35,targetSpacingKm()*.7):targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:template.fixedDestination?null:window,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
"    const window=template.anywhere?{min:0,max:0}:researchDistanceWindow(template,kind,options);\n    const validator=callbacks.isResearchSiteSuitable,anchor=template.anywhere?null:geographicAnchorFor(template);\n    const avoidPoints=[...state.targets,...state.offers,...(state.recentGrantSites||[])].filter(item=>item.status!=='completed');\n    let point=template.anywhere?{lat:origin.lat,lon:origin.lon}:(anchor?{lat:anchor.lat,lon:anchor.lon,siteName:anchor.name}:null);\n    let distance=0, bearing=0;\n    const spacing=options.nearby?Math.max(35,targetSpacingKm()*.7):targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:anchor?null:window,avoidPoints,minimumSpacingKm:spacing,preferred:anchor||null,...options});",
'buildTarget anchor setup')
rep_once("    if (!point && template.fixedDestination) {\n      for (let radius=3; radius<=30&&!point; radius+=3) for (let angle=0; angle<360; angle+=20) {\n        const candidate=destination(template.fixedDestination.lat,template.fixedDestination.lon,radius,angle);\n        distance=geoDistance(origin,candidate); bearing=angle;\n        if (pointIsSpaced(candidate,avoidPoints,spacing) && (!validator||validator(candidate,context()))) { point=candidate; break; }\n      }\n    }\n    if (!point && !template.fixedDestination) {",
"    if (!point && anchor) {\n      const step=Math.max(5,anchor.radiusKm/12);\n      for (let radius=step; radius<=anchor.radiusKm&&!point; radius+=step) for (let angle=0; angle<360; angle+=20) {\n        const candidate=destination(anchor.lat,anchor.lon,radius,angle);candidate.siteName=anchor.name;\n        distance=geoDistance(origin,candidate); bearing=angle;\n        if (pointIsSpaced(candidate,avoidPoints,spacing) && (!validator||validator(candidate,context()))) { point=candidate; break; }\n      }\n    }\n    if (!point && !anchor) {",
'anchored site search')
rep_once("      if (fallback&&Number.isFinite(fallback.lat)&&Number.isFinite(fallback.lon)&&(!template.fixedDestination||geoDistance(fallback,template.fixedDestination)<=35)&&pointIsSpaced(fallback,avoidPoints,spacing)&&(!validator||validator(fallback,context()))) point=fallback;",
"      if (fallback&&Number.isFinite(fallback.lat)&&Number.isFinite(fallback.lon)&&(!anchor||geoDistance(fallback,anchor)<=anchor.radiusKm)&&pointIsSpaced(fallback,avoidPoints,spacing)&&(!validator||validator(fallback,context()))) {point=fallback;if(anchor&&!point.siteName)point.siteName=anchor.name;}",
'anchored fallback guard')

# Richer first window at a discovered ? site.
discovery='''  function opportunityDiscoverySummary(target){
    const ids=participantIdsFor(target),people=state.scientists.filter(item=>ids.includes(item.id)),names=people.map(item=>item.name).filter(Boolean),fields=[...new Set(people.map(item=>specialtyById[item.specialty]?.name).filter(Boolean))];
    const gear=[...new Set([...(target.equipment||[]),...(target.consumables||[])])].map(id=>EQUIPMENT[id]?.name).filter(Boolean);
    const science=names.length?`${names.join(names.length>2?', ':names.length===2?' & ':'')}${names.length>2?` & ${names.pop()}`:''} made this opportunity possible with ${fields.join(' / ')||'the science team'} expertise.`:`Your science team made this opportunity possible.`;
    const equipment=gear.length?`Required equipment: ${gear.join(' + ')}.`:'Required equipment: general field kit only.';
    return `<div class="arx-empty arx-opportunity-context"><b>WHY THIS OPPORTUNITY APPEARED</b><p>${escapeHtml(science)}</p><small>${escapeHtml(equipment)}</small></div>`;
  }
'''
marker='  function renderResearchWindow(target,{phase=\'ready\',resultTitle=\'\',resultBody=\'\',resultStats=[]}={}) {'
if s.count(marker)!=1: raise SystemExit('renderResearchWindow marker')
s=s.replace(marker,discovery+marker,1)
rep_once("${mediaMarkup(target,'hero')}<p>${escapeHtml(target.description)}</p><div class=\"arx-target-facts arx-research-facts\">",
"${mediaMarkup(target,'hero')}<p>${escapeHtml(target.description)}</p>${opportunityDiscoverySummary(target)}<div class=\"arx-target-facts arx-research-facts\">",
'opportunity discovery summary')

# Grant life: 21 days. Expired grants are retired one at a time, at most weekly.
s=s.replace('offer.expiresAtDay=state.elapsedDays+14','offer.expiresAtDay=state.elapsedDays+21')
if s.count('offer.expiresAtDay=state.elapsedDays+21')<2: raise SystemExit('grant acceptance deadlines not updated')
rep_once("lastProfessorGrantDay:-999, remoteOffer:null","lastProfessorGrantDay:-999, lastExpiredGrantRemovalDay:-999, remoteOffer:null",'state expiry throttle')
sub_once(r"    const expiredGrantIds=new Set\(\);\n    for\(const target of state\.targets\)\{.*?\n    if\(expiredGrantIds\.size\)\{.*?\}\n\n    const activeWeather=",
'''    const expiredCandidates=state.targets.filter(target=>(target.kind==='grant'||target.kind==='contract')&&!['completed','failed','dropped'].includes(target.status)&&Number.isFinite(target.expiresAtDay)&&state.elapsedDays>=target.expiresAtDay&&activeOperation?.targetId!==target.id).sort((a,b)=>(a.expiresAtDay||0)-(b.expiresAtDay||0));
    const expiryThrottleReady=state.elapsedDays-(Number(state.lastExpiredGrantRemovalDay??-999))>=7;
    if(expiredCandidates.length&&expiryThrottleReady){
      const target=expiredCandidates[0];target.status='dropped';target.selected=false;state.targets=state.targets.filter(item=>item.id!==target.id);if(state.navigation?.id===target.id)state.navigation=null;state.lastExpiredGrantRemovalDay=state.elapsedDays;addLog(`Research grant expired after 21 days: ${target.title}.`);if(target.professorOriginated)state.lastProfessorGrantDay=state.elapsedDays;toast('RESEARCH GRANT EXPIRED · 21-DAY DEADLINE');
    }

    const activeWeather=''', 'weekly expiry removal')
rep_once("state.lastPortId=state.lastPortId||null; state.lastProfessorGrantDay=Number(state.lastProfessorGrantDay??-999); state.remoteOffer=state.remoteOffer||null;",
"state.lastPortId=state.lastPortId||null; state.lastProfessorGrantDay=Number(state.lastProfessorGrantDay??-999); state.lastExpiredGrantRemovalDay=Number(state.lastExpiredGrantRemovalDay??-999); state.remoteOffer=state.remoteOffer||null;",
'restore expiry throttle')
rep_once("    for(const grant of activeGrants()){if(!Number.isFinite(grant.acceptedAtDay))grant.acceptedAtDay=state.elapsedDays;if(!Number.isFinite(grant.expiresAtDay))grant.expiresAtDay=grant.acceptedAtDay+14;}",
"    for(const grant of activeGrants()){if(!Number.isFinite(grant.acceptedAtDay))grant.acceptedAtDay=state.elapsedDays;const legacyDeadline=grant.acceptedAtDay+14;if(!Number.isFinite(grant.expiresAtDay)||grant.expiresAtDay<=legacyDeadline+.01)grant.expiresAtDay=grant.acceptedAtDay+21;}",
'legacy deadline migration')

# Publication result explicitly says letter/article/book.
rep_once("      heading='Manuscript accepted'; message=`Published in ${level.journal}. ${new Intl.NumberFormat().format(state.data)} overflow data remain available for the next paper.`;\n      addLog(`Article published in ${level.journal}; sponsor recognition received.`); callbacks.onSound?.('paper-accepted');\n    } else {\n      heading='Manuscript rejected'; message='Reviewers requested revision and resubmission.';\n      addLog('Manuscript rejected; all data retained for revision.'); callbacks.onSound?.('paper-rejected');",
"      heading=`${level.label} published`; message=`Your team published a ${level.label.toLowerCase()} in ${level.journal}. ${new Intl.NumberFormat().format(state.data)} overflow data remain available for the next publication.`;\n      addLog(`${level.label} published in ${level.journal}; sponsor recognition received.`); callbacks.onSound?.('paper-accepted');\n    } else {\n      heading=`${level.label} submission rejected`; message=`Reviewers requested revision and resubmission of the ${level.label.toLowerCase()}.`;\n      addLog(`${level.label} submission rejected; all data retained for revision.`); callbacks.onSound?.('paper-rejected');",
'publication type messaging')
rep_once("<small>${automatic?'AUTOMATIC TOP-TIER SUBMISSION':'EDITORIAL DECISION'}${accepted?' · ACCEPTED':''}</small>",
"<small>${escapeHtml(level.label.toUpperCase())} · ${automatic?'AUTOMATIC TOP-TIER SUBMISSION':'EDITORIAL DECISION'}${accepted?' · ACCEPTED':''}</small>",
'publication modal type')

p.write_text(s)

# Cache bust the three main assets touched by this pass.
ip=Path('index.html'); html=ip.read_text(); html=html.replace('expedition-23aa-equipment-grants','expedition-23ac-grant-clarity-images'); ip.write_text(html)
print('ARS 23ac patch applied')
