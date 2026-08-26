from pathlib import Path

exp_path=Path('expedition.js')
game_path=Path('game.js')
index_path=Path('index.html')
exp=exp_path.read_text()
game=game_path.read_text()
index=index_path.read_text()

def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise RuntimeError(f'{label}: expected 1 match, found {count}')
    return text.replace(old,new,1)

# Keep higher-tier research reachable without pushing every site hundreds of km away.
exp=one(exp,
"    const grantRanges={fishing:[25,150],trawler:[260,720],coastal:[950,1700],global:[1200,2300],icebreaker:[1400,2700],nuclear:[1600,3100]};\n    const opportunityRanges={fishing:[25,100],trawler:[70,230],coastal:[170,480],global:[260,700],icebreaker:[320,850],nuclear:[380,1000]};\n    const nearbyRanges={fishing:[20,70],trawler:[55,150],coastal:[120,300],global:[180,420],icebreaker:[220,520],nuclear:[260,620]};",
"    const grantRanges={fishing:[25,150],trawler:[70,350],coastal:[120,650],global:[180,900],icebreaker:[220,1350],nuclear:[260,1700]};\n    const opportunityRanges={fishing:[25,100],trawler:[45,160],coastal:[70,240],global:[100,320],icebreaker:[120,400],nuclear:[140,480]};\n    const nearbyRanges={fishing:[20,70],trawler:[35,110],coastal:[55,160],global:[75,220],icebreaker:[95,280],nuclear:[110,330]};",
'distance windows')

# Anywhere work really is anywhere; named geographic programs are not rejected by a generic distance band.
exp=one(exp,
"    const window=researchDistanceWindow(template,kind,options);\n    const validator=callbacks.isResearchSiteSuitable;\n    const avoidPoints=[...state.targets,...state.offers,...(state.recentGrantSites||[])].filter(item=>item.status!=='completed');\n    let point=template.fixedDestination ? {...template.fixedDestination} : null;",
"    const window=template.anywhere?{min:0,max:0}:researchDistanceWindow(template,kind,options);\n    const validator=callbacks.isResearchSiteSuitable;\n    const avoidPoints=[...state.targets,...state.offers,...(state.recentGrantSites||[])].filter(item=>item.status!=='completed');\n    let point=template.anywhere?{lat:origin.lat,lon:origin.lon}:(template.fixedDestination ? {...template.fixedDestination} : null);",
'anywhere site initialization')
exp=one(exp,
"    const spacing=options.nearby?Math.max(35,targetSpacingKm()*.7):targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:window,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
"    const spacing=options.nearby?Math.max(35,targetSpacingKm()*.7):targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:template.fixedDestination?null:window,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});",
'fixed destination distance exemption')

