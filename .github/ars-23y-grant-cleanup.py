from pathlib import Path

exp_path=Path('expedition.js')
game_path=Path('game.js')
index_path=Path('index.html')
exp=exp_path.read_text()
game=game_path.read_text()
index=index_path.read_text()

def replace_once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly 1 match, found {count}')
    return text.replace(old,new,1)

def replace_between(text, start, end, new_middle, label):
    a=text.find(start)
    if a<0: raise RuntimeError(f'{label}: start marker not found')
    b=text.find(end,a+len(start))
    if b<0: raise RuntimeError(f'{label}: end marker not found')
    return text[:a]+new_middle+text[b:]

# --- GRANT CAREER LEVELS: local work stays graduate-level; advanced careers get advanced projects.
exp=replace_once(exp,
"  function templateCareerLevel(template) {\n    let level=1; for (const id of [...(template.equipment||[]),...(template.consumables||[])]) level=Math.max(level,EQUIPMENT[id]?.tier||1); return Math.min(3,level);\n  }",
"  function templateCareerLevel(template) {\n    if(Number.isFinite(template?.careerLevel))return clamp(Math.round(template.careerLevel),1,3);\n    if(template?.professorOpportunity)return 3;\n    if(template?.postdocOpportunity)return 2;\n    if(template?.tier==='local')return 1;\n    let level=1;for(const id of [...(template.equipment||[]),...(template.consumables||[])])level=Math.max(level,EQUIPMENT[id]?.tier||1);return Math.min(3,level);\n  }",
'career-aware template level')

# --- HARD GRANT RULES + VESSEL PROGRESSION RANK.
anchor="  function grantCapacity() { const level=playerCareerLevel();if(level<2)return Math.max(1,state.scientists.length);const postdocs=state.scientists.filter(item=>item.career==='postdoc').length,professors=state.scientists.filter(item=>item.career==='professor').length;return Math.max(2,postdocs*2+professors*3); }"
insert="""  const HARD_ACTIVE_GRANT_LIMIT=5;
  const VESSEL_PROGRESSION_ORDER=['fishing','trawler','coastal','global','icebreaker','nuclear'];
  function vesselProgressionRank(id){const rank=VESSEL_PROGRESSION_ORDER.indexOf(id);return rank<0?-1:rank;}
  function activeGrantTemplateExists(templateId,excludeId=null){return !!templateId&&activeGrants().some(item=>item.templateId===templateId&&item.id!==excludeId);}
  function makeRoomForNewGrant(){
    while(grantLoad()>=HARD_ACTIVE_GRANT_LIMIT){
      const droppable=activeGrants().filter(item=>activeOperation?.targetId!==item.id&&!item.deploymentId).sort((a,b)=>(Number(a.acceptedAtDay)||0)-(Number(b.acceptedAtDay)||0));
      const oldest=droppable[0];if(!oldest)return false;
      state.targets=state.targets.filter(item=>item.id!==oldest.id);if(state.navigation?.id===oldest.id)state.navigation=null;
      addLog(`Research grant dropped to make room: ${oldest.title}.`);
    }
    return true;
  }
"""+anchor
exp=replace_once(exp,anchor,insert,'grant hard-limit helpers')

# Shipyard attention: ONLY an affordable, unlocked vessel higher in progression than the current one.
exp=replace_once(exp,
"    const fleetAttention=vesselsForPort().some(vesselPurchaseReady);",
"    const fleetAttention=vesselsForPort().some(item=>vesselProgressionRank(item.id)>vesselProgressionRank(state.currentVessel)&&vesselPurchaseReady(item));",
'shipyard upgrade attention')

# --- CAREER-SENSITIVE FALLBACK: no professor/postdoc Field Recon loop.
start="  function compatibleFallbackTemplate() {"
end="  const GRANT_MEDIA_POOL="
new_fallback="""  function compatibleFallbackTemplate() {
    const scientist=state.scientists[0],specialty=scientist?.specialty||'physical',spec=specialtyById[specialty]?.name||'Arctic',level=playerCareerLevel();
    if(level>=3)return mission({id:`fallback-professor-${specialty}`,careerLevel:3,professorOpportunity:true,title:`Arctic Basin ${spec} Synthesis Transect`,shortTitle:'BASIN SYNTHESIS',specialties:[specialty],equipment:[],data:72,reward:125000,supplies:14,workHours:90,anywhere:true,media:MEDIA.ctd,description:'Design and execute a basin-scale synthesis transect that connects the expedition’s observations to a major Arctic process question.',steps:['Define the basin-scale hypothesis','Select a defensible transect','Collect the core observations','Synthesize regional context','Deliver the sponsor science report']});
    if(level===2)return mission({id:`fallback-postdoc-${specialty}`,careerLevel:2,postdocOpportunity:true,title:`Regional ${spec} Process Survey`,shortTitle:'PROCESS SURVEY',specialties:[specialty],equipment:[],data:42,reward:58000,supplies:8,workHours:56,anywhere:true,media:MEDIA.winch,description:'Resolve a regional Arctic process with a focused multi-station survey appropriate to a postdoctoral expedition.',steps:['Form the process hypothesis','Lay out regional stations','Collect repeatable observations','Resolve the spatial gradient','Prepare the sponsor synthesis']});
    return mission({id:`fallback-${specialty}`,tier:'local',careerLevel:1,title:`${spec} Field Reconnaissance`,shortTitle:'FIELD RECON',specialties:[specialty],equipment:[],data:7,reward:7500,supplies:1,workHours:10,anywhere:true,coastal:['coastal-oceanography','coastal-ecology','plankton','fisheries'].includes(specialty),fjordPreferred:true,media:MEDIA.local,description:'A flexible sponsor call that matches the expertise currently aboard.',steps:['Define the local observation plan','Collect a repeatable field record','Check metadata and position','Preserve samples or imagery','Transmit the sponsor summary']});
  }
"""
exp=replace_between(exp,start,end,new_fallback,end,'career-sensitive fallback')

