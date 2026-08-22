from pathlib import Path

EXP_VERSION='expedition-23o-review-split'

exp=Path('expedition.js').read_text()
game=Path('game.js').read_text()
index=Path('index.html').read_text()
style=Path('style.css').read_text()

def replace_once(text,old,new,label):
    if old not in text:
        raise SystemExit(f'MISSING {label}')
    return text.replace(old,new,1)

# Build/version isolation: every playtest build gets a fresh save universe.
game=replace_once(game,"const GAME_VERSION='expedition-23n-clean-playtest',SAVE_VERSION=1;",f"const GAME_VERSION='{EXP_VERSION}',SAVE_VERSION=1;",'game version')
index=index.replace('expedition.js?v=expedition-23n-clean-playtest',f'expedition.js?v={EXP_VERSION}')
index=index.replace('game.js?v=expedition-23n-clean-playtest',f'game.js?v={EXP_VERSION}')
index=index.replace('style.css?v=expedition-23j-overscan',f'style.css?v={EXP_VERSION}')

# Always-visible cash readout in the main HUD.
weather='        <span class="weather-status"><small>WEATHER</small><b id="weather-value">CLEAR</b></span>\n'
cash=weather+'        <span class="cash-status"><small>CASH</small><b id="cash-balance">$185,000</b></span>\n'
index=replace_once(index,weather,cash,'cash HUD insertion')

# Fuel and food both begin green.
style=replace_once(style,'.fuel-status > i em { display: block; width: 100%; height: 100%; background: #f6d365; transition: width .2s, background .2s; }','.fuel-status > i em { display: block; width: 100%; height: 100%; background: #73d6a1; transition: width .2s, background .2s; }','fuel default color')
style += '''\n\n/* ARS expedition-23o HUD and modal layering */\n#arx-mobile-toggle,#arx-dev-toggle{z-index:5!important}\n.cash-status{flex:0 0 auto}\n.cash-status b{color:#f6d365;white-space:nowrap}\n@media(max-width:760px) and (orientation:portrait){\n  .cash-status{position:absolute!important;left:42px;top:0;display:block!important;width:94px;height:34px;padding:4px 7px;border-radius:6px;background:rgba(5,31,48,.72);text-align:left;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}\n  .cash-status small{display:block!important;margin:0!important;color:#93bdc8!important;font-size:5px!important;letter-spacing:.08em!important}\n  .cash-status b{display:block!important;margin:3px 0 0!important;color:#f6d365!important;font-size:9px!important;letter-spacing:.02em!important}\n}\n'''

# Restore the earlier dedicated echosounder photograph.
old_ek="    ek80: {src:'assets/vessels/noaa-rv-brown.webp', alt:'Oceanographic research vessel carrying scientific acoustic systems', credit:'Wade Blake / NOAA', source:'https://oceanexplorer.noaa.gov/technology/noaa-ship-brown/'},"
new_ek="    ek80: {src:'assets/equipment/ek80-scientific-echosounder.webp', alt:'Scientific echosounder system used for fisheries and water-column acoustics', credit:'Scientific echosounder equipment photograph', source:''},"
exp=replace_once(exp,old_ek,new_ek,'echosounder photo')

# Keep the always-visible HUD cash amount synchronized with research money.
old="  function addLog(message) { state.log.unshift(message); state.log = state.log.slice(0,18); }\n  function animateCashReadouts() {"
new="  function addLog(message) { state.log.unshift(message); state.log = state.log.slice(0,18); }\n  function syncGlobalCash() { const node=document.getElementById('cash-balance'); if(node)node.textContent=cash(state.money); }\n  function animateCashReadouts() {"
exp=replace_once(exp,old,new,'cash sync helper')
old="    const from=state.money; state.money+=delta; cashAnimation={from,to:state.money};"
new="    const from=state.money; state.money+=delta; syncGlobalCash(); cashAnimation={from,to:state.money};"
exp=replace_once(exp,old,new,'cash sync on money change')
exp=replace_once(exp,'    document.body.appendChild(root);','    document.body.appendChild(root);\n    syncGlobalCash();','cash sync on init')

# Split research interaction into review/accept and work/progress stages.
start=exp.find('  function renderResearchWindow(')
end=exp.find('  function openTarget(',start)
if start<0 or end<0:
    raise SystemExit('MISSING renderResearchWindow block')
