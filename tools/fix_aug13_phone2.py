from pathlib import Path
import re
p=Path('tools/ars_aug13_phone2.py')
s=p.read_text()

def section(start,end,repl):
    global s
    a=s.index(start); b=s.index(end,a)
    s=s[:a]+repl+s[b:]

# Fix avatar sources and the spaced characterDraft declaration.
section("# Avatar labels disappear; user gets an editable name.\n","# Only report equipment capacities the hull actually has.\n",'''# Avatar labels disappear; user gets an editable name.
e=replace_regex(e,r"const PLAYER_AVATARS = \\[.*?\\n  \\];",''' + "'''" + '''const PLAYER_AVATARS = [
    {id:'chief-1',src:'assets/scientists/maya-chen.webp'},
    {id:'chief-2',src:'assets/scientists/noah-okafor.webp'},
    {id:'chief-3',src:'assets/scientists/amara-singh.webp'},
    {id:'chief-4',src:'assets/scientists/nuka-petersen.webp'},
    {id:'chief-5',src:'assets/scientists/hana-suzuki.webp'},
    {id:'chief-6',src:'assets/scientists/owen-clarke.webp'}
  ];''' + "'''" + ''','avatar definitions',re.S)
e=replace_once(e,"name:'You'","name:'Chief Scientist'",'initial player name')
e=replace_once(e,"let characterDraft = {avatar:PLAYER_AVATARS[0].id,specialty:'coastal-oceanography'};","let characterDraft = {avatar:PLAYER_AVATARS[0].id,specialty:'coastal-oceanography',name:''};",'character draft')

''')

# Replace the character setup/action patch with exact current-source guards.
section("# Full character setup block with name entry and image-only avatar choices.\n","# Prefer unique pictures on a single grant board; duplicates are only a fallback when necessary.\n",'''# Full character setup block with name entry and image-only avatar choices.
character_block=r''' + "'''" + '''  function openCharacterSetup() {
    if (state.playerConfigured) { callbacks.onCharacterReady?.(getVesselModifiers()); return false; }
    const modal=root.querySelector('#arx-character-modal'), starterIds=['coastal-oceanography','physical','coastal-ecology','sea-ice-physics','atmosphere','marine-mammals'], selected=PLAYER_AVATARS.find(item=>item.id===characterDraft.avatar)||PLAYER_AVATARS[0];
    modal.innerHTML=`<div class="arx-modal-card arx-character-card"><small>EXPEDITION SETUP</small><h2>Create your Chief Scientist</h2><p>Choose your portrait, enter your name, and select the specialty that will shape your first research opportunities.</p><label class="arx-character-name"><span>YOUR NAME</span><input data-arx-character-name maxlength="40" autocomplete="name" placeholder="Chief Scientist" value="${escapeHtml(characterDraft.name||'')}"></label><div class="arx-avatar-grid">${PLAYER_AVATARS.map((avatar,index)=>`<button class="${characterDraft.avatar===avatar.id?'selected':''}" data-arx-action="choose-avatar" data-id="${avatar.id}" aria-label="Portrait ${index+1}"><img src="${escapeHtml(avatar.src)}" alt="Portrait ${index+1}"></button>`).join('')}</div><label class="arx-specialty-select"><span>STARTING SPECIALIZATION</span><select data-arx-character-specialty>${starterIds.map(id=>`<option value="${id}" ${characterDraft.specialty===id?'selected':''}>${escapeHtml(specialtyById[id].name)}</option>`).join('')}</select><small>${escapeHtml(specialtyById[characterDraft.specialty]?.description||'')}</small></label><div class="arx-character-summary"><img src="${selected.src}" alt=""><div><b>${escapeHtml((characterDraft.name||'').trim()||'Chief Scientist')}</b><span>${escapeHtml(specialtyById[characterDraft.specialty]?.name||'Coastal Oceanographer')}</span><small>Graduate Student · Chief Scientist</small></div></div><button data-arx-action="confirm-character">BEGIN IN LONGYEARBYEN</button></div>`;
    modal.classList.add('open'); return true;
  }
  function confirmCharacter() {
    const modal=root.querySelector('#arx-character-modal'), select=modal.querySelector('[data-arx-character-specialty]'), input=modal.querySelector('[data-arx-character-name]');
    characterDraft.specialty=select?.value||characterDraft.specialty; characterDraft.name=(input?.value||characterDraft.name||'').trim().slice(0,40);
    const avatar=PLAYER_AVATARS.find(item=>item.id===characterDraft.avatar)||PLAYER_AVATARS[0], player=state.scientists.find(item=>item.isPlayer)||state.scientists[0], name=characterDraft.name||'Chief Scientist';
    Object.assign(player,{id:'player',name,role:'Chief Scientist',specialty:characterDraft.specialty,career:'grad',portrait:avatar.src,isPlayer:true,hiredAt:-1});
    state.playerConfigured=true; modal.classList.remove('open'); addLog(`${name} joined as Chief Scientist · ${specialtyById[player.specialty]?.name||player.specialty}.`); changed({port:false}); callbacks.onCharacterReady?.(getVesselModifiers());
  }
''' + "'''" + '''
e=replace_regex(e,r"  function openCharacterSetup\\(\\) \\{.*?\\n  function openNpcVessel",character_block+'  function openNpcVessel','character setup block',re.S)
e=replace_once(e,"else if (action==='choose-avatar') { characterDraft.specialty=root.querySelector('[data-arx-character-specialty]')?.value||characterDraft.specialty; characterDraft.avatar=id; openCharacterSetup(); }","else if (action==='choose-avatar') { characterDraft.specialty=root.querySelector('[data-arx-character-specialty]')?.value||characterDraft.specialty; characterDraft.name=root.querySelector('[data-arx-character-name]')?.value||characterDraft.name; characterDraft.avatar=id; openCharacterSetup(); }",'avatar handler')

''')