# Port grant board: use the Chief Scientist's actual career level, not all lower levels.
exp=replace_once(exp,
"    const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)<=careerFloor&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);",
"    const careerFloor=playerCareerLevel(),lastAcceptedTemplate=(state.recentGrantTemplates||[])[0]||null,available=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)===careerFloor&&item.id!==lastAcceptedTemplate&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);",
'career-specific port grants')

# Add explicit professor-scale geographic programs.
prof_marker="    mission({id:'deep-ctd', title:'Deep Arctic CTD Section'"
prof_projects="""    mission({id:'fram-strait-deep-section',careerLevel:3,professorOpportunity:true,title:'Fram Strait Deep-Water Exchange Transect',shortTitle:'FRAM STRAIT',specialties:['physical','biogeochemistry'],equipment:['ctd-rosette','heavy-winch','deep-adcp'],transect:true,stationCounts:{global:5,icebreaker:7,nuclear:10},stationSpacingKm:55,fixedDestination:{lat:79.5,lon:-1.5},data:84,reward:168000,supplies:24,workHours:126,media:MEDIA.deepCtd,description:'Resolve the deep Atlantic-water inflow and Arctic-water export across Fram Strait with full-depth hydrography and velocity structure.',steps:['Occupy the eastern boundary station','Run full-depth CTD and bottle casts','Cross the central strait','Resolve the deep current structure','Close the western boundary station','Synthesize heat and freshwater transport']}),
    mission({id:'lomonosov-ridge-transect',careerLevel:3,professorOpportunity:true,title:'Lomonosov Ridge Deep-Water Transect',shortTitle:'LOMONOSOV RIDGE',specialties:['physical','biogeochemistry'],equipment:['ctd-rosette','heavy-winch','deep-adcp'],transect:true,stationCounts:{icebreaker:6,nuclear:9},stationSpacingKm:65,fixedDestination:{lat:86.2,lon:140},iceAllowed:true,data:96,reward:195000,supplies:28,workHours:144,media:MEDIA.deepCtd,description:'Cross the Lomonosov Ridge with full-depth hydrography and deep-current measurements to resolve basin exchange and deep-water structure.',steps:['Approach the ridge in workable ice','Occupy the first deep station','Run full-depth CTD and velocity sections','Cross the ridge crest','Sample the opposite basin flank','Synthesize the cross-ridge exchange']}),
"""+prof_marker
exp=replace_once(exp,prof_marker,prof_projects,'professor geographic grants')

# --- MEDIA: crop user-supplied atlas images everywhere, rather than displaying the whole contact sheet.
media_anchor="  function mediaMarkup(item, className='') {"
media_helper="""  function mediaVisualMarkup(media,alt='',role='default') {
    if(!media?.src)return '';
    const safeAlt=escapeHtml(alt||media.alt||''),box=role==='gear'?'width:42px;height:42px;flex:0 0 42px;border-radius:7px;':role==='offer'?'width:100%;height:100%;border-radius:0;':'width:100%;aspect-ratio:4/3;border-radius:6px;';
    if(Array.isArray(media.atlas)){const col=Number(media.atlas[0])||0,row=Number(media.atlas[1])||0,x=(col/3*100).toFixed(3),y=(row/2*100).toFixed(3);return `<div class=\"arx-atlas-photo arx-media-visual\" role=\"img\" aria-label=\"${safeAlt}\" style=\"${box}background-color:#123d51;background-image:url(&quot;${escapeHtml(media.src)}&quot;);background-size:400% 300%;background-position:${x}% ${y}%;background-repeat:no-repeat\"></div>`;}
    return `<img class=\"arx-media-visual\" src=\"${escapeHtml(media.src)}\" alt=\"${safeAlt}\">`;
  }
"""+media_anchor
exp=replace_once(exp,media_anchor,media_helper,'atlas media helper')

exp=replace_once(exp,
"<div class=\"arx-offer-thumb\"><img src=\"${escapeHtml(media?.src||MEDIA.fieldKit.src)}\" alt=\"${escapeHtml(media?.alt||item.title)}\"></div>",
"<div class=\"arx-offer-thumb\">${mediaVisualMarkup(media||MEDIA.fieldKit,media?.alt||item.title,'offer')}</div>",
'grant offer hero media crop')