new_render=r'''  function renderResearchWindow(target,{phase='ready',resultTitle='',resultBody='',resultStats=[]}={}) {
    const running=phase==='running',complete=phase==='complete',programFinished=complete&&target.status==='completed';
    const readiness=missionReadiness(target),projection=readiness.projection,station=currentStation(target),stationLabel=station?`${station.number} of ${target.stations.length}`:'Single station';
    const contextDistance=state.lastTargetContext?.id===target.id?state.lastTargetContext.distanceKm:null,navDistance=state.navigation?.id===target.id?state.navigation.distanceKm:null,distance=Number.isFinite(contextDistance)?contextDistance:Number.isFinite(navDistance)?navDistance:Infinity,atSite=target.anywhere||distance<=RESEARCH_INTERACTION_KM;
    const opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity',accepted=!opportunity||target.accepted===true,missing=readiness.rows.find(row=>!row.ready),participants=participantIdsFor(target),rate=workRate(target),workHours=Math.round(running?(activeOperation?.workHours||operationWorkHours(target)):remainingWorkHours(target));
    const progress=running?0:complete?100:0,steps=target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station'];
    const canBegin=accepted&&atSite&&readiness.ready&&!running&&!complete;
    const primaryLabel=running?'RESEARCH IN PROGRESS':complete?'RESEARCH COMPLETE':!atSite&&!target.anywhere?'SAIL TO SITE FIRST':readiness.ready?'BEGIN RESEARCH':`CANNOT BEGIN · ${missing?.label||'MISSING CAPABILITY'}`;
    const decline=opportunity?`<button class="${accepted?'danger':'ghost'}" data-arx-action="cancel-opportunity" data-id="${target.id}" ${running||complete?'disabled':''}>${accepted?'ABANDON OPPORTUNITY':'DECLINE'}</button>`:(target.kind==='grant'||target.kind==='contract')?`<button class="danger" data-arx-action="drop-grant" data-id="${target.id}" ${running||programFinished||(target.deploymentId&&target.missionMode!=='staged-recovery')?'disabled':''}>${target.missionMode==='staged-recovery'?'DROP RETURN PICKUP':'DROP GRANT'}</button>`:'<button class="ghost" disabled>NO DROP ACTION</button>';
    const result=resultTitle||'Research result',modal=root.querySelector('#arx-target-modal');

    if(!accepted){
      modal.innerHTML=`<div class="arx-modal-card arx-target-card arx-research-unified arx-research-review"><button class="arx-close" data-arx-action="close-target" aria-label="Close research opportunity">×</button><small>${target.weather?'LIVE WEATHER RESEARCH':'DISCOVERED RESEARCH OPPORTUNITY'}</small><h2>${escapeHtml(target.title)}</h2>${mediaMarkup(target,'hero')}<p>${escapeHtml(target.description)}</p><div class="arx-target-facts arx-research-facts"><span><small>STATION</small><b>${stationLabel}</b></span><span><small>WORK</small><b>${workHours} person-hours · team rate ${rate.toFixed(1)}×</b></span><span><small>AWARD</small><b>${cash(target.reward||0)}</b></span><span><small>PAYMENT</small><b>ON COMPLETION</b></span><span><small>RESULT</small><b>${['mooring-deploy','staged-deploy','autonomous'].includes(target.missionMode)?'Data after telemetry / recovery':`+${target.data} data`}</b></span><span><small>DISTANCE</small><b>${target.anywhere?'REMOTE / ONBOARD':Number.isFinite(distance)?`${Math.round(distance)} km`:'OFF-SCREEN SITE'}</b></span></div><h3 class="arx-operation-subhead">RESPONSIBLE SCIENTISTS</h3>${operationScientistsMarkup(target)}<h3 class="arx-operation-subhead">EQUIPMENT USED</h3>${operationEquipmentMarkup(target)}<h3 class="arx-check-title">MISSION READINESS</h3>${readinessMarkup(readiness)}<div class="arx-research-review-actions">${decline}<button data-arx-action="accept-opportunity" data-id="${target.id}" ${atSite?'':'disabled'}>${atSite?'ACCEPT OPPORTUNITY':'ARRIVE AT SITE FIRST'}</button></div></div>`;
      modal.classList.add('open');
      return;
    }

    modal.innerHTML=`<div class="arx-modal-card arx-target-card arx-operation arx-research-unified arx-research-work ${complete?'arx-complete':''}"><button class="arx-close" data-arx-action="close-target" aria-label="Close research site" ${running?'disabled':''}>×</button><div class="arx-operation-progress"><div><b id="arx-operation-percent">${progress}%</b><span><strong>${escapeHtml(target.shortTitle||target.title)}</strong> · ${workHours} person-hours · ~${projection.days} game days · ${participants.length||1} scientist${participants.length===1?'':'s'} assigned</span></div><i><em id="arx-operation-bar" style="width:${progress}%"></em></i></div>${!readiness.ready&&!running&&!complete?`<div class="arx-work-readiness">${readinessMarkup(readiness)}</div>`:''}<ol>${steps.map((step,index)=>`<li data-arx-step="${index}" class="${complete?'done':''}"><i>${complete?'✓':index+1}</i><b>${escapeHtml(step)}</b><span>${complete?'Complete':'Queued'}</span></li>`).join('')}</ol><div class="arx-operation-result-space">${complete?`<div class="arx-research-result"><small>${escapeHtml(result)}</small><p>${escapeHtml(resultBody)}</p>${resultStats.length?`<div class="arx-chance">${resultStats.map(item=>`<span>${escapeHtml(item.label)}<b>${escapeHtml(item.value)}</b></span>`).join('')}</div>`:''}</div>`:'<div class="arx-result-placeholder">Results will appear here without replacing this research card.</div>'}</div><div class="arx-research-actions">${decline}<button data-arx-action="complete-target" data-id="${target.id}" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button><button data-arx-action="acknowledge-research" ${complete?'':'disabled'}>OKAY</button></div></div>`;
    modal.classList.add('open');
  }
'''
exp=exp[:start]+new_render+exp[end:]

