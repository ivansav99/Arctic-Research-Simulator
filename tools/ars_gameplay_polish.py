from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


# ---------------- expedition.js ----------------
path = Path('expedition.js')
exp = path.read_text()

exp = replace_once(exp, "short:'GRAD'", "short:'Grad Student'", 'Grad Student career label')
exp = replace_once(exp, "const tier=['','GRAD','POSTDOC','PROFESSOR'][item.tier]", "const tier=['','Grad Student','POSTDOC','PROFESSOR'][item.tier]", 'Grad Student equipment label')
exp = replace_once(exp, "className:'LOCAL CLASS', price:0, berths:3", "className:'LOCAL CLASS', price:0, marketPrice:120000, berths:3", 'starter vessel market price')
exp = replace_once(exp, "papers:[], publicationCooldown:0, publishAttempts:0,", "papers:[], publicationCooldown:0, publishAttempts:0, lastPublicationRejected:false,", 'publication rejection state')

exp = replace_once(
    exp,
    "  function payroll() { return state.scientists.reduce((sum,item) => sum + (CAREERS[item.career]?.salary || 0), 0); }",
    """  function missionMinCrew(template) {
    const explicit=Number(template?.minCrew); if(Number.isFinite(explicit)&&explicit>0)return Math.max(1,Math.round(explicit));
    const level=templateCareerLevel(template),bounds={1:[1,3],2:[3,10],3:[10,20]}[level]||[1,3];
    const rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level).map(item=>Number(item.reward)||0).filter(value=>value>0);
    const low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low,reward=Math.max(low,Number(template?.reward)||low),t=high>low?clamp((reward-low)/(high-low),0,1):0;
    return Math.round(bounds[0]+(bounds[1]-bounds[0])*t);
  }
  function payroll() { return state.scientists.reduce((sum,item) => sum + (CAREERS[item.career]?.salary || 0), 0); }""",
    'minimum crew helper'
)

exp = replace_once(
    exp,
    """  function eligible(template, weather=null) {
    if (!hasSpecialty(template)) return false;
    if ((template.equipment || []).some(id => !equipmentOperational(id))) return false;
    if (template.weather && weather && template.weather !== weather.type) return false;
    return true;
  }""",
    """  function eligible(template, weather=null) {
    if (!hasSpecialty(template)) return false;
    if ((template.equipment || []).some(id => !equipmentOperational(id))) return false;
    if (state.scientists.length<missionMinCrew(template)) return false;
    if (template.weather && weather && template.weather !== weather.type) return false;
    return true;
  }""",
    'crew eligibility'
)

exp = replace_once(
    exp,
    """  function teamCouldDoWithEquipment(template) {
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&!eligible(template)&&(template.equipment||[]).some(id=>!equipmentOperational(id));
  }""",
    """  function teamCouldDoWithEquipment(template) {
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&!eligible(template)&&(template.equipment||[]).some(id=>!equipmentOperational(id));
  }
  function teamCouldDoWithMoreCrew(template) {
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&(template.equipment||[]).every(id=>equipmentOperational(id))&&state.scientists.length<missionMinCrew(template);
  }""",
    'crew aspirational opportunity helper'
)

exp = replace_once(
    exp,
    "equipment:[...(template.equipment || [])], consumables:[...(template.consumables || [])],",
    "equipment:[...(template.equipment || [])], consumables:[...(template.consumables || [])], minCrew:missionMinCrew(template),",
    'target min crew field'
)

exp = replace_once(
    exp,
    "const ready=weighted.filter(item=>eligible(item)), aspirational=weighted.filter(teamCouldDoWithEquipment), otherMissing=weighted.filter(item=>!eligible(item));",
    "const ready=weighted.filter(item=>eligible(item)), aspirational=weighted.filter(item=>teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item)), otherMissing=weighted.filter(item=>!eligible(item));",
    'crew aspirational pool'
)

exp = replace_once(
    exp,
    "const template=pool[Math.floor(rng()*pool.length)],target=buildTarget(template,payload.position,rng,'opportunity',{nearby:inIce,iceThickness}); if (!target) return null;\n    state.targets.push(target);",
    "const template=pool[Math.floor(rng()*pool.length)],target=buildTarget(template,payload.position,rng,'opportunity',{nearby:inIce,iceThickness}); if (!target) return null;\n    if(!state.targets.some(item=>item.selected))target.selected=true;\n    state.targets.push(target);",
    'auto select opportunity'
)