# Replace grant-board selection with a version matching the current compressed code.
section("# Prefer unique pictures on a single grant board; duplicates are only a fallback when necessary.\n","# Port tab viewport gets unobtrusive overflow chevrons.\n",'''# Prefer unique pictures on a single grant board; duplicates are only a fallback when necessary.
old="""    state.offers=[]; const specialtyCount=new Set(state.scientists.map(item=>item.specialty)).size,seniorBonus=hiredCareerCount('postdoc')+hiredCareerCount('professor')*2,offerLimit=Math.min(9,Math.max(3,2+specialtyCount+seniorBonus));
    for(const template of pool){if(state.offers.length>=offerLimit)break;const target=buildTarget(template,port,rng,'grant');if(target)state.offers.push(target);} if(!state.offers.length&&playerCareerLevel()<2){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback)state.offers.push(fallback);}
"""
new="""    state.offers=[]; const specialtyCount=new Set(state.scientists.map(item=>item.specialty)).size,seniorBonus=hiredCareerCount('postdoc')+hiredCareerCount('professor')*2,offerLimit=Math.min(9,Math.max(3,2+specialtyCount+seniorBonus)),builtOffers=[];
    for(const template of pool){const target=buildTarget(template,port,rng,'grant');if(target)builtOffers.push(target);} const usedPictures=new Set(),duplicatePictures=[];for(const target of builtOffers){const src=target.media?.src||'';if(src&&usedPictures.has(src)){duplicatePictures.push(target);continue;}state.offers.push(target);if(src)usedPictures.add(src);if(state.offers.length>=offerLimit)break;}if(state.offers.length<offerLimit)for(const target of duplicatePictures){state.offers.push(target);if(state.offers.length>=offerLimit)break;} if(!state.offers.length&&playerCareerLevel()<2){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback)state.offers.push(fallback);}
"""
e=replace_once(e,old,new,'unique grant images')

''')

# Ensure the obsolete vessel-to-port action is completely removed and zero helideck capacity is not printed.
needle='e=e.replace("${!inPort&&state.port?\'<button data-arx-action=\\"open-vessel-port\\">OPEN YOUR VESSEL TAB IN PORT</button>\':\'\'}","",1)\n'
if needle in s:
    s=s.replace(needle,needle+'''e=replace_once(e,"    else if (action==='open-vessel-port'&&state.port) { root.querySelector('#arx-vessel-modal').classList.remove('open'); activePortTab='vessel'; renderPort(); }\\n","",'vessel port action')
e=replace_once(e,"${slotSummary(ship,usage)} · Helidecks ${helideckUsage()}/${ship.helidecks}","${slotSummary(ship,usage)}${ship.helidecks?` · Helidecks ${helideckUsage()}/${ship.helidecks}`:''}",'vessel helideck capacity')
e=replace_once(e,"${slotSummary(ship,usage)} · helidecks ${helideckUsage()}/${ship.helidecks}.","${slotSummary(ship,usage)}${ship.helidecks?` · helidecks ${helideckUsage()}/${ship.helidecks}`:''}.",'store helideck capacity')
''')
else:
    raise SystemExit('vessel info patch insertion point missing')

# Correct the current one-line minimap and NPC renderer matchers.
section("# Special, tightly-trimmed passenger vessel map symbol with bow forward.\n","# Minimap follows the vessel and uses its actual rendered size instead of a hidden 120px minimum.\n",'''# Special, tightly-trimmed passenger vessel map symbol with bow forward.
old="""  function drawNpcIcon(npc){
    const cls=String(npc.classId||'').toLowerCase(),sprite=SPRITES.vessels[cls];ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
"""
new="""  function drawNpcIcon(npc){
    const cls=String(npc.classId||'').toLowerCase(),sprite=SPRITES.vessels[cls];ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
    if(npc.id==='mv-boreal-crown'){ctx.shadowColor='rgba(0,17,28,.38)';ctx.shadowBlur=4;ctx.fillStyle='#173c50';ctx.beginPath();ctx.moveTo(0,-23);ctx.lineTo(9,-13);ctx.lineTo(8,19);ctx.lineTo(-8,19);ctx.lineTo(-9,-13);ctx.closePath();ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='#eef8f8';ctx.beginPath();ctx.moveTo(0,-15);ctx.lineTo(6,-8);ctx.lineTo(6,11);ctx.lineTo(-6,11);ctx.lineTo(-6,-8);ctx.closePath();ctx.fill();ctx.fillStyle='#5cb1d0';ctx.fillRect(-5,-6,10,5);ctx.fillRect(-5,3,10,4);ctx.fillStyle='#f6d365';ctx.fillRect(-1,-19,2,7);ctx.strokeStyle='rgba(230,250,252,.85)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(-7,14);ctx.lineTo(7,14);ctx.stroke();ctx.restore();return;}
"""
g=replace_once(g,old,new,'Boreal map icon')

''')