exp=replace_once(exp,
"return `<div class=\"arx-operation-equipment\">${items.map(item=>`<div class=\"arx-operation-gear\"><img src=\"${escapeHtml(item.media?.src||MEDIA.fieldKit.src)}\" alt=\"${escapeHtml(item.media?.alt||item.name)}\"><span>${escapeHtml(item.name)}</span></div>`).join('')}</div>`;",
"return `<div class=\"arx-operation-equipment\">${items.map(item=>`<div class=\"arx-operation-gear\">${mediaVisualMarkup(item.media||MEDIA.fieldKit,item.media?.alt||item.name,'gear')}<span>${escapeHtml(item.name)}</span></div>`).join('')}</div>`;",
'equipment atlas crop')

# Harden missing-equipment links as explicit buttons.
exp=exp.replace('<button data-arx-action=\"shop-equipment\" data-id=\"${id}\">EQUIPMENT SHOP · ${escapeHtml(EQUIPMENT[id]?.name||id)}</button>','<button type=\"button\" data-arx-action=\"shop-equipment\" data-id=\"${id}\">EQUIPMENT SHOP · ${escapeHtml(EQUIPMENT[id]?.name||id)}</button>')

# --- PROFESSOR ON-THE-GO GRANTS: slower, level-appropriate, no duplicates, no offers at 3+ active grants.
prof_start="  function maybeOfferProfessorGrant(environment={}) {"
prof_end="  function liveFieldOpportunities()"
prof_func="""  function maybeOfferProfessorGrant(environment={}) {
    const professorCount=state.scientists.filter(item=>item.career==='professor').length,cooldown=7;
    if(!professorCount||state.port||state.remoteOffer||grantLoad()>=3||state.elapsedDays-(state.lastProfessorGrantDay||-999)<cooldown)return false;
    const activeTemplates=new Set(activeGrants().map(item=>item.templateId)),recentTemplates=new Set((state.recentGrantTemplates||[]).slice(0,3));
    let candidates=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)===3&&eligible(item)&&!(item.onlyPorts?.length)&&!activeTemplates.has(item.id)&&!recentTemplates.has(item.id));
    if(!candidates.length)candidates=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)===3&&eligible(item)&&!(item.onlyPorts?.length)&&!activeTemplates.has(item.id)&&item.id!==(state.recentGrantTemplates||[])[0]);
    if(!candidates.length)return false;
    const rng=seeded(`professor-${Math.floor(state.elapsedDays)}-${professorCount}`),template=candidates[Math.floor(rng()*candidates.length)],origin=environment.position||{lat:78,lon:15},target=buildTarget(template,origin,rng,'grant',{nearby:!!(environment.iceEdge||environment.iceThickness),iceThickness:Number(environment.iceThickness)||0});if(!target)return false;
    target.professorOriginated=true;state.remoteOffer=target;state.lastProfessorGrantDay=state.elapsedDays;
    const modal=root.querySelector('#arx-target-modal');modal.innerHTML=`<div class=\"arx-modal-card arx-target-card\"><small>PROFESSOR-ORIGINATED PROPOSAL</small><h2>${escapeHtml(target.title)}</h2><p>A professor aboard has developed a fundable research idea from conditions observed at sea. Accept it and the site will receive normal grant navigation guidance.</p>${mediaMarkup(target,'hero')}<div class=\"arx-operation-actions\"><button class=\"ghost\" data-arx-action=\"decline-professor-grant\">DECLINE</button><button data-arx-action=\"accept-professor-grant\">ACCEPT GRANT</button></div></div>`;modal.classList.add('open');return true;
  }
"""+prof_end
exp=replace_between(exp,prof_start,prof_end,prof_func,'professor grant cooldown')

# Port acceptance: no duplicate template, hard cap five, 14-day deadline.
exp=replace_once(exp,
"    if(!eligible(offer)){const missing=missingMissionEquipment(offer);toast(missing.length?`GRANT NOT READY · NEED ${EQUIPMENT[missing[0]]?.name||missing[0]}`:'GRANT NOT READY · CHECK CREW AND EQUIPMENT');return;}\n    if (grantLoad()>=grantCapacity()) { toast(`ACTIVE RESEARCH GRANT LIMIT · ${grantLoad()}/${grantCapacity()}`); return; }",
"    if(!eligible(offer)){const missing=missingMissionEquipment(offer);toast(missing.length?`GRANT NOT READY · NEED ${EQUIPMENT[missing[0]]?.name||missing[0]}`:'GRANT NOT READY · CHECK CREW AND EQUIPMENT');return;}\n    if(activeGrantTemplateExists(offer.templateId)){toast('THAT RESEARCH GRANT IS ALREADY ACTIVE');return;}\n    if(grantLoad()>=HARD_ACTIVE_GRANT_LIMIT&&!makeRoomForNewGrant()){toast('ACTIVE GRANT LIMIT · COMPLETE OR DROP A GRANT FIRST');return;}\n    if (grantLoad()>=grantCapacity()) { toast(`ACTIVE RESEARCH GRANT LIMIT · ${grantLoad()}/${grantCapacity()}`); return; }",
'accept grant guards')
exp=replace_once(exp,
"    state.targets.forEach(item=>item.selected=false);offer.selected=true;offer.upfront=0;offer.advancePaid=0;state.targets.push(offer);",
"    state.targets.forEach(item=>item.selected=false);offer.selected=true;offer.upfront=0;offer.advancePaid=0;offer.acceptedAtDay=state.elapsedDays;offer.expiresAtDay=state.elapsedDays+14;state.targets.push(offer);",
'port grant deadline')