exp = replace_once(
    exp,
    """    const teamReady=hasSpecialty(target);
    rows.push({label:'Qualified science team',ready:teamReady,detail:target.anyScientist?'Any scientist aboard':target.specialties.map(id=>specialtyById[id]?.name||id).join(' / ')});""",
    """    const teamReady=hasSpecialty(target);
    rows.push({label:'Qualified science team',ready:teamReady,detail:target.anyScientist?'Any scientist aboard':target.specialties.map(id=>specialtyById[id]?.name||id).join(' / ')});
    const minCrew=target.minCrew||missionMinCrew(target);
    rows.push({label:'Minimum expedition team',ready:state.scientists.length>=minCrew,detail:`${state.scientists.length} aboard · ${minCrew} required`});""",
    'mission readiness crew row'
)

exp = replace_once(
    exp,
    "<span>+${item.data} data</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span>",
    "<span>+${item.data} data</span><span>${item.minCrew||missionMinCrew(item)} people minimum</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span>",
    'offer crew display'
)

exp = replace_once(
    exp,
    "const available=state.data, used=level.threshold, quality=averageQuality(), connected=equipmentOperational('starlink-terminal'), chance=publicationChance(level,available), accepted=!level.next||Math.random()<chance;\n    state.publishAttempts++; state.publicationCooldown=accepted?0:4*(connected?.75:1);",
    "const available=state.data, used=level.threshold, quality=averageQuality(), connected=equipmentOperational('starlink-terminal'), baseChance=publicationChance(level,available), guaranteed=state.papers.length===0||state.lastPublicationRejected===true, chance=guaranteed?1:baseChance, accepted=guaranteed||!level.next||Math.random()<chance;\n    state.publishAttempts++; state.lastPublicationRejected=!accepted; state.publicationCooldown=accepted?0:4*(connected?.75:1);",
    'guaranteed paper acceptance'
)

exp = replace_once(
    exp,
    "message:'Two published papers and 100 citations have earned postdoc status. You may now hire postdocs (one per 100 citations), purchase medium-duty science systems, commission a coastal-class research vessel, and receive much more sophisticated postdoc-level research programs.'",
    "message:'Congratulations, you finally earned your PhD degree! Two published papers and 100 citations have earned postdoc status. You may now hire postdocs (one per 100 citations), purchase medium-duty science systems, commission a coastal-class research vessel, relocate your expedition to ports around the Arctic, and receive much more sophisticated postdoc-level research programs.'",
    'postdoc promotion message'
)

exp = replace_once(
    exp,
    "  function vesselTradeInValue(ship=vessel()) {",
    "  function vesselPurchasePrice(ship) { return ship?.id==='fishing'?(ship.marketPrice||120000):(ship?.price||0); }\n  function vesselTradeInValue(ship=vessel()) {",
    'vessel market price helper'
)
exp = replace_once(exp, "credit=vesselTradeInValue(),due=Math.max(0,item.price-credit)", "credit=vesselTradeInValue(),listPrice=vesselPurchasePrice(item),due=Math.max(0,listPrice-credit)", 'vessel card list price')
exp = replace_once(exp, "(item.price?cash(item.price):'STARTER VESSEL')", "(listPrice?cash(listPrice):'STARTER VESSEL')", 'vessel badge market price')
exp = replace_once(exp, "List price ${cash(item.price)} · current trade credit ${cash(credit)}", "List price ${cash(listPrice)} · current vessel trade credit ${cash(credit)}", 'vessel detail market price')
exp = replace_once(exp, "credit=vesselTradeInValue(), due=Math.max(0,next.price-credit);", "credit=vesselTradeInValue(), listPrice=vesselPurchasePrice(next), due=Math.max(0,listPrice-credit);", 'vessel purchase due')
exp = replace_once(exp, "adjustMoney(credit-next.price);", "adjustMoney(credit-listPrice);", 'vessel purchase charge')