section("# Minimap follows the vessel and uses its actual rendered size instead of a hidden 120px minimum.\n","# Add nav readouts at the end of drawMiniMap before context restore if marker exists.\n",'''# Minimap follows the vessel and uses its actual rendered size instead of a hidden 120px minimum.
g=replace_once(g,"  function miniMapGeometry(){const fullRadius=terrainLatitudeRadius(MIN_LAT),localRadius=520,t=Math.max(0,Math.min(1,(2.8-zoomLevel)/(2.8-.7))),ease=t*t*(3-2*t),worldRadius=localRadius+(fullRadius-localRadius)*ease,blend=Math.max(0,Math.min(1,(fullRadius-worldRadius)/(fullRadius-localRadius)));return{worldRadius,centerX:state.x*blend,centerY:state.y*blend};}","  function miniMapGeometry(){return{worldRadius:minimapExpanded?1100:520,centerX:state.x,centerY:state.y};}",'minimap geometry')
g=replace_once(g,"const size=Math.max(120,miniCanvas.clientWidth||148),","const measured=Math.round(miniCanvas.clientWidth||148),size=Math.max(minimapExpanded?260:64,measured);if(miniCanvas.width!==size||miniCanvas.height!==size){miniCanvas.width=size;miniCanvas.height=size;}const ",'minimap backing size')

''')

section("# Add nav readouts at the end of drawMiniMap before context restore if marker exists.\n","# Expanded mini map behaves like a modal and pauses the simulation.\n",'''# Add navigation readouts after the minimap drawing pass.
marker="    mini.fillStyle='#e84f4f';mini.strokeStyle='rgba(255,240,225,.9)';mini.lineWidth=.7;cityLabels.forEach(city=>{const w=polar(city.lat,city.lon),dot=project(w.x,w.y);if(Math.hypot(dot.x-c,dot.y-c)>radius+3)return;mini.beginPath();mini.arc(dot.x,dot.y,1.8,0,Math.PI*2);mini.fill();mini.stroke();});const p=project(state.x,state.y);mini.fillStyle='#f9d55d';mini.shadowColor='#fff3a4';mini.shadowBlur=7;mini.beginPath();mini.arc(p.x,p.y,3.7,0,Math.PI*2);mini.fill();mini.shadowBlur=0;mini.strokeStyle='#fff';mini.lineWidth=1;mini.stroke();const viewW=Math.min(radius*2,width/scale/worldRadius*radius),viewH=Math.min(radius*2,height/scale/worldRadius*radius);mini.strokeStyle='rgba(255,243,164,.68)';mini.lineWidth=.8;mini.strokeRect(p.x-viewW/2,p.y-viewH/2,viewW,viewH);mini.restore();mini.strokeStyle='rgba(218,247,252,.6)';mini.lineWidth=1;mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.stroke();\n"
readouts=marker+"    const currentPos=unpolar(state.x,state.y),ew=currentPos.lon<0?'W':'E',weather=currentWeather(),profile=iceNavigationProfileAt(state.x,state.y),course=state.commandActive?((Math.atan2(state.tx-state.x,state.ty-state.y)*180/Math.PI+360)%360):null;if(ui.miniLocation)ui.miniLocation.textContent=locationName(currentPos.lat,currentPos.lon);if(ui.miniPosition)ui.miniPosition.textContent=`${currentPos.lat.toFixed(2)}°N ${Math.abs(currentPos.lon).toFixed(2)}°${ew}`;if(ui.miniCourse)ui.miniCourse.textContent=course==null?'STOPPED':`${Math.round(course).toString().padStart(3,'0')}°`;if(ui.miniIce)ui.miniIce.textContent=iceStatusText(profile,state.ramming);if(ui.miniWeather)ui.miniWeather.textContent=weather.type==='clear'?'CLEAR':weather.label.toUpperCase();\n"
g=replace_once(g,marker,readouts,'minimap readouts')

''')

# Correct menu helper names and require an actually configured autosave before showing Continue.
s=s.replace("const validAuto=!!(auto?.research?.playerConfigured||auto?.research?.completed?.length||auto?.meta?.missions);","const validAuto=!!auto?.research?.playerConfigured;")
s=s.replace("saveSlotMarkup(slot,readSave(slot),false)","slotMarkup(slot,'load')").replace("saveSlotMarkup(slot,readSave(slot),true)","slotMarkup(slot,'save')")
s=s.replace("if(save?.research?.playerConfigured)restoreGameSave(save,'auto');","if(save)restoreGameSave(save,'auto');")

p.write_text(s)
print('corrected guarded phone patch script')