# Professor acceptance/decline: same duplicate/limit/deadline rules and record history.
old_prof_accept="    else if (action==='accept-professor-grant'&&state.remoteOffer) { state.targets.forEach(item=>item.selected=false);state.remoteOffer.selected=true;state.remoteOffer.upfront=0;state.remoteOffer.advancePaid=0;state.targets.push(state.remoteOffer);addLog(`Professor-originated grant accepted: ${state.remoteOffer.title}. Payment due on completion.`);state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed(); }\n    else if (action==='decline-professor-grant') { state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');changed(); }"
new_prof_accept="""    else if (action==='accept-professor-grant'&&state.remoteOffer) {
      const offer=state.remoteOffer;
      if(grantLoad()>=3){toast('ON-THE-GO GRANTS PAUSE AT THREE ACTIVE GRANTS');state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');changed();}
      else if(activeGrantTemplateExists(offer.templateId)){toast('THAT RESEARCH GRANT IS ALREADY ACTIVE');state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');changed();}
      else if(grantLoad()>=HARD_ACTIVE_GRANT_LIMIT&&!makeRoomForNewGrant()){toast('ACTIVE GRANT LIMIT · COMPLETE OR DROP A GRANT FIRST');}
      else{state.targets.forEach(item=>item.selected=false);offer.selected=true;offer.upfront=0;offer.advancePaid=0;offer.acceptedAtDay=state.elapsedDays;offer.expiresAtDay=state.elapsedDays+14;state.targets.push(offer);recordGrantUse(offer.templateId,offer,'field');addLog(`Professor-originated grant accepted: ${offer.title}. Payment due on completion.`);state.lastProfessorGrantDay=state.elapsedDays;state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed();}
    }
    else if (action==='decline-professor-grant') { state.lastProfessorGrantDay=state.elapsedDays;state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');changed(); }"""
exp=replace_once(exp,old_prof_accept,new_prof_accept,'professor acceptance rules')

# Completion restarts professor proposal cooldown.
exp=replace_once(exp,
"    target.status='completed'; target.selected=false;",
"    target.status='completed'; target.selected=false;if(target.professorOriginated)state.lastProfessorGrantDay=state.elapsedDays;",
'professor completion cooldown')

# Existing saves: active grants without deadlines get a fresh 14-day deadline from load time.
restore_anchor="    state.offers=(state.offers||[]).filter(Boolean).slice(0,9);"
restore_new=restore_anchor+"\n    for(const grant of activeGrants()){if(!Number.isFinite(grant.acceptedAtDay))grant.acceptedAtDay=state.elapsedDays;if(!Number.isFinite(grant.expiresAtDay))grant.expiresAtDay=grant.acceptedAtDay+14;}"
exp=replace_once(exp,restore_anchor,restore_new,'restore grant deadlines')

# Expire unfinished grants after 14 game days.
tick_anchor="    state.recentGrantSites=(state.recentGrantSites||[]).filter(site=>state.elapsedDays-(site.day||0)<90).slice(0,18);"
tick_new=tick_anchor+"""
    const expiredGrantIds=new Set();
    for(const target of state.targets){if((target.kind==='grant'||target.kind==='contract')&&!['completed','failed','dropped'].includes(target.status)&&Number.isFinite(target.expiresAtDay)&&state.elapsedDays>=target.expiresAtDay&&activeOperation?.targetId!==target.id){target.status='dropped';target.selected=false;expiredGrantIds.add(target.id);addLog(`Research grant expired after 14 days: ${target.title}.`);if(target.professorOriginated)state.lastProfessorGrantDay=state.elapsedDays;}}
    if(expiredGrantIds.size){state.targets=state.targets.filter(target=>!expiredGrantIds.has(target.id));if(state.navigation?.id&&expiredGrantIds.has(state.navigation.id))state.navigation=null;toast(expiredGrantIds.size===1?'RESEARCH GRANT EXPIRED · 14-DAY DEADLINE':`${expiredGrantIds.size} RESEARCH GRANTS EXPIRED · 14-DAY DEADLINE`);}
"""
exp=replace_once(exp,tick_anchor,tick_new,'14-day expiration')

# Show deadline on active grant cards.
exp=replace_once(exp,
"    const missing=!eligible(item), projection=missionFoodProjection(item);",
"    const missing=!eligible(item), projection=missionFoodProjection(item),daysLeft=Number.isFinite(item.expiresAtDay)?Math.max(0,Math.ceil(item.expiresAtDay-state.elapsedDays)):null;",
'active grant days left')
exp=replace_once(exp,
"<span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><div class=\"arx-grant-actions\">",
"<span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span>${daysLeft!==null?`<span>Deadline ${daysLeft} day${daysLeft===1?'':'s'}</span>`:''}</div><div class=\"arx-grant-actions\">",
'active grant deadline display')

