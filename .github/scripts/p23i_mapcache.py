from pathlib import Path
import re

GAME=Path('game.js')
EXP=Path('expedition.js')
STYLE=Path('style.css')
INDEX=Path('index.html')
game=GAME.read_text()
exp=EXP.read_text()
style=STYLE.read_text()
index=INDEX.read_text()

def once(text, old, new, label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 occurrence, got {n}')
    return text.replace(old,new,1)

# ---------------------------------------------------------------------------
# GAME: cached moving world instead of rebuilding the expensive chart every frame
# ---------------------------------------------------------------------------
game=once(game,
"  const canvas=document.getElementById('map'),ctx=canvas.getContext('2d');\n",
"  const canvas=document.getElementById('map'),ctx=canvas.getContext('2d');\n  const worldCacheCanvas=document.createElement('canvas'),worldCacheCtx=worldCacheCanvas.getContext('2d');\n  let worldCacheValid=false,worldCacheX=0,worldCacheY=0,worldCacheScale=0,worldCacheAt=0;\n  const invalidateWorldCache=()=>{worldCacheValid=false;};\n",
'world cache declarations')

game=once(game,
"image.onload=()=>{tile.image=image;tile.ready=true;tile.failed=false;tile.year=year;if(cors)buildTerrainTileMask(tile);};",
"image.onload=()=>{tile.image=image;tile.ready=true;tile.failed=false;tile.year=year;if(cors)buildTerrainTileMask(tile);invalidateWorldCache();};",
'terrain tile cache invalidation')

old_resize="function resize(){dpr=Math.min(devicePixelRatio||1,IS_COARSE_POINTER?1.35:2);width=innerWidth;height=innerHeight;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);lightCanvas.width=Math.round(width*dpr);lightCanvas.height=Math.round(height*dpr);light.setTransform(dpr,0,0,dpr,0,0);oceanCanvas.width=Math.max(1,Math.round(width));oceanCanvas.height=Math.max(1,Math.round(height));oceanPattern=null;baseScale=Math.max(3.4,Math.min(5.2,Math.min(width,height)/145));scale=baseScale*zoomLevel;const s=miniCanvas.clientWidth;miniCanvas.width=Math.round(s*dpr);miniCanvas.height=Math.round(s*dpr);mini.setTransform(dpr,0,0,dpr,0,0);}"
new_resize="function resize(){dpr=Math.min(devicePixelRatio||1,IS_COARSE_POINTER?1.25:2);width=innerWidth;height=innerHeight;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);worldCacheCanvas.width=canvas.width;worldCacheCanvas.height=canvas.height;worldCacheCtx.setTransform(1,0,0,1,0,0);invalidateWorldCache();lightCanvas.width=Math.round(width*dpr);lightCanvas.height=Math.round(height*dpr);light.setTransform(dpr,0,0,dpr,0,0);oceanCanvas.width=Math.max(1,Math.round(width));oceanCanvas.height=Math.max(1,Math.round(height));oceanPattern=null;baseScale=Math.max(3.4,Math.min(5.2,Math.min(width,height)/145));scale=baseScale*zoomLevel;const s=miniCanvas.clientWidth;miniCanvas.width=Math.round(s*dpr);miniCanvas.height=Math.round(s*dpr);mini.setTransform(dpr,0,0,dpr,0,0);}"
game=once(game,old_resize,new_resize,'resize cache setup')

cache_fn=r'''
  function captureWorldCache(now){
    if(worldCacheCanvas.width!==canvas.width||worldCacheCanvas.height!==canvas.height){worldCacheCanvas.width=canvas.width;worldCacheCanvas.height=canvas.height;}
    worldCacheCtx.setTransform(1,0,0,1,0,0);worldCacheCtx.clearRect(0,0,worldCacheCanvas.width,worldCacheCanvas.height);worldCacheCtx.drawImage(canvas,0,0);
    worldCacheX=state.x;worldCacheY=state.y;worldCacheScale=scale;worldCacheAt=now;worldCacheValid=true;
  }
  function drawWorldCached(now){
    const scaleMatch=worldCacheValid&&Math.abs(worldCacheScale-scale)<.0001,dx=scaleMatch?(worldCacheX-state.x)*scale:0,dy=scaleMatch?(worldCacheY-state.y)*scale:0;
    const refreshMs=IS_COARSE_POINTER?125:85,shiftLimit=IS_COARSE_POINTER?64:52;
    if(!scaleMatch||!worldCacheValid||now-worldCacheAt>=refreshMs||Math.abs(dx)>shiftLimit||Math.abs(dy)>shiftLimit){drawMap();captureWorldCache(now);return;}
    ctx.save();ctx.fillStyle='#3f91aa';ctx.fillRect(0,0,width,height);try{drawTerrainRaster(ctx,worldToScreen,.96);}catch(error){}
    ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(worldCacheCanvas,Math.round(dx*dpr),Math.round(dy*dpr));ctx.restore();
  }
'''
game=once(game,"\n\n  function miniMapGeometry()",cache_fn+"\n  function miniMapGeometry()",'insert map cache renderer')

# Track: long dark-gray dashes, no glow.
track_pat=re.compile(r"  function drawVesselTrack\(\)\{.*?\n  \}",re.S)
track_new="""  function drawVesselTrack(){
    const track=state.track;if(!Array.isArray(track)||!track.length)return;
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.setLineDash([18,11]);ctx.strokeStyle='rgba(48,55,58,.88)';ctx.lineWidth=2.35;ctx.beginPath();
    let started=false;for(const point of track){const p=worldToScreen(point.x,point.y);if(!started){ctx.moveTo(p.x,p.y);started=true;}else ctx.lineTo(p.x,p.y);}const live=worldToScreen(state.x,state.y);if(started)ctx.lineTo(live.x,live.y);ctx.stroke();ctx.setLineDash([]);ctx.restore();
  }"""
game,n=track_pat.subn(track_new,game,count=1)
if n!=1: raise SystemExit('track renderer replacement failed')

# Drop foam wake for now. Icebreaker broken-ice floes remain a separate ice effect.
game=game.replace("drawIceThicknessAndCracks();drawMarginalFloes();drawVesselTrack();drawWakeTrail();drawWakeFloes();","drawIceThicknessAndCracks();drawMarginalFloes();drawVesselTrack();drawWakeFloes();")
game=game.replace("if(commanded&&!state.ramming&&groundStep>.05)appendWakeSegment(fromX,fromY,state.x,state.y);appendVesselTrack();","appendVesselTrack();")

# Remove halo/ring around player ship only.
game=game.replace("    const x=width/2,y=height/2,item=vesselModifiers(),sprite=vesselSpriteFor(item),size=vesselSpriteMetrics(item),tone=markerSurfaceTone(state.x,state.y);\n", "    const x=width/2,y=height/2,item=vesselModifiers(),sprite=vesselSpriteFor(item),size=vesselSpriteMetrics(item);\n",1)
game=game.replace("    drawMarkerBackdrop(size.r,tone);\n    ctx.shadowColor='rgba(0,25,40,.32)';", "    ctx.shadowColor='rgba(0,25,40,.32)';",1)

# Start the campaign at the closest actual water berth beside Longyearbyen.
old_begin="function beginExpedition(){if(state.started)return;startFlowPending=false;state.started=true;menuOpen=false;ui.welcome.classList.add('hidden');if(currentPortCity)enterPort(currentPortCity);analytics.track('game_started');scheduleAutosave(800);}"
new_begin="function beginExpedition(){if(state.started)return;startFlowPending=false;state.started=true;menuOpen=false;ui.welcome.classList.add('hidden');if(currentPortCity){const berth=findPortTeleportPosition(currentPortCity)||findPortApproach(currentPortCity);if(berth){state.x=berth.x;state.y=berth.y;state.tx=berth.x;state.ty=berth.y;state.track=[{x:berth.x,y:berth.y}];invalidateWorldCache();}enterPort(currentPortCity,{immediate:true});}analytics.track('game_started');scheduleAutosave(800);}"
game=once(game,old_begin,new_begin,'initial port berth')

# Port UI opens before checkpoint serialization/analytics, and the arrival pause is tiny.
finish_pat=re.compile(r"  function finishPortEntry\(city\)\{.*?\n  function enterPort\(city,\{immediate=false\}=\{\}\)\{",re.S)
m=finish_pat.search(game)
if not m: raise SystemExit('finishPortEntry block not found')
new_finish="""  function finishPortEntry(city){clearTimeout(pendingPortEntryTimer);pendingPortEntryTimer=0;pendingPortEntryCity=null;if(!city||state.dockedPort!==city.name||currentPortCity!==city)return;state.track=[{x:state.x,y:state.y}];invalidateWorldCache();research?.enterPort?.(city,{resources:{fuel:state.fuel,food:state.food},suppressPortSound:true});showToast(`PORT CALL — ${city.name} · SERVICES & RESEARCH GRANTS OPEN`,1800);setTimeout(()=>{if(state.dockedPort!==city.name||currentPortCity!==city)return;saveCheckpoint(city);saveGame('auto','port');analytics.track('port_entered',{port_name:city.name||'',port_country:city.countryCode||''});},0);}
  function enterPort(city,{immediate=false}={}){"""
game=game[:m.start()]+new_finish+game[m.end():]
game=game.replace("pendingPortEntryTimer=setTimeout(()=>{if(state.dockedPort===city.name&&currentPortCity===city)finishPortEntry(city);},780);","pendingPortEntryTimer=setTimeout(()=>{if(state.dockedPort===city.name&&currentPortCity===city)finishPortEntry(city);},140);",1)

# Wildlife: hide clicked individual immediately and force a fresh cached world.
game=once(game,"if(opened){wildlifeEncounterClock=1;return;}","if(opened){observedWildlifeFallback.add(animal.individualId);wildlifeEncounterClock=1;invalidateWorldCache();return;}",'wildlife immediate removal')

# Low-resource state lives under the gauges; no giant transient toast.
game=game.replace("    if(state.started&&!previousFuel&&resourceAlertState.fuel)showToast('LOW FUEL · LESS THAN 20% REMAINING · RETURN TO PORT',3600);\n","")
game=game.replace("    if(state.started&&!previousFood&&resourceAlertState.food){showToast('LOW FOOD · LESS THAN 20% REMAINING',3600);research?.maybeHelicopterFoodReminder?.();}\n","    if(state.started&&!previousFood&&resourceAlertState.food)research?.maybeHelicopterFoodReminder?.();\n")

# Make random opportunities arrive soon enough to be obvious, and auto-open their card.
game=game.replace("opportunityEnv.fjord?.38:opportunityEnv.coastal?.55:.85;","opportunityEnv.fjord?.24:opportunityEnv.coastal?.32:.45;",1)
old_wrap="if(research?.maybeSpawnOpportunity){const spawnOpportunity=research.maybeSpawnOpportunity.bind(research);research.maybeSpawnOpportunity=payload=>spawnOpportunity({...researchEnvironment(payload?.weather),...payload});}"
new_wrap="if(research?.maybeSpawnOpportunity){const spawnOpportunity=research.maybeSpawnOpportunity.bind(research);research.maybeSpawnOpportunity=payload=>{const target=spawnOpportunity({...researchEnvironment(payload?.weather),...payload});if(target?.id)setTimeout(()=>{if(!currentPortCity)research?.openNavigationPrompt?.(target.id);},0);return target;};}"
game=once(game,old_wrap,new_wrap,'opportunity popup wrapper')

# Throttle expensive wildlife motion math; visual movement is supplied by the moving world cache.
game=game.replace("wildlifeEncounterClock=0,wildlifeEncounterSerial=0;","wildlifeEncounterClock=0,wildlifeEncounterSerial=0,wildlifeMotionAccumulator=0;",1)
old_updates="updateWakeFloes(dt/zoomLevel);updateWakeTrail(dt/zoomLevel);updateWildlifeEncounters(dt);updateFishSchools(dt/zoomLevel);updateWildlife(dt/zoomLevel);updateNpcVessels(dt/zoomLevel);"
new_updates="updateWakeFloes(dt/zoomLevel);updateWildlifeEncounters(dt);wildlifeMotionAccumulator+=dt/zoomLevel;if(wildlifeMotionAccumulator>=.12){const wildlifeStep=Math.min(.25,wildlifeMotionAccumulator);wildlifeMotionAccumulator=0;updateFishSchools(wildlifeStep);updateWildlife(wildlifeStep);}updateNpcVessels(dt/zoomLevel);"
game=once(game,old_updates,new_updates,'wildlife throttling')

# Use cached world in the render pipeline.
game=once(game,"if(!paused&&renderDue){lastRender=now;drawMap();drawResearchTargets();","if(!paused&&renderDue){lastRender=now;drawWorldCached(now);drawResearchTargets();",'render cached world')

# ---------------------------------------------------------------------------
# EXPEDITION: immediate vessel tab, lazy port work, guaranteed grants, rich wildlife
# ---------------------------------------------------------------------------
enter_pat=re.compile(r"  function enterPort\(port,options=\{\}\) \{.*?\n  function closePort\(\)",re.S)
m=enter_pat.search(exp)
if not m: raise SystemExit('expedition enterPort block not found')
new_enter="""  function enterPort(port,options={}) {
    const incomingId=port.id||slug(port.name),previousPortId=state.lastPortId;
    state.port={name:port.name,lat:port.lat,lon:port.lon,id:incomingId,country:port.country||null,countryCode:port.countryCode||null};
    const differentPort=!!previousPortId&&previousPortId!==incomingId;
    if(!options.resume){state.lastPortId=incomingId;state.portVisits++;activePortTab='vessel';portScrollTop=0;portTabsScrollLeft=0;openStoreDetail=null;state.droppedGrantTemplates=[];state.bridgeSupportNotice=null;state.candidates=[];state.offers=[];state.grantOfferCycle=null;}
    if(!options.suppressPortSound)callbacks.onSound?.('port');
    renderSidebar();renderPort();
    const visitAtOpen=state.portVisits;
    setTimeout(()=>{
      if(!state.port||normalizedPortId(state.port)!==incomingId||state.portVisits!==visitAtOpen)return;
      if(!options.resume){
        const interrupted=state.targets.filter(target=>target.stations?.some(station=>station.status==='completed')&&target.stations.some(station=>station.status!=='completed'));
        for(const target of interrupted){target.stationIndex=0;target.stations.forEach(station=>station.status='pending');target.lat=target.stations[0].lat;target.lon=target.stations[0].lon;target.selected=false;addLog(`${target.shortTitle||target.title} section was interrupted by a port call and reset to station 1.`);}
        generateCandidates(state.port);
        const resources=callbacks.getResources?.()||{fuel:100,food:100},quote=resupplyAllQuote(resources,vessel());
        if(quote>0&&state.money<quote){const support=fullResupplyCost(vessel())*2;adjustMoney(support);state.bridgeSupportNotice=`Cash reserves could not cover one full resupply. Your home university extended ${cash(support)} in emergency bridge support — enough for two full resupplies of this vessel.`;addLog(`Home university bridge support received · ${cash(support)}.`);toast(`UNIVERSITY BRIDGE SUPPORT · +${cash(support)}`);}
        const readyAt=state.grantMarketReady?.[incomingId]||0;if(differentPort||state.elapsedDays>=readyAt)state.grantMarketReady[incomingId]=state.elapsedDays+3.5;
      }else if(!state.candidates.length)generateCandidates(state.port);
      renderSidebar();if(portOpen)renderPort();if(!state.offers.length)scheduleGrantRefresh(10);
    },18);
  }
  function closePort()"""
exp=exp[:m.start()]+new_enter+exp[m.end():]

# Grant board must never remain empty; and loading the grants tab triggers generation.
exp=exp.replace("if(fallback)state.offers=[fallback];","if(fallback){giveGrantUniqueMedia(fallback,new Set(),rng);state.offers=[fallback];}",1)
old_tabs="    renderPort();\n  }\n\n  function ensureUI()"
new_tabs="    renderPort();if(activePortTab==='contracts'&&!state.offers.length)scheduleGrantRefresh(0);if(activePortTab==='crew'&&!state.candidates.length){setTimeout(()=>{if(state.port){generateCandidates(state.port);if(portOpen&&activePortTab==='crew')renderPort();}},0);}\n  }\n\n  function ensureUI()"
exp=once(exp,old_tabs,new_tabs,'lazy tab generation')

# Rich wildlife modal for all labels: aliases/fuzzy display-name match, never fall back to a one-line toast.
old_wild="""  function openWildlife(species,context={}) {
    const key=String(species).replace(/ SCHOOL$/,'').toUpperCase(), item=catalog[key];
    if (!item) { toast(`FIELD OBSERVATION · ${key}`); return false; }
"""
new_wild="""  function openWildlife(species,context={}) {
    const rawKey=String(species).replace(/ SCHOOL$/,'').trim().toUpperCase(),aliases={'BOWHEAD WHALE':'BOWHEAD','BELUGA WHALE':'BELUGA','HUMPBACK WHALE':'HUMPBACK','GREY WHALE':'GRAY WHALE','POLAR BEAR':'POLAR BEAR'},key=aliases[rawKey]||rawKey;
    let item=catalog[key];if(!item){const compact=value=>String(value||'').toUpperCase().replace(/[^A-Z0-9]/g,'');item=Object.values(catalog).find(entry=>compact(entry.displayName)===compact(rawKey));}
    if(!item){item={displayName:String(species||'Arctic wildlife'),scientificName:'Field identification pending',group:'Arctic Wildlife Observation',photo:'assets/wildlife/polar-bear.jpg',credit:'Field observation record',source:'#',facts:['A wildlife observation was recorded from the expedition chart.','The individual has been removed from the active chart after observation.','Species reference details can be expanded in a future field-guide update.']};}
"""
exp=once(exp,old_wild,new_wild,'wildlife rich fallback')

# If a regular opportunity site generator fails, fall back to a nearby flexible mission rather than silently doing nothing.
old_final="const template=pool[Math.floor(rng()*pool.length)],target=buildTarget(template,payload.position,rng,'opportunity',{nearby:inIce,iceThickness}); if (!target) return null;\n    target.selected=false;\n    state.targets.push(target); toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`); changed(); return target;"
new_final="const template=pool[Math.floor(rng()*pool.length)];let target=buildTarget(template,payload.position,rng,'opportunity',{nearby:inIce,iceThickness});if(!target){const fallback=compatibleFallbackTemplate();fallback.anywhere=false;fallback.minDistance=12;fallback.distanceRange=45;target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:true,iceThickness});}if(!target)return null;target.selected=false;state.targets.push(target);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;"
exp=once(exp,old_final,new_final,'opportunity fallback')

# ---------------------------------------------------------------------------
# CSS: tiny warning directly beneath the resource gauges rather than a phone-blocking banner.
# ---------------------------------------------------------------------------
style=re.sub(r"\.resource-warning \{.*?\}\n\.resource-warning\.show \{.*?\}",""".resource-warning { position: fixed; z-index: 6; top: max(78px, calc(env(safe-area-inset-top) + 66px)); right: 105px; left: auto; max-width: 240px; transform: none; padding: 5px 8px; border: 1px solid rgba(255,196,117,.58); border-radius: 6px; background: rgba(87,31,35,.88); color: #fff0d0; font: 900 8px/1.2 system-ui,sans-serif; letter-spacing: .08em; text-align: right; opacity: 0; pointer-events: none; transition: opacity .16s; }
.resource-warning.show { opacity: 1; transform: none; }""",style,count=1,flags=re.S)
style=style.replace("  .resource-warning { top: 70px; max-width: calc(100vw - 18px); padding: 8px 11px; font-size: 8px; }","  .resource-warning { top: max(64px, calc(env(safe-area-inset-top) + 54px)); right: 72px; left: auto; max-width: 170px; padding: 4px 6px; font-size: 7px; text-align:right; }")

# New cache tags ensure installed web-app/browser copies fetch the new runtime.
for old in ['expedition-23h-startup','expedition-23g-port-wildlife']:
    index=index.replace(old,'expedition-23i-mapcache')

# Assertions
for marker in ['drawWorldCached(now)','setLineDash([18,11])','findPortTeleportPosition(currentPortCity)','pendingPortEntryTimer=setTimeout','observedWildlifeFallback.add(animal.individualId)']:
    if marker not in game: raise SystemExit(f'missing game marker: {marker}')
for marker in ["setTimeout(()=>{", "scheduleGrantRefresh(0)", "Field identification pending"]:
    if marker not in exp: raise SystemExit(f'missing expedition marker: {marker}')
if 'expedition-23i-mapcache' not in index: raise SystemExit('cache tag not updated')

GAME.write_text(game)
EXP.write_text(exp)
STYLE.write_text(style)
INDEX.write_text(index)