exp = replace_once(
    exp,
    """  function relocationPorts() { return (callbacks.getRelocationPorts?.()||[]).map(item=>({...item,id:item.id||slug(item.name)})); }
  function relocationPanelMarkup() {
    const ports=relocationPorts();
    if (playerCareerLevel()<2) return '<div class=\"arx-empty\"><b>POSTDOCTORAL CAREER REQUIRED</b><p>Relocating the expedition home port unlocks when the Chief Scientist reaches postdoctoral status.</p></div>';""",
    """  function relocationPorts() { return (callbacks.getRelocationPorts?.()||[]).map(item=>({...item,id:item.id||slug(item.name)})); }
  function emergencyRelocationAllowed() {
    if(playerCareerLevel()>=2||['icebreaker','nuclear'].includes(state.currentVessel))return false;
    const currentId=normalizedPortId(state.port),current=relocationPorts().find(item=>item.id===currentId);
    return !!current?.frozen;
  }
  function relocationUnlocked() { return playerCareerLevel()>=2||emergencyRelocationAllowed(); }
  function relocationPanelMarkup() {
    const ports=relocationPorts(),emergency=playerCareerLevel()<2&&emergencyRelocationAllowed();
    if (!relocationUnlocked()) return '<div class=\"arx-empty\"><b>POSTDOCTORAL CAREER REQUIRED</b><p>Relocating the expedition home port unlocks when the Chief Scientist reaches postdoctoral status.</p></div>';""",
    'emergency relocation helpers'
)
exp = replace_once(
    exp,
    "return `<p class=\"arx-help\">Move the entire expedition and vessel to another Arctic home port for ${cash(RELOCATION_COST)}. Frozen ports remain selectable aboard an icebreaker; other vessels must wait for the ice to clear.</p>",
    "return `<p class=\"arx-help\">${emergency?'EMERGENCY RELOCATION · Your current port is frozen in, so relocation is temporarily available before postdoctoral status. ':''}Move the entire expedition and vessel to another Arctic home port for ${cash(RELOCATION_COST)}. Frozen destination ports remain selectable only aboard an icebreaker.</p>",
    'emergency relocation explanation'
)
exp = replace_once(exp, "if (playerCareerLevel()<2) { toast('POSTDOCTORAL CAREER REQUIRED'); return; }", "if (!relocationUnlocked()) { toast('POSTDOCTORAL CAREER REQUIRED'); return; }", 'relocate gate')
exp = replace_once(exp, "${playerCareerLevel()>=2?tab('relocate','Relocate Home Port'):''}", "${relocationUnlocked()?tab('relocate','Relocate Home Port'):''}", 'relocate tab visibility')
exp = replace_once(exp, "${playerCareerLevel()>=2?`<section class=\"${panel('relocate')}\" data-arx-panel=\"relocate\"><h3>Relocate home port</h3>${relocationPanelMarkup()}</section>`:''}", "${relocationUnlocked()?`<section class=\"${panel('relocate')}\" data-arx-panel=\"relocate\"><h3>Relocate home port</h3>${relocationPanelMarkup()}</section>`:''}", 'relocate panel visibility')

exp = replace_once(
    exp,
    "<div class=\"arx-metrics\"><span><small>CITATIONS</small><b>${Math.floor(state.citations)}</b></span>",
    "<div class=\"arx-metrics\"><span><small>CITATIONS</small><b>${Math.floor(state.citations)}</b><em>${state.papers.length} PAPER${state.papers.length===1?'':'S'}</em></span>",
    'paper count metric'
)
exp = replace_once(
    exp,
    ".arx-metrics b{display:block;margin-top:3px;font-size:10px}",
    ".arx-metrics b{display:block;margin-top:3px;font-size:10px}.arx-metrics em{display:block;margin-top:2px;color:#91bac4;font-size:7px;font-style:normal;font-weight:800}",
    'paper count metric style'
)

old_nav = "<span class=\"${navOpportunity?'arx-question':'arx-arrow'}\" ${navOpportunity?'':`style=\"transform:rotate(${nav.bearingDeg}deg)\"`}>${navOpportunity?'?':'↑'}</span>"
new_nav = "<span class=\"arx-arrow\" style=\"transform:rotate(${nav.bearingDeg}deg)\">↑</span>"
exp = replace_once(exp, old_nav, new_nav, 'opportunity navigation arrow')
exp = replace_once(exp, "${Math.round(nav.distanceKm)} km${navOpportunity?'':` · ${Math.round(nav.bearingDeg)}°`}", "${Math.round(nav.distanceKm)} km · ${Math.round(nav.bearingDeg)}°", 'opportunity bearing text')