# Golden-arrow preview: open details instead of immediately navigating when off-site.
exp=replace_once(exp,
"    if(!target.anywhere&&distance>RESEARCH_INTERACTION_KM){callbacks.onNavigate?.(target);renderSidebar();return true;}",
"    if(!target.anywhere&&distance>RESEARCH_INTERACTION_KM&&!context.previewOnly){callbacks.onNavigate?.(target);renderSidebar();return true;}",
'open target preview-only')
exp=replace_once(exp,
"    const workActions=complete?'<button data-arx-action=\"acknowledge-research\">OKAY</button>':`${decline}<button data-arx-action=\"complete-target\" data-id=\"${target.id}\" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button>`;",
"    const navigateAction=accepted&&!atSite&&!target.anywhere?`<button data-arx-action=\"navigate-target\" data-id=\"${target.id}\">NAVIGATE TO SITE</button>`:'';\n    const workActions=complete?'<button data-arx-action=\"acknowledge-research\">OKAY</button>':navigateAction?`${decline}${navigateAction}`:`${decline}<button data-arx-action=\"complete-target\" data-id=\"${target.id}\" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button>`;",
'gold arrow navigate/drop actions')

# --- GAME: golden arrow opens the target preview modal.
old_guidance="if(guidance){const target=researchTargets().find(item=>item.id===guidance.targetId);if(target){const item=researchTargetWorld(target);if(item.distance<=RESEARCH_INTERACTION_KM){research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:true,target});}else navigateToResearchTarget(target);}return;}"
new_guidance="if(guidance){const target=researchTargets().find(item=>item.id===guidance.targetId);if(target){const item=researchTargetWorld(target);research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:item.distance<=RESEARCH_INTERACTION_KM,target,previewOnly:item.distance>RESEARCH_INTERACTION_KM,fromGuidance:true});}return;}"
game=replace_once(game,old_guidance,new_guidance,'golden arrow popup')

# --- REMOVE FAST ICE COMPLETELY: source classification, rendering, navigation and labels.
game=replace_once(game,"    fast:loadSprite(window.AR_VISUAL_ASSETS?.ice?.fast||'')\n",'', 'fast ice texture')
game=replace_once(game,"  function fastIceGrowth(){const d=state.seasonDay;if(d<91||d>=274)return 0;if(d<=182)return.5-.5*Math.cos(Math.PI*(d-91)/91);return.5+.5*Math.cos(Math.PI*(d-182)/92);}\n",'', 'fast ice growth')

game=replace_once(game,
"  function addBrokenIce(x,y,radius=8,anchored=false){if(isBrokenIceAt(x,y))return;const natural=naturalIceTypeAt(x,y),fixed=anchored||natural==='fast',flow=fixed?{vx:0,vy:0}:currentAt(x,y,false),point={x,y,radius,life:fixed?34:18+Math.random()*8,anchored:fixed,vx:flow.vx,vy:flow.vy,flowAge:.35+Math.random()*.3};brokenIceChannels.push(point);indexBrokenIce(point);if(brokenIceChannels.length>700){brokenIceChannels.splice(0,80);rebuildBrokenIceGrid();}}",
"  function addBrokenIce(x,y,radius=8){if(isBrokenIceAt(x,y))return;const flow=currentAt(x,y,false),point={x,y,radius,life:18+Math.random()*8,anchored:false,vx:flow.vx,vy:flow.vy,flowAge:.35+Math.random()*.3};brokenIceChannels.push(point);indexBrokenIce(point);if(brokenIceChannels.length>700){brokenIceChannels.splice(0,80);rebuildBrokenIceGrid();}}",
'broken ice no fast anchoring')
game=replace_once(game,
"  function updateBrokenIceDrift(dt){if(!brokenIceChannels.length)return;let changed=false;for(let i=brokenIceChannels.length-1;i>=0;i--){const point=brokenIceChannels[i];point.life-=dt*(point.anchored?.035:.07);if(point.life<=0){brokenIceChannels.splice(i,1);changed=true;continue;}if(point.anchored)continue;point.flowAge-=dt;if(point.flowAge<=0){const flow=currentAt(point.x,point.y,false);point.vx=flow.vx*.72;point.vy=flow.vy*.72;point.flowAge=.35+Math.random()*.35;}const nx=point.x+point.vx*dt,ny=point.y+point.vy*dt;if(!isLand(nx,ny)&&naturalIceTypeAt(nx,ny)!=='fast'){point.x=nx;point.y=ny;changed=true;}}if(changed)rebuildBrokenIceGrid();}",
"  function updateBrokenIceDrift(dt){if(!brokenIceChannels.length)return;let changed=false;for(let i=brokenIceChannels.length-1;i>=0;i--){const point=brokenIceChannels[i];point.life-=dt*.07;if(point.life<=0){brokenIceChannels.splice(i,1);changed=true;continue;}point.flowAge-=dt;if(point.flowAge<=0){const flow=currentAt(point.x,point.y,false);point.vx=flow.vx*.72;point.vy=flow.vy*.72;point.flowAge=.35+Math.random()*.35;}const nx=point.x+point.vx*dt,ny=point.y+point.vy*dt;if(!isLand(nx,ny)){point.x=nx;point.y=ny;changed=true;}}if(changed)rebuildBrokenIceGrid();}",
'broken ice drift')

