from pathlib import Path
import re


def read(path):
    return Path(path).read_text(encoding='utf-8')

def write(path, text):
    Path(path).write_text(text, encoding='utf-8')

def replace_once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old,new,1)

def regex_once(text, pattern, replacement, label, flags=0):
    text2,count=re.subn(pattern,replacement,text,count=1,flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text2

# ---------------- expedition.js ----------------
p='expedition.js'
s=read(p)

s=replace_once(s,
"    global:'assets/vessels/global-rv.webp?v=23ae',",
"    global:'assets/vessels/global-rv-clean.webp?v=23af',",
'global vessel image')

reward_old="""  function missionRewardAmount(template,kind,distanceKm,rng,actualWorkHours=template.workHours) {
    const official=kind==='grant'||kind==='contract',base=official?[40000,60000]:[10000,15000];
    const score=clamp(missionRewardScore(template,distanceKm,kind,actualWorkHours)+(rng()-.5)*.05,0,1);
    const careerFactor=playerCareerLevel()>=3?2.4:playerCareerLevel()===2?1.55:1;
    const vesselFactor={fishing:1,trawler:1.25,coastal:1.8,global:3,icebreaker:4.5,nuclear:6}[state.currentVessel]||1;
    const templateFactor=1+Math.max(0,templateCareerLevel(template)-1)*.18;
    const value=(base[0]+(base[1]-base[0])*score)*careerFactor*vesselFactor*templateFactor;
    return Math.round(value/500)*500;
  }
"""
reward_new="""  function missionRewardAmount(template,kind,distanceKm,rng,actualWorkHours=template.workHours) {
    const official=kind==='grant'||kind==='contract',base=official?[40000,60000]:[10000,15000];
    const score=clamp(missionRewardScore(template,distanceKm,kind,actualWorkHours)+(rng()-.5)*.05,0,1);
    const careerFactor=playerCareerLevel()>=3?2.4:playerCareerLevel()===2?1.55:1;
    const vesselFactor={fishing:1,trawler:1.25,coastal:1.8,global:3,icebreaker:4.5,nuclear:6}[state.currentVessel]||1;
    const templateFactor=1+Math.max(0,templateCareerLevel(template)-1)*.18;
    const durableItems=[...new Set(template.equipment||[])].map(id=>EQUIPMENT[id]).filter(Boolean);
    const durableValue=durableItems.reduce((sum,item)=>sum+(Number(item.price)||0),0);
    const professorCount=missionSpecialistRequirements(template).filter(item=>item.minCareer==='professor').reduce((sum,item)=>sum+(item.count||1),0);
    const heavyDuty=durableItems.some(item=>item.slotType==='heavy'||(item.slots||0)>=3)||durableValue>=250000;
    const modestSingleProfessor=professorCount<=1&&!heavyDuty&&durableValue<140000;
    const complexityFactor=official&&playerCareerLevel()>=3?(professorCount>=2&&heavyDuty?1.15:modestSingleProfessor?.92:1):1;
    const value=(base[0]+(base[1]-base[0])*score)*careerFactor*vesselFactor*templateFactor*complexityFactor;
    return Math.round(value/500)*500;
  }
"""
s=replace_once(s,reward_old,reward_new,'professor reward scaling')

s=replace_once(s,
"    const grantRanges={fishing:[25,150],trawler:[70,350],coastal:[120,650],global:[180,900],icebreaker:[220,1350],nuclear:[260,1700]};",
"    const grantRanges={fishing:[25,150],trawler:[70,350],coastal:[120,650],global:playerCareerLevel()>=3?[600,3000]:[180,900],icebreaker:[220,1350],nuclear:[260,1700]};",
'global RV grant range')

s=replace_once(s,
"  let root = null;\n  let portOpen = false;",
"  let root = null;\n  let pendingWildlifeArticle = null;\n  let portOpen = false;",
'wildlife article pending state')

nav_marker="""    const navigateAction=accepted&&!atSite&&!target.anywhere?`<button data-arx-action=\"navigate-target\" data-id=\"${target.id}\">NAVIGATE TO SITE</button>`:'';
"""
nav_insert=nav_marker+"""    const guidancePreview=!!(state.lastTargetContext?.id===target.id&&state.lastTargetContext?.previewOnly&&!atSite&&!running&&!complete);
    if(guidancePreview){
      modal.innerHTML=`<div class=\"arx-modal-card arx-target-card arx-research-unified arx-guidance-preview\"><button class=\"arx-close\" data-arx-action=\"close-target\" aria-label=\"Close research preview\">×</button><small>ACTIVE RESEARCH GRANT · COURSE PREVIEW</small><h2>${escapeHtml(target.title)}</h2>${mediaMarkup(target,'hero')}<p>${escapeHtml(target.description)}</p><div class=\"arx-target-facts arx-research-facts\"><span><small>CASH AWARD</small><b>${cash(target.reward||0)}</b></span><span><small>DATA AWARD</small><b>+${target.data} data</b></span><span><small>DISTANCE</small><b>${Number.isFinite(distance)?`${Math.round(distance)} km`:'OFF-SCREEN SITE'}</b></span></div><h3 class=\"arx-operation-subhead\">SCIENTISTS MAKING THIS POSSIBLE</h3>${operationScientistsMarkup(target)}<h3 class=\"arx-operation-subhead\">EQUIPMENT MAKING THIS POSSIBLE</h3>${operationEquipmentMarkup(target)}<div class=\"arx-research-review-actions\">${decline}${navigateAction}</div></div>`;
      modal.classList.add('open');
      return;
    }
"""
s=replace_once(s,nav_marker,nav_insert,'gold arrow preview')

wildlife_helpers="""  function publishWildlifeJournalArticle(group) {
    const level=PAPER_LEVELS.find(item=>item.id==='national')||PAPER_LEVELS[1];
    const award=level.award,initialCitations=level.initialCitations,potential=level.potential,title=`Article: ${group} of the Arctic`;
    adjustMoney(award);state.citations+=initialCitations;
    state.papers.push({id:`wildlife-paper-${Date.now()}`,title,journal:level.journal,tier:level.label,data:0,award,initialCitations,potential,citations:initialCitations,ageDays:0,citationRemainder:0,wildlifeGroup:group});
    for(const scientist of state.scientists){scientist.papers=(scientist.papers||0)+1;recordScientist(scientist);}
    state.claimedGroups=state.claimedGroups||[];state.claimedGroups.push(group);state.claimedGroups=state.claimedGroups.slice(-40);
    state.observed=(state.observed||[]).filter(key=>catalog[key]?.group!==group);
    pendingWildlifeArticle={group,title,journal:level.journal,award,initialCitations};
    addLog(`Field journal complete: ${group}. Article published in ${level.journal}; checklist reset for a new survey cycle.`);
    callbacks.onSound?.('paper-accepted');checkPromotions();
  }
  function showPendingWildlifeArticle() {
    if(!pendingWildlifeArticle||!root)return false;
    const article=pendingWildlifeArticle;pendingWildlifeArticle=null;
    const modal=root.querySelector('#arx-publish-modal');if(!modal)return false;
    modal.innerHTML=`<div class=\"arx-modal-card arx-result-card accepted\"><button class=\"arx-close\" data-arx-action=\"close-publish\">×</button><small>FIELD JOURNAL ACHIEVEMENT · ARTICLE ACCEPTED</small><h2>${escapeHtml(article.group)} article published</h2><p>Your completed field journal on <b>${escapeHtml(article.group)}</b> has been published as a peer-reviewed article in ${escapeHtml(article.journal)}. The ${escapeHtml(article.group)} checklist has been reset, so a new survey cycle can begin.</p><div class=\"arx-award\"><span>${cash(article.award)}</span><small>JOURNAL ARTICLE AWARD · +${article.initialCitations} INITIAL CITATIONS</small></div><button data-arx-action=\"close-publish\">CONTINUE EXPEDITION</button></div>`;
    modal.classList.add('open');changed();return true;
  }

"""
s=replace_once(s,"  function groupProgress(group) {",wildlife_helpers+"  function groupProgress(group) {",'wildlife article helpers')

old_group="""    if (progress.complete&&!state.claimedGroups.includes(item.group)) {
      state.claimedGroups.push(item.group); adjustMoney(GROUP_REWARDS[item.group]||30000); state.citations+=5;
      addLog(`Field assignment complete: ${item.group}. Illustrated article published in Northern Field Notes.`);
      toast(`${item.group.toUpperCase()} COMPLETE · NORTHERN FIELD NOTES PUBLISHED`);
    }
"""
new_group="""    if (progress.complete) {
      publishWildlifeJournalArticle(item.group);
      toast(`${item.group.toUpperCase()} COMPLETE · JOURNAL ARTICLE PUBLISHED`);
    }
"""
s=replace_once(s,old_group,new_group,'wildlife completion publication')

s=replace_once(s,
"<em>${state.claimedGroups.includes(group)?'PUBLISHED':'IN PROGRESS'}</em>",
"<em>${progress.complete?'COMPLETE':'IN PROGRESS'}</em>",
'field guide reset state')

s=replace_once(s,
"    else if (action==='close-wildlife') { root.querySelector('#arx-wildlife-modal').classList.remove('open'); setTimeout(maybeAutoPublish,0); }",
"    else if (action==='close-wildlife') { root.querySelector('#arx-wildlife-modal').classList.remove('open'); if(!showPendingWildlifeArticle())setTimeout(maybeAutoPublish,0); }",
'wildlife achievement popup')

write(p,s)

# ---------------- game.js ----------------
p='game.js'
s=read(p)

s=replace_once(s,
"    let ac=null,waveSource=null,waveGain=null,lastCrack=0,lastAnimal=0,unlockChimed=false;",
"    let ac=null,waveSource=null,waveGain=null,lastCrack=0,lastAnimal=0,unlockChimed=false,unlockPromise=null;",
'audio state')

unlock_old="""    const unlock=()=>{const c=ensure();if(!c)return;const confirm=()=>{if(unlockChimed||c.state!=='running')return;unlockChimed=true;tone(660,.10,.10,0,'sine');tone(880,.14,.09,.10,'sine');};if(c.state==='suspended'){const resumed=c.resume();if(resumed&&typeof resumed.then==='function')resumed.then(confirm).catch(()=>{});else confirm();}else confirm();};
"""
unlock_new="""    const unlock=()=>{const c=ensure();if(!c)return;try{if(navigator.audioSession)navigator.audioSession.type='playback';}catch(error){}try{const primer=c.createOscillator(),primerGain=c.createGain();primerGain.gain.value=.0001;primer.connect(primerGain).connect(c.destination);primer.start(c.currentTime);primer.stop(c.currentTime+.025);}catch(error){}const confirm=()=>{if(unlockChimed||c.state!=='running')return;unlockChimed=true;tone(660,.10,.10,0,'sine');tone(880,.14,.09,.10,'sine');};if(c.state!=='running'){if(!unlockPromise)unlockPromise=Promise.resolve(c.resume()).catch(()=>{}).finally(()=>{unlockPromise=null;});unlockPromise.then(confirm).catch(()=>{});}else confirm();};
"""
s=replace_once(s,unlock_old,unlock_new,'ios audio unlock')

s=replace_once(s,
"    const play=(type)=>{const c=ensure();if(!c)return;if(c.state==='suspended')c.resume();switch(type){",
"    const play=(type)=>{const c=ensure();if(!c)return;const run=()=>{switch(type){",
'audio play deferred start')
s=replace_once(s,
"case'fish':tone(1150,.025,.012);tone(900,.025,.01,.05);break;}}",
"case'fish':tone(1150,.025,.012);tone(900,.025,.01,.05);break;}};if(c.state!=='running'){Promise.resolve(c.resume()).then(()=>{if(c.state==='running')run();}).catch(()=>{});return;}run();}",
'audio play deferred tail')
s=replace_once(s,
"  document.addEventListener('touchstart',()=>sound.unlock(),{capture:true,passive:true});",
"  document.addEventListener('touchstart',()=>sound.unlock(),{capture:true,passive:true});\n  document.addEventListener('touchend',()=>sound.unlock(),{capture:true,passive:true});",
'touchend audio unlock')

s=replace_once(s,
"    if((siteIce==='packed'||siteIce==='cracked')&&!iceAllowed)return false;",
"    if(official&&vesselIceId()==='global'&&siteIce!=='open')return false;\n    if((siteIce==='packed'||siteIce==='cracked')&&!iceAllowed)return false;",
'global RV open-water research only')

s=replace_once(s,
"  function drawMap(){\n    const g=ctx.createRadialGradient",
"  function drawMap(){\n    ctx.fillStyle='#04131d';ctx.fillRect(0,0,width,height);const chartCenter=worldToScreen(0,0),chartRadius=terrainLatitudeRadius(MIN_LAT)*scale;ctx.save();ctx.beginPath();ctx.arc(chartCenter.x,chartCenter.y,chartRadius,0,Math.PI*2);ctx.clip();\n    const g=ctx.createRadialGradient",
'main chart clip start')
s=replace_once(s,
"    drawGraticule();drawCurrentArrows();drawChartBoundary();if(brokenIceChannels.length)captureOceanLayer();else oceanPattern=null;",
"    drawGraticule();drawCurrentArrows();if(brokenIceChannels.length)captureOceanLayer();else oceanPattern=null;",
'main chart boundary move')

# Insert restore + boundary at the end of drawMap, immediately before rebuildWorldCache.
m=re.search(r"(  function drawMap\(\)\{.*?)(\n  \}\n  function rebuildWorldCache)",s,re.S)
if not m: raise SystemExit('drawMap end: no match')
body=m.group(1)
if "ctx.restore();drawChartBoundary();" not in body:
    body += "\n    ctx.restore();drawChartBoundary();"
s=s[:m.start()]+body+m.group(2)+s[m.end():]

mini_start="""mini.clearRect(0,0,size,size);mini.save();mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.clip();const project=(x,y)=>({x:c+(x-geometry.centerX)/worldRadius*radius,y:c+(y-geometry.centerY)/worldRadius*radius});const miniTerrain=drawTerrainRaster(mini,project,.94);"""
mini_new="""mini.clearRect(0,0,size,size);mini.save();mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.clip();mini.fillStyle='#04131d';mini.fillRect(0,0,size,size);const project=(x,y)=>({x:c+(x-geometry.centerX)/worldRadius*radius,y:c+(y-geometry.centerY)/worldRadius*radius});const chartPole=project(0,0),chartRadius=terrainLatitudeRadius(MIN_LAT)/worldRadius*radius;mini.beginPath();mini.arc(chartPole.x,chartPole.y,chartRadius,0,Math.PI*2);mini.clip();const miniTerrain=drawTerrainRaster(mini,project,.94);"""
s=replace_once(s,mini_start,mini_new,'minimap chart clip')

s=replace_once(s,
"mini.restore();mini.strokeStyle='rgba(218,247,252,.6)';mini.lineWidth=1;mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.stroke();",
"mini.restore();mini.strokeStyle='rgba(248,221,125,.82)';mini.lineWidth=1.4;mini.setLineDash([7,5]);mini.beginPath();mini.arc(chartPole.x,chartPole.y,chartRadius,0,Math.PI*2);mini.stroke();mini.setLineDash([]);mini.strokeStyle='rgba(218,247,252,.6)';mini.lineWidth=1;mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.stroke();",
'minimap chart boundary')

frame_old="""    if(!paused&&renderDue){lastRender=now;drawWorldCached(now);drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);drawResearchGuidance();drawVessel();}
"""
frame_new="""    if(!paused&&renderDue){lastRender=now;drawWorldCached(now);const chartCenter=worldToScreen(0,0),chartRadius=terrainLatitudeRadius(MIN_LAT)*scale;ctx.save();ctx.beginPath();ctx.arc(chartCenter.x,chartCenter.y,chartRadius,0,Math.PI*2);ctx.clip();drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);drawResearchGuidance();drawVessel();ctx.restore();}
"""
s=replace_once(s,frame_old,frame_new,'dynamic main chart clip')

write(p,s)

# ---------------- index.html ----------------
p='index.html'
s=read(p)
s=replace_once(s,
"        <span class=\"cash-status\"><small>CASH</small><b id=\"cash-balance\">$185,000</b></span>\n",
"",
'hide main HUD cash')
s=s.replace('expedition-23ae-grant-clarity-images','expedition-23af-audio-rewards-journal-map')
write(p,s)