insert_before = "  function confirmDeparture(resources,proceed) {"
nav_helpers = """  function cancelOpportunity(id) {
    const target=state.targets.find(item=>item.id===id&&(item.kind==='opportunity'||item.kind==='weather-opportunity')); if(!target)return;
    state.targets=state.targets.filter(item=>item.id!==id);
    if(state.navigation?.id===id)state.navigation=null;
    if(state.lastTargetContext?.id===id)state.lastTargetContext=null;
    addLog(`Research opportunity declined: ${target.title}.`); root?.querySelector('#arx-target-modal')?.classList.remove('open'); toast('RESEARCH OPPORTUNITY CANCELLED'); changed({port:false});
  }
  function openNavigationPrompt(id=state.navigation?.id) {
    const target=state.targets.find(item=>item.id===id); if(!target)return false;
    const nav=state.navigation?.id===id?state.navigation:null,distance=nav?.distanceKm??Infinity,opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity';
    if(!opportunity){if(distance<=RESEARCH_INTERACTION_KM||target.anywhere)openTarget(id,{distanceKm:distance,atSite:true});else callbacks.onNavigate?.(target);return true;}
    const modal=root.querySelector('#arx-target-modal'),minCrew=target.minCrew||missionMinCrew(target);
    modal.innerHTML=`<div class=\"arx-modal-card arx-target-card\"><button class=\"arx-close\" data-arx-action=\"close-target\" aria-label=\"Close research opportunity\">×</button><small>DISCOVERED RESEARCH OPPORTUNITY</small><h2>${escapeHtml(target.title)}</h2><p>${escapeHtml(target.description)}</p><div class=\"arx-target-facts compact\"><span><small>DISTANCE</small><b>${Math.round(distance)} km</b></span><span><small>BEARING</small><b>${Math.round(nav?.bearingDeg||0)}°</b></span><span><small>MINIMUM TEAM</small><b>${minCrew} people</b></span></div><div class=\"arx-modal-actions\"><button class=\"ghost\" data-arx-action=\"cancel-opportunity\" data-id=\"${target.id}\">CANCEL OPPORTUNITY</button><button data-arx-action=\"navigate-opportunity\" data-id=\"${target.id}\">NAVIGATE TO OPPORTUNITY</button></div></div>`;
    modal.classList.add('open'); return true;
  }

"""
exp = replace_once(exp, insert_before, nav_helpers + insert_before, 'navigation prompt helpers')

exp = replace_once(
    exp,
    """    else if (action==='open-nav'&&state.navigation) {
      const target=state.targets.find(item=>item.id===state.navigation.id);
      if (state.navigation.distanceKm<=RESEARCH_INTERACTION_KM||target?.anywhere) openTarget(state.navigation.id,{distanceKm:state.navigation.distanceKm,atSite:true});
      else callbacks.onNavigate?.(target);
    } else if (action==='complete-target') completeTarget(id);""",
    """    else if (action==='open-nav'&&state.navigation) openNavigationPrompt();
    else if (action==='navigate-opportunity') { const target=state.targets.find(item=>item.id===id); root.querySelector('#arx-target-modal')?.classList.remove('open'); if(target)callbacks.onNavigate?.(target); }
    else if (action==='cancel-opportunity') cancelOpportunity(id);
    else if (action==='complete-target') completeTarget(id);""",
    'navigation prompt actions'
)

exp = replace_once(
    exp,
    "initialize,enterPort,leavePort,tickDays,getVesselModifiers,getMapTargets,selectTarget,updateNavigation,openTarget,",
    "initialize,enterPort,leavePort,tickDays,getVesselModifiers,getMapTargets,selectTarget,updateNavigation,openTarget,openNavigationPrompt,",
    'navigation prompt API'
)

# ---------------- game.js ----------------
path_game = Path('game.js')
game = path_game.read_text()

game = replace_once(game, "let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,startFlowPending=false,npcUpdateAccumulator=0;", "let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,startFlowPending=false,npcUpdateAccumulator=0,researchGuidanceHit=null;", 'research guidance hit state')

game = replace_once(
    game,
    "const ensure=()=>{if(ac)return ac;try{ac=new(window.AudioContext||window.webkitAudioContext)();const seconds=2,buffer=ac.createBuffer(1,ac.sampleRate*seconds,ac.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*(.45+.35*Math.sin(i/2400));waveSource=ac.createBufferSource();waveSource.buffer=buffer;waveSource.loop=true;const filter=ac.createBiquadFilter();filter.type='lowpass';filter.frequency.value=700;waveGain=ac.createGain();waveGain.gain.value=0;waveSource.connect(filter).connect(waveGain).connect(ac.destination);waveSource.start();}catch(e){}return ac;};",
    "const ensure=()=>{if(ac)return ac;try{ac=new(window.AudioContext||window.webkitAudioContext)();const seconds=5,buffer=ac.createBuffer(1,ac.sampleRate*seconds,ac.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*(.38+.28*Math.sin(i/6200));waveSource=ac.createBufferSource();waveSource.buffer=buffer;waveSource.loop=true;const filter=ac.createBiquadFilter();filter.type='lowpass';filter.frequency.value=430;waveGain=ac.createGain();waveGain.gain.value=0;waveSource.connect(filter).connect(waveGain).connect(ac.destination);waveSource.start();}catch(e){}return ac;};",
    'longer lower wave sound'
)
game = replace_once(game, "case'port':tone(92,1.7,.085,0,'sawtooth');tone(138,1.6,.05,.03,'sine');tone(86,1.4,.07,1.95,'sawtooth');tone(129,1.3,.045,1.98,'sine');tone(740,.22,.045,.42,'sine');tone(1120,.18,.035,.64,'sine');tone(820,.22,.04,1.02,'sine');tone(1260,.18,.032,1.24,'sine');break;", "case'port':tone(520,1.45,.07,0,'sine');tone(780,1.25,.05,.015,'sine');tone(1040,.95,.035,.025,'sine');tone(520,1.5,.065,1.15,'sine');tone(780,1.3,.045,1.165,'sine');tone(1040,1,.03,1.175,'sine');break;", 'marine bell sound')
game = replace_once(game, "case'ice':burst(.18,.09,900,4500);tone(150,.12,.04,0,'square');break;", "case'ice':burst(.48,.12,110,1750);burst(.24,.085,380,3200,.09);burst(.18,.065,700,4200,.23);tone(92,.38,.055,0,'sawtooth');tone(138,.22,.035,.12,'square');break;", 'heavy ice cracking sound')
game = replace_once(game, "state.moving&&!state.ramming?.055:0", "state.moving&&!state.ramming?.05:0", 'wave gain')