game=replace_once(game,
"  function iceTypeAt(x,y){if(isLand(x,y))return'open';const pos=unpolar(x,y),growth=iceGrowth(),packEdge=packIceEdge(pos.lon),marginalEdge=packEdge-(2.1+1.5*growth),broken=isBrokenIceAt(x,y);if(pos.lat>=packEdge){if(broken)return'open';return isCrackedIceAt(x,y)?'cracked':'packed';}const fastGrowth=fastIceGrowth(),fastWidth=23.5*fastGrowth,d=coastDistance(x,y,fastWidth+3);if(fastWidth>0&&d<=fastWidth)return broken?'open':'fast';if(pos.lat>=marginalEdge)return'marginal';return'open';}\n  function naturalIceTypeAt(x,y){if(isLand(x,y))return'open';const pos=unpolar(x,y),growth=iceGrowth(),packEdge=packIceEdge(pos.lon),marginalEdge=packEdge-(2.1+1.5*growth);if(pos.lat>=packEdge)return isCrackedIceAt(x,y)?'cracked':'packed';const fastGrowth=fastIceGrowth(),fastWidth=23.5*fastGrowth,d=coastDistance(x,y,fastWidth+3);if(pos.lat>=71.5&&fastWidth>0&&d<=fastWidth)return'fast';if(pos.lat>=marginalEdge)return'marginal';return'open';}",
"  function iceTypeAt(x,y){if(isLand(x,y))return'open';const pos=unpolar(x,y),growth=iceGrowth(),packEdge=packIceEdge(pos.lon),marginalEdge=packEdge-(2.1+1.5*growth),broken=isBrokenIceAt(x,y);if(pos.lat>=packEdge){if(broken)return'open';return isCrackedIceAt(x,y)?'cracked':'packed';}if(pos.lat>=marginalEdge)return'marginal';return'open';}\n  function naturalIceTypeAt(x,y){if(isLand(x,y))return'open';const pos=unpolar(x,y),growth=iceGrowth(),packEdge=packIceEdge(pos.lon),marginalEdge=packEdge-(2.1+1.5*growth);if(pos.lat>=packEdge)return isCrackedIceAt(x,y)?'cracked':'packed';if(pos.lat>=marginalEdge)return'marginal';return'open';}",
'fast ice classification')

# Remove fast rules in vessel capability table.
game=game.replace("      fast:Object.freeze({speedFactor:.1,breaking:true}),\n",'')
game=game.replace("      fast:Object.freeze({speedFactor:.6,breaking:true}),\n",'')
game=replace_once(game,"  function iceRuleKey(type,thickness=0){if(type==='marginal'||type==='fast')return type;if(type==='packed'||type==='cracked')return`${type}${thickness}`;return'open';}","  function iceRuleKey(type,thickness=0){if(type==='marginal')return type;if(type==='packed'||type==='cracked')return`${type}${thickness}`;return'open';}",'ice rule key')
game=replace_once(game,"    const type=naturalIceTypeAt(x,y),thickness=type==='fast'?1:(type==='packed'||type==='cracked')?iceThicknessAt(x,y):0;","    const type=naturalIceTypeAt(x,y),thickness=(type==='packed'||type==='cracked')?iceThicknessAt(x,y):0;",'break natural ice')
game=replace_once(game,"      addBrokenIce(cx,cy,radius,naturalIceTypeAt(cx,cy)==='fast');","      addBrokenIce(cx,cy,radius);",'icebreaker track')

# Remove shoreline fast-ice rendering block, retaining pack ice render and function close.
fast_render_start="    const fastGrowth=fastIceGrowth(),fastWidth=23.5*fastGrowth,marginalWidth=fastWidth+10+15*fastGrowth;"
fast_render_end="    ctx.restore();\n  }\n  function drawIceThicknessAndCracks(){"
a=game.find(fast_render_start)
b=game.find(fast_render_end,a)
if a<0 or b<0: raise RuntimeError('fast ice render block markers not found')
game=game[:a]+fast_render_end+game[b+len(fast_render_end):]
game=game.replace("[3,iceTextures.fast,'rgba(238,247,247,.28)',.92,360]","[3,iceTextures.dense,'rgba(238,247,247,.28)',.92,360]")

