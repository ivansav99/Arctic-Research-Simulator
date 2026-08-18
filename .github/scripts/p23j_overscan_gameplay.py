from pathlib import Path
import re

GAME=Path('game.js'); EXP=Path('expedition.js'); STYLE=Path('style.css'); INDEX=Path('index.html')
game=GAME.read_text(); exp=EXP.read_text(); style=STYLE.read_text(); index=INDEX.read_text()

def once(text, old, new, label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 occurrence, got {n}')
    return text.replace(old,new,1)

# --- Moving world cache: render a 150% viewport directly into the offscreen cache. ---
game=once(game,
"  const canvas=document.getElementById('map'),ctx=canvas.getContext('2d');\n  const worldCacheCanvas=document.createElement('canvas'),worldCacheCtx=worldCacheCanvas.getContext('2d');\n",
"  const canvas=document.getElementById('map'),mainCtx=canvas.getContext('2d');\n  let ctx=mainCtx;\n  const WORLD_CACHE_OVERSCAN=1.5;\n  const worldCacheCanvas=document.createElement('canvas'),worldCacheCtx=worldCacheCanvas.getContext('2d');\n",
'ctx overscan declaration')

# Keep low-food warning physically attached to the FOOD readout.
game=once(game,
"  const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i'),minimapPanel=document.getElementById('minimap-panel'),minimapClose=document.getElementById('minimap-close'),miniZoomIn=document.getElementById('mini-zoom-in'),miniZoomOut=document.getElementById('mini-zoom-out'),miniZoomValue=document.getElementById('mini-zoom-level');\n",
"  const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i'),minimapPanel=document.getElementById('minimap-panel'),minimapClose=document.getElementById('minimap-close'),miniZoomIn=document.getElementById('mini-zoom-in'),miniZoomOut=document.getElementById('mini-zoom-out'),miniZoomValue=document.getElementById('mini-zoom-level');\n  const foodStatus=document.querySelector('.food-status');if(foodStatus&&ui.resourceWarning)foodStatus.appendChild(ui.resourceWarning);\n",
'attach resource warning')

resize_pat=re.compile(r"  function resize\(\)\{.*?\}\n  const worldToScreen=",re.S)
m=resize_pat.search(game)
if not m: raise SystemExit('resize block not found')
new_resize="""  function resize(){dpr=Math.min(devicePixelRatio||1,IS_COARSE_POINTER?1.25:2);width=innerWidth;height=innerHeight;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);mainCtx.setTransform(dpr,0,0,dpr,0,0);worldCacheCanvas.width=Math.round(width*WORLD_CACHE_OVERSCAN*dpr);worldCacheCanvas.height=Math.round(height*WORLD_CACHE_OVERSCAN*dpr);worldCacheCtx.setTransform(dpr,0,0,dpr,0,0);invalidateWorldCache();lightCanvas.width=Math.round(width*dpr);lightCanvas.height=Math.round(height*dpr);light.setTransform(dpr,0,0,dpr,0,0);oceanCanvas.width=Math.max(1,Math.round(width));oceanCanvas.height=Math.max(1,Math.round(height));oceanPattern=null;baseScale=Math.max(3.4,Math.min(5.2,Math.min(width,height)/145));scale=baseScale*zoomLevel;const s=miniCanvas.clientWidth;miniCanvas.width=Math.round(s*dpr);miniCanvas.height=Math.round(s*dpr);mini.setTransform(dpr,0,0,dpr,0,0);}\n  const worldToScreen="""
game=game[:m.start()]+new_resize+game[m.end():]

# Ocean capture should follow whichever canvas is currently being rendered.
game=game.replace("ocean.drawImage(canvas,0,0,canvas.width,canvas.height,0,0,oceanCanvas.width,oceanCanvas.height);","ocean.drawImage(ctx.canvas,0,0,ctx.canvas.width,ctx.canvas.height,0,0,oceanCanvas.width,oceanCanvas.height);",1)

cache_pat=re.compile(r"  function captureWorldCache\(now\)\{.*?\n  \}\n  function drawWorldCached\(now\)\{.*?\n  \}",re.S)
m=cache_pat.search(game)
if not m: raise SystemExit('world cache functions not found')
cache_new=r'''  function rebuildWorldCache(now){
    const screenWidth=width,screenHeight=height,renderWidth=Math.ceil(screenWidth*WORLD_CACHE_OVERSCAN),renderHeight=Math.ceil(screenHeight*WORLD_CACHE_OVERSCAN),previousCtx=ctx;
    const requiredWidth=Math.round(renderWidth*dpr),requiredHeight=Math.round(renderHeight*dpr);
    if(worldCacheCanvas.width!==requiredWidth||worldCacheCanvas.height!==requiredHeight){worldCacheCanvas.width=requiredWidth;worldCacheCanvas.height=requiredHeight;}
    worldCacheCtx.setTransform(dpr,0,0,dpr,0,0);worldCacheCtx.clearRect(0,0,renderWidth,renderHeight);
    ctx=worldCacheCtx;width=renderWidth;height=renderHeight;
    try{drawMap();}finally{ctx=previousCtx;width=screenWidth;height=screenHeight;}
    worldCacheX=state.x;worldCacheY=state.y;worldCacheScale=scale;worldCacheAt=now;worldCacheValid=true;
  }
  function drawWorldCached(now){
    const scaleMatch=worldCacheValid&&Math.abs(worldCacheScale-scale)<.0001,dx=scaleMatch?(worldCacheX-state.x)*scale:0,dy=scaleMatch?(worldCacheY-state.y)*scale:0;
    const cacheCssWidth=worldCacheCanvas.width/dpr,cacheCssHeight=worldCacheCanvas.height/dpr,marginX=Math.max(0,(cacheCssWidth-width)/2),marginY=Math.max(0,(cacheCssHeight-height)/2);
    const refreshMs=IS_COARSE_POINTER?420:280,safeX=Math.max(24,marginX-18),safeY=Math.max(24,marginY-18);
    if(!scaleMatch||!worldCacheValid||now-worldCacheAt>=refreshMs||Math.abs(dx)>safeX||Math.abs(dy)>safeY)rebuildWorldCache(now);
    const freshMarginX=Math.max(0,(worldCacheCanvas.width/dpr-width)/2),freshMarginY=Math.max(0,(worldCacheCanvas.height/dpr-height)/2),freshDx=(worldCacheX-state.x)*scale,freshDy=(worldCacheY-state.y)*scale;
    const sx=Math.max(0,Math.min(worldCacheCanvas.width-canvas.width,Math.round((freshMarginX-freshDx)*dpr))),sy=Math.max(0,Math.min(worldCacheCanvas.height-canvas.height,Math.round((freshMarginY-freshDy)*dpr)));
    ctx.save();ctx.setTransform(dpr,0,0,dpr,0,0);ctx.drawImage(worldCacheCanvas,sx,sy,canvas.width,canvas.height,0,0,width,height);ctx.restore();
  }'''
game=game[:m.start()]+cache_new+game[m.end():]

# Rendering got efficient enough that the old frame-time clamp no longer slowed the simulation accidentally.
# Restore approximately the previous real-world pacing explicitly.
game=once(game,"elapsedDays=state.started&&!stationBusy?dt*.2*(state.frozen?100:effectiveTimeScale):0;","elapsedDays=state.started&&!stationBusy?dt*.07*(state.frozen?100:effectiveTimeScale):0;",'calendar pace')

# Guarantee an early field opportunity after leaving a port.
old_depart="function departWithCheck(proceed){const depart=()=>{if(currentPortCity){sound.play('depart');research?.leavePort?.();state.dockedPort=null;currentPortCity=null;}proceed();};const warned=!!currentPortCity&&!!research?.confirmDeparture?.({fuel:state.fuel,food:state.food},depart);if(!warned)depart();}"
new_depart="function departWithCheck(proceed){const depart=()=>{const leavingPort=!!currentPortCity;if(currentPortCity){sound.play('depart');research?.leavePort?.();state.dockedPort=null;currentPortCity=null;}if(leavingPort)researchOpportunityClock=Math.max(researchOpportunityClock,1);proceed();};const warned=!!currentPortCity&&!!research?.confirmDeparture?.({fuel:state.fuel,food:state.food},depart);if(!warned)depart();}"
game=once(game,old_depart,new_depart,'departure opportunity prime')

# --- Wildlife: fix the undefined data helper that was throwing before the modal could open. ---
old_wild="""    const individualId=String(context.individualId||context.id||`${key}:${Number(context.lat||0).toFixed(3)}:${Number(context.lon||0).toFixed(3)}`);
    const firstSpecies=!state.observed.includes(key), firstIndividual=!state.observedIndividuals.includes(individualId);
    if (firstSpecies) state.observed.push(key);
    if (firstIndividual) { const wildlifeData=wildlifeObservationData(); state.observedIndividuals.push(individualId); addData(wildlifeData); addLog(`${item.displayName} observation archived · +${wildlifeData} data.`); }"""
new_wild="""    const dataValue=Math.max(1,Math.round(Number(context.dataValue)||2));
    const individualId=String(context.individualId||context.id||`${key}:${Number(context.lat||0).toFixed(3)}:${Number(context.lon||0).toFixed(3)}`);
    const firstSpecies=!state.observed.includes(key), firstIndividual=!(state.observedIndividuals||[]).includes(individualId);
    if (firstSpecies) state.observed.push(key);
    if (firstIndividual) { state.observedIndividuals=state.observedIndividuals||[]; state.observedIndividuals.push(individualId); addData(dataValue); addLog(`${item.displayName} observation archived · +${dataValue} data.`); }"""
exp=once(exp,old_wild,new_wild,'wildlife data value')
exp=exp.replace("${firstIndividual?`OBSERVATION ARCHIVED · +${wildlifeObservationData()} DATA`:'THIS INDIVIDUAL ALREADY OBSERVED · +0 DATA'}","${firstIndividual?`OBSERVATION ARCHIVED · +${dataValue} DATA`:'THIS INDIVIDUAL ALREADY OBSERVED · +0 DATA'}",1)
exp=exp.replace("isWildlifeObserved:id=>state.observedIndividuals.includes(String(id))","isWildlifeObserved:id=>(state.observedIndividuals||[]).includes(String(id))",1)

# --- Grants: generate synchronously when the player actually opens the tab, with guarded fallback. ---
sched_pat=re.compile(r"  let grantRefreshTimer=0;\n  function scheduleGrantRefresh\(delay=120\)\{.*?\n  \}",re.S)
m=sched_pat.search(exp)
if not m: raise SystemExit('grant refresh block not found')
grant_new=r'''  let grantRefreshTimer=0;
  function refreshGrantOffersNow({render=true}={}){
    if(!state.port)return false;
    const portId=normalizedPortId(state.port);state.grantOfferCycle=null;
    try{generateOffers(state.port,{fresh:true});}catch(error){console.error('GRANT GENERATION FAILED',error);state.offers=[];}
    if(!state.offers.length){
      try{const rng=seeded(`${portId}-${state.portVisits}-guaranteed-grant`),fallback=buildTarget(compatibleFallbackTemplate(),state.port,rng,'grant');if(fallback){giveGrantUniqueMedia(fallback,new Set(),rng);state.offers=[fallback];}}catch(error){console.error('FALLBACK GRANT FAILED',error);}
    }
    renderSidebar();if(render&&portOpen)renderPort();callbacks.onStateChange?.();return state.offers.length>0;
  }
  function scheduleGrantRefresh(delay=120){
    if(!state.port)return;
    clearTimeout(grantRefreshTimer);const portId=normalizedPortId(state.port);
    grantRefreshTimer=setTimeout(()=>{if(!state.port||normalizedPortId(state.port)!==portId)return;refreshGrantOffersNow();},delay);
  }'''
exp=exp[:m.start()]+grant_new+exp[m.end():]

old_tabs="""    activePortTab=button.dataset.arxTab; portScrollTop=0; portTabsScrollLeft=tabs.scrollLeft; openStoreDetail=null;
    renderPort();if(activePortTab==='contracts'&&!state.offers.length)scheduleGrantRefresh(0);if(activePortTab==='crew'&&!state.candidates.length){setTimeout(()=>{if(state.port){generateCandidates(state.port);if(portOpen&&activePortTab==='crew')renderPort();}},0);} """
if old_tabs not in exp:
    old_tabs=old_tabs.rstrip()
new_tabs="""    activePortTab=button.dataset.arxTab; portScrollTop=0; portTabsScrollLeft=tabs.scrollLeft; openStoreDetail=null;
    if(activePortTab==='contracts'&&!state.offers.length)refreshGrantOffersNow({render:false});
    if(activePortTab==='crew'&&!state.candidates.length)generateCandidates(state.port);
    renderPort();"""
exp=once(exp,old_tabs,new_tabs,'synchronous tab loading')

# --- Resource warning lives under the FOOD gauge, not across the map. ---
style=style.replace(".food-status > i { display: block; width: 58px; height: 3px; margin-top: 4px; overflow: hidden; border-radius: 3px; background: #315e70; }",".food-status { position: relative; }\n.food-status > i { display: block; width: 58px; height: 3px; margin-top: 4px; overflow: hidden; border-radius: 3px; background: #315e70; }",1)
style=re.sub(r"\.resource-warning \{.*?\}\n\.resource-warning\.show \{.*?\}",".resource-warning { position: absolute; z-index: 8; top: calc(100% + 5px); right: 0; left: auto; width: max-content; max-width: 190px; transform: none; padding: 4px 7px; border: 1px solid rgba(255,196,117,.58); border-radius: 5px; background: rgba(87,31,35,.9); color: #fff0d0; font: 900 7px/1.2 system-ui,sans-serif; letter-spacing: .07em; text-align: right; white-space: normal; opacity: 0; pointer-events: none; transition: opacity .16s; }\n.resource-warning.show { opacity: 1; transform: none; }",style,count=1,flags=re.S)
style=re.sub(r"  \.resource-warning \{.*?\}\n", "  .resource-warning { top: calc(100% + 4px); right: 0; left: auto; max-width: 148px; padding: 3px 5px; font-size: 6px; line-height: 1.15; text-align: right; }\n", style, count=1, flags=re.S)

# Cache-bust runtime assets.
index=index.replace('style.css?v=expedition-23i-mapcache','style.css?v=expedition-23j-overscan')
index=index.replace('expedition.js?v=expedition-23i-mapcache','expedition.js?v=expedition-23j-overscan')
index=index.replace('game.js?v=expedition-23i-mapcache','game.js?v=expedition-23j-overscan')

GAME.write_text(game); EXP.write_text(exp); STYLE.write_text(style); INDEX.write_text(index)