old_find_port = "function findPortApproach(city){const portIce=portIceInfo(city),center=polar(city.lat,city.lon);let best=null,bestDistance=Infinity;for(let radius=2;radius<=68;radius+=2)for(let i=0;i<48;i++){const a=i*Math.PI/24,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);if(pos.lat<MIN_LAT||isLand(x,y))continue;const profile=iceNavigationProfileAt(x,y);if(!profile.allowed)continue;const distance=Math.hypot(x-state.x,y-state.y);if(distance<bestDistance){best={x,y,shoreDistance:radius,ice:portIce};bestDistance=distance;}}return best;}"
new_find_port = "function findPortApproach(city){const portIce=portIceInfo(city),center=polar(city.lat,city.lon);let reachable=null,reachableScore=Infinity,fallback=null,fallbackDistance=Infinity;for(let radius=2;radius<=82;radius+=2)for(let i=0;i<72;i++){const a=i*Math.PI/36,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);if(pos.lat<MIN_LAT||isLand(x,y))continue;const profile=iceNavigationProfileAt(x,y);if(!profile.allowed)continue;const distance=Math.hypot(x-state.x,y-state.y);if(distance<fallbackDistance){fallback={x,y,shoreDistance:radius,ice:portIce};fallbackDistance=distance;}if(clearDisplacement(state.x,state.y,x,y)){const score=distance+radius*.28;if(score<reachableScore){reachable={x,y,shoreDistance:radius,ice:portIce};reachableScore=score;}}}return reachable||fallback;}"
game = replace_once(game, old_find_port, new_find_port, 'reachable port approach')

old_foreach = "function forEachWildlifeVisual(callback){for(const whale of whales)callback(whale,whale.species,'whale',whale);for(const school of fishSchools)callback(school,school.species,'fish',school);for(const animal of iceWildlife)callback(animal,animal.type==='bear'?'POLAR BEAR':animal.species,animal.type==='bear'?'mammal':animal.type==='walrus'?'walrus':'seal',iceAnimalWorld(animal));for(const fox of arcticFoxes)callback(fox,'ARCTIC FOX','mammal',foxWorld(fox));for(const animal of landWildlife)callback(animal,animal.species,'mammal',landAnimalWorld(animal));if(summerWildlifeVisible())for(const bird of summerBirds)callback(bird,bird.species,'bird',summerBirdWorld(bird));}"
new_foreach = "function forEachWildlifeVisual(callback){const emit=(entity,species,category,w)=>{const id=ensureWildlifeId(entity);if(wildlifeObservationAvailable(id))callback(entity,species,category,w);};for(const whale of whales)emit(whale,whale.species,'whale',whale);for(const school of fishSchools)emit(school,school.species,'fish',school);for(const animal of iceWildlife)emit(animal,animal.type==='bear'?'POLAR BEAR':animal.species,animal.type==='bear'?'mammal':animal.type==='walrus'?'walrus':'seal',iceAnimalWorld(animal));for(const fox of arcticFoxes)emit(fox,'ARCTIC FOX','mammal',foxWorld(fox));for(const animal of landWildlife)emit(animal,animal.species,'mammal',landAnimalWorld(animal));if(summerWildlifeVisible())for(const bird of summerBirds)emit(bird,bird.species,'bird',summerBirdWorld(bird));}"
game = replace_once(game, old_foreach, new_foreach, 'hide observed wildlife')