# Remove remaining fast-type branches from research, wildlife, navigation and UI.
replacements={
"(siteIce==='packed'||siteIce==='cracked'||siteIce==='fast')":"(siteIce==='packed'||siteIce==='cracked')",
"ice==='fast'?1:(ice==='packed'||ice==='cracked')?iceThicknessAt(state.x,state.y):0":"(ice==='packed'||ice==='cracked')?iceThicknessAt(state.x,state.y):0",
"ice==='marginal'||ice==='fast'||Math.abs(position.lat-packEdge)<2.8":"ice==='marginal'||Math.abs(position.lat-packEdge)<2.8",
"iceType(center.x,center.y)==='fast'||iceType(center.x,center.y)==='packed'":"iceType(center.x,center.y)==='packed'",
"type==='fast'||type==='packed'":"type==='packed'",
"ice==='packed'||ice==='cracked'||ice==='fast'||isLand":"ice==='packed'||ice==='cracked'||isLand",
"isLand(x,y)||ice==='packed'||ice==='cracked'||ice==='fast'||ice==='marginal'":"isLand(x,y)||ice==='packed'||ice==='cracked'||ice==='marginal'",
"ice==='packed'||ice==='cracked'||ice==='fast'||isLand(w.x,w.y)":"ice==='packed'||ice==='cracked'||isLand(w.x,w.y)",
"type==='packed'||type==='fast'||type==='cracked'":"type==='packed'||type==='cracked'",
"habitat==='packed'||habitat==='fast'||habitat==='cracked'":"habitat==='packed'||habitat==='cracked'",
"currentType!=='packed'&&currentType!=='fast'&&currentType!=='cracked'":"currentType!=='packed'&&currentType!=='cracked'",
"edgeType!=='packed'&&edgeType!=='fast'&&edgeType!=='cracked'":"edgeType!=='packed'&&edgeType!=='cracked'",
"type!=='packed'&&type!=='fast'&&type!=='cracked'":"type!=='packed'&&type!=='cracked'",
"return ice!=='packed'&&ice!=='fast'&&ice!=='cracked'":"return ice!=='packed'&&ice!=='cracked'",
"if(isBlocked(cx,cy)||ice==='fast'||ice==='packed')":"if(isBlocked(cx,cy)||ice==='packed')",
}
for old,new in replacements.items(): game=game.replace(old,new)

old_profile="  function iceNavigationProfileAt(x,y,vessel=vesselModifiers()){\n    const type=iceTypeAt(x,y),thickness=type==='fast'?1:(type==='packed'||type==='cracked')?iceThicknessAt(x,y):0,id=vesselIceId(vessel),cracked=type==='cracked',rule=iceNavigationRule(type,thickness,vessel);\n    const iceLabel=type==='open'?'OPEN WATER':type==='marginal'?'MARGINAL ICE':type==='fast'?'FAST ICE · 1 M EQUIVALENT':`${thickness} M ${cracked?'FRACTURED':'PACK'} ICE`;\n    if(rule)return{allowed:true,speedFactor:rule.speedFactor,breaking:!!rule.breaking,ramming:!!rule.breaking,reason:'',type,thickness,id,iceLabel};\n    let reason='SEA ICE · VESSEL NOT ICE-CAPABLE';\n    if(type==='fast')reason='FAST ICE · ICEBREAKER REQUIRED';\n    else if(['fishing','trawler','coastal'].includes(id))reason='MARGINAL ICE · GLOBAL-CLASS R/V OR ICEBREAKER REQUIRED';\n    else if(id==='global')reason='PACK ICE · ICEBREAKER REQUIRED';\n    else if(id==='icebreaker')reason=`${thickness} M ICE · EXCEEDS BASIC ICEBREAKER CAPABILITY`;\n    else if(id==='nuclear')reason=thickness>=4?'4 M ICE · IMPASSABLE':'3 M UNFRACTURED PACK · IMPASSABLE';\n    return{allowed:false,speedFactor:0,breaking:false,ramming:false,reason,type,thickness,id,iceLabel};\n  }"
new_profile="  function iceNavigationProfileAt(x,y,vessel=vesselModifiers()){\n    const type=iceTypeAt(x,y),thickness=(type==='packed'||type==='cracked')?iceThicknessAt(x,y):0,id=vesselIceId(vessel),cracked=type==='cracked',rule=iceNavigationRule(type,thickness,vessel);\n    const iceLabel=type==='open'?'OPEN WATER':type==='marginal'?'MARGINAL ICE':`${thickness} M ${cracked?'FRACTURED':'PACK'} ICE`;\n    if(rule)return{allowed:true,speedFactor:rule.speedFactor,breaking:!!rule.breaking,ramming:!!rule.breaking,reason:'',type,thickness,id,iceLabel};\n    let reason='SEA ICE · VESSEL NOT ICE-CAPABLE';\n    if(['fishing','trawler','coastal'].includes(id))reason='MARGINAL ICE · GLOBAL-CLASS R/V OR ICEBREAKER REQUIRED';\n    else if(id==='global')reason='PACK ICE · ICEBREAKER REQUIRED';\n    else if(id==='icebreaker')reason=`${thickness} M ICE · EXCEEDS BASIC ICEBREAKER CAPABILITY`;\n    else if(id==='nuclear')reason=thickness>=4?'4 M ICE · IMPASSABLE':'3 M UNFRACTURED PACK · IMPASSABLE';\n    return{allowed:false,speedFactor:0,breaking:false,ramming:false,reason,type,thickness,id,iceLabel};\n  }"
game=replace_once(game,old_profile,new_profile,'ice navigation profile')

