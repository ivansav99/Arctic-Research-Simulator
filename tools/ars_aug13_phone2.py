from pathlib import Path
import re


def replace_once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old,new,1)


def replace_regex(text, pattern, repl, label, flags=0):
    out,count=re.subn(pattern,repl,text,count=1,flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return out

# ---------- index.html ----------
p=Path('index.html'); s=p.read_text()
s=replace_once(s,'style.css?v=expedition-22k-mobile','style.css?v=expedition-22m-phone2','css cache')
s=replace_once(s,'expedition.js?v=expedition-22j-progression','expedition.js?v=expedition-22m-phone2','expedition cache')
s=replace_once(s,'game.js?v=expedition-22k-mobile','game.js?v=expedition-22m-phone2','game cache')
s=replace_once(s,'          <button id="resume-button" class="secondary hidden" type="button">RETURN TO EXPEDITION</button>\n','', 'duplicate resume button')
old='<aside class="minimap hud" aria-label="Overview map showing vessel position"><div><small>ARCTIC OVERVIEW</small><b id="mini-location">SVALBARD</b></div><canvas id="minimap" width="300" height="300"></canvas></aside>'
new='''<aside id="minimap-panel" class="minimap hud" aria-label="Navigation overview map">
      <button id="minimap-close" class="minimap-close" type="button" aria-label="Close navigation chart">×</button>
      <div class="minimap-heading"><small>NAVIGATION CHART</small><b id="mini-location">SVALBARD</b></div>
      <canvas id="minimap" width="300" height="300" aria-label="Open navigation chart"></canvas>
      <div class="minimap-nav-details">
        <span><small>POSITION</small><b id="mini-position">—</b></span>
        <span><small>COURSE</small><b id="mini-course">STOPPED</b></span>
        <span><small>SEA ICE</small><b id="mini-ice">OPEN WATER</b></span>
        <span><small>WEATHER</small><b id="mini-weather">CLEAR</b></span>
      </div>
    </aside>'''
s=replace_once(s,old,new,'minimap markup')
p.write_text(s)

# ---------- expedition.js ----------
p=Path('expedition.js'); e=p.read_text()
e=replace_once(e,"short:'POSTDOC'","short:'Postdoc'",'postdoc label')
e=replace_once(e,"short:'PROF'","short:'Professor'",'professor label')
e=replace_once(e,"id:'icebreaker', name:'Basic Icebreaker'","id:'icebreaker', name:'Icebreaker'",'icebreaker name')

# Avatar labels disappear; user gets an editable name.
e=replace_regex(e,r"const PLAYER_AVATARS = \[.*?\n  \];",'''const PLAYER_AVATARS = [
    {id:'chief-1',src:'assets/scientists/maya-chen.webp'},
    {id:'chief-2',src:'assets/scientists/elena-petrova.webp'},
    {id:'chief-3',src:'assets/scientists/daniel-okafor.webp'},
    {id:'chief-4',src:'assets/scientists/sofia-lindgren.webp'},
    {id:'chief-5',src:'assets/scientists/henrik-larsen.webp'},
    {id:'chief-6',src:'assets/scientists/ana-silva.webp'}
  ];''','avatar definitions',re.S)
e=e.replace("name:'You'","name:'Chief Scientist'",1)
e=replace_regex(e,r"let characterDraft=\{avatar:PLAYER_AVATARS\[0\]\.id,specialty:'coastal-oceanography'\};","let characterDraft={avatar:PLAYER_AVATARS[0].id,specialty:'coastal-oceanography',name:''};",'character draft')

# Only report equipment capacities the hull actually has.
e=replace_regex(e,r"  function slotSummary\(ship=vessel\(\), usage=slotUsage\(\)\) \{.*?\n  \}",'''  function slotSummary(ship=vessel(), usage=slotUsage()) {
    const parts=SLOT_TYPES.filter(type=>(ship.slots[type]||0)>0).map(type=>`${type[0].toUpperCase()+type.slice(1)} ${usage[type]||0}/${ship.slots[type]}`);
    return `Equipment capacity: ${parts.join(' · ')}`;
  }''','slot summary',re.S)

# Vessel information at sea is information only: X dismisses it; never route back to last port.
e=e.replace("${!inPort&&state.port?'<button data-arx-action=\"open-vessel-port\">OPEN YOUR VESSEL TAB IN PORT</button>':''}","",1)

# Full character setup block with name entry and image-only avatar choices.
character_block='''  function openCharacterSetup() {
    if (!root||state.playerConfigured) return false;
    const modal=root.querySelector('#arx-character-modal'), selected=PLAYER_AVATARS.find(item=>item.id===characterDraft.avatar)||PLAYER_AVATARS[0];
    modal.innerHTML=`<div class="arx-modal-card arx-character-card"><small>CHIEF SCIENTIST</small><h2>Create your scientist</h2><p>Choose your portrait, enter your name, and select the specialty that will shape your first research opportunities.</p><label class="arx-character-name"><span>YOUR NAME</span><input data-arx-character-name maxlength="40" autocomplete="name" placeholder="Chief Scientist" value="${escapeHtml(characterDraft.name||'')}"></label><div class="arx-avatar-grid">${PLAYER_AVATARS.map((avatar,index)=>`<button data-arx-action="choose-avatar" data-id="${avatar.id}" class="${avatar.id===selected.id?'selected':''}" aria-label="Portrait ${index+1}"><img src="${avatar.src}" alt="Portrait ${index+1}"></button>`).join('')}</div><label class="arx-specialty-select"><span>STARTING SPECIALTY</span><select data-arx-character-specialty>${SPECIALTIES.map(item=>`<option value="${item.id}" ${item.id===characterDraft.specialty?'selected':''}>${escapeHtml(item.name)}</option>`).join('')}</select></label><div class="arx-character-summary"><img src="${selected.src}" alt=""><div><b>${escapeHtml((characterDraft.name||'').trim()||'Chief Scientist')}</b><span>${escapeHtml(specialtyById[characterDraft.specialty]?.name||'Coastal Oceanographer')}</span><small>Graduate Student · Chief Scientist</small></div></div><button data-arx-action="confirm-character">BEGIN CAREER</button></div>`;
    modal.classList.add('open'); return true;
  }
  function confirmCharacter() {
    const modal=root.querySelector('#arx-character-modal'), select=modal?.querySelector('[data-arx-character-specialty]'), input=modal?.querySelector('[data-arx-character-name]');
    characterDraft.specialty=select?.value||characterDraft.specialty;
    characterDraft.name=(input?.value||characterDraft.name||'').trim().slice(0,40);
    const player=playerScientist(), avatar=PLAYER_AVATARS.find(item=>item.id===characterDraft.avatar)||PLAYER_AVATARS[0], name=characterDraft.name||'Chief Scientist';
    Object.assign(player,{id:'player',name,specialty:characterDraft.specialty,career:'grad',isPlayer:true,profileId:'player',portrait:avatar.src,recruitmentPool:'player'});
    state.playerConfigured=true; recordScientist(player); modal?.classList.remove('open'); addLog(`${name} began the Arctic research career as a ${specialtyById[characterDraft.specialty]?.name||'scientist'}.`); changed(); callbacks.onCharacterReady?.();
  }
'''
e=replace_regex(e,r"  function openCharacterSetup\(\) \{.*?\n  function openNpcVessel",character_block+'  function openNpcVessel','character setup block',re.S)
# Preserve current name/specialty when selecting another portrait.
e=replace_once(e,"if(action==='choose-avatar'){characterDraft.avatar=id;characterDraft.specialty=root.querySelector('[data-arx-character-specialty]')?.value||characterDraft.specialty;openCharacterSetup();return;}","if(action==='choose-avatar'){characterDraft.avatar=id;characterDraft.specialty=root.querySelector('[data-arx-character-specialty]')?.value||characterDraft.specialty;characterDraft.name=root.querySelector('[data-arx-character-name]')?.value||characterDraft.name;root.querySelector('#arx-character-modal')?.classList.remove('open');openCharacterSetup();return;}",'avatar handler')

# Prefer unique pictures on a single grant board; duplicates are only a fallback when necessary.
old="""    state.offers=[];
    for (const template of pool) {
      if (state.offers.length>=offerLimit) break;
      const target=buildTarget(template,port,rng,'grant');
      if (target) state.offers.push(target);
    }
"""
new="""    state.offers=[];
    const builtOffers=[];
    for (const template of pool) { const target=buildTarget(template,port,rng,'grant'); if(target)builtOffers.push(target); }
    const usedPictures=new Set(), duplicatePictures=[];
    for(const target of builtOffers){const src=target.media?.src||'';if(src&&usedPictures.has(src)){duplicatePictures.push(target);continue;}state.offers.push(target);if(src)usedPictures.add(src);if(state.offers.length>=offerLimit)break;}
    if(state.offers.length<offerLimit)for(const target of duplicatePictures){state.offers.push(target);if(state.offers.length>=offerLimit)break;}
"""
e=replace_once(e,old,new,'unique grant images')

# Port tab viewport gets unobtrusive overflow chevrons.
e=replace_once(e,'<div class="arx-port-navrow"><nav class="arx-tabs arx-tabs-top">','<div class="arx-port-navrow"><div class="arx-tabs-viewport"><i class="arx-tab-hint left">‹</i><nav class="arx-tabs arx-tabs-top">','tab viewport start')
e=replace_once(e,"${relocationUnlocked()?tab('relocate','Relocate Home Port'):''}</nav><div class=\"arx-port-cash\">","${relocationUnlocked()?tab('relocate','Relocate Home Port'):''}</nav><i class=\"arx-tab-hint right\">›</i></div><div class=\"arx-port-cash\">",'tab viewport end')

# Add late CSS overrides inside the injected research stylesheet.
needle="    root.addEventListener('click',event=>{"
extra=r'''    style.textContent+=`
      .arx-character-name{display:block;margin:16px 0 12px}.arx-character-name span,.arx-specialty-select>span{display:block;margin-bottom:6px;color:#8fb7c2;font-size:7px;font-weight:900;letter-spacing:.11em}.arx-character-name input{width:100%;padding:11px 12px;border:1px solid rgba(166,230,244,.24);border-radius:8px;background:#123d51;color:#eff9fb;font:700 14px system-ui}.arx-avatar-grid button{overflow:hidden}.arx-avatar-grid button img{display:block}.arx-tabs-viewport{position:relative;display:flex;flex:1 1 auto;min-width:0}.arx-tabs-viewport .arx-tabs{flex:1 1 auto;min-width:0}.arx-tab-hint{display:none;pointer-events:none}.arx-tabs button.attention{outline:1px solid rgba(142,240,207,.9)!important;outline-offset:-2px!important;box-shadow:inset 0 0 0 1px rgba(142,240,207,.2),inset 0 0 15px rgba(142,240,207,.12)!important;border-radius:5px}
      @media(max-width:760px) and (orientation:portrait){.arx-modal{padding:calc(env(safe-area-inset-top) + 9px) 9px calc(env(safe-area-inset-bottom) + 9px)!important}.arx-modal-card{max-height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 18px)!important}.arx-port-navrow{display:block!important}.arx-tabs-viewport{padding:0 13px}.arx-tab-hint{position:absolute;z-index:5;top:0;bottom:1px;width:16px;display:grid;place-items:center;color:#dffaff;font:900 18px/1 system-ui;background:linear-gradient(90deg,rgba(4,27,40,.98),rgba(4,27,40,.25))}.arx-tab-hint.left{left:0}.arx-tab-hint.right{right:0;transform:none;background:linear-gradient(270deg,rgba(4,27,40,.98),rgba(4,27,40,.25))}.arx-port-cash{justify-content:space-between!important;padding:8px 0!important;border-left:0!important;border-bottom:1px solid rgba(166,230,244,.14)!important}}
      @media(max-width:900px) and (orientation:landscape){.arx-port-navrow{display:flex!important}.arx-tabs-viewport{padding:0!important}.arx-tab-hint{display:none!important}.arx-port-cash{flex:0 0 auto!important;justify-content:flex-end!important;padding:0 10px!important;border-left:1px solid rgba(166,230,244,.18)!important;border-bottom:0!important}}
    `;
'''
e=replace_once(e,needle,extra+needle,'research mobile CSS')
p.write_text(e)

# ---------- game.js ----------
p=Path('game.js'); g=p.read_text()
# UI refs for expanded navigation chart.
g=replace_once(g,"miniLocation:document.getElementById('mini-location'),","miniLocation:document.getElementById('mini-location'),miniPosition:document.getElementById('mini-position'),miniCourse:document.getElementById('mini-course'),miniIce:document.getElementById('mini-ice'),miniWeather:document.getElementById('mini-weather'),",'mini ui refs')
g=replace_once(g,"const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i');","const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i'),minimapPanel=document.getElementById('minimap-panel'),minimapClose=document.getElementById('minimap-close');",'mini panel refs')
g=replace_once(g,"let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,startFlowPending=false,npcUpdateAccumulator=0,researchGuidanceHit=null;","let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,pendingResearchArrival=null,startFlowPending=false,npcUpdateAccumulator=0,researchGuidanceHit=null,minimapExpanded=false;",'navigation state')

# Better Boreal Crown detail art path.
g=replace_once(g,"image:SMALL_PASSENGER_SVG","image:'assets/vessels/boreal-crown.svg'",'Boreal detail art')

# Special, tightly-trimmed passenger vessel map symbol with bow forward.
old="""  function drawNpcIcon(npc,screen){
    ctx.save();ctx.translate(screen.x,screen.y);ctx.rotate(npc.angle+Math.PI/2);
    const sprite=SPRITES.vessels[npc.classId];
"""
new="""  function drawNpcIcon(npc,screen){
    ctx.save();ctx.translate(screen.x,screen.y);ctx.rotate(npc.angle+Math.PI/2);
    if(npc.id==='mv-boreal-crown'){
      ctx.shadowColor='rgba(0,17,28,.38)';ctx.shadowBlur=4;ctx.fillStyle='#173c50';ctx.beginPath();ctx.moveTo(0,-23);ctx.lineTo(9,-13);ctx.lineTo(8,19);ctx.lineTo(-8,19);ctx.lineTo(-9,-13);ctx.closePath();ctx.fill();ctx.shadowBlur=0;
      ctx.fillStyle='#eef8f8';ctx.beginPath();ctx.moveTo(0,-15);ctx.lineTo(6,-8);ctx.lineTo(6,11);ctx.lineTo(-6,11);ctx.lineTo(-6,-8);ctx.closePath();ctx.fill();ctx.fillStyle='#5cb1d0';ctx.fillRect(-5,-6,10,5);ctx.fillRect(-5,3,10,4);ctx.fillStyle='#f6d365';ctx.fillRect(-1,-19,2,7);ctx.strokeStyle='rgba(230,250,252,.85)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(-7,14);ctx.lineTo(7,14);ctx.stroke();ctx.restore();return;
    }
    const sprite=SPRITES.vessels[npc.classId];
"""
g=replace_once(g,old,new,'Boreal map icon')

# Minimap follows the vessel and uses its actual rendered size instead of a hidden 120px minimum.
g=replace_regex(g,r"  function miniMapGeometry\(\)\{.*?\n  \}",'''  function miniMapGeometry(){
    return {worldRadius:minimapExpanded?1100:520,centerX:state.x,centerY:state.y};
  }''','minimap geometry',re.S)
g=replace_once(g,"const size=Math.max(120,miniCanvas.clientWidth||148);","const measured=Math.round(miniCanvas.clientWidth||148),size=Math.max(minimapExpanded?260:64,measured);if(miniCanvas.width!==size||miniCanvas.height!==size){miniCanvas.width=size;miniCanvas.height=size;}",'minimap backing size')

# Add nav readouts at the end of drawMiniMap before context restore if marker exists.
marker="    mini.restore();\n  }\n  function drawVessel"
insert="""    const currentPos=unpolar(state.x,state.y),ew=currentPos.lon<0?'W':'E',weather=currentWeather(),profile=iceNavigationProfileAt(state.x,state.y),course=state.commandActive?((Math.atan2(state.tx-state.x,state.ty-state.y)*180/Math.PI+360)%360):null;
    if(ui.miniLocation)ui.miniLocation.textContent=locationName(currentPos.lat,currentPos.lon);if(ui.miniPosition)ui.miniPosition.textContent=`${currentPos.lat.toFixed(2)}°N ${Math.abs(currentPos.lon).toFixed(2)}°${ew}`;if(ui.miniCourse)ui.miniCourse.textContent=course==null?'STOPPED':`${Math.round(course).toString().padStart(3,'0')}°`;if(ui.miniIce)ui.miniIce.textContent=iceStatusText(profile,state.ramming);if(ui.miniWeather)ui.miniWeather.textContent=weather.type==='clear'?'CLEAR':weather.label.toUpperCase();
    mini.restore();
  }
  function drawVessel"""
g=replace_once(g,marker,insert,'minimap readouts')

# Expanded mini map behaves like a modal and pauses the simulation.
anchor="  function clampResource(value){return Math.max(0,Math.min(100,value));}\n"
addition="""  function openMinimap(){if(!minimapPanel||minimapExpanded)return;minimapExpanded=true;minimapPanel.classList.add('expanded');document.body.classList.add('nav-chart-open');drawMiniMap();}
  function closeMinimap(){if(!minimapPanel)return;minimapExpanded=false;minimapPanel.classList.remove('expanded');document.body.classList.remove('nav-chart-open');drawMiniMap();}
"""
g=replace_once(g,anchor,anchor+addition,'minimap modal functions')
g=replace_once(g,"const paused=state.gameOver||menuOpen||!!research?.isBusy?.();","const paused=state.gameOver||menuOpen||minimapExpanded||!!research?.isBusy?.();",'pause expanded minimap')
g=replace_once(g,"miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});navigateFromMiniMap(e);});","miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();e.preventDefault();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});if(!minimapExpanded)openMinimap();});\n  minimapClose?.addEventListener('click',e=>{e.stopPropagation();closeMinimap();});",'minimap click behavior')
g=replace_once(g,"addEventListener('keydown',e=>{if(e.key==='Escape'&&state.started&&!menuOpen){openGameMenu();return;}","addEventListener('keydown',e=>{if(e.key==='Escape'&&minimapExpanded){closeMinimap();return;}if(e.key==='Escape'&&state.started&&!menuOpen){openGameMenu();return;}",'escape minimap')

# One Continue button: return to current expedition if paused, otherwise only show a real configured autosave.
g=replace_regex(g,r"  function refreshMenu\(\)\{.*?\n  \}",'''  function refreshMenu(){
    const auto=readSave('auto'),continueButton=document.getElementById('continue-button'),saveButton=document.getElementById('save-button'),summary=document.getElementById('continue-summary'),loadSlots=document.getElementById('load-slots'),saveSlots=document.getElementById('save-slots');
    const validAuto=!!(auto?.research?.playerConfigured||auto?.research?.completed?.length||auto?.meta?.missions);
    if(continueButton){continueButton.textContent=state.started?'RETURN TO EXPEDITION':'CONTINUE EXPEDITION';continueButton.classList.toggle('hidden',!state.started&&!validAuto);}
    saveButton?.classList.toggle('hidden',!state.started);
    if(summary)summary.textContent=state.started?'Game paused. Return when ready.':validAuto?saveSummary(auto):'';
    const slots=['slot1','slot2','slot3'];if(loadSlots)loadSlots.innerHTML=slots.map(slot=>saveSlotMarkup(slot,readSave(slot),false)).join('');if(saveSlots)saveSlots.innerHTML=slots.map(slot=>saveSlotMarkup(slot,readSave(slot),true)).join('');
  }''','refresh menu',re.S)
g=replace_once(g,"document.getElementById('continue-button').addEventListener('click',()=>{sound.unlock();const save=readSave('auto');if(save)restoreGameSave(save,'auto');});","document.getElementById('continue-button').addEventListener('click',()=>{sound.unlock();if(state.started){resumeGame();return;}const save=readSave('auto');if(save?.research?.playerConfigured)restoreGameSave(save,'auto');});",'continue handler')
# Separate resume button was removed from HTML.
g=g.replace("  document.getElementById('resume-button').addEventListener('click',resumeGame);\n",'')

# Random opportunities can still open on arrival without ever becoming the arrow-guided selected grant.
g=replace_regex(g,r"  function updateResearchNavigation\(\)\{.*?\n  \}",'''  function updateResearchNavigation(){
    if(pendingResearchTargetId){const pending=researchTargets().find(item=>item.id===pendingResearchTargetId);if(!pending){pendingResearchTargetId=null;pendingResearchArrival=null;}else if(pendingResearchArrival&&!research?.isBusy?.()){const remaining=Math.hypot(state.x-pendingResearchArrival.x,state.y-pendingResearchArrival.y);if(remaining<=RESEARCH_INTERACTION_KM){pendingResearchTargetId=null;pendingResearchArrival=null;state.commandActive=false;state.moving=false;research?.openTarget?.(pending.id,{distanceKm:0,atSite:true});}}}
    const target=selectedResearchTarget();if(!target){research?.updateNavigation?.(null);return;}const position=researchTargetWorld(target),distance=Math.hypot(position.x-state.x,position.y-state.y);research?.updateNavigation?.({id:target.id,distanceKm:distance,bearing:Math.atan2(position.x-state.x,position.y-state.y)*180/Math.PI});
  }''','research navigation arrival',re.S)
g=replace_once(g,"pendingResearchTargetId=target.id;setWorldDestination(destination.x,destination.y);","pendingResearchTargetId=target.id;pendingResearchArrival={id:target.id,x:destination.x,y:destination.y};setWorldDestination(destination.x,destination.y);",'pending arrival point')
# Manual navigation clears a pending popup destination.
g=replace_once(g,"function setDestination(screenX,screenY){pendingResearchTargetId=null;","function setDestination(screenX,screenY){pendingResearchTargetId=null;pendingResearchArrival=null;",'manual destination clear')

# Local shoreline escape: try nearby safe headings before giving up a click command.
shore_anchor="  function shorelineSlide(x,y,vx,vy,dt,targetX,targetY){"
idx=g.find(shore_anchor)
if idx<0: raise SystemExit('shorelineSlide start missing')
next_idx=g.find('\n  function ',idx+len(shore_anchor))
if next_idx<0: raise SystemExit('shorelineSlide end missing')
escape_func='''
  function localNavigationEscape(x,y,targetX,targetY,motionDt){
    const distance=Math.hypot(targetX-x,targetY-y),desired=Math.atan2(targetY-y,targetX-x),step=Math.max(1.2,Math.min(4.2,120*motionDt));let best=null,bestScore=-1e9;
    for(let i=0;i<32;i++){const offset=(i===0?0:Math.ceil(i/2)*(Math.PI/16)*(i%2?1:-1)),a=desired+offset,cx=x+Math.cos(a)*step,cy=y+Math.sin(a)*step,pos=unpolar(cx,cy),profile=iceNavigationProfileAt(cx,cy);if(pos.lat<MIN_LAT||isBlocked(cx,cy)||!profile.allowed)continue;const nextDistance=Math.hypot(targetX-cx,targetY-cy),progress=distance-nextDistance,clearance=coastDistance(cx,cy,22),score=progress*3+Math.min(18,clearance)*.22-Math.abs(offset)*.35;if(score>bestScore){bestScore=score;best={x:cx,y:cy};}}
    return best;
  }
'''
g=g[:next_idx]+escape_func+g[next_idx:]
block="""      if(nextPos.lat<MIN_LAT||isBlocked(nx,ny)||!nextProfile.allowed){if(commanded){state.tx=state.x;state.ty=state.y;state.portDestination=null;if(!nextProfile.allowed)showToast(nextProfile.reason||'SEA ICE · IMPASSABLE',2000);}state.moving=false;state.commandActive=false;state.ramming=false;state.targetOnLand=false;ui.speed.textContent='0.0 KN';}
"""
replacement="""      if(commanded&&(nextPos.lat<MIN_LAT||isBlocked(nx,ny)||!nextProfile.allowed)){const escape=localNavigationEscape(state.x,state.y,state.tx,state.ty,motionDt);if(escape){nx=escape.x;ny=escape.y;nextPos=unpolar(nx,ny);nextProfile=iceNavigationProfileAt(nx,ny,vessel);groundX=(nx-state.x)/Math.max(.001,motionDt);groundY=(ny-state.y)/Math.max(.001,motionDt);groundStep=Math.hypot(nx-state.x,ny-state.y);}}
      if(nextPos.lat<MIN_LAT||isBlocked(nx,ny)||!nextProfile.allowed){if(commanded){state.tx=state.x;state.ty=state.y;state.portDestination=null;if(!nextProfile.allowed)showToast(nextProfile.reason||'SEA ICE · IMPASSABLE',2000);}state.moving=false;state.commandActive=false;state.ramming=false;state.targetOnLand=false;ui.speed.textContent='0.0 KN';}
"""
g=replace_once(g,block,replacement,'shore escape fallback')
p.write_text(g)

# ---------- style.css ----------
p=Path('style.css'); css=p.read_text()
css+='''\n/* Expedition 22m: phone safe areas, requested control layout, and expandable navigation chart. */
.minimap-close,.minimap-nav-details{display:none}.minimap{cursor:pointer}.minimap.expanded{z-index:30!important;inset:max(10px,env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left))!important;width:auto!important;height:auto!important;padding:18px!important;border-radius:16px!important;background:rgba(4,31,49,.97)!important;display:grid!important;grid-template-rows:auto minmax(0,1fr) auto!important;justify-items:center!important;align-items:center!important}.minimap.expanded .minimap-heading{display:flex!important;width:min(760px,92vw);justify-content:space-between!important;padding:0 42px 10px 2px!important}.minimap.expanded .minimap-heading small{font-size:9px!important}.minimap.expanded .minimap-heading b{display:block!important;font-size:9px!important}.minimap.expanded #minimap{width:min(76vw,620px)!important;height:min(76vw,620px)!important;max-height:64vh!important;border-radius:12px!important;cursor:default!important}.minimap.expanded .minimap-close{display:grid;place-items:center;position:absolute;right:12px;top:8px;width:34px;height:34px;border:0;border-radius:50%;background:rgba(3,22,34,.78);color:#dff7fb;font-size:27px;z-index:2}.minimap.expanded .minimap-nav-details{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;width:min(760px,92vw);margin-top:10px}.minimap-nav-details span{padding:9px;border-radius:7px;background:rgba(30,79,96,.5);text-align:center}.minimap-nav-details small,.minimap-nav-details b{display:block}.minimap-nav-details small{color:#82adba;font-size:7px;letter-spacing:.08em}.minimap-nav-details b{margin-top:3px;color:#eafaff;font-size:9px}.nav-chart-open .compass{display:grid!important;z-index:31!important;left:max(24px,calc(env(safe-area-inset-left) + 20px))!important;right:auto!important;top:max(72px,calc(env(safe-area-inset-top) + 62px))!important}
@media (pointer:coarse) and (max-width:900px){.top-hud .game-menu-button{position:fixed!important;left:max(10px,calc(env(safe-area-inset-left) + 8px))!important;right:auto!important;top:auto!important;bottom:max(10px,calc(env(safe-area-inset-bottom) + 8px))!important;pointer-events:auto!important}.minimap:not(.expanded){left:max(10px,calc(env(safe-area-inset-left) + 8px))!important;right:auto!important;bottom:auto!important;width:86px!important;height:86px!important;padding:0!important;border:0!important;border-radius:50%!important;background:transparent!important;box-shadow:none!important;overflow:hidden!important}.minimap:not(.expanded)>div,.minimap:not(.expanded)>.minimap-close,.minimap:not(.expanded)>.minimap-nav-details{display:none!important}.minimap:not(.expanded) #minimap{width:86px!important;height:86px!important;border-radius:50%!important}.top-hud .vessel-button{pointer-events:auto!important}#arx-root #arx-mobile-toggle{right:max(10px,calc(env(safe-area-inset-right) + 8px))!important;bottom:max(10px,calc(env(safe-area-inset-bottom) + 8px))!important}.scale{display:none!important}}
@media (pointer:coarse) and (max-width:900px) and (orientation:portrait){.top-hud{top:calc(env(safe-area-inset-top) + 10px)!important}.minimap:not(.expanded){top:calc(env(safe-area-inset-top) + 12px)!important}#arx-root #arx-dev-toggle{left:50%!important;right:auto!important;top:calc(env(safe-area-inset-top) + 12px)!important;bottom:auto!important;transform:translateX(-50%)!important}.resource-warning{top:calc(env(safe-area-inset-top) + 70px)!important}}
@media (pointer:coarse) and (max-width:900px) and (orientation:landscape){.minimap:not(.expanded){top:max(8px,calc(env(safe-area-inset-top) + 5px))!important}#arx-root #arx-dev-toggle{left:50%!important;right:auto!important;top:max(8px,calc(env(safe-area-inset-top) + 5px))!important;bottom:auto!important;transform:translateX(-50%)!important}}
@media(max-width:620px){.minimap.expanded .minimap-nav-details{grid-template-columns:1fr 1fr}.minimap.expanded #minimap{width:min(90vw,430px)!important;height:min(90vw,430px)!important;max-height:55vh!important}}
'''
p.write_text(css)

# ---------- Boreal Crown SVG ----------
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 480">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#a9d9e5"/><stop offset="1" stop-color="#eaf5f6"/></linearGradient><linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#3e8aa5"/><stop offset="1" stop-color="#123e55"/></linearGradient></defs>
<rect width="1000" height="300" fill="url(#sky)"/><rect y="300" width="1000" height="180" fill="url(#sea)"/><path d="M120 322 L835 322 L915 360 L860 400 L210 400 L145 365 Z" fill="#153b50"/><path d="M180 272 L810 272 L850 322 L150 322 Z" fill="#f4f8f7" stroke="#315f70" stroke-width="7"/><path d="M270 184 H700 L790 272 H205 Z" fill="#f7faf9" stroke="#315f70" stroke-width="7"/><path d="M365 118 H610 L690 184 H310 Z" fill="#f7faf9" stroke="#315f70" stroke-width="7"/><path d="M445 76 H555 L592 118 H414 Z" fill="#edf6f5" stroke="#315f70" stroke-width="6"/><g fill="#58b4d2">''' + ''.join(f'<rect x="{235+i*62}" y="217" width="38" height="25" rx="5"/>' for i in range(9)) + ''.join(f'<rect x="{340+i*56}" y="145" width="34" height="22" rx="5"/>' for i in range(6)) + '''</g><rect x="489" y="28" width="18" height="50" fill="#315f70"/><path d="M507 37 L620 72" stroke="#315f70" stroke-width="7"/><circle cx="623" cy="73" r="7" fill="#f6d365"/><path d="M195 401 Q500 428 865 400" fill="none" stroke="#75c5d7" stroke-width="8" opacity=".7"/><text x="500" y="450" text-anchor="middle" font-family="system-ui,sans-serif" font-size="27" font-weight="700" fill="#eafaff">M/V BOREAL CROWN</text></svg>'''
Path('assets/vessels/boreal-crown.svg').write_text(svg)

print('ARS Aug 13 phone/navigation patch applied')