old_local = "function localWildlifeCount(radius=175){const near=(x,y)=>wildlifeClearOfPorts(x,y)&&Math.hypot(x-state.x,y-state.y)<radius;let total=0;for(const whale of whales)if(near(whale.x,whale.y))total++;for(const school of fishSchools)if(near(school.x,school.y))total++;for(const animal of iceWildlife){const w=iceAnimalWorld(animal);if(near(w.x,w.y))total++;}for(const animal of landWildlife){const w=landAnimalWorld(animal);if(near(w.x,w.y))total++;}for(const fox of arcticFoxes){const w=foxWorld(fox);if(near(w.x,w.y))total++;}if(summerWildlifeVisible())for(const bird of summerBirds){const w=summerBirdWorld(bird);if(near(w.x,w.y))total++;}return total;}"
new_local = "function localWildlifeCount(radius=175){const near=(item,x,y)=>wildlifeObservationAvailable(ensureWildlifeId(item))&&wildlifeClearOfPorts(x,y)&&Math.hypot(x-state.x,y-state.y)<radius;let total=0;for(const whale of whales)if(near(whale,whale.x,whale.y))total++;for(const school of fishSchools)if(near(school,school.x,school.y))total++;for(const animal of iceWildlife){const w=iceAnimalWorld(animal);if(near(animal,w.x,w.y))total++;}for(const animal of landWildlife){const w=landAnimalWorld(animal);if(near(animal,w.x,w.y))total++;}for(const fox of arcticFoxes){const w=foxWorld(fox);if(near(fox,w.x,w.y))total++;}if(summerWildlifeVisible())for(const bird of summerBirds){const w=summerBirdWorld(bird);if(near(bird,w.x,w.y))total++;}return total;}"
game = replace_once(game, old_local, new_local, 'visible wildlife spawn count')
game = replace_once(game, "resetDistantWildlifeFromPort(city);research?.enterPort?.(city);", "research?.enterPort?.(city);", 'do not recycle observed wildlife')

old_mammal = """      }else if(category==='mammal'){
        ctx.fillStyle='#d7e8df';ctx.beginPath();ctx.arc(0,0,6,0,Math.PI*2);ctx.fill();ctx.lineWidth=1.4;ctx.strokeStyle='rgba(239,252,252,.9)';ctx.stroke();ctx.fillStyle='#173f50';ctx.fillRect(-1,-7,2,14);
      }"""
new_mammal = """      }else if(category==='mammal'){
        const mammalName=String(species||'').toUpperCase();
        if(mammalName.includes('REINDEER')||mammalName.includes('CARIBOU')){
          drawMarkerBackdrop(16,markerSurfaceTone(w.x,w.y));ctx.fillStyle=mammalName.includes('SVALBARD')?'#a8835f':'#98714f';ctx.strokeStyle='rgba(239,252,252,.92)';ctx.lineWidth=1.25;ctx.beginPath();ctx.ellipse(-1,2,8.5,5,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(5,-1);ctx.lineTo(9,-7);ctx.stroke();ctx.beginPath();ctx.arc(10,-8,3.2,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(-6,5);ctx.lineTo(-7,11);ctx.moveTo(3,5);ctx.lineTo(4,11);ctx.stroke();ctx.strokeStyle='#ead9b9';ctx.lineWidth=1.1;ctx.beginPath();ctx.moveTo(9,-11);ctx.lineTo(7,-16);ctx.moveTo(9,-13);ctx.lineTo(5,-14);ctx.moveTo(11,-11);ctx.lineTo(13,-16);ctx.moveTo(12,-13);ctx.lineTo(16,-14);ctx.stroke();
        }else{ctx.fillStyle='#d7e8df';ctx.beginPath();ctx.arc(0,0,6,0,Math.PI*2);ctx.fill();ctx.lineWidth=1.4;ctx.strokeStyle='rgba(239,252,252,.9)';ctx.stroke();ctx.fillStyle='#173f50';ctx.fillRect(-1,-7,2,14);}
      }"""
game = replace_once(game, old_mammal, new_mammal, 'reindeer map icon')

