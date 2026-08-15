from pathlib import Path

p=Path('game.js'); s=p.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected 1 match, found {n}')
    s=s.replace(old,new)

once("let wakeFloeClock=0,wakeTrailClock=0,miniLastDraw=0,miniZoomLevel=1,packPushToastDay=-1,wildlifeEncounterClock=0,wildlifeEncounterSerial=0;",
     "let wakeFloeClock=0,wakeTrailClock=0,miniLastDraw=0,miniZoomLevel=1,floeUpdateAccumulator=0,researchEnvCache=null,researchEnvCacheAt=0,researchEnvCacheX=Infinity,researchEnvCacheY=Infinity,packPushToastDay=-1,wildlifeEncounterClock=0,wildlifeEncounterSerial=0;",
     'performance cache state')

old="""  function researchEnvironment(weather=currentWeather()){
    const position=unpolar(state.x,state.y),coastDistanceKm=coastDistance(state.x,state.y,120),landSectors=[];
    for(let sector=0;sector<12;sector++){const angle=sector*Math.PI/6;let landSeen=false;for(const radius of[10,24,45])if(isLand(state.x+Math.cos(angle)*radius,state.y+Math.sin(angle)*radius)){landSeen=true;break;}landSectors.push(landSeen);}
    const landHits=landSectors.filter(Boolean).length,opposed=landSectors.slice(0,6).filter((value,index)=>value&&landSectors[index+6]).length;
    const fjordScore=Math.max(0,Math.min(1,landHits/12*.7+opposed/6*.75+(coastDistanceKm<35?.18:0)));
    const ice=iceTypeAt(state.x,state.y),iceThickness=ice==='fast'?1:(ice==='packed'||ice==='cracked')?iceThicknessAt(state.x,state.y):0,packEdge=packIceEdge(position.lon),iceEdge=ice==='marginal'||ice==='fast'||Math.abs(position.lat-packEdge)<2.8;return{position,ice,iceThickness,iceEdge,ramming:state.ramming,location:locationName(position.lat,position.lon),weather,coastDistanceKm,coastal:coastDistanceKm<=85,fjord:fjordScore>=.48,fjordScore};
  }"""
new="""  function researchEnvironment(weather=currentWeather()){
    const now=performance.now(),moved=Math.hypot(state.x-researchEnvCacheX,state.y-researchEnvCacheY);
    if(!researchEnvCache||now-researchEnvCacheAt>900||moved>7){
      const position=unpolar(state.x,state.y),coastDistanceKm=coastDistance(state.x,state.y,120),landSectors=[];
      for(let sector=0;sector<12;sector++){const angle=sector*Math.PI/6;let landSeen=false;for(const radius of[10,24,45])if(isLand(state.x+Math.cos(angle)*radius,state.y+Math.sin(angle)*radius)){landSeen=true;break;}landSectors.push(landSeen);}
      const landHits=landSectors.filter(Boolean).length,opposed=landSectors.slice(0,6).filter((value,index)=>value&&landSectors[index+6]).length,fjordScore=Math.max(0,Math.min(1,landHits/12*.7+opposed/6*.75+(coastDistanceKm<35?.18:0)));
      const ice=iceTypeAt(state.x,state.y),iceThickness=ice==='fast'?1:(ice==='packed'||ice==='cracked')?iceThicknessAt(state.x,state.y):0,packEdge=packIceEdge(position.lon),iceEdge=ice==='marginal'||ice==='fast'||Math.abs(position.lat-packEdge)<2.8;
      researchEnvCache={position,ice,iceThickness,iceEdge,location:locationName(position.lat,position.lon),coastDistanceKm,coastal:coastDistanceKm<=85,fjord:fjordScore>=.48,fjordScore};researchEnvCacheAt=now;researchEnvCacheX=state.x;researchEnvCacheY=state.y;
    }
    return{...researchEnvCache,ramming:state.ramming,weather};
  }"""
once(old,new,'cache expensive research environment')

once("const precisionNav=commanded&&(state.precisionNav||dist<75||coastDistance(state.x,state.y,42)<30);",
     "const precisionNav=commanded&&(state.precisionNav||dist<75);",
     'avoid per-frame coast scan')

once("if(!paused){updateFloes(dt/zoomLevel,minX,maxX,minY,maxY);updateWakeFloes(dt/zoomLevel);updateWakeTrail(dt/zoomLevel);updateWildlifeEncounters(dt);updateFishSchools(dt/zoomLevel);updateWildlife(dt/zoomLevel);updateNpcVessels(dt/zoomLevel);}",
     "if(!paused){floeUpdateAccumulator+=dt/zoomLevel;if(floeUpdateAccumulator>=.07){updateFloes(Math.min(.14,floeUpdateAccumulator),minX,maxX,minY,maxY);floeUpdateAccumulator=0;}updateWakeFloes(dt/zoomLevel);updateWakeTrail(dt/zoomLevel);updateWildlifeEncounters(dt);updateFishSchools(dt/zoomLevel);updateWildlife(dt/zoomLevel);updateNpcVessels(dt/zoomLevel);}",
     'throttle heavy floe physics')

p.write_text(s)
print('Runtime environment and floe calculations throttled without reducing vessel frame rate')