# Any attempt to open a site while away now just starts navigation; the modal opens only on arrival.
old_open="""  function openTarget(id,context={}) {
    const target=state.targets.find(item=>item.id===id);if(!target)return false;
    if(activeOperation&&activeOperation.targetId!==id){toast('RESEARCH STATION ALREADY IN PROGRESS');return false;}
    const distance=context.distanceKm??(state.navigation?.id===id?state.navigation.distanceKm:Infinity);
    state.targets.forEach(item=>item.selected=item.id===id);state.lastTargetContext={...context,id,distanceKm:distance};
    renderResearchWindow(target,{phase:activeOperation?.targetId===id?'running':'ready'});renderSidebar();return true;
  }
"""
new_open="""  function openTarget(id,context={}) {
    const target=state.targets.find(item=>item.id===id);if(!target)return false;
    if(activeOperation&&activeOperation.targetId!==id){toast('RESEARCH STATION ALREADY IN PROGRESS');return false;}
    const distance=context.distanceKm??(state.navigation?.id===id?state.navigation.distanceKm:Infinity);
    state.targets.forEach(item=>item.selected=item.id===id);state.lastTargetContext={...context,id,distanceKm:distance};
    if(!target.anywhere&&distance>RESEARCH_INTERACTION_KM){callbacks.onNavigate?.(target);renderSidebar();return true;}
    renderResearchWindow(target,{phase:activeOperation?.targetId===id?'running':'ready'});renderSidebar();return true;
  }
"""
exp=replace_once(exp,old_open,new_open,'openTarget navigation behavior')

# Accept random opportunities at the review step; acceptance stops the expiry clock.
needle="    else if (action==='accept') acceptOffer(id);"
insert=needle+"\n    else if (action==='accept-opportunity') { const target=state.targets.find(item=>item.id===id); if(target&&(target.kind==='opportunity'||target.kind==='weather-opportunity')){target.accepted=true;target.expiresAtDay=null;target.selected=true;addLog(`Research opportunity accepted: ${target.title}.`);toast(`RESEARCH OPPORTUNITY ACCEPTED · ${target.shortTitle||target.title}`);renderResearchWindow(target,{phase:'ready'});changed({port:false});} }"
exp=replace_once(exp,needle,insert,'accept opportunity action')

# Styling for the new two-stage research flow.
exp += "\n"

# Resource bars: green >40, yellow <=40, red <=20.
resource_anchor="  const RESEARCH_INTERACTION_KM=10,observedWildlifeFallback=new Set(),resourceAlertState={fuel:false,food:false};"
resource_new=resource_anchor+"\n  function updateResourceBarColors(){const color=value=>value<=20?'#ef5a5a':value<=40?'#f6d365':'#73d6a1';if(ui.fuelLevel)ui.fuelLevel.style.background=color(state.fuel);if(ui.foodLevel)ui.foodLevel.style.background=color(state.food);}"
game=replace_once(game,resource_anchor,resource_new,'resource color helper')
game=game.replace('updateResourceWarning();','updateResourceBarColors();updateResourceWarning();')

# Ensure the two-stage action rows look intentional rather than crowded.
style += '''\n.arx-research-review-actions{display:grid;grid-template-columns:1fr 1.35fr;gap:8px;margin-top:14px}\n.arx-research-review-actions button{width:100%;padding:10px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:8px;font-weight:900;letter-spacing:.07em}\n.arx-research-review-actions .ghost{border:1px solid rgba(166,230,244,.25);background:transparent;color:#a9d2dc}\n.arx-research-work .arx-operation-progress{margin-top:6px}\n.arx-research-work .arx-operation-progress strong{color:#eafaff}\n.arx-work-readiness{margin:10px 0}\n@media(max-width:760px){.arx-research-review-actions{grid-template-columns:1fr}.arx-research-work{padding-top:34px!important}}\n'''

Path('expedition.js').write_text(exp)
Path('game.js').write_text(game)
Path('index.html').write_text(index)
Path('style.css').write_text(style)
print('p23o patch applied')