# Career-specific synthetic programs guarantee a viable board without scaling grad-level jobs upward.
start=exp.index("  function compatibleFallbackTemplate() {")
end=exp.index("  const GRANT_MEDIA_POOL=",start)
if start<0 or end<0: raise RuntimeError('fallback template block not found')
new_fallback="""  function careerFallbackTemplate(specialty=playerScientist()?.specialty||'physical',variant=0) {
    const spec=specialtyById[specialty]?.name||'Arctic science',level=playerCareerLevel(),crew=Math.max(1,Math.min(vessel().berths,state.scientists.length||1)),iceCapable=['icebreaker','nuclear'].includes(state.currentVessel);
    if(level>=3)return mission({id:`fallback-professor-${specialty}-${variant?'section':'synthesis'}`,careerLevel:3,professorOpportunity:true,title:variant?`Trans-Arctic ${spec} Process Section`:`Arctic Basin ${spec} Synthesis Transect`,shortTitle:variant?'TRANS-ARCTIC SECTION':'BASIN SYNTHESIS',specialties:[specialty],equipment:[],minCrew:crew,data:72,reward:125000,supplies:14,workHours:90,iceAllowed:iceCapable,media:MEDIA.ctd,description:variant?'Resolve a basin-scale process along a defensible trans-Arctic section, combining repeated stations with regional context.':'Design and execute a basin-scale synthesis transect that connects the expedition’s observations to a major Arctic process question.',steps:['Define the basin-scale hypothesis','Select a defensible transect','Collect the core observations','Resolve the regional gradient','Deliver the sponsor science synthesis']});
    if(level===2)return mission({id:`fallback-postdoc-${specialty}-${variant?'gradient':'process'}`,careerLevel:2,postdocOpportunity:true,title:variant?`Shelf-Basin ${spec} Gradient Transect`:`Regional ${spec} Process Survey`,shortTitle:variant?'SHELF-BASIN GRADIENT':'PROCESS SURVEY',specialties:[specialty],equipment:[],minCrew:crew,data:42,reward:58000,supplies:8,workHours:56,media:MEDIA.winch,description:variant?'Resolve a regional shelf-to-basin gradient with a focused sequence of repeatable stations.':'Resolve a regional Arctic process with a focused multi-station survey appropriate to a postdoctoral expedition.',steps:['Form the process hypothesis','Lay out regional stations','Collect repeatable observations','Resolve the spatial gradient','Prepare the sponsor synthesis']});
    return mission({id:`fallback-grad-${specialty}-${variant?'station':'recon'}`,tier:'local',careerLevel:1,title:variant?`${spec} Local Process Station`:`${spec} Field Reconnaissance`,shortTitle:variant?'LOCAL PROCESS':'FIELD RECON',specialties:[specialty],equipment:[],minCrew:1,data:7,reward:7500,supplies:1,workHours:10,coastal:['coastal-oceanography','coastal-ecology','plankton','fisheries'].includes(specialty),fjordPreferred:true,media:MEDIA.local,description:variant?'A compact local station designed around one clear, graduate-scale process question.':'A flexible sponsor call that matches the expertise currently aboard.',steps:['Define the local observation plan','Collect a repeatable field record','Check metadata and position','Preserve samples or imagery','Transmit the sponsor summary']});
  }
  function careerFallbackTemplates() {
    const specialties=[...new Set([playerScientist()?.specialty,...state.scientists.map(item=>item.specialty)].filter(Boolean))].slice(0,4),templates=[];
    for(const specialty of specialties)for(const variant of [0,1])templates.push(careerFallbackTemplate(specialty,variant));
    return templates;
  }
  function compatibleFallbackTemplate() { return careerFallbackTemplates()[0]||careerFallbackTemplate(); }
"""
exp=exp[:start]+new_fallback+exp[end:]

# Port grant board: exact career scale, but include generated high-level programs for onboard specialties.
old="""    const rng=seeded(`${portId}-${state.portVisits}-grants-v6-${playerScientist()?.career||'grad'}-${state.currentVessel}`),activeTemplates=new Set(activeGrants().map(item=>item.templateId));
    const careerFloor=playerCareerLevel(),lastAcceptedTemplate=(state.recentGrantTemplates||[])[0]||null,available=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)===careerFloor&&item.id!==lastAcceptedTemplate&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);"""
new="""    const rng=seeded(`${portId}-${state.portVisits}-grants-v7-${playerScientist()?.career||'grad'}-${state.currentVessel}`),activeTemplates=new Set(activeGrants().map(item=>item.templateId));
    const careerFloor=playerCareerLevel(),lastAcceptedTemplate=(state.recentGrantTemplates||[])[0]||null,sourceTemplates=[...TEMPLATES,...careerFallbackTemplates()],available=sourceTemplates.filter(item=>!item.weather&&templateCareerLevel(item)===careerFloor&&item.id!==lastAcceptedTemplate&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);"""
exp=one(exp,old,new,'port grant source pool')

# If all mapped sites fail, an onboard version is a final fail-safe instead of a blank grant board.
exp=one(exp,
"    if(!state.offers.length){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback){giveGrantUniqueMedia(fallback,usedPictures,rng);state.offers.push(fallback);}}",
"    if(!state.offers.length){let template=compatibleFallbackTemplate(),fallback=buildTarget(template,port,rng,'grant');if(!fallback){template={...template,anywhere:true};fallback=buildTarget(template,port,rng,'grant');}if(fallback){giveGrantUniqueMedia(fallback,usedPictures,rng);state.offers.push(fallback);}}",
'port final fallback')

