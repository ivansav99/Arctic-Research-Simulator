from pathlib import Path
import re


def once(text, old, new, label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    return text.replace(old,new)


def sub_once(text, pattern, replacement, label, flags=re.S):
    new,n=re.subn(pattern,replacement,text,count=1,flags=flags)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 regex match, found {n}')
    return new

# ---------------- game.js ----------------
gp=Path('game.js'); g=gp.read_text()

g=once(g,
"const state={x:home.x,y:home.y,tx:home.x,ty:home.y,angle:Math.PI,moving:false,commandActive:false,travelled:0,seasonDay:0,year:2026,frozen:false,fuel:100,food:100,portDestination:null,dockedPort:null,gameOver:false,fogClearDays:7,ramming:false,ramClock:0,targetOnLand:false,started:false};",
"const state={x:home.x,y:home.y,tx:home.x,ty:home.y,angle:Math.PI,moving:false,commandActive:false,travelled:0,seasonDay:0,year:2026,frozen:false,fuel:100,food:100,portDestination:null,dockedPort:null,gameOver:false,fogClearDays:7,ramming:false,ramClock:0,targetOnLand:false,precisionNav:false,started:false};",
'precision navigation state')
g=once(g,
"const KNOT_TO_WORLD_SPEED=14,iceFloes=[],wakeFloes=[],brokenIceChannels=[],brokenIceGrid=new Map(),BROKEN_ICE_CELL=32;\n  let wakeFloeClock=0,packPushToastDay=-1,wildlifeEncounterClock=0,wildlifeEncounterSerial=0;",
"const KNOT_TO_WORLD_SPEED=14,iceFloes=[],wakeFloes=[],wakeTrail=[],brokenIceChannels=[],brokenIceGrid=new Map(),BROKEN_ICE_CELL=32;\n  let wakeFloeClock=0,wakeTrailClock=0,miniLastDraw=0,miniZoomLevel=1,packPushToastDay=-1,wildlifeEncounterClock=0,wildlifeEncounterSerial=0;",
'world wake and minimap state')

g=once(g,"const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i'),minimapPanel=document.getElementById('minimap-panel'),minimapClose=document.getElementById('minimap-close');",
"const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i'),minimapPanel=document.getElementById('minimap-panel'),minimapClose=document.getElementById('minimap-close'),miniZoomIn=document.getElementById('mini-zoom-in'),miniZoomOut=document.getElementById('mini-zoom-out'),miniZoomValue=document.getElementById('mini-zoom-level');",
'minimap zoom controls refs')

g=once(g,"const validAuto=!!auto?.research?.playerConfigured;","const validAuto=!!(auto?.research?.playerConfigured&&auto?.navigation?.started);",'valid saved profile')
g=once(g,"validAuto?saveSummary(auto):''","validAuto?saveDescription(auto):''",'permanent save summary formatter')

g=once(g,"function drawChartLabel(label){const defaultMin=", "function drawChartLabel(label){if(label.kind==='city')return;const defaultMin=", 'remove duplicate chart city labels')

# Replace vessel-attached wake with a persistent world-coordinate wake trail.
g=once(g,
"    if(state.moving){\n      ctx.fillStyle='rgba(235,251,255,.42)';\n      ctx.beginPath();\n      ctx.moveTo(-10,18);\n      ctx.quadraticCurveTo(-28,48,-8,76);\n      ctx.lineTo(0,30);\n      ctx.lineTo(8,76);\n      ctx.quadraticCurveTo(28,48,10,18);\n      ctx.fill();\n    }\n",
"",
'remove attached vessel wake')

wake_code=r'''  function updateWakeTrail(dt){
    for(let i=wakeTrail.length-1;i>=0;i--){wakeTrail[i].life-=dt;if(wakeTrail[i].life<=0)wakeTrail.splice(i,1);}
    if(!state.moving||state.ramming)return;
    wakeTrailClock+=dt;
    while(wakeTrailClock>.075&&wakeTrail.length<260){
      wakeTrailClock-=.075;
      const headingX=Math.sin(state.angle),headingY=-Math.cos(state.angle),sideX=Math.cos(state.angle),sideY=Math.sin(state.angle),back=7+Math.random()*5,side=(Math.random()-.5)*(5+Math.min(7,vesselSpriteMetrics(vesselModifiers()).w*.14));
      wakeTrail.push({x:state.x-headingX*back+sideX*side,y:state.y-headingY*back+sideY*side,life:5.8,maxLife:5.8,size:2.1+Math.random()*2.7});
    }
  }
  function drawWakeTrail(){
    if(!wakeTrail.length)return;ctx.save();
    for(const mark of wakeTrail){const p=worldToScreen(mark.x,mark.y);if(p.x<-30||p.x>width+30||p.y<60||p.y>height+30)continue;const age=1-mark.life/mark.maxLife,alpha=Math.max(0,Math.min(.42,mark.life/mark.maxLife*.42)),stretch=1.2+age*2.4;ctx.fillStyle=`rgba(236,251,255,${alpha})`;ctx.beginPath();ctx.ellipse(p.x,p.y,mark.size*stretch,mark.size*(.48+age*.28),0,0,Math.PI*2);ctx.fill();}
    ctx.restore();
  }
'''
g=once(g,"  function drawBrokenIceChannels(){",wake_code+"  function drawBrokenIceChannels(){",'add persistent wake trail')
g=once(g,"drawIceThicknessAndCracks();drawMarginalFloes();drawWakeFloes();","drawIceThicknessAndCracks();drawMarginalFloes();drawWakeTrail();drawWakeFloes();",'draw world wake')
# Clear persistent wake wherever dynamic wake is cleared.
g=g.replace("wakeFloes.length=0;", "wakeFloes.length=0;wakeTrail.length=0;")

# Precision navigation: instantaneous pivot near shore/for short moves; no jump escape.
g=once(g,
"function setWorldDestination(tx,ty){if(state.frozen){freezeIn();return;}const targetPos=unpolar(tx,ty);if(targetPos.lat<MIN_LAT){showToast('MAP BOUNDARY - TURN NORTH');return;}const targetOnLand=isLand(tx,ty),profile=targetOnLand?null:iceNavigationProfileAt(tx,ty);if(profile&&!profile.allowed){showToast(profile.reason||'SEA ICE · IMPASSABLE',2200);return;}departWithCheck(()=>{state.portDestination=null;state.tx=tx;state.ty=ty;state.moving=true;state.commandActive=true;state.targetOnLand=targetOnLand;state.ramming=!!profile?.breaking;state.ramClock=0;ui.welcome.classList.add('hidden');if(profile?.type==='marginal'&&profile.speedFactor<1)showToast(`MARGINAL ICE · ${Math.round(profile.speedFactor*100)}% SPEED`);});}",
"function setWorldDestination(tx,ty){if(state.frozen){freezeIn();return;}const targetPos=unpolar(tx,ty);if(targetPos.lat<MIN_LAT){showToast('MAP BOUNDARY - TURN NORTH');return;}const targetOnLand=isLand(tx,ty),profile=targetOnLand?null:iceNavigationProfileAt(tx,ty);if(profile&&!profile.allowed){showToast(profile.reason||'SEA ICE · IMPASSABLE',2200);return;}departWithCheck(()=>{const dx=tx-state.x,dy=ty-state.y,distance=Math.hypot(dx,dy),nearCoast=coastDistance(state.x,state.y,48)<32;state.portDestination=null;state.tx=tx;state.ty=ty;state.moving=true;state.commandActive=true;state.targetOnLand=targetOnLand;state.precisionNav=nearCoast||distance<75;if(state.precisionNav&&distance>.01)state.angle=Math.atan2(dy,dx)+Math.PI/2;state.ramming=!!profile?.breaking;state.ramClock=0;ui.welcome.classList.add('hidden');if(profile?.type==='marginal'&&profile.speedFactor<1)showToast(`MARGINAL ICE · ${Math.round(profile.speedFactor*100)}% SPEED`);});}",
'precision set destination')
g=once(g,
"departWithCheck(()=>{pendingResearchTargetId=null;pendingResearchArrival=null;state.portDestination=portItem.city;state.tx=approach.x;state.ty=approach.y;state.moving=true;state.commandActive=true;state.targetOnLand=false;state.ramming=false;ui.welcome.classList.add('hidden');showToast(`PORT APPROACH — ${portItem.city.name}`,1800);});",
"departWithCheck(()=>{pendingResearchTargetId=null;pendingResearchArrival=null;state.portDestination=portItem.city;state.tx=approach.x;state.ty=approach.y;state.moving=true;state.commandActive=true;state.targetOnLand=false;state.precisionNav=true;state.angle=Math.atan2(approach.y-state.y,approach.x-state.x)+Math.PI/2;state.ramming=false;ui.welcome.classList.add('hidden');showToast(`PORT APPROACH — ${portItem.city.name}`,1800);});",
'precision port approach')

new_slide="""function shorelineSlide(x,y,vx,vy,motionDt,targetX,targetY){const speed=Math.hypot(vx,vy);if(speed<.01)return null;const desired=Math.atan2(targetY-y,targetX-x),step=Math.max(.7,Math.min(speed*motionDt,3.4)),offsets=[0,8,-8,16,-16,27,-27,40,-40,55,-55,72,-72].map(v=>v*Math.PI/180);let best=null,bestScore=-Infinity;for(const fraction of[1,.72,.46])for(const offset of offsets){const a=desired+offset,cx=x+Math.cos(a)*step*fraction,cy=y+Math.sin(a)*step*fraction,pos=unpolar(cx,cy),profile=iceNavigationProfileAt(cx,cy);if(pos.lat<MIN_LAT||isBlocked(cx,cy)||!profile.allowed)continue;const probe=Math.max(4,step*2.3),px=x+Math.cos(a)*probe,py=y+Math.sin(a)*probe;if(isBlocked(px,py))continue;const oldDistance=Math.hypot(targetX-x,targetY-y),newDistance=Math.hypot(targetX-cx,targetY-cy),progress=oldDistance-newDistance,clearance=coastDistance(cx,cy,20),score=progress*4+Math.min(20,clearance)*.14-Math.abs(offset)*.48+fraction*.3;if(score>bestScore){bestScore=score;best={x:cx,y:cy,vx:(cx-x)/Math.max(.001,motionDt),vy:(cy-y)/Math.max(.001,motionDt)};}}return best;}"""
g=sub_once(g,r"function shorelineSlide\(x,y,vx,vy,motionDt,targetX,targetY\)\{.*?return null;\}",new_slide,'simplify shoreline slide')
g=sub_once(g,r"\n  function localNavigationEscape\(x,y,targetX,targetY,motionDt\)\{.*?\n  \}\n", "\n", 'remove jump escape')
g=once(g,
"      if(commanded&&(nextPos.lat<MIN_LAT||isBlocked(nx,ny)||!nextProfile.allowed)){const escape=localNavigationEscape(state.x,state.y,state.tx,state.ty,motionDt);if(escape){nx=escape.x;ny=escape.y;nextPos=unpolar(nx,ny);nextProfile=iceNavigationProfileAt(nx,ny,vessel);groundX=(nx-state.x)/Math.max(.001,motionDt);groundY=(ny-state.y)/Math.max(.001,motionDt);groundStep=Math.hypot(nx-state.x,ny-state.y);}}\n",
"",
'remove runtime jump escape')
g=once(g,
"      let cruise=commanded?normalCruise*driveProfile.speedFactor:0;",
"      let cruise=commanded?normalCruise*driveProfile.speedFactor:0;const precisionNav=commanded&&(state.precisionNav||dist<75||coastDistance(state.x,state.y,42)<30);if(precisionNav){state.precisionNav=true;state.angle=Math.atan2(dy,dx)+Math.PI/2;cruise=Math.min(cruise,vessel.cruiseKnots*KNOT_TO_WORLD_SPEED*.58);}",
'precision speed and pivot')
g=once(g,
"const target=Math.atan2(dy,dx)+Math.PI/2;let da=((target-state.angle+Math.PI*3)%(Math.PI*2))-Math.PI;{const turnRate=dist<Math.max(30,arrivalRadius*8)?9:4.8;state.angle+=da*Math.min(1,dt*turnRate);state.moving=through>.02;",
"const target=Math.atan2(dy,dx)+Math.PI/2;let da=((target-state.angle+Math.PI*3)%(Math.PI*2))-Math.PI;if(!precisionNav){const turnRate=dist<Math.max(30,arrivalRadius*8)?9:4.8;state.angle+=da*Math.min(1,dt*turnRate);}else state.angle=target;{state.moving=through>.02;",
'precision heading')
g=once(g,
"state.moving=false;state.commandActive=false;state.ramming=false;state.targetOnLand=false;ui.speed.textContent='0.0 KN';",
"state.moving=false;state.commandActive=false;state.ramming=false;state.targetOnLand=false;state.precisionNav=false;ui.speed.textContent='0.0 KN';",
'clear precision on blocked stop')
# reset precision whenever command naturally completes/drifts
old="state.moving=false;state.commandActive=false;state.ramming=false;ui.speed.textContent=driftKnots<.05?'0.0 KN':driftKnots.toFixed(1)+' KN DRIFT';if(state.portDestination)enterPort(state.portDestination);"
new="state.moving=false;state.commandActive=false;state.ramming=false;state.precisionNav=false;ui.speed.textContent=driftKnots<.05?'0.0 KN':driftKnots.toFixed(1)+' KN DRIFT';if(state.portDestination)enterPort(state.portDestination);"
g=once(g,old,new,'clear precision on arrival')

# Minimap: own zoom, twice the overview coverage when collapsed, longitude grid, and throttled redraw.
g=once(g,
"function miniMapGeometry(){const zoom=Math.max(.7,zoomLevel||1),base=minimapExpanded?1100:520;return{worldRadius:base/zoom,centerX:state.x,centerY:state.y};}",
"function miniMapGeometry(){const zoom=Math.max(.7,minimapExpanded?(miniZoomLevel||zoomLevel||1):(zoomLevel||1)),base=minimapExpanded?1100:1040;return{worldRadius:base/zoom,centerX:state.x,centerY:state.y};}\n  function miniZoomSteps(){const minZoom=Math.max(.7,vesselModifiers().minZoom),steps=[.7,1.1,1.45,1.8,2.3,2.8].filter(value=>value>=minZoom-.001);return steps.length?steps:[minZoom];}\n  function syncMiniZoomControls(){const steps=miniZoomSteps(),index=steps.reduce((best,value,i)=>Math.abs(value-miniZoomLevel)<Math.abs(steps[best]-miniZoomLevel)?i:best,0);miniZoomLevel=steps[index];if(miniZoomValue)miniZoomValue.textContent=Math.round(miniZoomLevel*100)+'%';if(miniZoomOut)miniZoomOut.disabled=index<=0;if(miniZoomIn)miniZoomIn.disabled=index>=steps.length-1;}\n  function setMiniZoom(direction){const steps=miniZoomSteps();let index=steps.reduce((best,value,i)=>Math.abs(value-miniZoomLevel)<Math.abs(steps[best]-miniZoomLevel)?i:best,0);index=Math.max(0,Math.min(steps.length-1,index+(direction>0?1:-1)));miniZoomLevel=steps[index];syncMiniZoomControls();miniLastDraw=0;drawMiniMap();}",
'minimap independent zoom')
# add longitude lines after existing latitude rings
g=once(g,
"});if(!miniTerrain)land.forEach(shape=>",
"});{const pole=project(0,0);mini.strokeStyle='rgba(255,255,255,.18)';mini.lineWidth=.65;for(let lon=-180;lon<180;lon+=30){const edge=polar(MIN_LAT,lon),pt=project(edge.x,edge.y);mini.beginPath();mini.moveTo(pole.x,pole.y);mini.lineTo(pt.x,pt.y);mini.stroke();}}if(!miniTerrain)land.forEach(shape=>",
'minimap longitude lines')
# Replace final course display with chart zoom display.
g=once(g,
"const currentPos=unpolar(state.x,state.y),ew=currentPos.lon<0?'W':'E',weather=currentWeather(),profile=iceNavigationProfileAt(state.x,state.y),course=state.commandActive?((Math.atan2(state.tx-state.x,state.ty-state.y)*180/Math.PI+360)%360):null;if(ui.miniLocation)ui.miniLocation.textContent=locationName(currentPos.lat,currentPos.lon);if(ui.miniPosition)ui.miniPosition.textContent=`${currentPos.lat.toFixed(2)}°N ${Math.abs(currentPos.lon).toFixed(2)}°${ew}`;if(ui.miniCourse)ui.miniCourse.textContent=course==null?'STOPPED':`${Math.round(course).toString().padStart(3,'0')}°`;if(ui.miniIce)ui.miniIce.textContent=iceStatusText(profile,state.ramming);if(ui.miniWeather)ui.miniWeather.textContent=weather.type==='clear'?'CLEAR':weather.label.toUpperCase();",
"const currentPos=unpolar(state.x,state.y),ew=currentPos.lon<0?'W':'E',weather=currentWeather(),profile=iceNavigationProfileAt(state.x,state.y),chartZoom=minimapExpanded?miniZoomLevel:zoomLevel;if(ui.miniLocation)ui.miniLocation.textContent=locationName(currentPos.lat,currentPos.lon);if(ui.miniPosition)ui.miniPosition.textContent=`${currentPos.lat.toFixed(2)}°N ${Math.abs(currentPos.lon).toFixed(2)}°${ew}`;if(ui.miniCourse)ui.miniCourse.textContent=Math.round(chartZoom*100)+'%';if(miniZoomValue)miniZoomValue.textContent=Math.round(chartZoom*100)+'%';if(ui.miniIce)ui.miniIce.textContent=iceStatusText(profile,state.ramming);if(ui.miniWeather)ui.miniWeather.textContent=weather.type==='clear'?'CLEAR':weather.label.toUpperCase();",
'minimap chart zoom readout')
g=once(g,
"function openMinimap(){if(!minimapPanel||minimapExpanded)return;minimapExpanded=true;minimapPanel.classList.add('expanded');document.body.classList.add('nav-chart-open');drawMiniMap();}",
"function openMinimap(){if(!minimapPanel||minimapExpanded)return;minimapExpanded=true;miniZoomLevel=zoomLevel;syncMiniZoomControls();minimapPanel.classList.add('expanded');document.body.classList.add('nav-chart-open');miniLastDraw=0;drawMiniMap();}",
'open minimap zoom sync')
g=once(g,
"miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();e.preventDefault();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});if(!minimapExpanded)openMinimap();});\n  minimapClose?.addEventListener('click',e=>{e.stopPropagation();closeMinimap();});",
"miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();e.preventDefault();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});if(!minimapExpanded)openMinimap();});\n  minimapClose?.addEventListener('click',e=>{e.stopPropagation();closeMinimap();});\n  miniZoomIn?.addEventListener('click',e=>{e.stopPropagation();setMiniZoom(1);});\n  miniZoomOut?.addEventListener('click',e=>{e.stopPropagation();setMiniZoom(-1);});",
'minimap zoom listeners')

# Frame optimizations: world wake update + minimap redraw throttling.
g=once(g,"updateFloes(dt/zoomLevel,minX,maxX,minY,maxY);updateWakeFloes(dt/zoomLevel);updateWildlifeEncounters(dt);",
"updateFloes(dt/zoomLevel,minX,maxX,minY,maxY);updateWakeFloes(dt/zoomLevel);updateWakeTrail(dt/zoomLevel);updateWildlifeEncounters(dt);",'update persistent wake')
g=once(g,
"try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}drawVessel();requestAnimationFrame(frame);",
"if(now-miniLastDraw>(minimapExpanded?45:160)){miniLastDraw=now;try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}}drawVessel();requestAnimationFrame(frame);",
'minimap redraw throttle')

# Low-food helicopter reminder hook.
g=once(g,
"if(state.started&&!previousFood&&resourceAlertState.food)showToast('LOW FOOD · LESS THAN 20% REMAINING · RETURN TO PORT',3600);",
"if(state.started&&!previousFood&&resourceAlertState.food){showToast('LOW FOOD · LESS THAN 20% REMAINING',3600);research?.maybeHelicopterFoodReminder?.();}",
'helicopter low food reminder hook')

gp.write_text(g)

# ---------------- expedition.js ----------------
ep=Path('expedition.js'); e=ep.read_text()

e=once(e,"const VESSEL_TRADE_IN_RATE = .5;","const VESSEL_TRADE_IN_RATE = 1;",'100 percent vessel trade in')
e=once(e,"{id:'local',threshold:100,next:1000,label:'Local science newsletter',journal:'Svalbard Science Bulletin',award:30000,initialCitations:5,potential:45},\n    {id:'national',threshold:1000,next:10000,label:'National research journal',journal:'Nordic Polar Research Review',award:350000,initialCitations:65,potential:700},\n    {id:'international',threshold:10000,next:null,label:'Prestigious international journal',journal:'International Journal of Polar Systems',award:4000000,initialCitations:850,potential:9000}",
"{id:'local',threshold:100,next:1000,label:'Local science newsletter',journal:'Svalbard Science Bulletin',award:30000,initialCitations:10,potential:90},\n    {id:'national',threshold:1000,next:10000,label:'National research journal',journal:'Nordic Polar Research Review',award:350000,initialCitations:130,potential:1400},\n    {id:'international',threshold:10000,next:null,label:'Prestigious international journal',journal:'International Journal of Polar Systems',award:4000000,initialCitations:1700,potential:18000}",
'double paper citations')
e=once(e,"const hull=ship.id==='fishing'?60000:Math.round((ship.price||0)*VESSEL_TRADE_IN_RATE);","const hull=Math.round(vesselPurchasePrice(ship)*VESSEL_TRADE_IN_RATE);",'starter vessel full trade credit')

# Correct face-free equipment illustrations as inline SVGs (text assets, no network dependency).
media_insert=r'''    shallowCorer: {src:'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520"><defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#d7eef2"/><stop offset="1" stop-color="#86b3bf"/></linearGradient></defs><rect width="900" height="520" fill="#0c3447"/><rect y="395" width="900" height="125" fill="#17495a"/><g stroke="#e5f6f7" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M250 95v285"/><path d="M205 95h90"/><path d="M225 380h50"/><path d="M250 385v55"/><path d="M520 110v250"/><path d="M470 110h100"/><path d="M490 360l-45 70M550 360l45 70"/></g><g fill="url(#b)" stroke="#dff5f7" stroke-width="7"><rect x="226" y="180" width="48" height="200" rx="12"/><path d="M495 220h50l20 140h-90z"/></g><g fill="#f6d365"><rect x="90" y="420" width="160" height="38" rx="8"/><rect x="650" y="413" width="160" height="48" rx="8"/></g><g fill="#d9f0f2"><rect x="105" y="430" width="20" height="92" rx="8" transform="rotate(-90 105 430)"/><rect x="676" y="420" width="18" height="95" rx="8" transform="rotate(-90 676 420)"/></g><text x="450" y="55" text-anchor="middle" fill="#eafaff" font-family="sans-serif" font-size="32" font-weight="700">SHALLOW PUSH + GRAVITY CORING KIT</text><text x="450" y="493" text-anchor="middle" fill="#8fc7d3" font-family="sans-serif" font-size="21">short core barrels · liners · sectioning case</text></svg>`), alt:'Portable shallow push corer, small gravity corer, core liners and sediment sectioning kit', credit:'Original face-free equipment illustration', source:''},
    surfaceNet: {src:'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520"><rect width="900" height="520" fill="#0c3447"/><g fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="305" cy="170" r="105" stroke="#f6d365" stroke-width="19"/><path d="M210 170L530 385M400 170L530 385M305 275L530 385" stroke="#dff5f7" stroke-width="8"/><path d="M530 385l75 25" stroke="#f6d365" stroke-width="18"/><path d="M207 90L95 40M400 90L505 35" stroke="#91d9e7" stroke-width="9"/><path d="M95 40L505 35" stroke="#91d9e7" stroke-width="6"/></g><path d="M218 183L530 385L393 183Z" fill="rgba(177,225,232,.22)" stroke="#91c8d2" stroke-width="5"/><rect x="605" y="390" width="85" height="58" rx="12" fill="#e7f4ee"/><text x="450" y="488" text-anchor="middle" fill="#8fc7d3" font-family="sans-serif" font-size="23">ring mouth · conical mesh · cod end · towing bridle</text><text x="450" y="55" text-anchor="middle" fill="#eafaff" font-family="sans-serif" font-size="32" font-weight="700">SURFACE PLANKTON RING NET</text></svg>`), alt:'Scientific surface plankton ring net with circular mouth, conical mesh, cod end and tow bridle', credit:'Original face-free equipment illustration', source:''},
    verticalNet: {src:'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520"><rect width="900" height="520" fill="#0c3447"/><path d="M450 35v70" stroke="#91d9e7" stroke-width="10"/><ellipse cx="450" cy="140" rx="125" ry="45" fill="none" stroke="#f6d365" stroke-width="18"/><path d="M325 140L410 390M575 140L490 390" stroke="#dff5f7" stroke-width="8"/><path d="M325 140L410 390L490 390L575 140Z" fill="rgba(177,225,232,.24)" stroke="#91c8d2" stroke-width="5"/><rect x="410" y="390" width="80" height="62" rx="12" fill="#e7f4ee"/><path d="M450 452v32" stroke="#f6d365" stroke-width="9"/><path d="M425 484h50l-25 24z" fill="#f6d365"/><path d="M365 100h170" stroke="#91d9e7" stroke-width="7" stroke-dasharray="15 12"/><text x="450" y="55" text-anchor="middle" fill="#eafaff" font-family="sans-serif" font-size="32" font-weight="700">VERTICAL PLANKTON NET</text><text x="450" y="505" text-anchor="middle" fill="#8fc7d3" font-family="sans-serif" font-size="21">weighted vertical haul · closing ring · cod end</text></svg>`), alt:'Weighted vertical plankton net with closing ring, mesh cone, cod end and weight', credit:'Original face-free equipment illustration', source:''},
    bongoNet: {src:'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520"><rect width="900" height="520" fill="#0c3447"/><g fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="330" cy="155" r="90" stroke="#f6d365" stroke-width="17"/><circle cx="570" cy="155" r="90" stroke="#f6d365" stroke-width="17"/><path d="M240 155L380 400M420 155L380 400M480 155L520 400M660 155L520 400" stroke="#dff5f7" stroke-width="8"/><path d="M330 65L450 35L570 65" stroke="#91d9e7" stroke-width="8"/></g><path d="M248 170L380 400L412 170Z" fill="rgba(177,225,232,.22)"/><path d="M488 170L520 400L652 170Z" fill="rgba(177,225,232,.22)"/><rect x="345" y="392" width="70" height="55" rx="10" fill="#e7f4ee"/><rect x="485" y="392" width="70" height="55" rx="10" fill="#e7f4ee"/><text x="450" y="490" text-anchor="middle" fill="#8fc7d3" font-family="sans-serif" font-size="23">paired net mouths · two mesh sizes · dual cod ends</text><text x="450" y="45" text-anchor="middle" fill="#eafaff" font-family="sans-serif" font-size="32" font-weight="700">BONGO PLANKTON NET</text></svg>`), alt:'Paired bongo plankton net with two circular mouths, mesh cones and cod ends', credit:'Original face-free equipment illustration', source:''},
'''
e=once(e,"    sedimentCorer: {src:'assets/equipment/box-corer.webp'",media_insert+"    sedimentCorer: {src:'assets/equipment/box-corer.webp'",'insert correct corer and plankton media')
e=once(e,"media:MEDIA.local}),\n    'bongo-plankton-net'", "media:MEDIA.surfaceNet}),\n    'bongo-plankton-net'",'surface ring net media')
e=once(e,"media:MEDIA.local}),\n    'vertical-plankton-net'", "media:MEDIA.bongoNet}),\n    'vertical-plankton-net'",'bongo net media')
# vertical is followed by portable-fluorometer
e=once(e,"media:MEDIA.local}),\n    'portable-fluorometer'", "media:MEDIA.verticalNet}),\n    'portable-fluorometer'",'vertical net media')
e=once(e,"media:MEDIA.sedimentCorer}),\n    'ice-core-system'", "media:MEDIA.shallowCorer}),\n    'ice-core-system'",'shallow corer media')

# state for one low-food helicopter prompt per episode
e=once(e,"lastProfessorGrantDay:-999, remoteOffer:null","lastProfessorGrantDay:-999, remoteOffer:null, helicopterFoodReminderShown:false",'helicopter reminder state')
e=once(e,"state.remoteOffer=state.remoteOffer||null; state.elapsedDays=Number(state.elapsedDays)||0;", "state.remoteOffer=state.remoteOffer||null; state.helicopterFoodReminderShown=!!state.helicopterFoodReminderShown; state.elapsedDays=Number(state.elapsedDays)||0;",'restore helicopter reminder state')

# Diverse grant media, and build only the handful of offers we actually display.
helper=r'''  const GRANT_MEDIA_POOL=[MEDIA.river,MEDIA.ice,MEDIA.aerial,MEDIA.storm,MEDIA.ctd,MEDIA.rov,MEDIA.radar,MEDIA.balloon,MEDIA.aerostat,MEDIA.drone,MEDIA.drifter,MEDIA.winch,MEDIA.handheldWater,MEDIA.iceCorer,MEDIA.miniRov,MEDIA.shallowAdcp,MEDIA.surfaceNet,MEDIA.verticalNet,MEDIA.bongoNet,MEDIA.shallowCorer,MEDIA.vessel].filter(Boolean);
  function giveGrantUniqueMedia(target,used,rng){
    const thematic=[];
    for(const id of [...(target.equipment||[]),...(target.consumables||[])]){const media=EQUIPMENT[id]?.media;if(media?.src)thematic.push(media);}
    if(target.specialties?.includes('plankton'))thematic.push(MEDIA.surfaceNet,MEDIA.verticalNet,MEDIA.bongoNet);
    if(target.specialties?.includes('benthic'))thematic.push(MEDIA.shallowCorer,MEDIA.sedimentCorer,MEDIA.rov);
    if(target.specialties?.includes('atmosphere'))thematic.push(MEDIA.radar,MEDIA.balloon,MEDIA.aerostat,MEDIA.storm);
    if(target.specialties?.includes('sea-ice-physics')||target.specialties?.includes('sea-ice-ecology'))thematic.push(MEDIA.ice,MEDIA.iceCorer,MEDIA.drone);
    if(target.specialties?.includes('marine-mammals'))thematic.push(MEDIA.aerial,MEDIA.hydrophone,MEDIA.sonobuoy);
    if(target.specialties?.includes('physical')||target.specialties?.includes('coastal-oceanography'))thematic.push(MEDIA.ctd,MEDIA.shallowAdcp,MEDIA.drifter,MEDIA.river);
    const candidates=[target.media,...thematic,...GRANT_MEDIA_POOL].filter(item=>item?.src);
    const shift=Math.floor(rng()*Math.max(1,candidates.length));
    for(let k=0;k<candidates.length;k++){const media=candidates[(k+shift)%candidates.length];if(!used.has(media.src)){target.media=clone(media);used.add(media.src);return true;}}
    return false;
  }
'''
e=once(e,"  function generateOffers(port,{fresh=false}={}) {",helper+"  function generateOffers(port,{fresh=false}={}) {",'grant media helper')
old_gen="""    state.offers=[]; const specialtyCount=new Set(state.scientists.map(item=>item.specialty)).size,seniorBonus=hiredCareerCount('postdoc')+hiredCareerCount('professor')*2,offerLimit=Math.min(9,Math.max(3,2+specialtyCount+seniorBonus)),builtOffers=[];
    for(const template of pool){const target=buildTarget(template,port,rng,'grant');if(target)builtOffers.push(target);} const usedPictures=new Set(),duplicatePictures=[];for(const target of builtOffers){const src=target.media?.src||'';if(src&&usedPictures.has(src)){duplicatePictures.push(target);continue;}state.offers.push(target);if(src)usedPictures.add(src);if(state.offers.length>=offerLimit)break;}if(state.offers.length<offerLimit)for(const target of duplicatePictures){state.offers.push(target);if(state.offers.length>=offerLimit)break;} if(!state.offers.length&&playerCareerLevel()<2){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback)state.offers.push(fallback);} 
"""
new_gen="""    state.offers=[]; const specialtyCount=new Set(state.scientists.map(item=>item.specialty)).size,seniorBonus=hiredCareerCount('postdoc')+hiredCareerCount('professor')*2,offerLimit=Math.min(9,Math.max(3,2+specialtyCount+seniorBonus)),usedPictures=new Set();
    let attempts=0;for(const template of pool){if(state.offers.length>=offerLimit||attempts>=offerLimit*3)break;attempts++;const target=buildTarget(template,port,rng,'grant');if(!target)continue;if(!giveGrantUniqueMedia(target,usedPictures,rng))continue;state.offers.push(target);} if(!state.offers.length&&playerCareerLevel()<2){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback){giveGrantUniqueMedia(fallback,usedPictures,rng);state.offers.push(fallback);}}
"""
e=once(e,old_gen,new_gen,'fast unique grant offers')
e=once(e,"state.grantMarketReady[portId]=state.elapsedDays+7;","state.grantMarketReady[portId]=state.elapsedDays+3.5;",'double grant refresh rate')

# At least 2/3 spontaneous opportunities ready when possible; guarantee a compatible fallback otherwise.
old_pool="""    let pool;
    if (aspirational.length&&rng()<.48) pool=aspirational; else if (ready.length) pool=ready; else pool=aspirational.length?aspirational:otherMissing;
    const template=pool[Math.floor(rng()*pool.length)],target=buildTarget(template,payload.position,rng,'opportunity',{nearby:inIce,iceThickness}); if (!target) return null;
"""
new_pool="""    let pool;
    if(!ready.length){const fallback=compatibleFallbackTemplate(),target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:inIce,iceThickness});if(!target)return null;target.selected=false;state.targets.push(target);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed();return target;}
    if (aspirational.length&&rng()<.30) pool=aspirational; else pool=ready;
    const template=pool[Math.floor(rng()*pool.length)],target=buildTarget(template,payload.position,rng,'opportunity',{nearby:inIce,iceThickness}); if (!target) return null;
"""
e=once(e,old_pool,new_pool,'70 percent ready opportunities')

# Decline means remove; X means merely close.
e=e.replace('>CANCEL OPPORTUNITY</button>','>DECLINE</button>')
e=once(e,"toast('RESEARCH OPPORTUNITY CANCELLED');","toast('RESEARCH OPPORTUNITY DECLINED');",'opportunity decline toast')
# Add decline button when opening an opportunity at the site too.
e=once(e,
"const missing=readiness.rows.find(row=>!row.ready), actionLabel=readiness.ready?'BEGIN RESEARCH':`CANNOT BEGIN · ${missing?.label||'MISSING CAPABILITY'}`;",
"const missing=readiness.rows.find(row=>!row.ready), actionLabel=readiness.ready?'BEGIN RESEARCH':`CANNOT BEGIN · ${missing?.label||'MISSING CAPABILITY'}`, opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity';",
'opportunity flag in target modal')
e=once(e,
"<div class=\"arx-modal-actions single\"><button data-arx-action=\"complete-target\" data-id=\"${target.id}\" ${!readiness.ready?'disabled':''}>${escapeHtml(actionLabel)}</button></div>",
"<div class=\"arx-modal-actions ${opportunity?'':'single'}\">${opportunity?`<button class=\"ghost\" data-arx-action=\"cancel-opportunity\" data-id=\"${target.id}\">DECLINE</button>`:''}<button data-arx-action=\"complete-target\" data-id=\"${target.id}\" ${!readiness.ready?'disabled':''}>${escapeHtml(actionLabel)}</button></div>",
'decline at opportunity site')

# Wildlife observation copy: badge already communicates the new observation.
e=once(e,
"<p class=\"arx-observation-note\">${firstIndividual?`A new individual observation added ${wildlifeObservationData()} data points. Its glowing chart ring is now cleared.`:'This is the same animal or school already recorded during this expedition, so no additional data were added.'}</p>",
"${firstIndividual?'':`<p class=\"arx-observation-note\">This is the same animal or school already recorded during this expedition, so no additional data were added.</p>`}",
'simplify wildlife observation message')

# Helicopter food resupply at 3x port price.
heli=r'''  function helicopterFoodStatus(){
    const ship=vessel(),resources=callbacks.getResources?.()||{fuel:100,food:100},available=ship.helidecks>0&&equipmentOperational('manned-helicopter'),steps=Math.max(0,Math.ceil((100-resources.food)/10)),cost=steps*foodStepCost(ship)*3;
    return{ship,resources,available,steps,cost};
  }
  function helicopterFoodRun(){
    const status=helicopterFoodStatus();if(!status.available||status.steps<=0||state.money<status.cost)return false;
    adjustMoney(-status.cost);callbacks.setResources?.({fuel:status.resources.fuel,food:100});state.helicopterFoodReminderShown=false;addLog(`Helicopter provision run completed · ${cash(status.cost)} · food stores full.`);toast(`HELICOPTER RESUPPLY COMPLETE · FOOD 100% · ${cash(status.cost)}`);changed({port:false});openVessel();return true;
  }
  function maybeHelicopterFoodReminder(){
    const status=helicopterFoodStatus();if(status.resources.food>20){state.helicopterFoodReminderShown=false;return false;}if(!status.available||state.port||state.helicopterFoodReminderShown||root?.querySelector('.arx-modal.open'))return false;
    state.helicopterFoodReminderShown=true;const modal=root?.querySelector('#arx-vessel-modal');if(!modal)return false;modal.innerHTML=`<div class="arx-modal-card arx-target-card"><button class="arx-close" data-arx-action="dismiss-helicopter-food">×</button><small>LOW FOOD · HELICOPTER AVAILABLE</small><h2>Fly a provision run?</h2><p>Your research helicopter can collect provisions without returning the vessel to port. Remote food costs three times the normal port price.</p><div class="arx-target-facts compact"><span><small>FOOD NOW</small><b>${Math.ceil(status.resources.food)}%</b></span><span><small>AFTER FLIGHT</small><b>100%</b></span><span><small>FLIGHT COST</small><b>${cash(status.cost)}</b></span></div><div class="arx-modal-actions"><button class="ghost" data-arx-action="dismiss-helicopter-food">NOT NOW</button><button data-arx-action="helicopter-food" ${state.money<status.cost?'disabled':''}>SEND HELICOPTER</button></div></div>`;modal.classList.add('open');changed({port:false});return true;
  }
'''
e=once(e,"  function vesselOverviewMarkup(inPort=false) {",heli+"  function vesselOverviewMarkup(inPort=false) {",'helicopter food functions')
# add button to vessel overview
old_line="""    const equipmentTiles=installed.map(item=>`<div class=\"arx-dashboard-thumb equipment ${equipmentOperational(item.id)?'':'inoperable'}\"><img src=\"${escapeHtml(item.media?.src||MEDIA.local.src)}\" alt=\"\"><span>${escapeHtml(item.name)}</span></div>`).join('');
    return `<div class=\"arx-vessel-overview\"><header>"""
new_line="""    const equipmentTiles=installed.map(item=>`<div class=\"arx-dashboard-thumb equipment ${equipmentOperational(item.id)?'':'inoperable'}\"><img src=\"${escapeHtml(item.media?.src||MEDIA.local.src)}\" alt=\"\"><span>${escapeHtml(item.name)}</span></div>`).join(''),heli=helicopterFoodStatus(),heliPanel=heli.available?`<div class=\"arx-heli-resupply\"><span><b>HELICOPTER PROVISION RUN</b><small>Food delivered anywhere at 3× the normal port price.</small></span><button data-arx-action=\"helicopter-food\" ${heli.steps<=0||state.money<heli.cost?'disabled':''}>${heli.steps<=0?'FOOD STORES FULL':`RESUPPLY FOOD TO 100% · ${cash(heli.cost)}`}</button></div>`:'';
    return `<div class=\"arx-vessel-overview\"><header>"""
e=once(e,old_line,new_line,'helicopter vessel panel variables')
e=once(e,"</div><div class=\"arx-vessel-columns\"><section><h3>Scientists aboard", "</div>${heliPanel}<div class=\"arx-vessel-columns\"><section><h3>Scientists aboard",'helicopter panel markup')

# Action handlers for helicopter.
e=once(e,"else if (action==='fuel'||action==='food'||action==='supplies') buyResource(action);",
"else if (action==='fuel'||action==='food'||action==='supplies') buyResource(action);\n    else if (action==='helicopter-food') helicopterFoodRun();\n    else if (action==='dismiss-helicopter-food') root.querySelector('#arx-vessel-modal')?.classList.remove('open');",'helicopter actions')
# Try reminder continuously while low, so an existing modal at the threshold does not suppress it forever.
e=once(e,"if(environment?.source==='sailing')maybeOfferProfessorGrant(environment);\n    if (state.data>=DATA_GAUGE_MAX)",
"if(environment?.source==='sailing')maybeOfferProfessorGrant(environment);\n    maybeHelicopterFoodReminder();\n    if (state.data>=DATA_GAUGE_MAX)", 'low food reminder tick')
# expose reminder API
e=once(e,"restoreSnapshot:restoreCheckpoint,ensureMinimumSupplies,maybeSpawnOpportunity,isWildlifeObserved:",
"restoreSnapshot:restoreCheckpoint,ensureMinimumSupplies,maybeSpawnOpportunity,maybeHelicopterFoodReminder,isWildlifeObserved:", 'expose helicopter reminder')

# Store imagery and portrait layout plus helicopter panel styling.
css1=""".arx-store-details .arx-detail-split>.arx-media img{object-fit:contain!important;background:#123d51}.arx-character-summary img{flex:0 0 auto;width:96px;height:96px;object-fit:cover;border-radius:10px}.arx-character-summary>div{min-width:0}.arx-character-summary b,.arx-character-summary span,.arx-character-summary small{display:block}.arx-heli-resupply{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;margin:12px 0;padding:11px;border:1px solid rgba(246,211,101,.32);border-radius:9px;background:rgba(246,211,101,.08)}.arx-heli-resupply b,.arx-heli-resupply small{display:block}.arx-heli-resupply b{color:#f6d365;font-size:9px}.arx-heli-resupply small{margin-top:3px;color:#9fc3cd;font-size:7px}.arx-heli-resupply button{width:auto!important;min-width:210px}@media(max-width:760px) and (orientation:portrait){.arx-character-summary{display:grid!important;grid-template-columns:1fr!important;justify-items:center!important;text-align:center!important}.arx-character-summary>div{width:100%}.arx-heli-resupply{grid-template-columns:1fr}.arx-heli-resupply button{width:100%!important;min-width:0}}@media(max-width:900px) and (orientation:landscape){.arx-store-details .arx-detail-split>.arx-media{height:min(230px,48vh)!important}.arx-store-details .arx-detail-split>.arx-media img{object-fit:contain!important}}"""
e=once(e,"    style.textContent+=`\n      .arx-operation-subhead", "    style.textContent+=`"+css1+"`;\n    style.textContent+=`\n      .arx-operation-subhead",'store/portrait/helicopter styles')

# Details expansion should anchor the summary at the top, leaving the new content below it.
e=once(e,"openStoreDetail=detail.dataset.arxStoreDetails;\n      detail.closest('.arx-port-card')?.querySelectorAll('[data-arx-store-details][open]').forEach(other=>{if(other!==detail)other.open=false;});",
"openStoreDetail=detail.dataset.arxStoreDetails;\n      detail.closest('.arx-port-card')?.querySelectorAll('[data-arx-store-details][open]').forEach(other=>{if(other!==detail)other.open=false;});\n      requestAnimationFrame(()=>detail.scrollIntoView({block:'start',behavior:'smooth'}));",
'details expand downward')

ep.write_text(e)

# ---------------- index.html ----------------
ip=Path('index.html'); h=ip.read_text()
h=once(h,
'''      <canvas id="minimap" width="300" height="300" aria-label="Open navigation chart"></canvas>\n      <div class="minimap-nav-details">\n        <span><small>POSITION</small><b id="mini-position">—</b></span>\n        <span><small>COURSE</small><b id="mini-course">STOPPED</b></span>\n        <span><small>SEA ICE</small><b id="mini-ice">OPEN WATER</b></span>\n        <span><small>WEATHER</small><b id="mini-weather">CLEAR</b></span>\n      </div>''',
'''      <canvas id="minimap" width="300" height="300" aria-label="Open navigation chart"></canvas>\n      <div class="minimap-zoom-controls" aria-label="Navigation chart zoom controls"><button id="mini-zoom-out" type="button" aria-label="Zoom navigation chart out">−</button><span id="mini-zoom-level">100%</span><button id="mini-zoom-in" type="button" aria-label="Zoom navigation chart in">+</button></div>\n      <div class="minimap-nav-details">\n        <span><small>POSITION</small><b id="mini-position">—</b></span>\n        <span><small>CHART ZOOM</small><b id="mini-course">100%</b></span>\n        <span><small>ICE CONDITIONS:</small><b id="mini-ice">OPEN WATER</b></span>\n        <span><small>WEATHER</small><b id="mini-weather">CLEAR</b></span>\n      </div>''',
'minimap controls and labels')
h=re.sub(r'game\.js\?v=[^\"]+','game.js?v=expedition-23e-polish',h,count=1)
h=re.sub(r'expedition\.js\?v=[^\"]+','expedition.js?v=expedition-23e-polish',h,count=1)
h=re.sub(r'style\.css\?v=[^\"]+','style.css?v=expedition-23e-polish',h,count=1)
ip.write_text(h)

# ---------------- style.css ----------------
sp=Path('style.css'); s=sp.read_text()
s += r'''

/* Expedition 23e: larger overview chart and phone navigation layout. */
.minimap-zoom-controls{display:none}
.minimap.expanded{grid-template-rows:auto minmax(0,1fr) auto auto!important}
.minimap.expanded .minimap-heading{display:grid!important;grid-template-columns:1fr!important;justify-items:center!important;text-align:center!important;width:min(760px,92vw)!important;padding:0 42px 7px!important}
.minimap.expanded .minimap-heading small{grid-row:1}.minimap.expanded .minimap-heading b{grid-row:2;margin-top:4px;font-size:12px!important;color:#f6d365!important}
.minimap.expanded .minimap-zoom-controls{display:flex!important;align-items:center;justify-content:center;gap:7px;margin-top:8px}
.minimap-zoom-controls button{width:38px;height:32px;border:1px solid rgba(166,230,244,.28);border-radius:7px;background:rgba(30,79,96,.55);color:#eafaff;font-size:19px}.minimap-zoom-controls button:disabled{opacity:.35}.minimap-zoom-controls span{min-width:58px;color:#f6d365;font-size:9px;font-weight:900;text-align:center}
.minimap.expanded .minimap-nav-details{box-sizing:border-box!important;padding:0 4px!important}
@media (pointer:coarse) and (max-width:900px){
  .minimap:not(.expanded){width:129px!important;height:129px!important}
  .minimap:not(.expanded) #minimap{width:129px!important;height:129px!important}
}
@media (pointer:coarse) and (max-width:900px) and (orientation:portrait){
  .minimap.expanded{padding:12px!important}
  .minimap.expanded #minimap{width:min(92vw,56vh,500px)!important;height:min(92vw,56vh,500px)!important}
  .minimap.expanded .minimap-nav-details{width:min(94vw,520px)!important;grid-template-columns:1fr 1fr!important;gap:7px!important;margin-top:7px!important}
  .minimap.expanded .minimap-nav-details span{min-width:0!important;padding:8px 5px!important}
}
@media (pointer:coarse) and (max-width:900px) and (orientation:landscape){
  .minimap.expanded{padding:max(8px,env(safe-area-inset-top)) max(12px,env(safe-area-inset-right)) max(8px,env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left))!important;grid-template-columns:minmax(0,1fr) minmax(180px,24vw)!important;grid-template-rows:auto minmax(0,1fr) auto!important;column-gap:12px!important}
  .minimap.expanded .minimap-heading{grid-column:1!important;grid-row:1!important;width:100%!important;padding:0 36px 4px!important}
  .minimap.expanded #minimap{grid-column:1!important;grid-row:2 / 4!important;width:min(78vh,calc(100vw - 230px))!important;height:min(78vh,calc(100vw - 230px))!important;max-width:100%!important;align-self:center!important}
  .minimap.expanded .minimap-zoom-controls{grid-column:2!important;grid-row:1!important;align-self:end!important;margin:0 0 8px!important}
  .minimap.expanded .minimap-nav-details{grid-column:2!important;grid-row:2 / 4!important;width:100%!important;grid-template-columns:1fr!important;align-content:center!important;gap:7px!important;margin:0!important;min-width:0!important}
  .minimap.expanded .minimap-nav-details span{min-width:0!important;padding:8px 5px!important;overflow:hidden!important}
  .minimap.expanded .minimap-nav-details b{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
}
'''
sp.write_text(s)

print('Expedition 23e polish patch applied')