old_rings = "function drawWildlifeObservationRings(){const pulse=.5+.5*Math.sin(performance.now()/420),weather=currentWeather(),lightLevel=seasonalBrightness();ctx.save();forEachWildlifeVisual((entity,species,category,w)=>{const id=ensureWildlifeId(entity);if(!wildlifeObservationAvailable(id)||!wildlifeClearOfPorts(w.x,w.y))return;const fog=wildlifeFogFactor(w.x,w.y,weather);if(fog<=.03)return;const ice=category==='fish'&&iceTypeAt(w.x,w.y);if(category==='fish'&&(ice==='packed'||ice==='cracked'||ice==='fast'||isLand(w.x,w.y)))return;const p=worldToScreen(w.x,w.y);if(p.x<-45||p.x>width+45||p.y<70||p.y>height+45)return;const radius=(category==='fish'?23:19)+pulse*2.5,alpha=(.13+pulse*.09)*lightLevel*fog;ctx.globalAlpha=1;ctx.strokeStyle=`rgba(255,225,94,${alpha})`;ctx.shadowColor=`rgba(255,226,94,${alpha*.7})`;ctx.shadowBlur=(2+pulse*2)*lightLevel*fog;ctx.lineWidth=1.15;ctx.beginPath();ctx.arc(p.x,p.y,radius,0,Math.PI*2);ctx.stroke();});ctx.restore();}"
new_rings = "function drawWildlifeObservationRings(){const pulse=.5+.5*Math.sin(performance.now()/420),weather=currentWeather(),lightLevel=seasonalBrightness(),daylight=clamp((lightLevel-.08)/.92,0,1);ctx.save();forEachWildlifeVisual((entity,species,category,w)=>{if(!wildlifeClearOfPorts(w.x,w.y))return;const fog=wildlifeFogFactor(w.x,w.y,weather);if(fog<=.03)return;const ice=category==='fish'&&iceTypeAt(w.x,w.y);if(category==='fish'&&(ice==='packed'||ice==='cracked'||ice==='fast'||isLand(w.x,w.y)))return;const p=worldToScreen(w.x,w.y);if(p.x<-45||p.x>width+45||p.y<70||p.y>height+45)return;const radius=(category==='fish'?23:19)+pulse*2.5,alpha=(.12+daylight*.48+pulse*(.05+daylight*.08))*fog;ctx.globalAlpha=1;ctx.strokeStyle=`rgba(255,225,94,${alpha})`;ctx.shadowColor=`rgba(255,226,94,${Math.min(.85,alpha*.9)})`;ctx.shadowBlur=(3+daylight*11+pulse*3)*fog;ctx.lineWidth=1.25+daylight*.9;ctx.beginPath();ctx.arc(p.x,p.y,radius,0,Math.PI*2);ctx.stroke();});ctx.restore();}"
game = replace_once(game, old_rings, new_rings, 'seasonal wildlife ring brightness')

old_guidance = "function drawResearchGuidance(){const target=selectedResearchTarget();if(!target||target.kind==='opportunity'||target.kind==='weather-opportunity')return;const item=researchTargetWorld(target),p=item.p;if(p.x>35&&p.x<width-35&&p.y>95&&p.y<height-35)return;const cx=width/2,cy=height/2,dx=p.x-cx,dy=p.y-cy,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length,edge=Math.min(width*.38,height*.36),x=cx+ux*edge,y=cy+uy*edge,a=Math.atan2(uy,ux);ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.fillStyle='rgba(246,211,101,.96)';ctx.strokeStyle='rgba(5,34,48,.9)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(14,0);ctx.lineTo(-8,-8);ctx.lineTo(-4,0);ctx.lineTo(-8,8);ctx.closePath();ctx.fill();ctx.stroke();ctx.rotate(-a);ctx.font='800 9px system-ui';ctx.textAlign='center';ctx.strokeStyle='rgba(5,34,48,.95)';ctx.lineWidth=3;ctx.strokeText(`${Math.round(item.distance)} KM`,0,24);ctx.fillStyle='#fff3aa';ctx.fillText(`${Math.round(item.distance)} KM`,0,24);ctx.restore();}"
new_guidance = "function drawResearchGuidance(){researchGuidanceHit=null;const target=selectedResearchTarget();if(!target)return;const item=researchTargetWorld(target),p=item.p;if(p.x>35&&p.x<width-35&&p.y>95&&p.y<height-35)return;const opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity',cx=width/2,cy=height/2,dx=p.x-cx,dy=p.y-cy,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length,edge=Math.min(width*.38,height*.36),x=cx+ux*edge,y=cy+uy*edge,a=Math.atan2(uy,ux);researchGuidanceHit={x,y,r:30,targetId:target.id};ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.fillStyle=opportunity?'rgba(142,240,207,.97)':'rgba(246,211,101,.96)';ctx.strokeStyle='rgba(5,34,48,.9)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(14,0);ctx.lineTo(-8,-8);ctx.lineTo(-4,0);ctx.lineTo(-8,8);ctx.closePath();ctx.fill();ctx.stroke();ctx.rotate(-a);ctx.font='800 9px system-ui';ctx.textAlign='center';ctx.strokeStyle='rgba(5,34,48,.95)';ctx.lineWidth=3;ctx.strokeText(`${Math.round(item.distance)} KM`,0,24);ctx.fillStyle=opportunity?'#b9f7df':'#fff3aa';ctx.fillText(`${Math.round(item.distance)} KM`,0,24);ctx.restore();}"
game = replace_once(game, old_guidance, new_guidance, 'research opportunity guidance arrow')
game = replace_once(game, "  function navigateToResearchTarget(target){", "  function researchGuidanceAt(x,y){return researchGuidanceHit&&Math.hypot(x-researchGuidanceHit.x,y-researchGuidanceHit.y)<=researchGuidanceHit.r?researchGuidanceHit:null;}\n  function navigateToResearchTarget(target){", 'guidance hit helper')