# Professor-originated grants: three-day cooldown, no duplicates, and generated professor programs if the fixed library has no match.
exp=one(exp,"    const professorCount=state.scientists.filter(item=>item.career==='professor').length,cooldown=7;","    const professorCount=state.scientists.filter(item=>item.career==='professor').length,cooldown=3;",'professor cooldown')
exp=one(exp,
"    let candidates=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)===3&&eligible(item)&&!(item.onlyPorts?.length)&&!activeTemplates.has(item.id)&&!recentTemplates.has(item.id));\n    if(!candidates.length)candidates=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)===3&&eligible(item)&&!(item.onlyPorts?.length)&&!activeTemplates.has(item.id)&&item.id!==(state.recentGrantTemplates||[])[0]);",
"    const professorTemplates=[...TEMPLATES,...careerFallbackTemplates()].filter(item=>templateCareerLevel(item)===3);\n    let candidates=professorTemplates.filter(item=>!item.weather&&eligible(item)&&!(item.onlyPorts?.length)&&!activeTemplates.has(item.id)&&!recentTemplates.has(item.id));\n    if(!candidates.length)candidates=professorTemplates.filter(item=>!item.weather&&eligible(item)&&!(item.onlyPorts?.length)&&!activeTemplates.has(item.id)&&item.id!==(state.recentGrantTemplates||[])[0]);",
'professor candidate fallbacks')

# Underway opportunities stay at the Chief Scientist's career scale; synthetic programs prevent an empty pool.
exp=one(exp,
"  function opportunityMoveGateKm(){return{fishing:45,trawler:90,coastal:150,global:220,icebreaker:270,nuclear:330}[state.currentVessel]||45;}",
"  function opportunityMoveGateKm(){return{fishing:45,trawler:70,coastal:100,global:140,icebreaker:180,nuclear:220}[state.currentVessel]||45;}",
'opportunity movement gate')
exp=one(exp,
"    const coastal=payload.fjord||payload.fjordScore>.38||payload.coastal||payload.coastDistanceKm<30,iceEdge=!!payload.iceEdge||payload.ice==='marginal'||payload.ice==='fast',iceThickness=Math.max(0,Number(payload.iceThickness)||0),deepIce=payload.ice==='packed'||payload.ice==='cracked'||payload.ice==='fast',inIce=iceEdge||deepIce,teamLevel=Math.max(1,...state.scientists.map(item=>careerLevel(item.career))),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length,careerFloor=playerCareerLevel(),unlockCredit=teamLevel>=3?8:teamLevel>=2?3:0;\n    const basePossible=TEMPLATES.filter(item=>!item.weather&&templateSupportedByVessel(item)&&templateCareerLevel(item)<=careerFloor&&(item.unlockAfter||0)<=state.completed.length+unlockCredit&&!activeTypes.has(item.id));",
"    const coastal=payload.fjord||payload.fjordScore>.38||payload.coastal||payload.coastDistanceKm<30,iceEdge=!!payload.iceEdge||payload.ice==='marginal',iceThickness=Math.max(0,Number(payload.iceThickness)||0),deepIce=payload.ice==='packed'||payload.ice==='cracked',inIce=iceEdge||deepIce,teamLevel=Math.max(1,...state.scientists.map(item=>careerLevel(item.career))),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length,careerFloor=playerCareerLevel(),unlockCredit=teamLevel>=3?8:teamLevel>=2?3:0,opportunityTemplates=[...TEMPLATES,...careerFallbackTemplates()];\n    const basePossible=opportunityTemplates.filter(item=>!item.weather&&templateSupportedByVessel(item)&&templateCareerLevel(item)===careerFloor&&(item.unlockAfter||0)<=state.completed.length+unlockCredit&&!activeTypes.has(item.id));",
'underway career pool')
exp=one(exp,
"    const allowGenericFallback=careerFloor===1&&state.currentVessel==='fishing';\n    if(!possible.length){if(!allowGenericFallback)return null;const fallback=compatibleFallbackTemplate();if(recent.has(fallback.id))return null;const rng=seeded(`fallback-${payload.position.lat.toFixed(2)}-${payload.position.lon.toFixed(2)}-${Math.floor(state.elapsedDays*4)}`),target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:false,iceThickness});if(!target)return null;target.selected=false;state.targets.push(target);recordOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;}",
"    if(!possible.length){const fallbacks=careerFallbackTemplates().filter(item=>!activeTypes.has(item.id)&&!recent.has(item.id)),fallback=fallbacks[0]||careerFallbackTemplates().find(item=>item.id!==recentList[0])||compatibleFallbackTemplate(),rng=seeded(`fallback-${payload.position.lat.toFixed(2)}-${payload.position.lon.toFixed(2)}-${Math.floor(state.elapsedDays*4)}`),target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:false,iceThickness});if(!target)return null;target.selected=false;state.targets.push(target);recordOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;}",
'underway final fallback')