game=replace_once(game,
"  function researchSiteValueMultiplier(point,template={}){if(!template.iceAllowed)return 1;const w=polar(point.lat,point.lon),type=iceTypeAt(w.x,w.y),thickness=type==='fast'?1:iceThicknessAt(w.x,w.y);if(type==='marginal')return 1.25;if(type==='fast')return 1.75;if(type!=='packed'&&type!=='cracked')return 1;return thickness>=3?4:thickness===2?2.75:1.75;}",
"  function researchSiteValueMultiplier(point,template={}){if(!template.iceAllowed)return 1;const w=polar(point.lat,point.lon),type=iceTypeAt(w.x,w.y),thickness=iceThicknessAt(w.x,w.y);if(type==='marginal')return 1.25;if(type!=='packed'&&type!=='cracked')return 1;return thickness>=3?4:thickness===2?2.75:1.75;}",
'ice research value')

game=replace_once(game,
"  function portIceInfo(city){const center=polar(city.lat,city.lon);let sample=null;for(let radius=3;radius<=64&&!sample;radius+=3)for(let i=0;i<48;i++){const a=i*Math.PI/24,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);if(pos.lat<MIN_LAT||isBlocked(x,y))continue;sample={x,y};break;}if(!sample)return{frozen:true,iceLabel:'NO SEA APPROACH',type:'blocked',thickness:0,navigationAllowed:false};const type=naturalIceTypeAt(sample.x,sample.y),thickness=type==='fast'?1:(type==='packed'||type==='cracked')?iceThicknessAt(sample.x,sample.y):0,frozen=type==='fast'||type==='packed'||type==='cracked',navigationAllowed=iceNavigationProfileAt(sample.x,sample.y).allowed;return{frozen,type,thickness,navigationAllowed,iceLabel:type==='open'?'OPEN WATER':type==='marginal'?'MARGINAL ICE':type==='fast'?'FAST ICE':`${thickness} M ${type==='cracked'?'FRACTURED':'PACK'} ICE`};}",
"  function portIceInfo(city){const center=polar(city.lat,city.lon);let sample=null;for(let radius=3;radius<=64&&!sample;radius+=3)for(let i=0;i<48;i++){const a=i*Math.PI/24,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);if(pos.lat<MIN_LAT||isBlocked(x,y))continue;sample={x,y};break;}if(!sample)return{frozen:true,iceLabel:'NO SEA APPROACH',type:'blocked',thickness:0,navigationAllowed:false};const type=naturalIceTypeAt(sample.x,sample.y),thickness=(type==='packed'||type==='cracked')?iceThicknessAt(sample.x,sample.y):0,frozen=type==='packed'||type==='cracked',navigationAllowed=iceNavigationProfileAt(sample.x,sample.y).allowed;return{frozen,type,thickness,navigationAllowed,iceLabel:type==='open'?'OPEN WATER':type==='marginal'?'MARGINAL ICE':`${thickness} M ${type==='cracked'?'FRACTURED':'PACK'} ICE`};}",
'port ice info')

# Final sweep for exact fast-ice branch fragments that should now be dead.
for old,new in [
("||type==='fast'",''),("||ice==='fast'",''),("||siteIce==='fast'",''),("||habitat==='fast'",''),
("&&type!=='fast'",''),("&&ice!=='fast'",''),("&&currentType!=='fast'",''),("&&edgeType!=='fast'",''),
]: game=game.replace(old,new)

# Cache bust.
index=index.replace('expedition-23x-safe-reimplementation','expedition-23y-grant-cleanup')

# Source-level assertions before writing.
checks=[
    ('expedition.js','HARD_ACTIVE_GRANT_LIMIT=5',exp),('expedition.js','Fram Strait Deep-Water Exchange Transect',exp),
    ('expedition.js','Lomonosov Ridge Deep-Water Transect',exp),('expedition.js','expiresAtDay=state.elapsedDays+14',exp),
    ('expedition.js','grantLoad()>=3',exp),('expedition.js','mediaVisualMarkup',exp),('expedition.js','previewOnly',exp),
    ('expedition.js','vesselProgressionRank',exp),('expedition.js','data-arx-action=\"shop-equipment\"',exp),
]
for filename,needle,text in checks:
    if needle not in text: raise RuntimeError(f'{filename}: missing validation marker {needle}')
for forbidden in ['fastIceGrowth','iceTextures.fast',"return'fast'",'FAST ICE']:
    if forbidden in game: raise RuntimeError(f'game.js: fast ice residue remains: {forbidden}')
if exp.count('function capturePortView')!=1: raise RuntimeError('capturePortView helper count changed')
if exp.count('function offerCard')!=1: raise RuntimeError('offerCard helper count changed')
if exp.count('function activeGrantCard')!=1: raise RuntimeError('activeGrantCard helper count changed')

exp_path.write_text(exp)
game_path.write_text(game)
index_path.write_text(index)
print('ARS_23Y_PATCH_OK')