game = replace_once(
    game,
    "function handleMapPointer(clientX,clientY){const portItem=nearbyCityAt(clientX,clientY);",
    "function handleMapPointer(clientX,clientY){const guidance=researchGuidanceAt(clientX,clientY);if(guidance){research?.openNavigationPrompt?.(guidance.targetId);return;}const portItem=nearbyCityAt(clientX,clientY);",
    'clickable guidance arrow'
)
game = replace_once(game, "canvas.style.cursor=wildlifeAtScreenPoint(e.clientX,e.clientY)||nearbyNpcVesselAt(e.clientX,e.clientY)||nearbyResearchTargetAt(e.clientX,e.clientY)||nearbyCityAt(e.clientX,e.clientY)?'pointer':'crosshair';", "canvas.style.cursor=researchGuidanceAt(e.clientX,e.clientY)||wildlifeAtScreenPoint(e.clientX,e.clientY)||nearbyNpcVesselAt(e.clientX,e.clientY)||nearbyResearchTargetAt(e.clientX,e.clientY)||nearbyCityAt(e.clientX,e.clientY)?'pointer':'crosshair';", 'guidance pointer cursor')

game = replace_once(game, "endGame('OUT OF FOOD','The expedition has exhausted its provisions. Return to port before supplies run out.');", "endGame('OUT OF FOOD','Oh, no! Your expedition failed because you ran out of food! Restart from last known port.');", 'dramatic food failure')
game = replace_once(game, "endGame('OUT OF FUEL','The vessel is stranded and the expedition cannot continue. Plan a shorter route between ports.');", "endGame('OUT OF FUEL','Oh, no! Your expedition failed because you ran out of fuel! The ship is dead in the water and the crew is getting cold. Restart from last known port.');", 'dramatic fuel failure')

old_end = "function endGame(title,message){if(state.gameOver)return;state.gameOver=true;state.moving=false;state.commandActive=false;state.ramming=false;state.tx=state.x;state.ty=state.y;research?.leavePort?.();ui.gameOverTitle.textContent=title;ui.gameOverMessage.textContent=message;ui.gameOver.classList.remove('hidden');ui.resourceWarning?.classList.remove('show');sound.play('paper-rejected');}"
new_end = "function endGame(title,message){if(state.gameOver)return;state.gameOver=true;state.moving=false;state.commandActive=false;state.ramming=false;state.tx=state.x;state.ty=state.y;research?.leavePort?.();ui.gameOverTitle.textContent=title;ui.gameOverMessage.textContent=message;let image=ui.gameOver.querySelector('.failure-scientist');if(!image){image=document.createElement('img');image.className='failure-scientist';image.style.cssText='display:block;width:92px;height:92px;margin:12px auto;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,.55);box-shadow:0 8px 24px rgba(0,0,0,.32)';ui.gameOver.insertBefore(image,ui.gameOverMessage);}const chief=research?.getState?.()?.scientists?.find(item=>item.isPlayer)||research?.getState?.()?.scientists?.[0];image.src=chief?.portrait||'assets/scientists/maya-chen.webp';image.alt=title==='OUT OF FOOD'?'Hungry Chief Scientist':'Cold Chief Scientist';image.style.filter=title==='OUT OF FOOD'?'sepia(.35) saturate(.7) brightness(.78)':'grayscale(.35) hue-rotate(145deg) saturate(.75) brightness(.8)';ui.gameOver.classList.remove('hidden');ui.resourceWarning?.classList.remove('show');sound.play('paper-rejected');}"
game = replace_once(game, old_end, new_end, 'failure scientist image')

# Cache bust the changed scripts.
index = Path('index.html')
html = index.read_text()
html = replace_once(html, 'expedition.js?v=expedition-22f-funding', 'expedition.js?v=expedition-22g-gameplay', 'expedition cache bust')
html = replace_once(html, 'game.js?v=expedition-22f-icedrift', 'game.js?v=expedition-22g-gameplay', 'game cache bust')

# Write only after every deterministic replacement has succeeded.
Path('expedition.js').write_text(exp)
Path('game.js').write_text(game)
Path('index.html').write_text(html)