# Port exclusion should prevent marker overlap, not erase huge swaths of the Arctic for larger vessels.
game=one(game,
"    const researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,fieldBuffer=({fishing:35,trawler:90,coastal:170,global:250,icebreaker:320,nuclear:380}[vesselIceId()]||35)+(careerLevel-1)*20,grantBuffer=({fishing:45,trawler:120,coastal:220,global:300,icebreaker:350,nuclear:400}[vesselIceId()]||45);",
"    const fieldBuffer=45,grantBuffer=80;",
'port exclusion radii')

game=one(game,
"    const shore=!!(template.shore||template.terrestrial),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,opportunityStart=({fishing:25,trawler:70,coastal:170,global:260,icebreaker:320,nuclear:380}[vesselIceId()]||25)+(careerLevel-1)*20,window=context.distanceWindow,windowDistances=window?[window.min,window.min+(window.max-window.min)*.2,window.min+(window.max-window.min)*.4,window.min+(window.max-window.min)*.6,window.min+(window.max-window.min)*.8,window.max]:null,distances=windowDistances||(shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[opportunityStart,opportunityStart+50,opportunityStart+110,opportunityStart+190,opportunityStart+280]:[45,65,85,105,130,165,210])),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150,180];",
"    const shore=!!(template.shore||template.terrestrial),researchState=research?.getState?.(),chief=researchState?.scientists?.find(item=>item.isPlayer)||researchState?.scientists?.[0],careerLevel=chief?.career==='professor'?3:chief?.career==='postdoc'?2:1,opportunityStart=({fishing:25,trawler:45,coastal:70,global:100,icebreaker:120,nuclear:140}[vesselIceId()]||25)+(careerLevel-1)*10,window=context.distanceWindow,windowDistances=window?[window.min,window.min+(window.max-window.min)*.2,window.min+(window.max-window.min)*.4,window.min+(window.max-window.min)*.6,window.min+(window.max-window.min)*.8,window.max]:null,distances=windowDistances||(shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[opportunityStart,opportunityStart+35,opportunityStart+75,opportunityStart+125,opportunityStart+190]:[45,65,85,105,130,165,210])),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150,180];",
'find research site distances')

# Remove remaining dead fast-ice references encountered in live movement logic.
game=game.replace("&&nextProfile.type!=='fast'","")

# Cache bust.
if 'expedition-23y-grant-cleanup' not in index:
    raise RuntimeError('expected 23y cache key')
index=index.replace('expedition-23y-grant-cleanup','expedition-23z-opportunity-hotfix')

# Source assertions.
for needle in [
    'careerFallbackTemplates()',
    'grants-v7-',
    'cooldown=3',
    'templateCareerLevel(item)===careerFloor',
    'fieldBuffer=45,grantBuffer=80',
    'expedition-23z-opportunity-hotfix',
]:
    text=exp if needle not in ('fieldBuffer=45,grantBuffer=80','expedition-23z-opportunity-hotfix') else game if needle=='fieldBuffer=45,grantBuffer=80' else index
    if needle not in text: raise RuntimeError(f'missing marker: {needle}')
if "payload.ice==='fast'" in exp: raise RuntimeError('fast ice still referenced in expedition opportunity logic')
if "nextProfile.type!=='fast'" in game: raise RuntimeError('fast ice still referenced in movement logic')

exp_path.write_text(exp)
game_path.write_text(game)
index_path.write_text(index)
print('ARS_23Z_OPPORTUNITY_HOTFIX_OK')
