(() => {
  'use strict';
  const canvas=document.getElementById('map'),ctx=canvas.getContext('2d');
  const miniCanvas=document.getElementById('minimap'),mini=miniCanvas.getContext('2d');
  const lightCanvas=document.createElement('canvas'),light=lightCanvas.getContext('2d');
  const oceanCanvas=document.createElement('canvas'),ocean=oceanCanvas.getContext('2d');
  const ui={position:document.getElementById('position'),speed:document.getElementById('speed'),progress:document.getElementById('mission-progress'),welcome:document.getElementById('welcome'),toast:document.getElementById('toast'),resourceWarning:document.getElementById('resource-warning'),miniLocation:document.getElementById('mini-location'),zoomLevel:document.getElementById('zoom-level'),zoomIn:document.getElementById('zoom-in'),zoomOut:document.getElementById('zoom-out'),scaleDistance:document.getElementById('scale-distance'),calendarDate:document.getElementById('calendar-date'),seasonProgress:document.getElementById('season-progress'),seasonNote:document.getElementById('season-note'),iceCondition:document.getElementById('ice-condition'),weatherValue:document.getElementById('weather-value'),fuelValue:document.getElementById('fuel-value'),fuelLevel:document.getElementById('fuel-level'),foodValue:document.getElementById('food-value'),foodLevel:document.getElementById('food-level'),timeSpeed:document.getElementById('time-speed'),vesselButton:document.getElementById('vessel-button'),vesselButtonImage:document.getElementById('vessel-button-image'),gameOver:document.getElementById('game-over'),gameOverTitle:document.getElementById('game-over-title'),gameOverMessage:document.getElementById('game-over-message')};
  const compass=document.querySelector('.compass'),compassNorth=compass.querySelector('span'),compassNeedle=compass.querySelector('i');
  const brandShip=document.querySelector('.brand small');
  const research=window.ArcticResearch||null;
  const SMALL_PASSENGER_SVG='data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360"><rect width="900" height="360" fill="#dcecf0"/><path d="M105 250h665l-78 65H182z" fill="#173c50"/><path d="M220 160h420l45 90H175z" fill="#f7faf9" stroke="#315f70" stroke-width="8"/><path d="M275 92h250l80 68H230z" fill="#f7faf9" stroke="#315f70" stroke-width="8"/><path d="M360 48h105l28 44H330z" fill="#f7faf9" stroke="#315f70" stroke-width="8"/><rect x="390" y="20" width="18" height="45" fill="#315f70"/><path d="M408 25l80 22" stroke="#315f70" stroke-width="7"/><g fill="#5cb1d0">${Array.from({length:8},(_,i)=>`<rect x="${250+i*45}" y="118" width="28" height="20" rx="5"/>`).join('')}${Array.from({length:11},(_,i)=>`<rect x="${205+i*43}" y="190" width="28" height="22" rx="5"/>`).join('')}</g><path d="M160 315h580" stroke="#69b4c9" stroke-width="8" stroke-linecap="round"/><text x="450" y="342" text-anchor="middle" font-family="sans-serif" font-size="24" fill="#315f70">SMALL ARCTIC PASSENGER VESSEL</text></svg>`);

  // Arctic terrain overview + high-resolution on-demand tiles. The overview
  // keeps the minimap fast. The main chart requests only the 256 km tiles that
  // intersect the current viewport, at 1024 px per tile (~125 m/pixel request
  // spacing; the underlying IBCAO grid remains the limiting resolution).
  // PNG is intentional here: it avoids the JPEG grain that became obvious when
  // the single 2048 px overview was enlarged on the main chart.
  const TERRAIN_EXTENT_KM=2910;
  const TERRAIN_TEXTURE_SIZE=2048;
  const TERRAIN_TILE_KM=128;
  const TERRAIN_TILE_PIXELS=1024;
  const TERRAIN_MASK_PIXELS=512;
  const TERRAIN_TILE_CACHE_LIMIT=32;
  const terrainTexture=new Image();
  const terrainTileCache=new Map();
  let terrainTextureReady=false,terrainTextureFallbackTried=false,terrainTileClock=0;
  const terrainWmsUrl=(year,layer)=>`https://wms.gebco.net/${year}/north-polar/mapserv?BBOX=-2910000%2C-2910000%2C2910000%2C2910000&crs=EPSG%3A3996&format=image%2Fjpeg&height=${TERRAIN_TEXTURE_SIZE}&layers=${layer}&request=getmap&service=wms&version=1.3.0&width=${TERRAIN_TEXTURE_SIZE}`;
  const TERRAIN_PRIMARY_URL=terrainWmsUrl(2024,'GEBCO_NORTH_POLAR_VIEW_bed_2024');
  const TERRAIN_FALLBACK_URL=terrainWmsUrl(2022,'GEBCO_NORTH_POLAR_VIEW_bed_2022');
  terrainTexture.decoding='async';
  terrainTexture.onload=()=>{terrainTextureReady=true;};
  terrainTexture.onerror=()=>{terrainTextureReady=false;if(!terrainTextureFallbackTried){terrainTextureFallbackTried=true;terrainTexture.src=TERRAIN_FALLBACK_URL;}};
  terrainTexture.src=TERRAIN_PRIMARY_URL;



  // WGS 84 / IBCAO Polar Stereographic (EPSG:3996), expressed in km in the
  // game world. Keeping the game in the same projection as IBCAO removes the
  // small radial mismatch that was visible when the raster was laid over the
  // older approximate Arctic geometry. Game +y is opposite EPSG northing so
  // longitude orientation remains the same as the original chart code.
  const PS_A=6378137,PS_F=1/298.257223563,PS_E=Math.sqrt(PS_F*(2-PS_F)),PS_LAT_TS=75*Math.PI/180;
  const psT=phi=>Math.tan(Math.PI/4-phi/2)/Math.pow((1-PS_E*Math.sin(phi))/(1+PS_E*Math.sin(phi)),PS_E/2);
  const PS_MC=Math.cos(PS_LAT_TS)/Math.sqrt(1-PS_E*PS_E*Math.sin(PS_LAT_TS)**2),PS_TC=psT(PS_LAT_TS);
  const polar=(lat,lon)=>{if(lat>=89.999999)return{x:0,y:0,lat,lon};const phi=lat*Math.PI/180,a=lon*Math.PI/180,r=PS_A*PS_MC*psT(phi)/PS_TC/1000;return{x:r*Math.sin(a),y:r*Math.cos(a),lat,lon};};
  const unpolar=(x,y)=>{const rho=Math.hypot(x,y)*1000;if(rho<1e-7)return{lat:90,lon:0};const t=rho*PS_TC/(PS_A*PS_MC);let phi=Math.PI/2-2*Math.atan(t);for(let i=0;i<7;i++)phi=Math.PI/2-2*Math.atan(t*Math.pow((1-PS_E*Math.sin(phi))/(1+PS_E*Math.sin(phi)),PS_E/2));return{lat:phi*180/Math.PI,lon:Math.atan2(x,y)*180/Math.PI};};
  const ll=points=>points.map(([lat,lon])=>polar(lat,lon));
  const home=polar(78.23,14.5),port=polar(78.23,15.65);
  const state={x:home.x,y:home.y,tx:home.x,ty:home.y,angle:Math.PI,moving:false,commandActive:false,travelled:0,seasonDay:0,year:2026,frozen:false,fuel:100,food:100,portDestination:null,dockedPort:null,gameOver:false,fogClearDays:7,ramming:false,ramClock:0,targetOnLand:false,started:false};
  let width=0,height=0,dpr=1,baseScale=4.6,zoomLevel=1,scale=4.6,last=performance.now(),toastTimer,announcedWeatherEvent=null,oceanPattern=null,brokenIceDriftClock=0;
  const KNOT_TO_WORLD_SPEED=14,iceFloes=[],wakeFloes=[],brokenIceChannels=[],brokenIceGrid=new Map(),BROKEN_ICE_CELL=32;
  let wakeFloeClock=0,packPushToastDay=-1,wildlifeEncounterClock=0,wildlifeEncounterSerial=0;
  const CHECKPOINT_KEY='arctic-research-last-port';
  let checkpoint={x:home.x,y:home.y,seasonDay:0,year:2026,travelled:0,angle:Math.PI,portName:'LONGYEARBYEN'};
  let currentPortCity=null,researchOpportunityClock=0,lastResearchNavigation=0,pendingResearchTargetId=null,startFlowPending=false,npcUpdateAccumulator=0;
  const RESEARCH_INTERACTION_KM=10,observedWildlifeFallback=new Set(),resourceAlertState={fuel:false,food:false};
  const GLACIER_SITES=[
    {name:'Nordenskiöldbreen',lat:78.666667,lon:17.116667},{name:'Tunabreen',lat:78.50411,lon:17.46552},{name:'Negribreen',lat:78.56382,lon:19.14997},
    {name:'Monacobreen',lat:79.4,lon:12.5667},{name:'Fjortende Julibreen',lat:79.1122,lon:11.9775},{name:'Blomstrandbreen',lat:79.0319,lon:12.1764},
    {name:'Kronebreen',lat:78.83333,lon:13.33333},{name:'Hansbreen',lat:77.07481,lon:15.65048},{name:'Hornbreen',lat:77.06618,lon:16.68931},{name:'Bråsvellbreen',lat:79.33863,lon:23.57491}
  ];

  const sound=(()=>{
    let ac=null,waveSource=null,waveGain=null,lastCrack=0,lastAnimal=0;
    const ensure=()=>{if(ac)return ac;try{ac=new(window.AudioContext||window.webkitAudioContext)();const seconds=2,buffer=ac.createBuffer(1,ac.sampleRate*seconds,ac.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*(.45+.35*Math.sin(i/2400));waveSource=ac.createBufferSource();waveSource.buffer=buffer;waveSource.loop=true;const filter=ac.createBiquadFilter();filter.type='lowpass';filter.frequency.value=700;waveGain=ac.createGain();waveGain.gain.value=0;waveSource.connect(filter).connect(waveGain).connect(ac.destination);waveSource.start();}catch(e){}return ac;};
    const unlock=()=>{const c=ensure();if(c?.state==='suspended')c.resume();};
    const tone=(freq=440,duration=.15,gain=.08,when=0,type='sine')=>{const c=ensure();if(!c)return;const o=c.createOscillator(),g=c.createGain();o.type=type;o.frequency.setValueAtTime(freq,c.currentTime+when);g.gain.setValueAtTime(.0001,c.currentTime+when);g.gain.exponentialRampToValueAtTime(gain,c.currentTime+when+.012);g.gain.exponentialRampToValueAtTime(.0001,c.currentTime+when+duration);o.connect(g).connect(c.destination);o.start(c.currentTime+when);o.stop(c.currentTime+when+duration+.02);};
    const burst=(duration=.3,gain=.06,low=300,high=2200,when=0)=>{const c=ensure();if(!c)return;const b=c.createBuffer(1,Math.ceil(c.sampleRate*duration),c.sampleRate),d=b.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*(1-i/d.length);const src=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain();src.buffer=b;f.type='bandpass';f.frequency.value=(low+high)/2;f.Q.value=.7;g.gain.value=gain;src.connect(f).connect(g).connect(c.destination);src.start(c.currentTime+when);};
    const play=(type)=>{if(!ac)return;switch(type){case'cash-in':burst(.055,.055,1800,5200);tone(1250,.045,.04,.01,'square');tone(1650,.07,.035,.07,'square');burst(.08,.035,900,2800,.14);break;case'cash-out':burst(.055,.05,1400,4200);tone(920,.05,.035,.01,'square');tone(620,.09,.035,.08,'square');burst(.07,.03,700,2200,.16);break;case'data':tone(980,.07,.035,0,'square');tone(1260,.06,.025,.07,'square');break;case'paper-accepted':for(let i=0;i<7;i++)burst(.35,.035,500,3500,i*.07);tone(523,.5,.07,.05);tone(659,.5,.06,.12);tone(784,.6,.06,.2);break;case'paper-rejected':tone(430,.5,.06);tone(350,.6,.055,.15);tone(270,.75,.05,.3);break;case'port':tone(92,1.7,.085,0,'sawtooth');tone(138,1.6,.05,.03,'sine');tone(86,1.4,.07,1.95,'sawtooth');tone(129,1.3,.045,1.98,'sine');tone(740,.22,.045,.42,'sine');tone(1120,.18,.035,.64,'sine');tone(820,.22,.04,1.02,'sine');tone(1260,.18,.032,1.24,'sine');break;case'ice':burst(.18,.09,900,4500);tone(150,.12,.04,0,'square');break;case'whale':tone(145,.9,.045,0,'sine');tone(105,1.2,.035,.4,'sine');break;case'bird':tone(1800,.08,.03);tone(2350,.08,.025,.1);tone(1600,.09,.02,.2);break;case'seal':burst(.16,.035,500,1700);tone(330,.16,.025,.04,'square');break;case'mammal':tone(520,.12,.025,0,'square');tone(390,.15,.02,.13,'square');break;case'fish':tone(1150,.025,.012);tone(900,.025,.01,.05);break;}}
    const nearbyAnimal=()=>{let best=null,dist=45;try{forEachWildlifeVisual((entity,species,category,w)=>{const d=Math.hypot(w.x-state.x,w.y-state.y);if(d<dist){dist=d;best=category;}});}catch(e){}return best;};
    const update=()=>{if(!ac)return;const now=performance.now();if(waveGain)waveGain.gain.setTargetAtTime(state.moving&&!state.ramming?.055:0,ac.currentTime,.35);if(state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};
    return{unlock,play,update};
  })();

  // Simplified but geographically ordered coastlines and the major islands
  // that define navigable Arctic waters.
  const legacyLand=[
    {name:'NORWAY',color:'#b2cfb7',label:[70.7,20],pts:ll([[60,4],[60,32],[69,31],[71,28],[71.2,24],[70.1,19],[69,16],[67.5,14],[65,12],[62,7]])},
    {name:'RUSSIA',color:'#b8d4bd',label:[69,88],pts:ll([[60,31],[60,180],[66,180],[68.3,176],[69.6,170],[70,160],[71.5,150],[72.8,140],[73.7,125],[73.3,112],[74.5,100],[76.5,95],[75.4,83],[73.6,73],[72.8,61],[70.8,55],[69.2,46],[68,40],[69,33]])},
    {name:'ALASKA',color:'#c2d9bc',label:[67,-157],pts:ll([[60,180],[60,-141],[69,-141],[70.5,-145],[71.4,-153],[71.3,-160],[70.8,-166],[69.5,-168],[68.8,-164],[66.2,-166],[65,-170],[66,180]])},
    {name:'CANADA',color:'#b8d4bd',label:[67,-105],pts:ll([[60,-141],[60,-52],[65,-52],[67,-64],[68,-72],[69,-79],[68.5,-86],[69,-95],[70,-104],[69.5,-114],[69,-124],[70,-133],[69,-141]])},
    {name:'GREENLAND',color:'#d8e9dc',label:[74,-41],pts:ll([[59.8,-43],[61,-48],[65,-53],[69,-55],[73,-56],[77,-70],[80,-67],[82,-54],[83,-35],[81.5,-20],[78,-18],[74,-20],[70,-23],[66,-32],[62,-39]])},
    {name:'ICELAND',color:'#bfd7be',label:[65,-19],pts:ll([[63.3,-24],[64,-14],[66,-13],[67,-18],[66,-24],[64.5,-25]])},
    {name:'SVALBARD',color:'#d1e2cc',label:[79,19],pts:ll([[76.4,10],[77,8],[78.2,9],[79.5,10],[80.8,16],[80.5,23],[79.8,28],[78.7,25],[77.5,22],[76.5,17]])},
    {name:'NOVAYA ZEMLYA',color:'#c8ddc4',label:[74,56],pts:ll([[70.5,52],[72.5,53],[75,56],[77,62],[76,68],[73.5,58],[71,56]])},
    {name:'FRANZ JOSEF LAND',color:'#d4e4cf',pts:ll([[79,43],[80,42],[81.8,48],[82.2,60],[81,65],[79.5,58]])},
    {name:'SEVERNAYA ZEMLYA',color:'#c9ddc5',pts:ll([[77.5,90],[78.5,93],[81,95],[82,104],[80,108],[78,103]])},
    {name:'NEW SIBERIAN IS.',color:'#c9ddc5',pts:ll([[74,135],[75.5,137],[76,150],[74,153],[73,142]])},
    {name:'WRANGEL I.',color:'#c9ddc5',pts:ll([[70,176],[71.7,177],[72,169],[70.5,166]])},
    {name:'ELLESMERE I.',color:'#c9ddc5',pts:ll([[76,-88],[78,-92],[81,-90],[83,-76],[82,-62],[79,-66]])},
    {name:'DEVON I.',color:'#c9ddc5',pts:ll([[74,-92],[75,-84],[76,-78],[75,-68],[73.5,-80]])},
    {name:'BAFFIN I.',color:'#c3d9bf',pts:ll([[62,-78],[65,-72],[69,-67],[73,-74],[72,-85],[68,-89],[64,-84]])},
    {name:'VICTORIA I.',color:'#c9ddc5',pts:ll([[68,-115],[70,-111],[73,-105],[72,-98],[69,-101]])},
    {name:'BANKS I.',color:'#c9ddc5',pts:ll([[70,-126],[73,-125],[74,-119],[72,-115],[70,-119]])}
  ];
  const MIN_LAT=63.25;
  const smoothCoast=pts=>pts.flatMap((point,i)=>{const next=pts[(i+1)%pts.length],q={x:point.x*.84+next.x*.16,y:point.y*.84+next.y*.16},r={x:point.x*.16+next.x*.84,y:point.y*.16+next.y*.84};return[q,r].map(p=>({...p,...unpolar(p.x,p.y)}));});
  const land=ARCTIC_LAND.map(ring=>{
    const pts=smoothCoast(ll(ring)),xs=pts.map(p=>p.x),ys=pts.map(p=>p.y);
    return{name:'',color:'#c5dcc4',pts,minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys)};
  });
  const svalbardLand=land.filter(shape=>shape.pts.some(p=>p.lat>=76&&p.lat<=81.5&&p.lon>=5&&p.lon<=36));
  const COAST_CELL=100,coastGrid=new Map();
  const coastKey=(gx,gy)=>`${gx},${gy}`;
  land.forEach(shape=>{for(let i=0;i<shape.pts.length;i++){const a=shape.pts[i],b=shape.pts[(i+1)%shape.pts.length];if(Math.abs(a.lat-MIN_LAT)<.02&&Math.abs(b.lat-MIN_LAT)<.02)continue;const segment={a,b};const x0=Math.floor(Math.min(a.x,b.x)/COAST_CELL),x1=Math.floor(Math.max(a.x,b.x)/COAST_CELL),y0=Math.floor(Math.min(a.y,b.y)/COAST_CELL),y1=Math.floor(Math.max(a.y,b.y)/COAST_CELL);for(let gx=x0;gx<=x1;gx++)for(let gy=y0;gy<=y1;gy++){const key=coastKey(gx,gy);if(!coastGrid.has(key))coastGrid.set(key,[]);coastGrid.get(key).push(segment);}}});
  const rivers=ARCTIC_RIVERS.map(river=>{const item={name:river.name,rank:river.rank,paths:river.paths.map(path=>ll(path))};const all=item.paths.flat();item.labelPoint=all.reduce((best,p)=>!best||p.lat>best.lat?p:best,null);return item;});
  const riverSegments=[];
  rivers.forEach(river=>river.paths.forEach(path=>{for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i];riverSegments.push({river,a,b,minX:Math.min(a.x,b.x)-4,maxX:Math.max(a.x,b.x)+4,minY:Math.min(a.y,b.y)-4,maxY:Math.max(a.y,b.y)+4});}}));
  const chartLabels=[
    // Countries and large land masses
    {name:'RUSSIA',lat:69.5,lon:95,kind:'country'},{name:'ALASKA',lat:67.5,lon:-153,kind:'country'},
    {name:'CANADA',lat:67.5,lon:-105,kind:'country'},{name:'GREENLAND',lat:73,lon:-42,kind:'country'},
    {name:'NORWAY',lat:69,lon:19,kind:'country'},{name:'ICELAND',lat:65,lon:-19,kind:'country'},
    // Islands and archipelagos
    {name:'SPITSBERGEN',lat:78.7,lon:16,kind:'land'},{name:'NORDAUSTLANDET',lat:79.8,lon:22.5,kind:'land'},
    {name:'EDGE\u00D8YA',lat:77.8,lon:22.5,kind:'land'},{name:'FRANZ JOSEF LAND',lat:80.7,lon:54,kind:'land'},
    {name:'NOVAYA ZEMLYA',lat:74.2,lon:56,kind:'land'},{name:'SEVERNAYA ZEMLYA',lat:79.5,lon:98,kind:'land'},
    {name:'NEW SIBERIAN ISLANDS',lat:75,lon:145,kind:'land'},{name:'WRANGEL ISLAND',lat:71.2,lon:-178,kind:'land'},
    {name:'ELLESMERE ISLAND',lat:79.5,lon:-78,kind:'land'},{name:'DEVON ISLAND',lat:75.2,lon:-85,kind:'land'},
    {name:'BAFFIN ISLAND',lat:68,lon:-72,kind:'land'},{name:'VICTORIA ISLAND',lat:71,lon:-110,kind:'land'},
    {name:'BANKS ISLAND',lat:73,lon:-122,kind:'land'},
    {name:'SVALBARD',lat:79,lon:20,kind:'land',size:450,minZoom:.3},
    {name:'Isfjorden',lat:78.23,lon:14.4,kind:'strait',size:50,minZoom:.3},
    // Smaller islands become visible only at closer chart scales
    {name:'PRINS KARLS FORLAND',lat:78.6,lon:11,kind:'land',size:85,minZoom:1.05},
    {name:'BARENTS\u00D8YA',lat:78.45,lon:21,kind:'land',size:50,minZoom:1.05},
    {name:'KONG KARLS LAND',lat:78.9,lon:28.5,kind:'land',size:40,minZoom:1.1},
    {name:'BJ\u00D8RN\u00D8YA',lat:74.45,lon:19,kind:'land',size:20,minZoom:1.15},
    {name:'HOPEN',lat:76.55,lon:25.1,kind:'land',size:12,minZoom:1.25},
    {name:'KVIT\u00D8YA',lat:80.1,lon:32.5,kind:'land',size:20,minZoom:1.2},
    {name:'MOFFEN',lat:80.0,lon:14.5,kind:'land',size:5,minZoom:1.5},
    {name:'KOLGUYEV ISLAND',lat:69.1,lon:49,kind:'land',size:80,minZoom:1.05},
    {name:'VAYGACH ISLAND',lat:70.3,lon:59,kind:'land',size:100,minZoom:1.05},
    {name:'KOTELNY ISLAND',lat:75.4,lon:140,kind:'land',size:230,minZoom:.9},
    {name:'BELKOVSKY ISLAND',lat:75.6,lon:135,kind:'land',size:50,minZoom:1.15},
    {name:'BENNETT ISLAND',lat:76.7,lon:149,kind:'land',size:30,minZoom:1.2},
    {name:'HENRIETTA ISLAND',lat:77.1,lon:156,kind:'land',size:12,minZoom:1.35},
    {name:'BIG DIOMEDE',lat:65.78,lon:-169.05,kind:'land',size:4,minZoom:1.5},
    {name:'LITTLE DIOMEDE',lat:65.76,lon:-168.95,kind:'land',size:3,minZoom:1.65},
    {name:'ST. LAWRENCE ISLAND',lat:63.65,lon:-170.3,kind:'land',size:145,minZoom:1.0},
    {name:'AXEL HEIBERG ISLAND',lat:79.5,lon:-91,kind:'land',size:370,minZoom:.8},
    {name:'PRINCE PATRICK ISLAND',lat:76.5,lon:-120,kind:'land',size:160,minZoom:.95},
    {name:'MELVILLE ISLAND',lat:75,lon:-111,kind:'land',size:320,minZoom:.85},
    {name:'BATHURST ISLAND',lat:76,lon:-100,kind:'land',size:190,minZoom:.95},
    {name:'CORNWALLIS ISLAND',lat:75,lon:-95,kind:'land',size:115,minZoom:1.0},
    {name:'SOMERSET ISLAND',lat:73.3,lon:-94,kind:'land',size:225,minZoom:.9},
    {name:'KING WILLIAM ISLAND',lat:69,lon:-98,kind:'land',size:125,minZoom:1.0},
    {name:'SOUTHAMPTON ISLAND',lat:64.5,lon:-84,kind:'land',size:340,minZoom:.85},
    {name:'JAN MAYEN',lat:70.98,lon:-8.55,kind:'land',size:38,minZoom:.75},
    {name:'PRINCE OF WALES ISLAND',lat:72.6,lon:-98.5,kind:'land',size:330,minZoom:.75},
    {name:'MACKENZIE KING ISLAND',lat:77.75,lon:-111.4,kind:'land',size:55,minZoom:1.0},
    {name:'ELLEF RINGNES ISLAND',lat:78.6,lon:-102.5,kind:'land',size:110,minZoom:.9},
    {name:'AMUNDSEN RINGNES ISLAND',lat:78.3,lon:-96.4,kind:'land',size:60,minZoom:1.05},
    {name:'OCTOBER REVOLUTION ISLAND',lat:79.5,lon:96.5,kind:'land',size:140,minZoom:.9},
    {name:'BOLSHEVIK ISLAND',lat:78.6,lon:102.5,kind:'land',size:115,minZoom:.95},
    {name:'KOMSOMOLETS ISLAND',lat:80.6,lon:94.8,kind:'land',size:70,minZoom:1.05},
    {name:'VICTORIA ISLAND',lat:80.15,lon:36.75,kind:'land',size:14,minZoom:1.25},
    // Seas, bays and ocean regions
    {name:'ARCTIC OCEAN',lat:86,lon:0,kind:'water'},{name:'GREENLAND SEA',lat:75,lon:-7,kind:'water'},
    {name:'NORWEGIAN SEA',lat:67,lon:2,kind:'water'},{name:'BARENTS SEA',lat:74,lon:38,kind:'water'},
    {name:'KARA SEA',lat:76,lon:75,kind:'water'},{name:'LAPTEV SEA',lat:76.5,lon:125,kind:'water'},
    {name:'EAST SIBERIAN SEA',lat:73.5,lon:160,kind:'water'},{name:'CHUKCHI SEA',lat:71.5,lon:-170,kind:'water'},
    {name:'BEAUFORT SEA',lat:74,lon:-140,kind:'water'},{name:'BAFFIN BAY',lat:71,lon:-60,kind:'water'},
    // Important navigation passages
    {name:'Fram Strait',lat:78.5,lon:-3,kind:'strait'},{name:'Bering Strait',lat:66,lon:-169,kind:'strait'},
    {name:'Davis Strait',lat:66,lon:-58,kind:'strait'},{name:'Nares Strait',lat:80,lon:-68,kind:'strait'},
    {name:'Vilkitsky Strait',lat:77.8,lon:103,kind:'strait'},{name:'Denmark Strait',lat:66,lon:-28,kind:'strait'},
    {name:'Lancaster Sound',lat:74.2,lon:-82,kind:'strait'}
    ,
    // Coastal settlements. Smaller ports appear as the chart is enlarged.
    {name:'LONGYEARBYEN',lat:78.223,lon:15.647,kind:'city',minZoom:.3,capital:true},
    {name:'TROMS\u00D8',lat:69.649,lon:18.956,kind:'city',minZoom:.45},
    {name:'HAMMERFEST',lat:70.663,lon:23.682,kind:'city',minZoom:.75},
    {name:'VARD\u00D8',lat:70.371,lon:31.110,kind:'city',minZoom:.85},
    {name:'MURMANSK',lat:68.971,lon:33.075,kind:'city',minZoom:.45},
    {name:'ARKHANGELSK',lat:64.539,lon:40.516,kind:'city',minZoom:.6},
    {name:'DIKSON',lat:73.507,lon:80.546,kind:'city',minZoom:.65},
    {name:'TIKSI',lat:71.638,lon:128.868,kind:'city',minZoom:.55},
    {name:'PEVEK',lat:69.701,lon:170.299,kind:'city',minZoom:.65},
    {name:'ANADYR',lat:64.733,lon:177.517,kind:'city',minZoom:.75},
    {name:'UTQIA\u0120VIK / BARROW',lat:71.291,lon:-156.789,kind:'city',minZoom:.45},
    {name:'PRUDHOE BAY',lat:70.255,lon:-148.337,kind:'city',minZoom:.75},
    {name:'NOME',lat:64.501,lon:-165.406,kind:'city',minZoom:.75},
    {name:'TUKTOYAKTUK',lat:69.445,lon:-133.034,kind:'city',minZoom:.65},
    {name:'INUVIK',lat:68.360,lon:-133.724,kind:'city',minZoom:.7},
    {name:'CAMBRIDGE BAY',lat:69.117,lon:-105.059,kind:'city',minZoom:.65},
    {name:'RESOLUTE',lat:74.697,lon:-94.830,kind:'city',minZoom:.6},
    {name:'POND INLET',lat:72.700,lon:-77.959,kind:'city',minZoom:.7},
    {name:'IQALUIT',lat:63.746,lon:-68.517,kind:'city',minZoom:.85},
    {name:'QAANAAQ',lat:77.467,lon:-69.231,kind:'city',minZoom:.6},
    {name:'ILULISSAT',lat:69.219,lon:-51.098,kind:'city',minZoom:.65},
    {name:'REYKJAV\u00CDK',lat:64.147,lon:-21.943,kind:'city',minZoom:.7}
  ];
  const bathymetricRidges=[
    {name:'LOMONOSOV RIDGE',pts:ll([[80,-62],[84,-70],[87,-95],[89,-135],[87,152],[83,143],[79,137]])},
    {name:'GAKKEL RIDGE',pts:ll([[79,-5],[82,8],[85,28],[87,52],[86,78],[83,105],[80,125]])},
    {name:'ALPHA–MENDELEEV RIDGE',pts:ll([[81,-88],[83,-112],[83,-140],[81,-165],[78,174]])},
    {name:'NORTHWIND RIDGE',pts:ll([[76,-158],[79,-154],[82,-150]])},
    {name:'MOHNS–KNIPOVICH RIDGE',pts:ll([[68,-2],[72,-3],[76,-5],[79,-7]])}
  ];
  const bathymetricLabels=[{name:'NANSEN BASIN',lat:84,lon:25},{name:'AMUNDSEN BASIN',lat:86.2,lon:100},{name:'MAKAROV BASIN',lat:85,lon:-155},{name:'CANADA BASIN',lat:79,lon:-138},{name:'GREENLAND BASIN',lat:75,lon:-6},{name:'NORWEGIAN BASIN',lat:68,lon:1}];
  const whales=[
    ['BOWHEAD',77.1,4,'#263f52'],['BELUGA',76.7,18,'#e8f1ed'],['HUMPBACK',75.1,-2,'#304d61'],
    ['BOWHEAD',72,-150,'#263f52'],['BELUGA',74,-130,'#e8f1ed'],['BOWHEAD',70.7,-143,'#263f52'],
    ['GRAY WHALE',69,-168,'#667981'],['GRAY WHALE',71.5,-161,'#667981'],['BELUGA',72.4,-121,'#e8f1ed'],
    ['NARWHAL',76,-64,'#7d929b'],['NARWHAL',74.3,-78,'#7d929b'],['BOWHEAD',71.8,-58,'#263f52'],
    ['HUMPBACK',70,4,'#304d61'],['HUMPBACK',72.5,13,'#304d61'],['BELUGA',75,38,'#e8f1ed'],
    ['BOWHEAD',72,45,'#263f52'],['BELUGA',73,105,'#e8f1ed'],['BOWHEAD',74.5,137,'#263f52'],
    ['BELUGA',71.4,171,'#e8f1ed'],['NARWHAL',77.1,-18,'#7d929b']
  ].map(([species,lat,lon,color],i)=>{const p=polar(lat,lon);return{species,color,x:p.x,y:p.y,angle:i*.91+.4,phase:i*1.7};});
  const FISH_STYLES={
    'ARCTIC COD':{color:'#d7e7df',size:4.8},'SAFFRON COD':{color:'#c8b783',size:5.2},'CAPELIN':{color:'#91c9c4',size:3.8},'PACIFIC HERRING':{color:'#83b5c9',size:4.2},
    'ATLANTIC HERRING':{color:'#8fc2d0',size:4.2},'SAND LANCE':{color:'#d3cda7',size:3.5},'GREENLAND HALIBUT':{color:'#7e8e8c',size:5.5},'NORTHEAST ARCTIC COD':{color:'#b9c7b9',size:5.8}
  };
  const fishSchools=[
    ['ARCTIC COD',76,-145,15],['ARCTIC COD',75,-118,14],['ARCTIC COD',77,-72,16],['ARCTIC COD',78,32,16],['ARCTIC COD',76,102,14],['ARCTIC COD',74.5,168,15],
    ['SAFFRON COD',68.5,-166,12],['SAFFRON COD',69.2,166,12],['SAFFRON COD',70,-154,11],
    ['CAPELIN',69,-7,18],['CAPELIN',72,31,17],['CAPELIN',68,-28,16],['CAPELIN',71,-158,14],['CAPELIN',72,-52,15],
    ['PACIFIC HERRING',66,-168,17],['PACIFIC HERRING',68.2,-156,16],['ATLANTIC HERRING',67,2,17],['ATLANTIC HERRING',69.2,25,15],
    ['SAND LANCE',70.5,-156,15],['SAND LANCE',69.5,-136,13],['GREENLAND HALIBUT',73,-62,10],['GREENLAND HALIBUT',75,-46,10],
    ['NORTHEAST ARCTIC COD',72,20,12],['NORTHEAST ARCTIC COD',74,42,12]
  ].map(([species,lat,lon,count],i)=>{const p=polar(lat,lon);return{species,count,x:p.x,y:p.y,homeX:p.x,homeY:p.y,angle:i*.83+.2,phase:i*1.37,speed:.65+(i%4)*.12};});
  const iceWildlife=[
    {type:'bear',mode:'pack',lon:-42,phase:.3},{type:'bear',mode:'pack',lon:12,phase:1.2,depth:2.2},{type:'bear',mode:'pack',lon:68,phase:1.7},{type:'bear',mode:'pack',lon:118,phase:2.1,depth:3.4},{type:'bear',mode:'pack',lon:174,phase:3.2},{type:'bear',mode:'pack',lon:-145,phase:4.2,depth:2.7},{type:'bear',mode:'pack',lon:-92,phase:5.4},{type:'bear',mode:'pack',lon:38,phase:5.9,depth:4.6},{type:'bear',mode:'pack',lon:-118,phase:6.4,depth:4.1},
    {type:'bear',mode:'gyre-floe',lon:-25,phase:.55},{type:'seal',species:'RINGED SEAL',mode:'gyre-floe',lon:18,phase:1.05},{type:'bear',mode:'gyre-floe',lon:72,phase:1.55},{type:'seal',species:'BEARDED SEAL',mode:'gyre-floe',lon:115,phase:2.05},{type:'bear',mode:'gyre-floe',lon:160,phase:2.55},{type:'seal',species:'RINGED SEAL',mode:'gyre-floe',lon:-150,phase:3.05},{type:'bear',mode:'gyre-floe',lon:-105,phase:3.55},{type:'seal',species:'BEARDED SEAL',mode:'gyre-floe',lon:-62,phase:4.05},
    {type:'bear',mode:'coast',lat:79.7,lon:19,phase:1.1},{type:'bear',mode:'coast',lat:76.4,lon:-59,phase:2.4},{type:'bear',mode:'coast',lat:74.8,lon:55,phase:4.5},
    {type:'seal',species:'RINGED SEAL',mode:'pack',lon:-125,phase:.2},{type:'seal',species:'HOODED SEAL',mode:'pack',lon:-70,phase:.8},{type:'seal',species:'HARP SEAL',mode:'pack',lon:-20,phase:1.7},{type:'seal',species:'HARP SEAL',mode:'pack',lon:35,phase:2.8},{type:'seal',species:'BEARDED SEAL',mode:'pack',lon:92,phase:3.6},{type:'seal',species:'RIBBON SEAL',mode:'pack',lon:165,phase:4.8},
    {type:'seal',species:'RINGED SEAL',mode:'coast',lat:78.4,lon:12,phase:1.9},{type:'seal',species:'BEARDED SEAL',mode:'coast',lat:79.1,lon:25,phase:2.5},{type:'seal',species:'HOODED SEAL',mode:'coast',lat:73.5,lon:-56,phase:3.7},{type:'seal',species:'SPOTTED SEAL',mode:'coast',lat:71.3,lon:-156,phase:4.3},{type:'seal',species:'HARP SEAL',mode:'coast',lat:72.8,lon:52,phase:5.1},
    {type:'bear',mode:'floe',lat:77.4,lon:7,phase:.4},{type:'seal',species:'HARP SEAL',mode:'floe',lat:77.1,lon:2,phase:1.1},{type:'seal',species:'RINGED SEAL',mode:'floe',lat:76.8,lon:20,phase:1.8},{type:'bear',mode:'floe',lat:75.8,lon:-8,phase:2.4},{type:'seal',species:'HOODED SEAL',mode:'floe',lat:74.8,lon:-35,phase:3.1},
    {type:'bear',mode:'floe',lat:73.5,lon:-137,phase:3.8},{type:'seal',species:'RIBBON SEAL',mode:'floe',lat:72.5,lon:-168,phase:4.4},{type:'seal',species:'HARP SEAL',mode:'floe',lat:74.2,lon:-60,phase:5.0},{type:'bear',mode:'floe',lat:74.5,lon:47,phase:5.6},{type:'seal',species:'BEARDED SEAL',mode:'floe',lat:73.6,lon:102,phase:6.2},{type:'seal',species:'SPOTTED SEAL',mode:'floe',lat:71.8,lon:170,phase:6.8},
    {type:'walrus',species:'WALRUS',mode:'coast',lat:79.25,lon:24.5,phase:.6},{type:'walrus',species:'WALRUS',mode:'floe',lat:78.1,lon:38,phase:1.8},{type:'walrus',species:'WALRUS',mode:'coast',lat:72.1,lon:-167,phase:2.7},{type:'walrus',species:'WALRUS',mode:'floe',lat:73.4,lon:-176,phase:3.9},{type:'walrus',species:'WALRUS',mode:'coast',lat:74.6,lon:105,phase:5.1}
  ];
  const arcticFoxes=[{lat:78.7,lon:18,phase:.2},{lat:78.9,lon:20,phase:.9},{lat:79.35,lon:23,phase:1.3},{lat:76,lon:-42,phase:1.8},{lat:73.2,lon:-25,phase:2.2},{lat:79,lon:-76,phase:2.8},{lat:75.2,lon:-96,phase:3.4},{lat:70.4,lon:-154,phase:3.8},{lat:74,lon:56,phase:4.1},{lat:76.2,lon:101,phase:4.7},{lat:66.6,lon:-19,phase:5.2},{lat:69.6,lon:19.5,phase:5.8}];
  const landWildlife=[
    {species:'CARIBOU',region:'NORTH AMERICA',lat:69.3,lon:-156,phase:.3},{species:'CARIBOU',region:'NORTH AMERICA',lat:67.8,lon:-148,phase:1.1},{species:'CARIBOU',region:'NORTH AMERICA',lat:68.2,lon:-124,phase:1.8},{species:'CARIBOU',region:'NORTH AMERICA',lat:67.4,lon:-108,phase:2.5},{species:'CARIBOU',region:'NORTH AMERICA',lat:72.3,lon:-119,phase:3.2},{species:'CARIBOU',region:'NORTH AMERICA',lat:74.2,lon:-92,phase:3.9},
    {species:'REINDEER',region:'EURASIA',lat:69.2,lon:23,phase:.7},{species:'REINDEER',region:'EURASIA',lat:69.3,lon:48,phase:1.4},{species:'REINDEER',region:'EURASIA',lat:70.8,lon:82,phase:2.1},{species:'REINDEER',region:'EURASIA',lat:70.5,lon:118,phase:2.8},{species:'REINDEER',region:'EURASIA',lat:69.6,lon:154,phase:3.5},{species:'SVALBARD REINDEER',region:'SVALBARD',lat:78.2,lon:15.6,phase:4.2}
  ];
  const summerBirds=[
    {species:'SNOWY OWL',kind:'owl',lat:70.8,lon:-157,phase:.2},{species:'SNOWY OWL',kind:'owl',lat:73.2,lon:-105,phase:1.1},{species:'SNOWY OWL',kind:'owl',lat:71.5,lon:112,phase:2.2},
    {species:'KING EIDER',lat:71.3,lon:-156,phase:.4,color:'#334f58'},{species:'KING EIDER',lat:73,lon:-120,phase:1.2,color:'#334f58'},{species:'KING EIDER',lat:74.5,lon:-57,phase:2,color:'#334f58'},{species:'KING EIDER',lat:72.5,lon:145,phase:2.8,color:'#334f58'},{species:'KING EIDER',lat:78.5,lon:17,phase:3.6,color:'#334f58'},
    {species:'COMMON EIDER',lat:78.2,lon:14,phase:.8,color:'#624f45'},{species:'COMMON EIDER',lat:65.5,lon:-20,phase:1.6,color:'#624f45'},{species:'COMMON EIDER',lat:72,lon:-51,phase:2.4,color:'#624f45'},{species:'COMMON EIDER',lat:69.8,lon:20,phase:3.2,color:'#624f45'},
    {species:'ARCTIC TERN',lat:65.2,lon:-18,phase:.5,color:'#e7ece8'},{species:'ARCTIC TERN',lat:77.8,lon:19,phase:1.5,color:'#e7ece8'},{species:'ARCTIC TERN',lat:73.5,lon:-45,phase:2.5,color:'#e7ece8'},{species:'ARCTIC TERN',lat:73.8,lon:-95,phase:3.5,color:'#e7ece8'},
    {species:'BARNACLE GOOSE',lat:78.4,lon:16,phase:.9,color:'#3e4548'},{species:'BARNACLE GOOSE',lat:71.5,lon:-23,phase:1.9,color:'#3e4548'},{species:'PINK-FOOTED GOOSE',lat:77.4,lon:15,phase:2.9,color:'#77685d'},{species:'BRENT GOOSE',lat:79,lon:21,phase:3.9,color:'#464b4b'},{species:'BRENT GOOSE',lat:74,lon:-96,phase:4.9,color:'#464b4b'},
    {species:'SNOW GOOSE',lat:71,lon:-154,phase:1.3,color:'#eef1e8'},{species:'SNOW GOOSE',lat:72.2,lon:-107,phase:2.3,color:'#eef1e8'},{species:'THICK-BILLED MURRE',lat:76,lon:-68,phase:3.3,color:'#272f33'},{species:'THICK-BILLED MURRE',lat:78.8,lon:20,phase:4.3,color:'#272f33'}
  ];
  const wildlifeKey=value=>String(value||'wildlife').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  whales.forEach((item,index)=>item.id=`whale-${wildlifeKey(item.species)}-${index+1}`);
  fishSchools.forEach((item,index)=>item.id=`school-${wildlifeKey(item.species)}-${index+1}`);
  iceWildlife.forEach((item,index)=>item.id=`ice-${wildlifeKey(item.type==='bear'?'polar-bear':item.species)}-${index+1}`);
  arcticFoxes.forEach((item,index)=>item.id=`arctic-fox-${index+1}`);
  landWildlife.forEach((item,index)=>item.id=`land-${wildlifeKey(item.species)}-${index+1}`);
  summerBirds.forEach((item,index)=>item.id=`bird-${wildlifeKey(item.species)}-${index+1}`);
  const ensureWildlifeId=(item,prefix='encounter')=>item.id||(item.id=`${prefix}-${++wildlifeEncounterSerial}`);

  const npcVessels=[
    {id:'fv-kvitungen',name:'F/V Kvitungen',classId:'fishing',kind:'fishing',typeLabel:'Barents Sea fishing vessel',speed:8.2,mission:'Longline survey and commercial cod fishing',captainName:'Captain Liv Arnesen',captainRole:'Master',captainPortrait:'assets/scientists/ingrid-nilsen.webp',image:'assets/vessels/fishing-vessel.webp',route:[[74.3,22],[74.8,34],[73.7,46],[72.8,30]]},
    {id:'fv-havglimt',name:'F/V Havglimt',classId:'trawler',kind:'fishing',typeLabel:'Barents Sea fishing trawler',speed:9,mission:'Tracking capelin and herring aggregations',captainName:'Captain Erik Lund',captainRole:'Master',captainPortrait:'assets/scientists/erik-johansen.webp',image:'assets/vessels/fishing-trawler.webp',route:[[72.2,18],[73.4,27],[72.6,41],[71.5,31]]},
    {id:'fv-varanger',name:'F/V Varanger',classId:'fishing',kind:'fishing',typeLabel:'Norwegian fishing vessel',speed:7.6,mission:'Weather-window trawling east of Svalbard',captainName:'Captain Jukka Mikkelsen',captainRole:'Master',captainPortrait:'assets/scientists/jukka-laine.webp',image:'assets/vessels/fishing-vessel.webp',route:[[75.2,18],[76.1,31],[74.8,45],[73.9,29]]},
    {id:'fv-chukchi-dawn',name:'F/V Chukchi Dawn',classId:'fishing',kind:'fishing',typeLabel:'Bering Strait fishing vessel',speed:7.4,mission:'Seasonal crab and pollock grounds transit',captainName:'Captain Aputi Kalluk',captainRole:'Master',captainPortrait:'assets/scientists/aputi-ivalu.webp',image:'assets/vessels/fishing-vessel.webp',route:[[65.7,-168.5],[67.1,-172.2],[68.5,-168.7],[66.8,-165.2]]},
    {id:'fv-beaufort-rose',name:'F/V Beaufort Rose',classId:'trawler',kind:'fishing',typeLabel:'Beaufort Sea fishing trawler',speed:8,mission:'Nearshore fish and invertebrate survey',captainName:'Captain Ariq Kalluk',captainRole:'Master',captainPortrait:'assets/scientists/ariq-kalluk.webp',image:'assets/vessels/fishing-trawler.webp',route:[[70.6,-155],[71.5,-149],[71.2,-141],[70.4,-147]]},
    {id:'mv-boreal-crown',name:'M/V Boreal Crown',classId:'global',kind:'cruise',typeLabel:'Passenger expedition vessel',speed:10,seasonal:true,mission:'Svalbard wildlife and glacier cruise',captainName:'Captain Claire Rousseau',captainRole:'Expedition Captain',captainPortrait:'assets/scientists/claire-rousseau.webp',image:SMALL_PASSENGER_SVG,route:[[77.8,7],[78.8,10],[79.7,16],[79.2,27],[77.7,22]]},
    {id:'mv-spitsbergen-star',name:'M/V Spitsbergen Star',classId:'coastal',kind:'cruise',typeLabel:'Small passenger cruise vessel',speed:8.5,seasonal:true,mission:'Tourist landing circuit around Spitsbergen',captainName:'Captain Jonas Berg',captainRole:'Master',captainPortrait:'assets/scientists/jonas-berg.webp',image:'assets/vessels/base-vessel.png',route:[[77.1,13],[77.7,6],[79.1,8],[80,15],[78.7,25]]},
    {id:'sv-nordurljos',name:'S/V Nordurljos',classId:'sailing',kind:'sailing',typeLabel:'Private Arctic sailing vessel',speed:6.2,seasonal:true,mission:'Passage from Iceland to Svalbard',captainName:'Skipper Elias Korhonen',captainRole:'Skipper',captainPortrait:'assets/scientists/elias-korhonen.webp',image:'assets/vessels/arctic-sailboat.svg',route:[[66,-17],[70,-7],[74,1],[77,7],[78.4,11]]},
    {id:'umiak-siku',name:'Umiak Siku',classId:'canoe',kind:'canoe',typeLabel:'Inupiat whaling crew',speed:4.2,seasonal:true,mission:'Community bowhead whale hunt near Utqiagvik',captainName:'Aanaq Siku',captainRole:'Whaling Captain',captainPortrait:'assets/scientists/aputi-ivalu.webp',image:'assets/vessels/whaling-umiak.svg',route:[[71.32,-156.9],[71.48,-157.8],[71.6,-156.7],[71.42,-155.8]]},
    {id:'umiak-nanuq',name:'Umiak Nanuq',classId:'canoe',kind:'canoe',typeLabel:'Inupiat whaling crew',speed:4,seasonal:true,mission:'Coastal subsistence whaling patrol',captainName:'Paniq Nanuq',captainRole:'Whaling Captain',captainPortrait:'assets/scientists/ariq-kalluk.webp',image:'assets/vessels/whaling-umiak.svg',route:[[71.25,-157.2],[71.38,-158.1],[71.55,-157.1],[71.36,-156.2]]},
    {id:'rv-nansen-fjord',name:'R/V Nansen Fjord',classId:'coastal',kind:'research',typeLabel:'Coastal-class research vessel',speed:10.5,mission:'Fram Strait hydrography and plankton stations',captainName:'Dr. Hana Suzuki',captainRole:'Chief Scientist',captainPortrait:'assets/scientists/hana-suzuki.webp',image:'assets/vessels/noaa-rv-brown.webp',route:[[76,-6],[78,-4],[79,2],[77,8],[75,2]]},
    {id:'rv-meridian-ice',name:'R/V Meridian Ice',classId:'global',kind:'research',typeLabel:'Global-class research vessel',speed:13,mission:'Pan-Arctic mooring service expedition',captainName:'Prof. Elena Morozova',captainRole:'Chief Scientist',captainPortrait:'assets/scientists/elena-morozova.webp',image:'assets/vessels/noaa-rv-brown.webp',route:[[75,38],[77,52],[79,63],[78,31],[76,22]]}
  ].map((item,index)=>{const route=item.route.map(([lat,lon])=>polar(lat,lon)),start=route[0];return{...item,route,x:start.x,y:start.y,angle:index*.61,routeIndex:1,ready:false,avoidMarginal:item.kind!=='research'};});
  const SEAL_STYLES={
    'RINGED SEAL':{body:'#758b91',size:8.2,mark:'#c8d8d7'},'BEARDED SEAL':{body:'#a59078',size:10.5,mark:'#5d5147'},'SPOTTED SEAL':{body:'#70848a',size:9,mark:'#263d43'},
    'RIBBON SEAL':{body:'#3e494d',size:9.3,mark:'#e1ece8'},'HARP SEAL':{body:'#aebcc0',size:9.5,mark:'#27383e'},'HOODED SEAL':{body:'#899a9e',size:10,mark:'#25363d'}
  };
  const featureSizes={RUSSIA:6000,ALASKA:1800,CANADA:5000,GREENLAND:2600,NORWAY:1700,ICELAND:500,SPITSBERGEN:450,NORDAUSTLANDET:170,'EDGE\u00D8YA':100,'FRANZ JOSEF LAND':375,'NOVAYA ZEMLYA':900,'SEVERNAYA ZEMLYA':380,'NEW SIBERIAN ISLANDS':300,'WRANGEL ISLAND':150,'ELLESMERE ISLAND':830,'DEVON ISLAND':520,'BAFFIN ISLAND':1500,'VICTORIA ISLAND':700,'BANKS ISLAND':380};

  function resize(){dpr=Math.min(devicePixelRatio||1,2);width=innerWidth;height=innerHeight;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);lightCanvas.width=Math.round(width*dpr);lightCanvas.height=Math.round(height*dpr);light.setTransform(dpr,0,0,dpr,0,0);oceanCanvas.width=Math.max(1,Math.round(width));oceanCanvas.height=Math.max(1,Math.round(height));oceanPattern=null;baseScale=Math.max(3.4,Math.min(5.2,Math.min(width,height)/145));scale=baseScale*zoomLevel;const s=miniCanvas.clientWidth;miniCanvas.width=Math.round(s*dpr);miniCanvas.height=Math.round(s*dpr);mini.setTransform(dpr,0,0,dpr,0,0);}
  const worldToScreen=(x,y)=>({x:width/2+(x-state.x)*scale,y:height/2+(y-state.y)*scale});
  function pathPolygon(c,pts,project){c.beginPath();pts.forEach((p,i)=>{const s=project(p.x,p.y);i?c.lineTo(s.x,s.y):c.moveTo(s.x,s.y);});c.closePath();}
  function pointInPolygon(x,y,pts){let inside=false;for(let i=0,j=pts.length-1;i<pts.length;j=i++){const a=pts[i],b=pts[j];if(((a.y>y)!==(b.y>y))&&x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x)inside=!inside;}return inside;}
  const polygonIsLand=(x,y)=>land.some(shape=>x>=shape.minX&&x<=shape.maxX&&y>=shape.minY&&y<=shape.maxY&&pointInPolygon(x,y,shape.pts));
  const isLand=(x,y)=>{const raster=terrainRasterLandAt(x,y);return raster==null?polygonIsLand(x,y):raster;};
  function segmentDistance(x,y,a,b){const dx=b.x-a.x,dy=b.y-a.y,len=dx*dx+dy*dy;if(!len)return Math.hypot(x-a.x,y-a.y);const t=Math.max(0,Math.min(1,((x-a.x)*dx+(y-a.y)*dy)/len));return Math.hypot(x-(a.x+t*dx),y-(a.y+t*dy));}
  function coastDistance(x,y,limit){let best=limit+1;const gx0=Math.floor((x-limit)/COAST_CELL),gx1=Math.floor((x+limit)/COAST_CELL),gy0=Math.floor((y-limit)/COAST_CELL),gy1=Math.floor((y+limit)/COAST_CELL),seen=new Set();for(let gx=gx0;gx<=gx1;gx++)for(let gy=gy0;gy<=gy1;gy++){for(const segment of coastGrid.get(coastKey(gx,gy))||[]){if(seen.has(segment))continue;seen.add(segment);best=Math.min(best,segmentDistance(x,y,segment.a,segment.b));}}return best;}
  const smoothstep=(a,b,v)=>{const t=Math.max(0,Math.min(1,(v-a)/(b-a)));return t*t*(3-2*t);};
  function coastalCurrentFactor(x,y){const pos=unpolar(x,y);return pos.lat>=82?1:smoothstep(8,65,coastDistance(x,y,70));}
  const addCurrent=(sum,east,north,strength)=>{sum.e+=east*strength;sum.n+=north*strength;};
  function currentAt(x,y,applyCoastalFriction=true){
    const pos=unpolar(x,y),r=Math.max(1,Math.hypot(x,y)),sum={e:0,n:0};
    // Central counterclockwise polar gyre: nearly solid-body rotation, fading
    // outward toward Svalbard's latitude.
    const gyreEdge=smoothstep(77,80,pos.lat),gyreRadius=Math.min(1,r/1150);
    const ccwX=y/r,ccwY=-x/r,localEastX=y/r,localEastY=-x/r,localNorthX=-x/r,localNorthY=-y/r;
    const gyreEast=ccwX*localEastX+ccwY*localEastY,gyreNorth=ccwX*localNorthX+ccwY*localNorthY;
    addCurrent(sum,gyreEast,gyreNorth,1.35*gyreRadius*gyreEdge);
    // Atlantic inflow on the eastern side of Fram Strait, turning east north
    // of Svalbard into the Arctic Ocean.
    const framEast=Math.exp(-Math.pow((pos.lon-7)/10,2))*smoothstep(68,75,pos.lat)*(1-smoothstep(81.5,84,pos.lat));
    const turn=smoothstep(78,81,pos.lat);addCurrent(sum,turn,1-turn,2*framEast);
    // Cold outflow down the western side of Fram Strait.
    const framWest=Math.exp(-Math.pow((pos.lon+8)/8,2))*smoothstep(72,76,pos.lat)*(1-smoothstep(82,84,pos.lat));
    addCurrent(sum,0,-1,1.75*framWest);
    // Pacific inflow through Bering Strait, spreading north into the gyre.
    const lonDelta=Math.abs(((pos.lon+169+540)%360)-180),bering=Math.exp(-Math.pow(lonDelta/13,2))*smoothstep(63.3,65,pos.lat)*(1-smoothstep(75,79,pos.lat));
    addCurrent(sum,-.2,.98,1.45*bering);
    // Boundary friction: currents are fastest offshore and taper smoothly in
    // the final 75 km before a coast.
    const offshore=typeof applyCoastalFriction==='number'?applyCoastalFriction:applyCoastalFriction?coastalCurrentFactor(x,y):1,mag=Math.hypot(sum.e,sum.n),cap=mag>2?2/mag:1;
    const east=sum.e*offshore*cap,north=sum.n*offshore*cap;
    return{knots:Math.hypot(east,north),vx:(east*localEastX+north*localNorthX)*KNOT_TO_WORLD_SPEED,vy:(east*localEastY+north*localNorthY)*KNOT_TO_WORLD_SPEED};
  }
  const iceGrowth=()=>.5-.5*Math.cos(Math.PI*2*state.seasonDay/365);
  function fastIceGrowth(){const d=state.seasonDay;if(d<91||d>=274)return 0;if(d<=182)return.5-.5*Math.cos(Math.PI*(d-91)/91);return.5+.5*Math.cos(Math.PI*(d-182)/92);}
  function packIceEdge(lon){const growth=iceGrowth(),wave=(Math.sin(lon*Math.PI/33)+Math.sin(lon*Math.PI/71))*.2;return 85.4-4.2*growth+wave;}
  const ICE_COLORS={1:'#effbf9',2:'#b8dbe6',3:'#73a9c1',4:'#315f85'};
  function thicknessThreshold(level){const g=iceGrowth();if(level===2)return.5-.28*g;if(level===3)return g>.03?1-.52*g:1.01;if(level===4)return g>.45?1-.3*((g-.45)/.55):1.01;return 0;}
  function iceThicknessAt(x,y){const pos=unpolar(x,y),edge=packIceEdge(pos.lon);if(pos.lat<edge)return 0;const depth=Math.max(0,Math.min(1,(pos.lat-edge)/(90-edge)));if(depth>=thicknessThreshold(4))return 4;if(depth>=thicknessThreshold(3))return 3;if(depth>=thicknessThreshold(2))return 2;return 1;}
  let crackZoneCacheKey=-1,crackZoneCache=[];
  function getCrackZones(){const key=state.seasonDay;if(key===crackZoneCacheKey)return crackZoneCache;const g=iceGrowth(),outer=terrainLatitudeRadius(85.4-4.2*g),zones=[],gyreTurn=state.seasonDay*.082;for(let i=0;i<8;i++){const a=i*Math.PI/4+.24*Math.sin(i*4.71)+gyreTurn;let r,rx,ry;if(i<3){const connection=.72+.28*Math.sin(state.seasonDay*.18+i*2.17);r=outer-(65+50*(1-connection));rx=82+60*connection;ry=45+i*8;}else{r=outer*(.38+(i%3)*.17);rx=60+(i%3)*19;ry=45+((i+1)%3)*15;}const angle=Math.PI/2-a+.08*Math.sin(state.seasonDay*.11+i);zones.push({x:r*Math.sin(a),y:r*Math.cos(a),rx,ry,angle,seed:i+1});}crackZoneCacheKey=key;crackZoneCache=zones;return zones;}
  function isCrackedIceAt(x,y){for(const zone of getCrackZones()){const c=Math.cos(zone.angle),s=Math.sin(zone.angle),dx=x-zone.x,dy=y-zone.y,lx=dx*c+dy*s,ly=-dx*s+dy*c;if(lx*lx/(zone.rx*zone.rx)+ly*ly/(zone.ry*zone.ry)<=1.18)return true;}return false;}
  const brokenIceKey=(gx,gy)=>`${gx},${gy}`;
  function indexBrokenIce(point){const r=point.radius,gx0=Math.floor((point.x-r)/BROKEN_ICE_CELL),gx1=Math.floor((point.x+r)/BROKEN_ICE_CELL),gy0=Math.floor((point.y-r)/BROKEN_ICE_CELL),gy1=Math.floor((point.y+r)/BROKEN_ICE_CELL);for(let gx=gx0;gx<=gx1;gx++)for(let gy=gy0;gy<=gy1;gy++){const key=brokenIceKey(gx,gy);if(!brokenIceGrid.has(key))brokenIceGrid.set(key,[]);brokenIceGrid.get(key).push(point);}}
  function rebuildBrokenIceGrid(){brokenIceGrid.clear();for(const point of brokenIceChannels)indexBrokenIce(point);}
  function addBrokenIce(x,y){const last=brokenIceChannels[brokenIceChannels.length-1];if(last&&Math.hypot(x-last.x,y-last.y)<2.8)return;const flow=currentAt(x,y,false),point={x,y,radius:7,life:4+Math.random()*2,vx:flow.vx,vy:flow.vy,flowAge:.2+Math.random()*.2};brokenIceChannels.push(point);indexBrokenIce(point);if(brokenIceChannels.length>450){brokenIceChannels.splice(0,60);rebuildBrokenIceGrid();}}
  function updateBrokenIceDrift(dt){if(!brokenIceChannels.length)return;let changed=false;for(let i=brokenIceChannels.length-1;i>=0;i--){const point=brokenIceChannels[i];point.life-=dt*.2;if(point.life<=0){brokenIceChannels.splice(i,1);changed=true;continue;}point.flowAge-=dt;if(point.flowAge<=0){const flow=currentAt(point.x,point.y,false);point.vx=flow.vx;point.vy=flow.vy;point.flowAge=.2+Math.random()*.2;}const nx=point.x+point.vx*dt,ny=point.y+point.vy*dt;if(!isLand(nx,ny)&&iceTypeAt(nx,ny)!=='fast'){point.x=nx;point.y=ny;changed=true;}}if(changed)rebuildBrokenIceGrid();}
  function isBrokenIceAt(x,y){const points=brokenIceGrid.get(brokenIceKey(Math.floor(x/BROKEN_ICE_CELL),Math.floor(y/BROKEN_ICE_CELL)))||[];for(const point of points)if(Math.hypot(x-point.x,y-point.y)<=point.radius)return true;return false;}
  function nearPortIceLane(x,y){return chartLabels.some(label=>label.kind==='city'&&Math.hypot(x-polar(label.lat,label.lon).x,y-polar(label.lat,label.lon).y)<24);}
  function iceTypeAt(x,y){const pos=unpolar(x,y),growth=iceGrowth(),packEdge=packIceEdge(pos.lon),marginalEdge=packEdge-(2.1+1.5*growth);if(pos.lat>=packEdge){if(isBrokenIceAt(x,y))return'marginal';return isCrackedIceAt(x,y)?'cracked':'packed';}const fastGrowth=fastIceGrowth(),fastWidth=23.5*fastGrowth,d=coastDistance(x,y,fastWidth+3);if(fastWidth>0&&d<=fastWidth&&!nearPortIceLane(x,y))return'fast';if(pos.lat>=marginalEdge)return'marginal';return'open';}
  function riverAt(x,y,limit=3.5){for(const segment of riverSegments){if(x<segment.minX||x>segment.maxX||y<segment.minY||y>segment.maxY)continue;if(segmentDistance(x,y,segment.a,segment.b)<=limit)return segment.river;}return null;}
  const isBlocked=(x,y)=>isLand(x,y)&&!riverAt(x,y);
  const cityLabels=chartLabels.filter(label=>label.kind==='city');
  const WILDLIFE_PORT_CLEARANCE=60;
  const cityWorldPositions=cityLabels.map(city=>{const w=polar(city.lat,city.lon);return{x:w.x,y:w.y};});
  const wildlifeClearOfPorts=(x,y)=>cityWorldPositions.every(city=>Math.hypot(x-city.x,y-city.y)>=WILDLIFE_PORT_CLEARANCE);
  currentPortCity=cityLabels.find(city=>city.name==='LONGYEARBYEN')||cityLabels[0]||null;
  if(currentPortCity)state.dockedPort=currentPortCity.name;

  // Expedition 13: local saves, title/pause menu, and analytics instrumentation.
  const GAME_VERSION='expedition-13',SAVE_VERSION=1;
  const SAVE_KEYS={auto:'arctic-research-save-auto-v1',slot1:'arctic-research-save-slot-1-v1',slot2:'arctic-research-save-slot-2-v1',slot3:'arctic-research-save-slot-3-v1'};
  const AUTO_NEW_KEY='arctic-research-start-new-v1';
  let menuOpen=true,autosaveSuspended=false,autosaveTimer=0,lastResearchAnalytics=null;
  const safeJson=value=>{try{return JSON.parse(JSON.stringify(value));}catch(error){return null;}};
  const readSave=slot=>{try{const raw=localStorage.getItem(SAVE_KEYS[slot]);if(!raw)return null;const parsed=JSON.parse(raw);return parsed?.version===SAVE_VERSION?parsed:null;}catch(error){return null;}};
  const hasAnySave=()=>Object.keys(SAVE_KEYS).some(slot=>!!readSave(slot));
  const activeClock={total:0,since:document.visibilityState==='visible'?performance.now():null};
  const updateActiveClock=()=>{if(activeClock.since!=null){activeClock.total+=performance.now()-activeClock.since;activeClock.since=null;}if(document.visibilityState==='visible')activeClock.since=performance.now();};
  const activeSeconds=()=>Math.max(0,Math.round((activeClock.total+(activeClock.since==null?0:performance.now()-activeClock.since))/1000));

  function analyticsContext(){
    const rs=research?.getState?.()||{},ship=research?.getVesselModifiers?.()||{},player=rs.scientists?.find?.(item=>item.isPlayer),pos=unpolar(state.x,state.y);
    return {
      game_version:GAME_VERSION,game_started:state.started?1:0,game_year:state.year,season_day:Math.round(state.seasonDay*10)/10,
      latitude:Math.round(pos.lat*100)/100,longitude:Math.round(pos.lon*100)/100,vessel_id:rs.currentVessel||'',money:Math.round(rs.money||0),
      citations:Math.floor(rs.citations||0),science_data:Math.round(rs.data||0),fuel_pct:Math.round(state.fuel),food_pct:Math.round(state.food),
      crew_count:rs.scientists?.length||0,equipment_count:rs.installedEquipment?.length||0,active_grants:rs.targets?.filter?.(item=>item.kind==='grant'||item.kind==='contract').length||0,
      missions_completed:rs.completed?.length||0,papers:rs.papers?.length||0,wildlife_seen:rs.observed?.length||0,port_visits:rs.portVisits||0,play_seconds:activeSeconds(),
      player_career:player?.career||'',player_specialty:player?.specialty||'',viewport:`${innerWidth}x${innerHeight}`,returning_player:hasAnySave()?1:0
    };
  }
  const analytics=(()=>{
    const measurementId=document.querySelector('meta[name="ar-analytics-id"]')?.content?.trim()||'';
    let enabled=/^G-[A-Z0-9]+$/i.test(measurementId);
    if(enabled){
      window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){window.dataLayer.push(arguments);};
      window.gtag('js',new Date());window.gtag('config',measurementId,{send_page_view:true});
      const script=document.createElement('script');script.async=true;script.src=`https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;document.head.appendChild(script);
    }
    const clean=value=>typeof value==='number'?(Number.isFinite(value)?value:0):typeof value==='boolean'?(value?1:0):String(value??'').slice(0,100);
    const track=(name,extra={})=>{
      if(!enabled)return false;
      const raw={...extra,...analyticsContext()},params={};let count=0;
      for(const [key,value] of Object.entries(raw)){if(value==null||value==='')continue;if(count>=25)break;params[key.slice(0,40)]=clean(value);count++;}
      window.gtag?.('event',String(name).replace(/[^a-zA-Z0-9_]/g,'_').slice(0,40),params);return true;
    };
    return{track,isEnabled:()=>enabled,measurementId};
  })();
  window.ARAnalytics=analytics;

  function saveMeta(){
    const rs=research?.getState?.()||{},ship=research?.getVesselModifiers?.()||{},pos=unpolar(state.x,state.y);
    return {savedAt:new Date().toISOString(),location:currentPortCity?.name||state.dockedPort||locationName(pos.lat,pos.lon),vessel:ship.name||rs.currentVessel||'Research Vessel',money:Math.round(rs.money||0),missions:rs.completed?.length||0,papers:rs.papers?.length||0,year:state.year,seasonDay:state.seasonDay};
  }
  function createGameSave(){return{version:SAVE_VERSION,gameVersion:GAME_VERSION,savedAt:new Date().toISOString(),meta:saveMeta(),navigation:safeJson(state),currentPortName:currentPortCity?.name||null,checkpoint:safeJson(checkpoint),research:safeJson(research?.createCheckpoint?.()||research?.getState?.()||null)};}
  function saveGame(slot='auto',reason='auto'){
    if(!state.started||!SAVE_KEYS[slot]||autosaveSuspended)return false;
    try{const payload=createGameSave();localStorage.setItem(SAVE_KEYS[slot],JSON.stringify(payload));refreshMenu();if(slot!=='auto')analytics.track('game_saved',{save_slot:slot,save_reason:reason});return true;}catch(error){showToast('SAVE FAILED — BROWSER STORAGE IS NOT AVAILABLE',2600);return false;}
  }
  function scheduleAutosave(delay=450){if(!state.started||autosaveSuspended)return;clearTimeout(autosaveTimer);autosaveTimer=setTimeout(()=>saveGame('auto','state_change'),delay);}
  function restoreGameSave(payload,source='auto'){
    if(!payload?.navigation||!payload?.research)return false;
    try{
      const nav=safeJson(payload.navigation)||{};Object.assign(state,nav,{started:true,gameOver:false,moving:false,commandActive:false,ramming:false,ramClock:0});
      state.tx=Number.isFinite(nav.tx)?nav.tx:state.x;state.ty=Number.isFinite(nav.ty)?nav.ty:state.y;
      checkpoint=payload.checkpoint||checkpoint;currentPortCity=payload.currentPortName?cityLabels.find(item=>item.name===payload.currentPortName)||null:null;
      research?.restoreCheckpoint?.(payload.research);pendingResearchTargetId=null;announcedWeatherEvent=null;iceFloes.length=0;wakeFloes.length=0;brokenIceChannels.length=0;brokenIceGrid.clear();
      ui.gameOver.classList.add('hidden');ui.fuelLevel.style.width=state.fuel+'%';ui.foodLevel.style.width=state.food+'%';updateResourceWarning();
      updateVesselButton(research?.getVesselModifiers?.()||vesselModifiers());zoomLevel=(research?.getVesselModifiers?.()||vesselModifiers()).minZoom||zoomLevel;setZoom(0,true);
      if(currentPortCity&&state.dockedPort)research?.enterPort?.(currentPortCity,{resume:true});else research?.leavePort?.();
      menuOpen=false;ui.welcome.classList.add('hidden');lastResearchAnalytics=research?.getState?.()||null;showToast(`EXPEDITION LOADED — ${payload.meta?.location||'ARCTIC OCEAN'}`,2400);
      analytics.track(source==='auto'?'continue_game':'load_game',{save_slot:source,save_age_hours:Math.round((Date.now()-Date.parse(payload.savedAt||Date.now()))/360000)/10});scheduleAutosave(900);return true;
    }catch(error){showToast('COULD NOT LOAD THIS SAVE',2600);return false;}
  }
  function saveDescription(save){if(!save?.meta)return'Empty slot';const m=save.meta,date=new Date(m.savedAt||save.savedAt);return`${m.location||'Arctic Ocean'} · ${m.vessel||'Research Vessel'} · ${m.missions||0} missions · ${new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(m.money||0)} · ${date.toLocaleString()}`;}
  function slotMarkup(slot,mode){const save=readSave(slot),label=slot==='auto'?'AUTOSAVE':`SAVE SLOT ${slot.slice(-1)}`,button=mode==='save'?'SAVE':save?'LOAD':'EMPTY';return`<div class="save-slot ${save?'':'empty'}"><div><b>${label}</b><span>${save?saveDescription(save):'No expedition saved here.'}</span>${save?`<small>Game ${save.gameVersion||'earlier version'}</small>`:''}</div><button type="button" data-${mode}-slot="${slot}" ${(!save&&mode==='load')||slot==='auto'&&mode==='save'?'disabled':''}>${button}</button></div>`;}
  function showTitlePane(id='title-main'){['title-main','title-load','title-save','title-help'].forEach(name=>document.getElementById(name)?.classList.toggle('hidden',name!==id));}
  function refreshMenu(){
    const auto=readSave('auto'),continueButton=document.getElementById('continue-button'),saveButton=document.getElementById('save-button'),resumeButton=document.getElementById('resume-button'),summary=document.getElementById('continue-summary');
    continueButton?.classList.toggle('hidden',!auto||state.started);saveButton?.classList.toggle('hidden',!state.started);resumeButton?.classList.toggle('hidden',!state.started);
    if(summary)summary.textContent=auto&&!state.started?`Latest autosave: ${saveDescription(auto)}`:state.started?'Game paused. Autosave is active in this browser.':'';
    const load=document.getElementById('load-slots'),save=document.getElementById('save-slots');if(load)load.innerHTML=['auto','slot1','slot2','slot3'].map(slot=>slotMarkup(slot,'load')).join('');if(save)save.innerHTML=['auto','slot1','slot2','slot3'].map(slot=>slotMarkup(slot,'save')).join('');
  }
  function openGameMenu(){menuOpen=true;ui.welcome.classList.remove('hidden');showTitlePane('title-main');refreshMenu();analytics.track('game_menu_opened',{menu_context:state.started?'in_game':'title'});}
  function resumeGame(){if(!state.started)return;menuOpen=false;ui.welcome.classList.add('hidden');analytics.track('game_resumed');}
  function startNewGame(){
    if(state.started){try{sessionStorage.setItem(AUTO_NEW_KEY,'1');}catch(error){}location.reload();return;}
    try{localStorage.removeItem(SAVE_KEYS.auto);}catch(error){}menuOpen=false;ui.welcome.classList.add('hidden');analytics.track('new_game');requestExpeditionStart();
  }
  function semanticAnalytics(){
    const next=research?.getState?.();if(!next)return;const prev=lastResearchAnalytics;if(prev){
      const completedBefore=new Set((prev.completed||[]).map(item=>item.id));for(const item of next.completed||[])if(!completedBefore.has(item.id))analytics.track('mission_completed',{mission_id:item.id||'',mission_kind:item.kind||'',mission_title:item.shortTitle||item.title||'',data_gain:item.dataGain||0,reward:item.reward||0});
      const papersBefore=new Set((prev.papers||[]).map(item=>item.id)),newPapers=(next.papers||[]).filter(paper=>!papersBefore.has(paper.id));for(const paper of newPapers)analytics.track('publication_accepted',{paper_tier:paper.tier||'',journal:paper.journal||'',data_used:paper.data||0,award:paper.award||0,initial_citations:paper.initialCitations||0});if((next.publishAttempts||0)>(prev.publishAttempts||0)&&!newPapers.length)analytics.track('publication_rejected',{attempt_number:next.publishAttempts||0,science_data:next.data||0});
      const targetBefore=new Map((prev.targets||[]).map(item=>[item.id,item]));for(const target of next.targets||[]){const before=targetBefore.get(target.id);if(!before&&['grant','contract'].includes(target.kind))analytics.track('grant_accepted',{grant_id:target.id||'',grant_title:target.shortTitle||target.title||'',grant_kind:target.kind||'',reward:target.reward||0});if(before&&target.stations?.length){const was=(before.stations||[]).filter(st=>st.status==='completed').length,now=target.stations.filter(st=>st.status==='completed').length;if(now>was)analytics.track('mission_station_completed',{mission_id:target.id||'',stations_completed:now,stations_total:target.stations.length});}}
      const peopleBefore=new Map((prev.scientists||[]).map(item=>[item.id,item]));const peopleNow=new Map((next.scientists||[]).map(item=>[item.id,item]));for(const [id,item] of peopleNow)if(!peopleBefore.has(id)&&!item.isPlayer)analytics.track('scientist_hired',{scientist_id:id,career:item.career||'',specialty:item.specialty||''});for(const [id,item] of peopleBefore)if(!peopleNow.has(id)&&!item.isPlayer)analytics.track('scientist_released',{scientist_id:id,career:item.career||'',specialty:item.specialty||''});
      const eqBefore=new Set(prev.installedEquipment||[]),eqNow=new Set(next.installedEquipment||[]);for(const id of eqNow)if(!eqBefore.has(id))analytics.track('equipment_installed',{equipment_id:id});for(const id of eqBefore)if(!eqNow.has(id))analytics.track('equipment_sold',{equipment_id:id});
      if(prev.currentVessel!==next.currentVessel)analytics.track('vessel_changed',{from_vessel:prev.currentVessel||'',to_vessel:next.currentVessel||''});
      const seenBefore=new Set(prev.observed||[]);for(const species of next.observed||[])if(!seenBefore.has(species))analytics.track('wildlife_observed',{species});
      if((next.promotions||[]).length>(prev.promotions||[]).length){const promo=next.promotions[next.promotions.length-1]||{};analytics.track('career_promotion',{scientist_id:promo.scientistId||promo.id||'',career:promo.career||promo.to||''});}
    }
    lastResearchAnalytics=safeJson(next);
  }
  function researchSnapshot(){return research?.createCheckpoint?.()??research?.getSnapshot?.()??null;}
  function saveCheckpoint(city){checkpoint={x:state.x,y:state.y,seasonDay:state.seasonDay,year:state.year,travelled:state.travelled,angle:state.angle,portName:city.name,fuel:state.fuel,food:state.food,research:researchSnapshot()};}
  function restoreCheckpoint(){const cp=checkpoint,city=cityLabels.find(item=>item.name===cp.portName)||cityLabels[0],restoreResearch=research?.restoreCheckpoint||research?.restoreSnapshot;restoreResearch?.call(research,cp.research);Object.assign(state,{x:cp.x,y:cp.y,tx:cp.x,ty:cp.y,angle:cp.angle??Math.PI,moving:false,commandActive:false,travelled:cp.travelled??0,seasonDay:cp.seasonDay??0,year:cp.year??2026,frozen:false,fuel:Math.max(25,cp.fuel??100),food:Math.max(25,cp.food??100),portDestination:null,dockedPort:cp.portName,gameOver:false,fogClearDays:7,ramming:false,ramClock:0,targetOnLand:false,started:true});currentPortCity=city;pendingResearchTargetId=null;announcedWeatherEvent=null;research?.ensureMinimumSupplies?.(.25);iceFloes.length=0;wakeFloes.length=0;brokenIceChannels.length=0;brokenIceGrid.clear();ui.gameOver.classList.add('hidden');ui.fuelLevel.style.width=state.fuel+'%';ui.foodLevel.style.width=state.food+'%';research?.enterPort?.(city,{resume:true});showToast(`RETURNED TO LAST PORT — ${cp.portName} · STORES RESTORED TO AT LEAST 25%`,3000);}
  function cityScreenPosition(city){const w=polar(city.lat,city.lon),p=worldToScreen(w.x,w.y);return{city,w,p};}
  function nearbyCityAt(clientX,clientY){let match=null,best=24;for(const city of cityLabels){const item=cityScreenPosition(city),distance=Math.hypot(item.w.x-state.x,item.w.y-state.y),hit=Math.hypot(item.p.x-clientX,item.p.y-clientY);if(hit<best){match=item;match.distance=distance;best=hit;}}return match;}
  function findPortApproach(city){const center=polar(city.lat,city.lon);for(let radius=2;radius<=68;radius+=2){let best=null,bestDistance=Infinity;for(let i=0;i<48;i++){const a=i*Math.PI/24,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,pos=unpolar(x,y);if(pos.lat<MIN_LAT||isBlocked(x,y))continue;const ice=iceTypeAt(x,y);if(ice==='fast'||ice==='packed')continue;const distance=Math.hypot(x-state.x,y-state.y);if(distance<bestDistance){best={x,y,shoreDistance:radius};bestDistance=distance;}}if(best)return best;}return null;}
  function resetDistantWildlifeFromPort(city){
    const center=polar(city.lat,city.lon),screenDistance=Math.max(width,height)/Math.max(.1,scale),ids=[];
    try{forEachWildlifeVisual((entity,species,category,w)=>{if(Math.hypot(w.x-center.x,w.y-center.y)>screenDistance){const id=ensureWildlifeId(entity);if(id){ids.push(id);observedWildlifeFallback.delete(id);}}});}catch(e){}
    if(ids.length)research?.resetWildlifeObservations?.(ids);
  }
  function enterPort(city){state.portDestination=null;state.dockedPort=city.name;state.moving=false;state.commandActive=false;state.tx=state.x;state.ty=state.y;currentPortCity=city;resetDistantWildlifeFromPort(city);if(state.started)research?.enterPort?.(city,{resources:{fuel:state.fuel,food:state.food}});saveCheckpoint(city);if(state.started){saveGame('auto','port');analytics.track('port_entered',{port_name:city.name||'',port_country:city.countryCode||''});showToast(`PORT CALL — ${city.name} · SERVICES & RESEARCH GRANTS OPEN`,2600);}}
  function refuelAt(city){enterPort(city);}
  function serviceNearbyPort(){if(!currentPortCity)return;const w=polar(currentPortCity.lat,currentPortCity.lon);if(Math.hypot(w.x-state.x,w.y-state.y)<=38)return;research?.leavePort?.();state.dockedPort=null;currentPortCity=null;}
  function endGame(title,message){if(state.gameOver)return;state.gameOver=true;state.moving=false;state.tx=state.x;state.ty=state.y;clearTimeout(toastTimer);ui.toast.classList.remove('show','frozen');ui.gameOverTitle.textContent=title;ui.gameOverMessage.textContent=message;ui.gameOver.classList.remove('hidden');analytics.track('game_over',{game_over_reason:title||'',game_over_message:message||''});}
  function text(name,lat,lon,size=16,color='#436c6b'){const w=polar(lat,lon),p=worldToScreen(w.x,w.y);ctx.fillStyle=color;ctx.font=`800 ${size}px system-ui`;ctx.textAlign='center';ctx.fillText(name,p.x,p.y);}
  function drawChartLabel(label){const defaultMin=label.kind==='country'?.3:label.kind==='water'?.3:label.kind==='strait'?.45:label.kind==='city'?.55:.4;if(zoomLevel<(label.minZoom??defaultMin))return;const w=polar(label.lat,label.lon);let p=worldToScreen(w.x,w.y);if(label.kind!=='city'&&Math.abs(p.x-width/2)<70&&Math.abs(p.y-height/2)<70)p={x:p.x,y:p.y-62};if(p.x<-150||p.x>width+150||p.y<82||p.y>height+35)return;const extent=label.size??featureSizes[label.name]??(label.kind==='water'?1200:label.kind==='strait'?80:100);const raw=(label.kind==='country'?9:label.kind==='water'?7.5:5.5)+Math.log10(Math.max(3,extent))*1.7;const fontSize=label.kind==='city'?Math.max(8,Math.min(11,8.5*Math.pow(zoomLevel,.2))):Math.max(7,Math.min(label.kind==='country'?20:15,raw*Math.pow(zoomLevel,.32)));ctx.save();ctx.textAlign='center';ctx.textBaseline='middle';if(label.kind==='city'){const nearby=Math.hypot(w.x-state.x,w.y-state.y)<=180;if(nearby){ctx.strokeStyle='rgba(246,211,101,.8)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(p.x,p.y,9,0,Math.PI*2);ctx.stroke();}ctx.fillStyle='#e84f4f';ctx.strokeStyle='rgba(255,244,230,.95)';ctx.lineWidth=2.5;ctx.beginPath();ctx.arc(p.x,p.y,label.capital?5:4.2,0,Math.PI*2);ctx.fill();ctx.stroke();p={x:p.x,y:p.y-12};ctx.fillStyle='#173f4e';ctx.font=`800 ${fontSize}px system-ui`;ctx.lineWidth=3;}else if(label.kind==='country'){ctx.fillStyle='rgba(46,86,81,.88)';ctx.font=`800 ${fontSize}px system-ui`;}else if(label.kind==='land'){ctx.fillStyle='rgba(55,91,86,.9)';ctx.font=`700 ${fontSize}px system-ui`;}else if(label.kind==='strait'){ctx.fillStyle='rgba(228,249,248,.9)';ctx.font=`italic 600 ${fontSize}px Georgia,serif`;}else{ctx.fillStyle='rgba(224,248,251,.8)';ctx.font=`italic 700 ${fontSize}px Georgia,serif`;}if(label.kind!=='city'){ctx.strokeStyle='rgba(50,107,123,.4)';ctx.lineWidth=Math.max(2,fontSize/4);}ctx.strokeText(label.name,p.x,p.y);ctx.fillText(label.name,p.x,p.y);ctx.restore();}
  function drawRivers(minX,maxX,minY,maxY){ctx.save();ctx.lineCap='round';ctx.lineJoin='round';rivers.forEach(river=>{ctx.strokeStyle='rgba(54,139,173,.9)';ctx.lineWidth=Math.max(1.5,scale*1.05);river.paths.forEach(path=>{let started=false;ctx.beginPath();path.forEach(point=>{if(point.x<minX-20||point.x>maxX+20||point.y<minY-20||point.y>maxY+20){started=false;return;}const p=worldToScreen(point.x,point.y);if(started)ctx.lineTo(p.x,p.y);else{ctx.moveTo(p.x,p.y);started=true;}});ctx.stroke();});if(zoomLevel>=.45&&river.labelPoint){const p=worldToScreen(river.labelPoint.x,river.labelPoint.y);if(p.x>30&&p.x<width-30&&p.y>90&&p.y<height-30){const fs=Math.max(8,Math.min(13,(10-river.rank*.35)*Math.pow(zoomLevel,.25)));ctx.font=`italic 700 ${fs}px Georgia,serif`;ctx.textAlign='center';ctx.strokeStyle='rgba(235,252,252,.92)';ctx.lineWidth=3.5;ctx.strokeText(river.name,p.x,p.y-10);ctx.fillStyle='#175d78';ctx.fillText(river.name,p.x,p.y-10);}}});ctx.restore();}

  function drawChartBoundary(){const center=worldToScreen(0,0),radius=terrainLatitudeRadius(MIN_LAT)*scale;ctx.save();ctx.beginPath();ctx.arc(center.x,center.y,radius,0,Math.PI*2);ctx.strokeStyle='rgba(248,221,125,.98)';ctx.lineWidth=5;ctx.setLineDash([18,9,3,9]);ctx.shadowColor='rgba(18,55,68,.55)';ctx.shadowBlur=5;ctx.stroke();ctx.setLineDash([]);ctx.shadowBlur=0;for(let lon=-180;lon<180;lon+=10){const a=lon*Math.PI/180,p=worldToScreen(radius/scale*Math.sin(a),radius/scale*Math.cos(a));if(p.x<-20||p.x>width+20||p.y<70||p.y>height+20)continue;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(-a);ctx.strokeStyle='rgba(248,221,125,.82)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-8,0);ctx.lineTo(8,0);ctx.stroke();ctx.restore();}const label=polar(MIN_LAT,0),lp=worldToScreen(label.x,label.y);if(lp.x>90&&lp.x<width-90&&lp.y>105&&lp.y<height-25){ctx.font='800 11px system-ui';ctx.textAlign='center';ctx.fillStyle='#173f4e';ctx.strokeStyle='rgba(255,242,180,.98)';ctx.lineWidth=5;ctx.strokeText(`CHART LIMIT  ${MIN_LAT.toFixed(2)}\u00B0 N`,lp.x,lp.y-12);ctx.fillText(`CHART LIMIT  ${MIN_LAT.toFixed(2)}\u00B0 N`,lp.x,lp.y-12);}ctx.restore();}
  let seafloorPattern=null;

  function drawTerrainRaster(targetCtx=ctx,project=worldToScreen,alpha=.96){
    if(!terrainTextureReady||!terrainTexture.naturalWidth)return false;
    const a=project(-TERRAIN_EXTENT_KM,-TERRAIN_EXTENT_KM),b=project(TERRAIN_EXTENT_KM,TERRAIN_EXTENT_KM),left=Math.min(a.x,b.x),top=Math.min(a.y,b.y),w=Math.abs(b.x-a.x),h=Math.abs(b.y-a.y);
    targetCtx.save();targetCtx.globalAlpha=alpha;targetCtx.imageSmoothingEnabled=true;try{targetCtx.imageSmoothingQuality='high';}catch(error){}targetCtx.drawImage(terrainTexture,left,top,w,h);targetCtx.restore();return true;
  }
  function terrainTileKey(ix,iy){return`${ix}:${iy}`;}
  function terrainTileUrl(tile,year=2024){
    // EPSG:3996 uses +northing upward; the game keeps +y downward, so invert
    // the y bounds in the WMS request. The image then draws directly into the
    // game's tile rectangle without another canvas flip.
    const minE=Math.round(tile.minX*1000),maxE=Math.round(tile.maxX*1000),minN=Math.round(-tile.maxY*1000),maxN=Math.round(-tile.minY*1000),layer=`GEBCO_NORTH_POLAR_VIEW_bed_${year}`;
    return`https://wms.gebco.net/${year}/north-polar/mapserv?BBOX=${minE}%2C${minN}%2C${maxE}%2C${maxN}&crs=EPSG%3A3996&format=image%2Fpng&height=${TERRAIN_TILE_PIXELS}&layers=${layer}&request=getmap&service=wms&version=1.3.0&width=${TERRAIN_TILE_PIXELS}`;
  }
  const terrainPixelIsLand=(r,g,b,a=255)=>{
    if(a<180)return false;
    // GEBCO's polar colour ramp keeps water cyan/blue and land green/tan/white.
    // Using colour relationships rather than a single RGB threshold keeps the
    // shallow continental shelf (pale cyan) on the water side of the mask.
    const green=g>b+12&&g>r+15;
    const tan=r>b+18&&g>b+7;
    const pale=r>212&&g>204&&b>188;
    return green||tan||pale;
  };
  function buildTerrainTileMask(tile){
    try{
      const c=document.createElement('canvas'),m=TERRAIN_MASK_PIXELS;c.width=c.height=m;const cc=c.getContext('2d',{willReadFrequently:true});cc.drawImage(tile.image,0,0,m,m);const pixels=cc.getImageData(0,0,m,m).data,landMask=new Uint8Array(m*m),heightProxy=new Uint8Array(m*m);
      for(let i=0,j=0;i<pixels.length;i+=4,j++){
        const r=pixels[i],g=pixels[i+1],b=pixels[i+2],a=pixels[i+3];if(!terrainPixelIsLand(r,g,b,a))continue;landMask[j]=1;
        const warm=Math.max(0,(r-b)/125),bright=Math.max(0,((r+g+b)/3-165)/90),proxy=Math.max(0,Math.min(1,warm*.72+bright*.48));heightProxy[j]=Math.round(proxy*255);
      }
      tile.landMask=landMask;tile.heightProxy=heightProxy;tile.maskSize=m;tile.maskReady=true;tile.seasonCanvas=null;tile.seasonBucket=-1;
    }catch(error){tile.maskReady=false;tile.maskBlocked=true;}
  }
  function loadTerrainTile(tile,cors=true,year=2024){
    const image=new Image();if(cors)image.crossOrigin='anonymous';image.decoding='async';
    image.onload=()=>{tile.image=image;tile.ready=true;tile.failed=false;tile.year=year;if(cors)buildTerrainTileMask(tile);};
    image.onerror=()=>{if(cors){loadTerrainTile(tile,false,year);return;}if(year===2024){loadTerrainTile(tile,false,2022);return;}tile.failed=true;tile.ready=false;};
    image.src=terrainTileUrl(tile,year);
  }
  function requestTerrainTile(ix,iy){
    const key=terrainTileKey(ix,iy);let tile=terrainTileCache.get(key);if(tile){tile.lastUsed=++terrainTileClock;return tile;}
    const minX=ix*TERRAIN_TILE_KM,minY=iy*TERRAIN_TILE_KM;tile={key,ix,iy,minX,minY,maxX:minX+TERRAIN_TILE_KM,maxY:minY+TERRAIN_TILE_KM,ready:false,failed:false,lastUsed:++terrainTileClock,maskReady:false};terrainTileCache.set(key,tile);loadTerrainTile(tile,true,2024);return tile;
  }
  function pruneTerrainTiles(){
    if(terrainTileCache.size<=TERRAIN_TILE_CACHE_LIMIT)return;const tiles=[...terrainTileCache.values()].sort((a,b)=>a.lastUsed-b.lastUsed);for(const tile of tiles){if(terrainTileCache.size<=TERRAIN_TILE_CACHE_LIMIT)break;terrainTileCache.delete(tile.key);}
  }
  function terrainRasterLandAt(x,y){
    if(Math.abs(x)>TERRAIN_EXTENT_KM+80||Math.abs(y)>TERRAIN_EXTENT_KM+80)return null;const ix=Math.floor(x/TERRAIN_TILE_KM),iy=Math.floor(y/TERRAIN_TILE_KM),tile=terrainTileCache.get(terrainTileKey(ix,iy));if(!tile?.maskReady)return null;const u=(x-tile.minX)/TERRAIN_TILE_KM,v=(y-tile.minY)/TERRAIN_TILE_KM,m=tile.maskSize,px=Math.max(0,Math.min(m-1,Math.floor(u*m))),py=Math.max(0,Math.min(m-1,Math.floor(v*m)));return!!tile.landMask[py*m+px];
  }
  function terrainSeasonCanvas(tile){
    if(!tile.maskReady)return null;const winter=iceGrowth(),bucket=Math.round(winter*16);if(tile.seasonCanvas&&tile.seasonBucket===bucket)return tile.seasonCanvas;const m=tile.maskSize,c=tile.seasonCanvas||document.createElement('canvas');c.width=c.height=m;const cc=c.getContext('2d'),image=cc.createImageData(m,m),out=image.data;
    for(let py=0;py<m;py++)for(let px=0;px<m;px++){const j=py*m+px;if(!tile.landMask[j])continue;const x=tile.minX+(px+.5)/m*TERRAIN_TILE_KM,y=tile.minY+(py+.5)/m*TERRAIN_TILE_KM,lat=unpolar(x,y).lat,high=tile.heightProxy[j]/255;
      const lowLat=Math.max(0,Math.min(1,(78-lat)/14)),summer=(1-winter),green=summer*lowLat*Math.max(0,1-high*1.5)*.34;
      const perennial=Math.max(0,Math.min(1,(high-.18)/.48))*Math.max(.18,smoothstep(68,79,lat));
      const latitudeSnow=smoothstep(76-winter*12,84-winter*5,lat),seasonal=winter*smoothstep(64,80,lat);
      const snow=Math.max(perennial*.78,latitudeSnow*.62,seasonal*.78),white=Math.min(.9,snow),a=Math.max(green,white);if(a<.01)continue;
      const mix=white/(white+green+.0001),i=j*4;out[i]=Math.round(66+(248-66)*mix);out[i+1]=Math.round(132+(251-132)*mix);out[i+2]=Math.round(76+(249-76)*mix);out[i+3]=Math.round(Math.min(.9,a)*255);
    }cc.putImageData(image,0,0);tile.seasonCanvas=c;tile.seasonBucket=bucket;return c;
  }
  function drawTerrainTiles(){
    if(zoomLevel<.58)return 0;const bounds=visibleWorldBounds(30),ix0=Math.floor(bounds.minX/TERRAIN_TILE_KM),ix1=Math.floor(bounds.maxX/TERRAIN_TILE_KM),iy0=Math.floor(bounds.minY/TERRAIN_TILE_KM),iy1=Math.floor(bounds.maxY/TERRAIN_TILE_KM);let ready=0;
    for(let ix=ix0;ix<=ix1;ix++)for(let iy=iy0;iy<=iy1;iy++){const minX=ix*TERRAIN_TILE_KM,minY=iy*TERRAIN_TILE_KM,maxX=minX+TERRAIN_TILE_KM,maxY=minY+TERRAIN_TILE_KM;if(maxX<-TERRAIN_EXTENT_KM||minX>TERRAIN_EXTENT_KM||maxY<-TERRAIN_EXTENT_KM||minY>TERRAIN_EXTENT_KM)continue;const tile=requestTerrainTile(ix,iy);if(!tile.ready||!tile.image?.naturalWidth)continue;tile.lastUsed=++terrainTileClock;const a=worldToScreen(tile.minX,tile.minY),b=worldToScreen(tile.maxX,tile.maxY),left=Math.min(a.x,b.x)-.6,top=Math.min(a.y,b.y)-.6,w=Math.abs(b.x-a.x)+1.2,h=Math.abs(b.y-a.y)+1.2;ctx.save();ctx.imageSmoothingEnabled=true;try{ctx.imageSmoothingQuality='high';}catch(error){}ctx.drawImage(tile.image,left,top,w,h);ctx.restore();ready++;}
    pruneTerrainTiles();return ready;
  }
  function drawTerrainMain(){const overview=drawTerrainRaster(ctx,worldToScreen,.96),ready=drawTerrainTiles();return overview||ready>0;}
  function drawRasterSeasonalOverlay(){
    if(zoomLevel<.58)return;const bounds=visibleWorldBounds(30),ix0=Math.floor(bounds.minX/TERRAIN_TILE_KM),ix1=Math.floor(bounds.maxX/TERRAIN_TILE_KM),iy0=Math.floor(bounds.minY/TERRAIN_TILE_KM),iy1=Math.floor(bounds.maxY/TERRAIN_TILE_KM);for(let ix=ix0;ix<=ix1;ix++)for(let iy=iy0;iy<=iy1;iy++){const tile=terrainTileCache.get(terrainTileKey(ix,iy));if(!tile?.ready||!tile.maskReady)continue;const overlay=terrainSeasonCanvas(tile);if(!overlay)continue;const a=worldToScreen(tile.minX,tile.minY),b=worldToScreen(tile.maxX,tile.maxY),left=Math.min(a.x,b.x),top=Math.min(a.y,b.y),w=Math.abs(b.x-a.x),h=Math.abs(b.y-a.y);ctx.drawImage(overlay,left,top,w,h);}
  }
  function terrainLatitudeRadius(lat){const p=polar(lat,0);return Math.hypot(p.x,p.y);}
  function drawSeasonalLandTint(shape){
    const pole=worldToScreen(0,0),winter=iceGrowth(),outer=terrainLatitudeRadius(MIN_LAT)*scale,r80=terrainLatitudeRadius(80)*scale,r72=terrainLatitudeRadius(72)*scale;
    ctx.save();pathPolygon(ctx,shape.pts,worldToScreen);ctx.clip();
    // Vegetation/tundra tint: greener at lower latitude in summer, muted toward the pole.
    const vegetation=ctx.createRadialGradient(pole.x,pole.y,0,pole.x,pole.y,outer);
    vegetation.addColorStop(0,`rgba(214,220,205,${.12+.14*winter})`);
    vegetation.addColorStop(Math.max(.001,Math.min(.999,r80/outer)),`rgba(121,151,116,${.16+.08*(1-winter)})`);
    vegetation.addColorStop(Math.max(.002,Math.min(.999,r72/outer)),`rgba(68,132,82,${.18+.18*(1-winter)})`);
    vegetation.addColorStop(1,`rgba(48,132,78,${.24+.22*(1-winter)})`);
    ctx.fillStyle=vegetation;ctx.fillRect(0,0,width,height);
    // Seasonal snowline: mostly high-Arctic in September, expanding south through winter.
    const snowEdgeLat=80-winter*15.5,fullSnowLat=Math.min(89,snowEdgeLat+5.5),snowOuter=terrainLatitudeRadius(snowEdgeLat)*scale,snowInner=terrainLatitudeRadius(fullSnowLat)*scale;
    const snow=ctx.createRadialGradient(pole.x,pole.y,snowInner,pole.x,pole.y,Math.max(snowInner+1,snowOuter));
    snow.addColorStop(0,`rgba(247,250,246,${.42+.43*winter})`);snow.addColorStop(.58,`rgba(242,248,243,${.18+.48*winter})`);snow.addColorStop(1,'rgba(242,248,243,0)');ctx.fillStyle=snow;ctx.fillRect(0,0,width,height);
    ctx.restore();
  }
  function makeSeafloorPattern(){const tile=document.createElement('canvas'),c=tile.getContext('2d'),size=384;tile.width=tile.height=size;c.clearRect(0,0,size,size);const rnd=n=>{const v=Math.sin(n*91.733+17.31)*43758.5453;return v-Math.floor(v);};for(let i=0;i<190;i++){const x=rnd(i*5.1)*size,y=rnd(i*5.1+1)*size,len=12+rnd(i*5.1+2)*55,a=rnd(i*5.1+3)*Math.PI*2,bend=(rnd(i*5.1+4)-.5)*18;c.lineCap='round';c.lineWidth=.6+rnd(i+70)*2.2;c.strokeStyle=`rgba(${rnd(i)>.5?'15,61,105':'126,181,196'},${.025+rnd(i+9)*.08})`;c.beginPath();c.moveTo(x,y);c.quadraticCurveTo(x+Math.cos(a)*len*.5-Math.sin(a)*bend,y+Math.sin(a)*len*.5+Math.cos(a)*bend,x+Math.cos(a)*len,y+Math.sin(a)*len);c.stroke();}seafloorPattern=ctx.createPattern(tile,'repeat');}
  function visibleWorldBounds(margin=0){return{minX:state.x-width/scale/2-margin,maxX:state.x+width/scale/2+margin,minY:state.y-height/scale/2-margin,maxY:state.y+height/scale/2+margin};}
  function shapeVisible(shape,bounds){return !(shape.maxX<bounds.minX||shape.minX>bounds.maxX||shape.maxY<bounds.minY||shape.minY>bounds.maxY);}
  function strokeWorldLine(points){ctx.beginPath();points.forEach((point,index)=>{const p=worldToScreen(point.x,point.y);index?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);});}
  function drawShelfRelief(){const bounds=visibleWorldBounds(190);ctx.save();ctx.lineJoin='round';ctx.lineCap='round';for(const shape of land){if(!shapeVisible(shape,bounds))continue;for(const band of [{km:165,color:'rgba(105,193,201,.13)'},{km:95,color:'rgba(119,205,208,.15)'},{km:42,color:'rgba(151,221,215,.18)'}]){pathPolygon(ctx,shape.pts,worldToScreen);ctx.strokeStyle=band.color;ctx.lineWidth=Math.min(300,band.km*2*scale);ctx.stroke();}}ctx.restore();}
  function drawRidgeRelief(){ctx.save();ctx.lineJoin='round';ctx.lineCap='round';for(const ridge of bathymetricRidges){const visible=ridge.pts.some(point=>{const p=worldToScreen(point.x,point.y);return p.x>-120&&p.x<width+120&&p.y>-50&&p.y<height+120;});if(!visible)continue;ctx.save();ctx.translate(3.5,4.5);strokeWorldLine(ridge.pts);ctx.strokeStyle='rgba(4,38,79,.38)';ctx.lineWidth=15;ctx.stroke();ctx.restore();strokeWorldLine(ridge.pts);ctx.strokeStyle='rgba(75,155,184,.26)';ctx.lineWidth=11;ctx.stroke();strokeWorldLine(ridge.pts);ctx.strokeStyle='rgba(152,213,221,.24)';ctx.lineWidth=3.2;ctx.stroke();}ctx.restore();}
  function drawBathymetry(){if(!seafloorPattern)makeSeafloorPattern();ctx.save();for(const label of bathymetricLabels){const w=polar(label.lat,label.lon),p=worldToScreen(w.x,w.y),radius=(label.name.includes('CANADA')?410:label.name.includes('GREENLAND')?310:270)*scale;if(p.x+radius<0||p.x-radius>width||p.y+radius<70||p.y-radius>height)continue;const g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,radius);g.addColorStop(0,'rgba(4,31,78,.34)');g.addColorStop(.5,'rgba(16,57,109,.22)');g.addColorStop(1,'rgba(62,132,164,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,radius,0,Math.PI*2);ctx.fill();}drawShelfRelief();drawRidgeRelief();const ox=(-state.x*scale)%384,oy=(-state.y*scale)%384;ctx.translate(ox,oy);ctx.globalAlpha=.72;ctx.fillStyle=seafloorPattern;ctx.fillRect(-384,-384,width+768,height+768);ctx.restore();}
  function terrainNoise(x,y,salt=0){const value=Math.sin(x*.01931+y*.02717+salt*47.113)*43758.5453;return value-Math.floor(value);}
  function terrainMarksFor(shape){if(shape.terrainMarks)return shape.terrainMarks;const center=unpolar((shape.minX+shape.maxX)/2,(shape.minY+shape.maxY)/2),maxLat=shape.pts.reduce((best,point)=>Math.max(best,point.lat),-90),compactPolar=maxLat>74&&(shape.maxX-shape.minX)<950&&(shape.maxY-shape.minY)<950,step=compactPolar?18:center.lat>70?48:72,marks=[];for(let gx=Math.floor(shape.minX/step)*step;gx<=shape.maxX;gx+=step)for(let gy=Math.floor(shape.minY/step)*step;gy<=shape.maxY;gy+=step){const x=gx+(terrainNoise(gx,gy,1)-.5)*step*.62,y=gy+(terrainNoise(gx,gy,2)-.5)*step*.62,pos=unpolar(x,y);if(pos.lat<MIN_LAT+.08||!pointInPolygon(x,y,shape.pts)||terrainNoise(x,y,3)<(compactPolar?.08:.27))continue;const glacier=pos.lat>69.5&&terrainNoise(x,y,4)>(compactPolar?.62:.76);marks.push({x,y,lat:pos.lat,kind:glacier?'glacier':'peak',angle:(terrainNoise(x,y,5)-.5)*.9,size:.76+terrainNoise(x,y,6)*.72});}shape.terrainMarks=marks;return marks;}
  function drawLandTopography(shape){
    ctx.save();pathPolygon(ctx,shape.pts,worldToScreen);ctx.clip();
    const a=worldToScreen(shape.minX,shape.minY),b=worldToScreen(shape.maxX,shape.maxY),left=Math.min(a.x,b.x)-30,top=Math.min(a.y,b.y)-30,boxW=Math.abs(b.x-a.x)+60,boxH=Math.abs(b.y-a.y)+60;
    const shade=ctx.createLinearGradient(a.x,a.y,b.x,b.y);shade.addColorStop(0,'rgba(255,255,240,.24)');shade.addColorStop(.43,'rgba(113,146,113,.04)');shade.addColorStop(1,'rgba(30,67,57,.3)');ctx.fillStyle=shade;ctx.fillRect(left,top,boxW,boxH);
    const crossShade=ctx.createLinearGradient(a.x,b.y,b.x,a.y);crossShade.addColorStop(0,'rgba(32,77,66,.2)');crossShade.addColorStop(.46,'rgba(234,246,221,.04)');crossShade.addColorStop(1,'rgba(252,255,236,.18)');ctx.fillStyle=crossShade;ctx.fillRect(left,top,boxW,boxH);
    if(zoomLevel>=.75)for(const mark of terrainMarksFor(shape)){
      const p=worldToScreen(mark.x,mark.y);if(p.x<-38||p.x>width+38||p.y<58||p.y>height+38)continue;
      const size=Math.min(21,(4.2+scale*.92)*mark.size);ctx.save();ctx.translate(p.x,p.y);ctx.rotate(mark.angle);
      ctx.strokeStyle='rgba(49,85,69,.27)';ctx.lineWidth=.85;ctx.beginPath();ctx.ellipse(0,size*.2,size*1.7,size*.79,0,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.ellipse(0,size*.17,size*1.3,size*.57,0,0,Math.PI*2);ctx.stroke();
      if(mark.kind==='glacier'){
        const ice=ctx.createLinearGradient(-size*1.55,-size*.2,size*1.55,size*.25);ice.addColorStop(0,'rgba(245,253,251,.96)');ice.addColorStop(.55,'rgba(214,240,243,.94)');ice.addColorStop(1,'rgba(171,216,226,.88)');ctx.fillStyle=ice;ctx.strokeStyle='rgba(88,158,179,.72)';ctx.lineWidth=1.1;ctx.beginPath();ctx.moveTo(-size*1.55,-size*.12);ctx.bezierCurveTo(-size*.82,-size*.72,size*.42,-size*.54,size*1.52,-size*.08);ctx.bezierCurveTo(size*.72,size*.55,-size*.58,size*.73,-size*1.55,-size*.12);ctx.closePath();ctx.fill();ctx.stroke();ctx.strokeStyle='rgba(83,157,181,.55)';ctx.lineWidth=.8;for(let i=-1;i<=1;i++){ctx.beginPath();ctx.moveTo(-size*.72+i*size*.32,-size*.2);ctx.quadraticCurveTo(i*size*.18,size*.1,size*.65+i*size*.2,size*.16);ctx.stroke();}
      }else{
        ctx.fillStyle='rgba(38,74,62,.26)';ctx.beginPath();ctx.moveTo(-size*1.45,size*.7);ctx.lineTo(-size*.28,-size*.74);ctx.lineTo(size*.35,size*.7);ctx.closePath();ctx.fill();
        ctx.fillStyle='rgba(66,105,82,.76)';ctx.strokeStyle='rgba(37,74,61,.82)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(-size,size*.68);ctx.lineTo(0,-size);ctx.lineTo(size,size*.68);ctx.closePath();ctx.fill();ctx.stroke();
        ctx.fillStyle='rgba(92,128,96,.68)';ctx.beginPath();ctx.moveTo(size*.15,size*.68);ctx.lineTo(size*.72,-size*.42);ctx.lineTo(size*1.38,size*.68);ctx.closePath();ctx.fill();ctx.stroke();
        ctx.fillStyle='rgba(248,252,239,.96)';ctx.beginPath();ctx.moveTo(-size*.33,-size*.49);ctx.lineTo(0,-size);ctx.lineTo(size*.32,-size*.49);ctx.lineTo(size*.12,-size*.33);ctx.lineTo(0,-size*.45);ctx.lineTo(-size*.14,-size*.3);ctx.closePath();ctx.fill();
      }
      ctx.restore();
    }
    ctx.restore();
  }
  function captureOceanLayer(){ocean.clearRect(0,0,oceanCanvas.width,oceanCanvas.height);ocean.drawImage(canvas,0,0,canvas.width,canvas.height,0,0,oceanCanvas.width,oceanCanvas.height);oceanPattern=ctx.createPattern(oceanCanvas,'no-repeat');}
  function iceEdgePoint(lon,kind){const growth=iceGrowth(),pack=packIceEdge(lon);return polar(kind==='pack'?pack:pack-(2.1+1.5*growth),lon);}
  function drawSeasonalIce(minX,maxX,minY,maxY){ctx.save();const ring=kind=>{ctx.beginPath();for(let lon=-180;lon<=180;lon+=4){const w=iceEdgePoint(lon,kind),p=worldToScreen(w.x,w.y);lon===-180?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y);}ctx.closePath();};ring('margin');ctx.strokeStyle='rgba(225,249,251,.5)';ctx.lineWidth=1.5;ctx.stroke();ring('pack');ctx.fillStyle='rgba(239,250,247,.9)';ctx.fill();ctx.strokeStyle='rgba(255,255,255,.92)';ctx.lineWidth=2;ctx.stroke();const fastGrowth=fastIceGrowth(),fastWidth=23.5*fastGrowth,marginalWidth=fastWidth+10+15*fastGrowth;land.forEach(shape=>{if(shape.maxX<minX-marginalWidth||shape.minX>maxX+marginalWidth||shape.maxY<minY-marginalWidth||shape.minY>maxY+marginalWidth)return;if(fastWidth>0){pathPolygon(ctx,shape.pts,worldToScreen);ctx.strokeStyle='rgba(239,249,246,.88)';ctx.lineWidth=Math.max(3,fastWidth*2*scale);ctx.stroke();}});ctx.restore();}
  function drawIceThicknessAndCracks(){
    const thicknessRing=level=>{ctx.beginPath();for(let lon=-180;lon<=180;lon+=3){const edge=packIceEdge(lon),lat=edge+(90-edge)*thicknessThreshold(level),w=polar(lat,lon),p=worldToScreen(w.x,w.y);lon===-180?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y);}ctx.closePath();};
    ctx.save();thicknessRing(1);ctx.fillStyle=ICE_COLORS[1];ctx.fill();
    for(const level of [2,3,4]){if(thicknessThreshold(level)>1)continue;thicknessRing(level);ctx.fillStyle=ICE_COLORS[level];ctx.fill();ctx.strokeStyle='rgba(229,248,252,.34)';ctx.lineWidth=1;ctx.stroke();}
    thicknessRing(1);ctx.clip();for(const zone of getCrackZones()){const p=worldToScreen(zone.x,zone.y),rx=zone.rx*scale,ry=zone.ry*scale;if(p.x+rx<0||p.x-rx>width||p.y+ry<70||p.y-ry>height)continue;const rnd=n=>Math.abs(Math.sin((n+zone.seed*97.13)*12.9898)*43758.5453)%1;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(zone.angle);ctx.beginPath();ctx.ellipse(0,0,rx,ry,0,0,Math.PI*2);ctx.fillStyle='rgba(91,169,194,.16)';ctx.fill();ctx.strokeStyle='rgba(67,139,165,.32)';ctx.lineWidth=1.2;ctx.stroke();ctx.clip();ctx.strokeStyle='rgba(28,82,109,.58)';ctx.lineWidth=Math.max(.6,scale*.2);for(let n=0;n<28;n++){const x=(rnd(n*7.1)-.5)*rx*2,y=(rnd(n*7.1+1.7)-.5)*ry*2;if(x*x/(rx*rx)+y*y/(ry*ry)>.94)continue;const a=rnd(n*7.1+3.2)*Math.PI*2,len=(.07+rnd(n*7.1+4.6)*.2)*Math.min(rx,ry),bend=(rnd(n*7.1+5.9)-.5)*len*.7,ex=x+Math.cos(a)*len,ey=y+Math.sin(a)*len;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+Math.cos(a)*len*.48-Math.sin(a)*bend,y+Math.sin(a)*len*.48+Math.cos(a)*bend);ctx.lineTo(ex,ey);ctx.stroke();}ctx.restore();}ctx.restore();
  }
  const iceVisualCache=new Map();
  function cachedVisualIce(x,y,grid){const key=`${Math.round(x/grid)},${Math.round(y/grid)},${Math.floor(state.seasonDay/5)},${grid.toFixed(1)}`;if(iceVisualCache.has(key))return iceVisualCache.get(key);if(iceVisualCache.size>12000)iceVisualCache.clear();const type=iceTypeAt(x,y);iceVisualCache.set(key,type);return type;}
  function seedFloe(minX,maxX,minY,maxY){for(let tries=0;tries<18;tries++){const x=minX+Math.random()*(maxX-minX),y=minY+Math.random()*(maxY-minY);if(!isLand(x,y)&&iceTypeAt(x,y)==='marginal'){const coastal=coastalCurrentFactor(x,y);iceFloes.push({x,y,size:7+Math.random()*11,shape:Math.random(),angle:Math.random()*Math.PI,spin:(Math.random()-.5)*.18,check:.5+Math.random(),coastal});return true;}}return false;}
  function updateFloes(dt,minX,maxX,minY,maxY){
    for(let i=iceFloes.length-1;i>=0;i--){const f=iceFloes[i],flow=currentAt(f.x,f.y,f.coastal),tx=f.x+flow.vx*dt,ty=f.y+flow.vy*dt,nextType=iceTypeAt(tx,ty);if(!isLand(tx,ty)&&nextType!=='fast'&&nextType!=='packed'&&nextType!=='cracked'){f.x=tx;f.y=ty;}else if(nextType==='packed'||nextType==='cracked'){const edge=slideAlongPackedEdge(f.x,f.y,flow.vx,flow.vy),px=f.x+edge.vx*dt,py=f.y+edge.vy*dt;if(!isLand(px,py)&&iceTypeAt(px,py)==='marginal'){f.x=px;f.y=py;}}f.angle+=f.spin*dt;const shipDistance=Math.hypot(f.x-state.x,f.y-state.y);if(shipDistance<22&&state.moving){const dx=f.x-state.x,dy=f.y-state.y,d=Math.max(1,shipDistance),push=(22-d)*dt*5,px=f.x+dx/d*push,py=f.y+dy/d*push;if(!isLand(px,py)&&iceTypeAt(px,py)==='marginal'){f.x=px;f.y=py;}}f.check-=dt;const outside=f.x<minX-25||f.x>maxX+25||f.y<minY-25||f.y>maxY+25;if(outside||(f.check<=0&&(isLand(f.x,f.y)||iceTypeAt(f.x,f.y)!=='marginal')))iceFloes.splice(i,1);else if(f.check<=0){f.coastal=coastalCurrentFactor(f.x,f.y);f.check=.8+Math.random()*.9;}}
    const target=Math.min(280,Math.max(110,Math.round(width*height/7200)));let attempts=0;while(iceFloes.length<target&&attempts++<24)seedFloe(minX,maxX,minY,maxY);
  }
  function drawMarginalFloes(){ctx.save();for(const f of iceFloes){const p=worldToScreen(f.x,f.y);if(p.x<-30||p.x>width+30||p.y<60||p.y>height+30)continue;const rr=f.size,s=f.shape;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(f.angle);ctx.beginPath();for(let k=0;k<8;k++){const radius=rr*(.72+.3*Math.abs(Math.sin(s*11+k*2.7))),px=Math.cos(k*Math.PI/4)*radius,py=Math.sin(k*Math.PI/4)*radius*(.58+s*.24);k?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.fillStyle=`rgba(239,251,249,${.92+s*.08})`;ctx.fill();ctx.strokeStyle='rgba(255,255,255,.96)';ctx.lineWidth=1.2;ctx.stroke();if(rr>12){ctx.strokeStyle='rgba(130,192,205,.45)';ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(-rr*.35,0);ctx.lineTo(rr*.15,-rr*.18);ctx.lineTo(rr*.42,rr*.08);ctx.stroke();}ctx.restore();}ctx.restore();}
  function updateWakeFloes(dt){for(let i=wakeFloes.length-1;i>=0;i--){const f=wakeFloes[i];f.flowAge-=dt;if(f.flowAge<=0){const flow=currentAt(f.x,f.y,false);f.vx=flow.vx;f.vy=flow.vy;f.flowAge=.2+Math.random()*.25;}const nx=f.x+f.vx*dt,ny=f.y+f.vy*dt;if(!isLand(nx,ny)&&iceTypeAt(nx,ny)!=='fast'){f.x=nx;f.y=ny;}f.life-=dt*.2;if(f.life<=0)wakeFloes.splice(i,1);}if(!state.ramming||!state.moving||state.ramClock<.4||state.ramClock>=2)return;wakeFloeClock+=dt;while(wakeFloeClock>.075&&wakeFloes.length<150){wakeFloeClock-=.075;const headingX=Math.sin(state.angle),headingY=-Math.cos(state.angle),sideX=Math.cos(state.angle),sideY=Math.sin(state.angle),spread=(Math.random()-.5)*15,flow=currentAt(state.x,state.y,false);wakeFloes.push({x:state.x-headingX*9+sideX*spread,y:state.y-headingY*9+sideY*spread,size:4+Math.random()*8,angle:Math.random()*Math.PI,life:3+Math.random()*2.5,vx:flow.vx,vy:flow.vy,flowAge:.2+Math.random()*.25});}}
  function drawBrokenIceChannels(){
    if(!brokenIceChannels.length||!oceanPattern)return;
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.beginPath();
    let previous=null;
    for(const point of brokenIceChannels){
      const p=worldToScreen(point.x,point.y);
      if(previous&&Math.hypot(point.x-previous.worldX,point.y-previous.worldY)<30)ctx.lineTo(p.x,p.y);else ctx.moveTo(p.x,p.y);
      previous={worldX:point.x,worldY:point.y};
    }
    ctx.strokeStyle=oceanPattern;ctx.lineWidth=Math.max(14,14*scale);ctx.stroke();
    ctx.restore();
  }
  function drawWakeFloes(){
    drawBrokenIceChannels();ctx.save();
    for(const f of wakeFloes){const p=worldToScreen(f.x,f.y),alpha=Math.min(1,f.life/.6);if(p.x<-20||p.x>width+20||p.y<60||p.y>height+20)continue;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(f.angle);ctx.fillStyle=`rgba(239,251,249,${.78*alpha})`;ctx.strokeStyle=`rgba(255,255,255,${.85*alpha})`;ctx.lineWidth=1;ctx.beginPath();for(let k=0;k<7;k++){const rr=f.size*(.72+.25*Math.sin(k*2.4+f.angle));const x=Math.cos(k*Math.PI*2/7)*rr,y=Math.sin(k*Math.PI*2/7)*rr*.65;k?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();}ctx.restore();
  }

  function drawGraticule(){ctx.save();ctx.strokeStyle='rgba(223,249,251,.27)';ctx.lineWidth=1;[60,65,70,75,80,85].forEach(lat=>{const r=terrainLatitudeRadius(lat)*scale,p=worldToScreen(0,0);ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.stroke();});for(let lon=-180;lon<180;lon+=30){const e=polar(58,lon),a=worldToScreen(0,0),b=worldToScreen(e.x,e.y);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}ctx.restore();}
  function drawCurrentArrows(){
    const spacing=Math.max(145,190*zoomLevel),margin=spacing*.45;
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.textAlign='center';ctx.textBaseline='top';
    for(let sx=margin;sx<width;sx+=spacing)for(let sy=95+margin;sy<height;sy+=spacing){
      const x=state.x+(sx-width/2)/scale,y=state.y+(sy-height/2)/scale;if(isLand(x,y))continue;
      const flow=currentAt(x,y),speed=flow.knots;if(speed<.08)continue;
      const mag=Math.max(.001,Math.hypot(flow.vx,flow.vy)),ux=flow.vx/mag,uy=flow.vy/mag,length=30+speed*18,x1=sx-ux*length*.5,y1=sy-uy*length*.5,x2=sx+ux*length*.5,y2=sy+uy*length*.5,head=10;
      ctx.strokeStyle=`rgba(229,251,255,${.12+speed*.035})`;ctx.fillStyle=`rgba(235,253,255,${.28+speed*.08})`;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.moveTo(x2,y2);ctx.lineTo(x2-ux*head-uy*head*.62,y2-uy*head+ux*head*.62);ctx.moveTo(x2,y2);ctx.lineTo(x2-ux*head+uy*head*.62,y2-uy*head-ux*head*.62);ctx.stroke();ctx.font='700 9px system-ui';ctx.fillText(speed.toFixed(1)+' kn',sx,sy+length*.56+4);
    }
    ctx.restore();
  }
  function drawFishSchools(){
    if(zoomLevel<.4)return;
    const now=performance.now()/420;
    ctx.save();
    for(const school of fishSchools){
      const ice=iceTypeAt(school.x,school.y);if(ice==='packed'||ice==='cracked'||ice==='fast'||isLand(school.x,school.y)||!wildlifeClearOfPorts(school.x,school.y))continue;
      const p=worldToScreen(school.x,school.y);if(p.x<-65||p.x>width+65||p.y<70||p.y>height+50)continue;
      const style=FISH_STYLES[school.species],visibleCount=Math.min(school.count,zoomLevel<.65?8:school.count);
      ctx.save();ctx.translate(p.x,p.y);ctx.rotate(school.angle);ctx.globalAlpha=.58;
      for(let i=0;i<visibleCount;i++){
        const row=Math.floor(i/5),col=i%5,ox=(col-2)*8+Math.sin(i*3.1+school.phase)*2,oy=(row-(visibleCount/5-1)/2)*7+Math.cos(i*2.7+school.phase)*2,wag=Math.sin(now+i*1.9+school.phase)*1.2,s=style.size*(.82+(i%3)*.1);
        ctx.fillStyle=style.color;ctx.strokeStyle='rgba(222,246,244,.68)';ctx.lineWidth=.7;ctx.beginPath();ctx.ellipse(ox,oy,s,s*.38,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(ox-s,oy);ctx.lineTo(ox-s-3,oy-2.8+wag);ctx.lineTo(ox-s-3,oy+2.8+wag);ctx.closePath();ctx.fill();
      }
      ctx.restore();drawAnimalLabel(`${school.species} SCHOOL`,p.x,p.y-8);
    }
    ctx.restore();
  }
  function drawMap(){
    const g=ctx.createRadialGradient(width*.5,height*.45,30,width*.5,height*.5,Math.max(width,height));g.addColorStop(0,'#8fcbd7');g.addColorStop(.56,'#3f91aa');g.addColorStop(1,'#1f607e');ctx.fillStyle=g;ctx.fillRect(0,0,width,height);
    const realTerrain=drawTerrainMain();if(!realTerrain)drawBathymetry();
    drawGraticule();drawCurrentArrows();drawChartBoundary();captureOceanLayer();
    drawFishSchools();const margin=20/scale,minX=state.x-width/scale/2-margin,maxX=state.x+width/scale/2+margin,minY=state.y-height/scale/2-margin,maxY=state.y+height/scale/2+margin;drawSeasonalIce(minX,maxX,minY,maxY);
    drawIceThicknessAndCracks();drawMarginalFloes();drawWakeFloes();
    if(realTerrain){drawRasterSeasonalOverlay();}else{const nearSvalbard=(()=>{const pos=unpolar(state.x,state.y);return pos.lat>74.5&&pos.lat<82.5&&pos.lon>-5&&pos.lon<45;})();land.forEach(shape=>{const visible=!(shape.maxX<minX||shape.minX>maxX||shape.maxY<minY||shape.minY>maxY)||nearSvalbard&&svalbardLand.includes(shape);if(!visible)return;pathPolygon(ctx,shape.pts,worldToScreen);ctx.fillStyle=shape.color;ctx.fill();ctx.strokeStyle='rgba(239,247,221,.9)';ctx.lineWidth=2;ctx.stroke();drawLandTopography(shape);});}
    drawRivers(minX,maxX,minY,maxY);
    chartLabels.forEach(drawChartLabel);
    const pole=worldToScreen(0,0);ctx.strokeStyle='rgba(255,255,255,.88)';ctx.lineWidth=1;ctx.beginPath();ctx.arc(pole.x,pole.y,22,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(pole.x-30,pole.y);ctx.lineTo(pole.x+30,pole.y);ctx.moveTo(pole.x,pole.y-30);ctx.lineTo(pole.x,pole.y+30);ctx.stroke();text('NORTH POLE',89.35,180,10,'#efffff');const hp=worldToScreen(port.x,port.y);ctx.fillStyle='#f6d365';ctx.beginPath();ctx.arc(hp.x,hp.y,6,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#fff5ba';ctx.lineWidth=2;ctx.beginPath();ctx.arc(hp.x,hp.y,12+Math.sin(performance.now()/350)*2,0,Math.PI*2);ctx.stroke();drawWildlifeIcons();
    if(realTerrain){ctx.save();ctx.font='700 7px system-ui';ctx.textAlign='right';ctx.fillStyle='rgba(230,248,250,.58)';ctx.fillText('TERRAIN: IBCAO / GEBCO · HI-RES TILES',width-12,height-10);ctx.restore();}
  }

  function miniMapGeometry(){const fullRadius=terrainLatitudeRadius(MIN_LAT),localRadius=520,t=Math.max(0,Math.min(1,(2.8-zoomLevel)/(2.8-.3))),ease=t*t*(3-2*t),worldRadius=localRadius+(fullRadius-localRadius)*ease,blend=Math.max(0,Math.min(1,(fullRadius-worldRadius)/(fullRadius-localRadius)));return{worldRadius,centerX:state.x*blend,centerY:state.y*blend};}
  function drawMiniMap(){
    const size=Math.max(120,miniCanvas.clientWidth||148),c=size/2,radius=size*.45,geometry=miniMapGeometry(),worldRadius=geometry.worldRadius;mini.clearRect(0,0,size,size);mini.save();mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.clip();const project=(x,y)=>({x:c+(x-geometry.centerX)/worldRadius*radius,y:c+(y-geometry.centerY)/worldRadius*radius});const miniTerrain=drawTerrainRaster(mini,project,.94);if(!miniTerrain){const g=mini.createRadialGradient(c,c,0,c,c,radius);g.addColorStop(0,'#8fd4e2');g.addColorStop(1,'#337f9a');mini.fillStyle=g;mini.fillRect(0,0,size,size);}[65,70,75,80,85].forEach(lat=>{const pole=project(0,0),ring=terrainLatitudeRadius(lat)/worldRadius*radius;mini.strokeStyle='rgba(255,255,255,.2)';mini.lineWidth=.7;mini.beginPath();mini.arc(pole.x,pole.y,ring,0,Math.PI*2);mini.stroke();});if(!miniTerrain)land.forEach(shape=>{pathPolygon(mini,shape.pts,project);mini.fillStyle=shape.color;mini.fill();mini.strokeStyle='rgba(245,251,231,.72)';mini.lineWidth=.35;mini.stroke();});
    mini.font='900 9px Georgia,serif';mini.textAlign='center';mini.textBaseline='middle';
    for(const target of researchTargets()){const w=polar(target.lat,target.lon),raw=project(w.x,w.y),dx=raw.x-c,dy=raw.y-c,d=Math.hypot(dx,dy),official=target.kind==='grant'||target.kind==='contract';let dot=raw;if(d>radius-5){if(!official)continue;const k=(radius-6)/(d||1);dot={x:c+dx*k,y:c+dy*k};}const eligible=target.mapEligible!==false;mini.fillStyle=official?'#f6d365':eligible?'#8ef0cf':'#83979c';mini.strokeStyle='rgba(5,34,48,.95)';mini.lineWidth=2;mini.strokeText('?',dot.x,dot.y);mini.fillText('?',dot.x,dot.y);if(official&&d>radius-5){mini.strokeStyle='rgba(246,211,101,.9)';mini.lineWidth=1;mini.beginPath();mini.arc(dot.x,dot.y,6,0,Math.PI*2);mini.stroke();}}
    mini.fillStyle='#e84f4f';mini.strokeStyle='rgba(255,240,225,.9)';mini.lineWidth=.7;cityLabels.forEach(city=>{const w=polar(city.lat,city.lon),dot=project(w.x,w.y);if(Math.hypot(dot.x-c,dot.y-c)>radius+3)return;mini.beginPath();mini.arc(dot.x,dot.y,1.8,0,Math.PI*2);mini.fill();mini.stroke();});const p=project(state.x,state.y);mini.fillStyle='#f9d55d';mini.shadowColor='#fff3a4';mini.shadowBlur=7;mini.beginPath();mini.arc(p.x,p.y,3.7,0,Math.PI*2);mini.fill();mini.shadowBlur=0;mini.strokeStyle='#fff';mini.lineWidth=1;mini.stroke();const viewW=Math.min(radius*2,width/scale/worldRadius*radius),viewH=Math.min(radius*2,height/scale/worldRadius*radius);mini.strokeStyle='rgba(255,243,164,.68)';mini.lineWidth=.8;mini.strokeRect(p.x-viewW/2,p.y-viewH/2,viewW,viewH);mini.restore();mini.strokeStyle='rgba(218,247,252,.6)';mini.lineWidth=1;mini.beginPath();mini.arc(c,c,radius,0,Math.PI*2);mini.stroke();
  }
  function seasonalBrightness(){const d=state.seasonDay;if(d<=111){const t=d/111;return 1-.97*(.5-.5*Math.cos(Math.PI*t));}if(d<=293){const t=(d-111)/182;return.03+.97*(.5-.5*Math.cos(Math.PI*t));}return 1;}
  function drawSeasonalLighting(){const darkness=(1-seasonalBrightness())*.985;if(darkness<.01)return;const floodlight=state.seasonDay>=21&&state.seasonDay<200,x=width/2,y=height/2,theta=state.angle-Math.PI/2,length=280;light.clearRect(0,0,width,height);light.globalCompositeOperation='source-over';light.fillStyle=`rgba(0,5,14,${darkness})`;light.fillRect(0,0,width,height);if(floodlight){light.globalCompositeOperation='destination-out';for(let i=18;i>=0;i--){const t=i/18,distance=t*length,cx=x+Math.cos(theta)*distance,cy=y+Math.sin(theta)*distance,radius=18+distance*.2,intensity=.52*Math.pow(1-t,1.35),beam=light.createRadialGradient(cx,cy,0,cx,cy,radius);beam.addColorStop(0,`rgba(0,0,0,${intensity})`);beam.addColorStop(.42,`rgba(0,0,0,${intensity*.72})`);beam.addColorStop(1,'rgba(0,0,0,0)');light.fillStyle=beam;light.beginPath();light.arc(cx,cy,radius,0,Math.PI*2);light.fill();}const nearGlow=light.createRadialGradient(x,y,0,x,y,58);nearGlow.addColorStop(0,'rgba(0,0,0,.72)');nearGlow.addColorStop(1,'rgba(0,0,0,0)');light.fillStyle=nearGlow;light.beginPath();light.arc(x,y,58,0,Math.PI*2);light.fill();}light.globalCompositeOperation='source-over';ctx.drawImage(lightCanvas,0,0,width,height);}
  const weatherRandom=n=>{const x=Math.sin(n*91.713+17.17)*43758.5453;return x-Math.floor(x);};
  function currentWeather(){
    if(state.fogClearDays>0)return{type:'clear',label:'CLEAR',rating:0,intensity:0,envelope:0,amount:0,eventId:`clear-${state.year}`,visibilityKm:40,windKnots:5};
    const windowDays=6.5,cycle=Math.floor(state.seasonDay/windowDays),local=state.seasonDay-cycle*windowDays,start=.7+weatherRandom(cycle+13)*1.5,duration=1.1+weatherRandom(cycle+83)*2,fade=.38;let envelope=0;if(local>=start-fade&&local<=start+duration+fade){if(local<start)envelope=smoothstep(start-fade,start,local);else if(local>start+duration)envelope=1-smoothstep(start+duration,start+duration+fade,local);else envelope=1;}if(envelope<=.025)return{type:'clear',label:'CLEAR',rating:0,intensity:0,envelope:0,amount:0,eventId:`clear-${state.year}-${cycle}`,visibilityKm:40,windKnots:5};
    const warm=state.seasonDay<38||state.seasonDay>270,dark=seasonalBrightness()<.28,choice=weatherRandom(cycle+251);let type;if(dark&&choice<.26)type='aurora';else if(warm)type=choice<.38?'fog':choice<.66?'high-wind':'rain';else type=choice<.3?'fog':choice<.58?'high-wind':'snow';
    const rating=1+Math.floor(weatherRandom(cycle+157)*10),amount=envelope*rating/10,eventId=`${state.year}-${cycle}-${type}`,visibilityKm=type==='aurora'?40:type==='fog'?Math.max(1,Math.round(1+37*Math.pow(1-amount,1.7))):type==='snow'?Math.max(3,Math.round(23-amount*18)):type==='rain'?Math.max(5,Math.round(28-amount*18)):Math.max(10,Math.round(35-amount*14)),windKnots=type==='aurora'?4+rating*.3:type==='high-wind'?24+rating*2:type==='snow'?9+rating:type==='rain'?11+rating:5+rating*.8;
    return{type,label:type==='high-wind'?'HIGH WIND':type.toUpperCase(),rating,intensity:amount,envelope,amount,eventId,visibilityKm,windKnots};
  }
  function updateWeatherAnnouncement(weather=currentWeather()){if(weather.type!=='clear'&&weather.envelope>.04&&announcedWeatherEvent!==weather.eventId){announcedWeatherEvent=weather.eventId;showToast(`${weather.label} DEVELOPING — INTENSITY ${weather.rating}/10`,3200);research?.maybeSpawnOpportunity?.({position:unpolar(state.x,state.y),ice:iceTypeAt(state.x,state.y),location:locationName(unpolar(state.x,state.y).lat,unpolar(state.x,state.y).lon),weather});}ui.weatherValue.textContent=weather.type==='clear'?'CLEAR':`${weather.label} ${weather.rating}/10 · ${weather.visibilityKm} KM`;return weather;}
  function drawWeather(weather=currentWeather()){if(weather.type==='clear'||weather.intensity<.03)return;const t=performance.now()/1000,count=Math.round(28+weather.rating*8);ctx.save();ctx.lineCap='round';if(weather.type==='rain'){ctx.strokeStyle=`rgba(174,225,241,${.13+weather.intensity*.38})`;ctx.lineWidth=1.2;for(let i=0;i<count;i++){const x=((i*137+t*(55+weather.windKnots*2))%(width+100))-50,y=((i*83+t*(150+i%5*7))%(height+100))-50;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+8+weather.windKnots*.18,y+16);ctx.stroke();}}else if(weather.type==='snow'){ctx.fillStyle=`rgba(230,245,247,${.18+weather.intensity*.5})`;for(let i=0;i<count;i++){const x=((i*149+t*(16+weather.windKnots))%(width+80))-40,y=((i*97+t*(25+i%7*3))%(height+80))-40,r=1+(i%4)*.38;ctx.beginPath();ctx.arc(x+Math.sin(t+i)*7,y,r,0,Math.PI*2);ctx.fill();}}else if(weather.type==='high-wind'){ctx.strokeStyle=`rgba(202,239,247,${.06+weather.intensity*.2})`;ctx.lineWidth=1;for(let i=0;i<Math.round(count*.55);i++){const y=(i*71+t*7)%(height+80)-40,x=((i*193+t*weather.windKnots*8)%(width+220))-110,len=25+weather.rating*3;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+len,y-5);ctx.stroke();}}else if(weather.type==='aurora'){ctx.globalCompositeOperation='screen';for(let band=0;band<4;band++){const y=80+band*38+Math.sin(t*.35+band)*28,g=ctx.createLinearGradient(0,y-35,width,y+35);g.addColorStop(0,'rgba(80,255,177,0)');g.addColorStop(.3,`rgba(80,255,177,${.08+weather.intensity*.2})`);g.addColorStop(.65,`rgba(135,220,255,${.06+weather.intensity*.14})`);g.addColorStop(1,'rgba(150,95,255,0)');ctx.strokeStyle=g;ctx.lineWidth=14+band*5;ctx.beginPath();for(let x=0;x<=width;x+=28){const yy=y+Math.sin(x/100+t*.45+band)*18+Math.sin(x/43-band)*5;x?ctx.lineTo(x,yy):ctx.moveTo(x,yy);}ctx.stroke();}}ctx.restore();}
  function drawFog(weather=currentWeather()){if(weather.type!=='fog'||weather.amount<.01)return;const amount=weather.amount,x=width/2,y=height/2,bonus=vesselModifiers().visibilityBonusKm,visibility=Math.max(58,(weather.visibilityKm+bonus)*scale),day=Math.pow(seasonalBrightness(),.42),fr=Math.round(18+(247-18)*day),fg=Math.round(29+(249-29)*day),fb=Math.round(43+(247-43)*day),g=ctx.createRadialGradient(x,y,20,x,y,visibility),outerOpacity=.06+amount*.91;colorStop(g,0,fr,fg,fb,amount*.05);colorStop(g,.42,fr,fg,fb,amount*.14);colorStop(g,.72,fr,fg,fb,amount*.48);colorStop(g,1,fr,fg,fb,outerOpacity);ctx.save();ctx.fillStyle=g;ctx.fillRect(0,0,width,height);const drift=performance.now()/9500;for(let i=0;i<7;i++){const cx=((i*317+drift*34)%(width+360))-180,cy=90+((i*173+Math.sin(drift+i)*70)%(height+180)),r=130+(i%3)*55,cloud=ctx.createRadialGradient(cx,cy,0,cx,cy,r);colorStop(cloud,0,fr,fg,fb,amount*.11);colorStop(cloud,1,fr,fg,fb,0);ctx.fillStyle=cloud;ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.fill();}ctx.restore();}
  function colorStop(gradient,position,r,g,b,a){gradient.addColorStop(position,`rgba(${r},${g},${b},${a})`);}
  function drawPortMarkers(){ctx.save();ctx.textAlign='center';ctx.textBaseline='bottom';cityLabels.forEach(city=>{const w=polar(city.lat,city.lon),p=worldToScreen(w.x,w.y);if(p.x<-18||p.x>width+18||p.y<75||p.y>height+18)return;const distance=Math.hypot(w.x-state.x,w.y-state.y),nearby=distance<=180;if(nearby){ctx.strokeStyle='rgba(246,211,101,.9)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(p.x,p.y,9+Math.sin(performance.now()/360)*1.2,0,Math.PI*2);ctx.stroke();}ctx.fillStyle='#ef4444';ctx.strokeStyle='#fff3df';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,4.5,0,Math.PI*2);ctx.fill();ctx.stroke();if(nearby){ctx.font='800 9px system-ui';ctx.strokeStyle='rgba(5,25,36,.92)';ctx.lineWidth=3;ctx.strokeText(city.name,p.x,p.y-10);ctx.fillStyle='#fff4e4';ctx.fillText(city.name,p.x,p.y-10);}});ctx.restore();}
  function isResearchSiteSuitable(point,context={}){
    if(!Number.isFinite(point?.lat)||!Number.isFinite(point?.lon)||point.lat<MIN_LAT+.08)return false;const site=polar(point.lat,point.lon),siteIce=iceTypeAt(site.x,site.y),template=context.template||{},iceAllowed=!!template.iceAllowed;if(isLand(site.x,site.y)||siteIce==='fast'||siteIce==='packed'||(siteIce==='cracked'&&!iceAllowed))return false;
    const clearance=coastDistance(site.x,site.y,120),shore=!!(template.shore||template.terrestrial),coastal=!!template.coastal;
    if(shore&&(clearance<.5||clearance>7))return false;if(coastal&&!shore&&(clearance<3||clearance>85))return false;if(!coastal&&!shore&&!iceAllowed&&clearance<8)return false;
    if(template.glacier){let best=Infinity;for(const g of GLACIER_SITES){const w=polar(g.lat,g.lon);best=Math.min(best,Math.hypot(site.x-w.x,site.y-w.y));}if(best>28)return false;}
    const dx=site.x-state.x,dy=site.y-state.y,length=Math.hypot(dx,dy),steps=Math.max(24,Math.ceil(length/2)),origin=context.origin&&polar(context.origin.lat,context.origin.lon),outX=origin?state.x-origin.x:0,outY=origin?state.y-origin.y:0,outLength=Math.hypot(outX,outY);if(outLength>4&&(dx*outX+dy*outY)/(Math.max(1,length)*outLength)<.05)return false;for(let step=1;step<=steps;step++){const x=state.x+dx*step/steps,y=state.y+dy*step/steps,type=iceTypeAt(x,y);if(unpolar(x,y).lat<MIN_LAT+.04||isLand(x,y)||type==='fast'||type==='packed'||(type==='cracked'&&!iceAllowed))return false;}return true;
  }
  function findResearchSite(context={}){
    const template=context.template||{};
    if(template.glacier){const origin=context.origin||unpolar(state.x,state.y),sites=[...GLACIER_SITES].sort((a,b)=>Math.hypot(polar(a.lat,a.lon).x-state.x,polar(a.lat,a.lon).y-state.y)-Math.hypot(polar(b.lat,b.lon).x-state.x,polar(b.lat,b.lon).y-state.y));for(const glacier of sites){const center=polar(glacier.lat,glacier.lon);for(let radius=2;radius<=28;radius+=2)for(let i=0;i<36;i++){const a=i*Math.PI/18,pt=unpolar(center.x+Math.cos(a)*radius,center.y+Math.sin(a)*radius);pt.siteName=glacier.name;if(isResearchSiteSuitable(pt,context))return pt;}}}
    const origin=context.origin&&polar(context.origin.lat,context.origin.lon),outX=origin?state.x-origin.x:0,outY=origin?state.y-origin.y:0,outLength=Math.hypot(outX,outY),base=outLength>4?Math.atan2(outY,outX):state.commandActive?Math.atan2(state.ty-state.y,state.tx-state.x):state.angle-Math.PI/2;
    const shore=!!(template.shore||template.terrestrial),distances=shore?[12,20,30,45,60,80]:(context.kind==='opportunity'?[28,45,65,85,110,140]:[45,65,85,105,130,165,210]),offsets=[0,-15,15,-30,30,-45,45,-60,60,-75,75,-90,90,120,-120,150,-150];for(const distance of distances)for(const degrees of offsets){const angle=base+degrees*Math.PI/180,point=unpolar(state.x+Math.cos(angle)*distance,state.y+Math.sin(angle)*distance);if(isResearchSiteSuitable(point,context))return point;}return null;
  }
  function researchEnvironment(weather=currentWeather()){
    const position=unpolar(state.x,state.y),coastDistanceKm=coastDistance(state.x,state.y,120),landSectors=[];
    for(let sector=0;sector<12;sector++){const angle=sector*Math.PI/6;let landSeen=false;for(const radius of[10,24,45])if(isLand(state.x+Math.cos(angle)*radius,state.y+Math.sin(angle)*radius)){landSeen=true;break;}landSectors.push(landSeen);}
    const landHits=landSectors.filter(Boolean).length,opposed=landSectors.slice(0,6).filter((value,index)=>value&&landSectors[index+6]).length;
    const fjordScore=Math.max(0,Math.min(1,landHits/12*.7+opposed/6*.75+(coastDistanceKm<35?.18:0)));
    const ice=iceTypeAt(state.x,state.y),packEdge=packIceEdge(position.lon),iceEdge=ice==='marginal'||Math.abs(position.lat-packEdge)<2.8;return{position,ice,iceEdge,location:locationName(position.lat,position.lon),weather,coastDistanceKm,coastal:coastDistanceKm<=85,fjord:fjordScore>=.48,fjordScore};
  }
  function targetStationPoints(target){return(target?.stations||target?.points||[]).filter(point=>Number.isFinite(point.lat)&&Number.isFinite(point.lon));}
  function estimateMissionResources(target,options={}){
    const resources={fuel:state.fuel,food:state.food},vessel=vesselModifiers(),stations=targetStationPoints(target),startIndex=Math.max(0,target?.stationIndex||0),remaining=stations.length?stations.slice(startIndex):Number.isFinite(target?.lat)&&Number.isFinite(target?.lon)?[{lat:target.lat,lon:target.lon}]:[];
    let previous={x:state.x,y:state.y},routeKm=0,last=previous;
    if(!target?.anywhere)for(const point of remaining){const next=polar(point.lat,point.lon);routeKm+=Math.hypot(next.x-previous.x,next.y-previous.y);previous=next;last=next;}
    let returnKm=Infinity,returnPort='nearest port';for(const city of cityLabels){const portPoint=polar(city.lat,city.lon),distance=Math.hypot(portPoint.x-last.x,portPoint.y-last.y);if(distance<returnKm){returnKm=distance;returnPort=city.name;}}
    if(!Number.isFinite(returnKm))returnKm=0;routeKm+=returnKm;
    const cruiseKmPerDay=Math.max(1,vessel.cruiseKnots*1.852*24),travelDays=routeKm/cruiseKmPerDay,workDays=Math.max(0,Number(options.workDays??target?.estimatedDays??((target?.workHours||0)/8))||0);
    const fuelBurn=vessel.nuclearFuel?0:travelDays*200/Math.max(1,vessel.fuelEnduranceDays),foodBurn=(travelDays+workDays)*100/Math.max(1,vessel.foodEnduranceDays);
    return{routeKm,returnKm,returnPort,travelDays,workDays,fuelAfter:vessel.nuclearFuel?100:resources.fuel-fuelBurn,foodAfter:resources.food-foodBurn};
  }
  function researchTargets(){return(research?.getMapTargets?.()||[]).filter(target=>Number.isFinite(target.lat)&&Number.isFinite(target.lon)&&target.status!=='completed');}
  function researchTargetWorld(target){const w=polar(target.lat,target.lon);return{target,w,p:worldToScreen(w.x,w.y),distance:Math.hypot(w.x-state.x,w.y-state.y)};}
  function nearbyResearchTargetAt(clientX,clientY){let match=null,best=27;for(const target of researchTargets()){const item=researchTargetWorld(target),hit=Math.hypot(item.p.x-clientX,item.p.y-clientY);if(hit<best){match=item;best=hit;}}return match;}
  function drawResearchTargets(afterFog=false){
    const pulse=.5+.5*Math.sin(performance.now()/350);ctx.save();ctx.textAlign='center';ctx.textBaseline='bottom';const targets=researchTargets().filter(target=>afterFog?(target.kind==='weather-opportunity'&&target.weather==='fog'):!(target.kind==='weather-opportunity'&&target.weather==='fog'));
    if(!afterFog)for(const target of targets){const stations=targetStationPoints(target);if(stations.length<2)continue;const active=Math.max(0,target.stationIndex||0),points=stations.map(station=>{const w=polar(station.lat,station.lon);return worldToScreen(w.x,w.y);});ctx.strokeStyle='rgba(246,211,101,.58)';ctx.lineWidth=2;ctx.setLineDash([6,5]);ctx.beginPath();points.forEach((point,index)=>index?ctx.lineTo(point.x,point.y):ctx.moveTo(point.x,point.y));ctx.stroke();ctx.setLineDash([]);points.forEach((point,index)=>{if(point.x<-30||point.x>width+30||point.y<70||point.y>height+30)return;ctx.fillStyle=index<active?'#6ee7b7':index===active?'#f6d365':'rgba(7,45,60,.9)';ctx.strokeStyle='#f4fdff';ctx.lineWidth=1.3;ctx.beginPath();ctx.arc(point.x,point.y,index===active?7:5.5,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle=index===active?'#183745':'#f4fdff';ctx.font='900 7px system-ui';ctx.textBaseline='middle';ctx.fillText(String(index+1),point.x,point.y+.5);ctx.textBaseline='bottom';});}
    for(const target of targets){const item=researchTargetWorld(target),p=item.p;if(p.x<-45||p.x>width+45||p.y<70||p.y>height+45)continue;const field=target.kind==='opportunity'||target.kind==='weather-opportunity',eligible=target.mapEligible!==false,official=!field,selected=target.selected||target.active,outer=selected?17+pulse*3:13+pulse*2;ctx.font='900 28px Georgia,serif';ctx.textBaseline='middle';ctx.lineWidth=4;ctx.strokeStyle='rgba(5,34,48,.95)';ctx.strokeText('?',p.x,p.y);ctx.fillStyle=official?'#f6d365':eligible?'#8ef0cf':'#8a9da2';ctx.fillText('?',p.x,p.y);if(official||eligible){ctx.strokeStyle=official?'rgba(246,211,101,.88)':'rgba(142,240,207,.82)';ctx.shadowColor=official?'#f6d365':'#8ef0cf';ctx.shadowBlur=10+pulse*7;ctx.lineWidth=1.8;ctx.beginPath();ctx.arc(p.x,p.y,outer,0,Math.PI*2);ctx.stroke();ctx.shadowBlur=0;}if(!afterFog&&(zoomLevel>=.55||item.distance<180)){const count=targetStationPoints(target).length,stationText=count?` · ${Math.min(count,(target.stationIndex||0)+1)}/${count}`:'',site=target.siteName?` · ${target.siteName}`:'',label=(target.shortTitle||target.title||'RESEARCH SITE')+stationText+site;ctx.font='800 9px system-ui';ctx.textBaseline='bottom';ctx.lineWidth=3;ctx.strokeStyle='rgba(4,28,42,.94)';ctx.strokeText(label.toUpperCase(),p.x,p.y-19);ctx.fillStyle='#f4fdff';ctx.fillText(label.toUpperCase(),p.x,p.y-19);}}
    ctx.restore();
  }
  function selectedResearchTarget(){return researchTargets().find(target=>target.selected||target.active)||null;}
  function updateResearchNavigation(){const target=selectedResearchTarget();if(!target){pendingResearchTargetId=null;research?.updateNavigation?.(null);return;}const item=researchTargetWorld(target),dx=item.w.x-state.x,dy=item.w.y-state.y,bearing=(Math.atan2(dx,dy)*180/Math.PI+360)%360;research?.updateNavigation?.({id:target.id,target,distanceKm:item.distance,bearingDeg:bearing});if(pendingResearchTargetId===target.id&&item.distance<=RESEARCH_INTERACTION_KM&&!research?.isBusy?.()){pendingResearchTargetId=null;state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:true,target});}}
  function drawResearchGuidance(){const target=selectedResearchTarget();if(!target||target.kind==='opportunity'||target.kind==='weather-opportunity')return;const item=researchTargetWorld(target),p=item.p;if(p.x>35&&p.x<width-35&&p.y>95&&p.y<height-35)return;const cx=width/2,cy=height/2,dx=p.x-cx,dy=p.y-cy,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length,edge=Math.min(width*.38,height*.36),x=cx+ux*edge,y=cy+uy*edge,a=Math.atan2(uy,ux);ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.fillStyle='rgba(246,211,101,.96)';ctx.strokeStyle='rgba(5,34,48,.9)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(14,0);ctx.lineTo(-8,-8);ctx.lineTo(-4,0);ctx.lineTo(-8,8);ctx.closePath();ctx.fill();ctx.stroke();ctx.rotate(-a);ctx.font='800 9px system-ui';ctx.textAlign='center';ctx.strokeStyle='rgba(5,34,48,.95)';ctx.lineWidth=3;ctx.strokeText(`${Math.round(item.distance)} KM`,0,24);ctx.fillStyle='#fff3aa';ctx.fillText(`${Math.round(item.distance)} KM`,0,24);ctx.restore();}
  function navigateToResearchTarget(target){if(!target)return;const center=polar(target.lat,target.lon);let destination=center;if(isBlocked(center.x,center.y)||iceTypeAt(center.x,center.y)==='fast'||iceTypeAt(center.x,center.y)==='packed'){let best=null,bestDistance=Infinity;for(let radius=8;radius<=55;radius+=5)for(let i=0;i<36;i++){const a=i*Math.PI/18,x=center.x+Math.cos(a)*radius,y=center.y+Math.sin(a)*radius,type=iceTypeAt(x,y);if(unpolar(x,y).lat<MIN_LAT||isBlocked(x,y)||type==='fast'||type==='packed')continue;const distance=Math.hypot(x-state.x,y-state.y);if(distance<bestDistance){best={x,y};bestDistance=distance;}}if(best)destination=best;}research?.selectTarget?.(target.id);target.selected=true;pendingResearchTargetId=target.id;setWorldDestination(destination.x,destination.y);showToast(`COURSE TO RESEARCH SITE — ${target.title||'OPPORTUNITY'}`,2200);}
  function nearestOpenWater(x,y,phase=0){if(!isLand(x,y)&&wildlifeClearOfPorts(x,y))return{x,y};for(let radius=8;radius<=180;radius+=8){for(let i=0;i<20;i++){const a=phase+i*Math.PI/10,cx=x+Math.cos(a)*radius,cy=y+Math.sin(a)*radius;if(!isLand(cx,cy)&&unpolar(cx,cy).lat>=MIN_LAT&&wildlifeClearOfPorts(cx,cy))return{x:cx,y:cy};}}return{x,y};}
  function nearestLand(x,y,phase=0){if(isLand(x,y)&&wildlifeClearOfPorts(x,y))return{x,y};for(let radius=4;radius<=180;radius+=4){for(let i=0;i<24;i++){const a=phase+i*Math.PI/12,cx=x+Math.cos(a)*radius,cy=y+Math.sin(a)*radius;if(isLand(cx,cy)&&wildlifeClearOfPorts(cx,cy))return{x:cx,y:cy};}}return{x,y};}
  function deepLand(x,y,phase=0,predicate=wildlifeClearOfPorts){for(let radius=0;radius<=220;radius+=4){for(let i=0;i<24;i++){const a=phase+i*Math.PI/12,cx=x+Math.cos(a)*radius,cy=y+Math.sin(a)*radius;if(!isLand(cx,cy)||!predicate(cx,cy))continue;let safe=true;for(let j=0;j<16;j++){const edge=j*Math.PI/8;if(!isLand(cx+Math.cos(edge)*6,cy+Math.sin(edge)*6)){safe=false;break;}}if(safe)return{x:cx,y:cy};}}return nearestLand(x,y,phase);}
  for(const fox of arcticFoxes){const anchor=polar(fox.lat,fox.lon),safe=deepLand(anchor.x,anchor.y,fox.phase),position=unpolar(safe.x,safe.y);fox.lat=position.lat;fox.lon=position.lon;}
  for(const animal of landWildlife){const anchor=polar(animal.lat,animal.lon),safe=deepLand(anchor.x,anchor.y,animal.phase);animal.x=safe.x;animal.y=safe.y;}
  for(const bird of summerBirds){if(bird.kind!=='owl')continue;const anchor=polar(bird.lat,bird.lon),safe=deepLand(anchor.x,anchor.y,bird.phase);bird.x=safe.x;bird.y=safe.y;}
  const summerWildlifeVisible=()=>state.seasonDay<28||state.seasonDay>=242;
  function landAnimalWorld(animal){const a=state.seasonDay*.22+animal.phase,r=2.5+Math.sin(animal.phase)*.7,nx=animal.x+Math.cos(a)*r,ny=animal.y+Math.sin(a)*r;return isLand(nx,ny)&&wildlifeClearOfPorts(nx,ny)?{x:nx,y:ny}:{x:animal.x,y:animal.y};}
  function summerBirdWorld(bird){if(bird.kind==='owl')return landAnimalWorld(bird);const anchor=polar(bird.lat,bird.lon),a=state.seasonDay*.82+bird.phase,r=7+3*Math.sin(state.seasonDay*.17+bird.phase),w={x:anchor.x+Math.cos(a)*r,y:anchor.y+Math.sin(a)*r};return wildlifeClearOfPorts(w.x,w.y)?w:anchor;}
  function foxWorld(fox){const anchor=polar(fox.lat,fox.lon),a=state.seasonDay*.9+fox.phase,w={x:anchor.x+Math.cos(a)*4,y:anchor.y+Math.sin(a)*4};return wildlifeClearOfPorts(w.x,w.y)?w:anchor;}
  const encounterPick=items=>items[Math.floor(Math.random()*items.length)];
  function regionalSeal(lon){if(lon>130||lon<-130)return encounterPick(['RINGED SEAL','BEARDED SEAL','SPOTTED SEAL','RIBBON SEAL']);if(lon>-85&&lon<10)return encounterPick(['RINGED SEAL','BEARDED SEAL','HARP SEAL','HOODED SEAL']);return encounterPick(['RINGED SEAL','BEARDED SEAL','HARP SEAL']);}
  function regionalWhale(lon){if(lon>130||lon<-130)return encounterPick(['BOWHEAD','BELUGA','GRAY WHALE']);if(lon>-90&&lon<-20)return encounterPick(['NARWHAL','BELUGA','BOWHEAD']);return encounterPick(['HUMPBACK','BELUGA','BOWHEAD']);}
  function regionalFish(lon){if(lon>130||lon<-130)return encounterPick(['ARCTIC COD','SAFFRON COD','CAPELIN','PACIFIC HERRING']);if(lon>-90&&lon<-20)return encounterPick(['ARCTIC COD','CAPELIN','GREENLAND HALIBUT']);return encounterPick(['ARCTIC COD','CAPELIN','ATLANTIC HERRING','NORTHEAST ARCTIC COD']);}
  function regionalBird(lon){if(lon>130||lon<-130)return encounterPick(['KING EIDER','ARCTIC TERN','SNOW GOOSE']);if(lon>-90&&lon<-20)return encounterPick(['KING EIDER','ARCTIC TERN','BRENT GOOSE','THICK-BILLED MURRE']);return encounterPick(['COMMON EIDER','ARCTIC TERN','BARNACLE GOOSE','PINK-FOOTED GOOSE']);}
  function localWildlifeCount(radius=175){const near=(x,y)=>wildlifeClearOfPorts(x,y)&&Math.hypot(x-state.x,y-state.y)<radius;let total=0;for(const whale of whales)if(near(whale.x,whale.y))total++;for(const school of fishSchools)if(near(school.x,school.y))total++;for(const animal of iceWildlife){const w=iceAnimalWorld(animal);if(near(w.x,w.y))total++;}for(const animal of landWildlife){const w=landAnimalWorld(animal);if(near(w.x,w.y))total++;}for(const fox of arcticFoxes){const w=foxWorld(fox);if(near(w.x,w.y))total++;}if(summerWildlifeVisible())for(const bird of summerBirds){const w=summerBirdWorld(bird);if(near(w.x,w.y))total++;}return total;}
  function retireDistantEncounters(){const far=(x,y)=>Math.hypot(x-state.x,y-state.y)>650,prune=(list,position)=>{for(let i=list.length-1;i>=0;i--){const item=list[i];if(!item.encounter)continue;const p=position(item);if(far(p.x,p.y))list.splice(i,1);}};prune(whales,item=>item);prune(fishSchools,item=>item);prune(iceWildlife,iceAnimalWorld);prune(landWildlife,landAnimalWorld);prune(arcticFoxes,foxWorld);prune(summerBirds,summerBirdWorld);}
  function spawnWildlifeEncounter(){const heading=state.commandActive?Math.atan2(state.ty-state.y,state.tx-state.x):state.angle-Math.PI/2;for(let attempt=0;attempt<16;attempt++){const a=heading+(Math.random()-.5)*2.15,distance=50+Math.random()*95,x=state.x+Math.cos(a)*distance,y=state.y+Math.sin(a)*distance,pos=unpolar(x,y);if(pos.lat<MIN_LAT+.15||!wildlifeClearOfPorts(x,y))continue;const phase=++wildlifeEncounterSerial*.83+Math.random(),roll=Math.random();if(isLand(x,y)){let species=null;if(pos.lon<-75)species='CARIBOU';else if(pos.lon>5&&pos.lat<76.5)species='REINDEER';else if(pos.lat>=76&&pos.lat<=81&&pos.lon>5&&pos.lon<35)species='SVALBARD REINDEER';if(species){landWildlife.push({species,region:'LOCAL ENCOUNTER',x,y,phase,encounter:true});return true;}const safe=deepLand(x,y,phase);if(!wildlifeClearOfPorts(safe.x,safe.y))continue;const ll=unpolar(safe.x,safe.y);arcticFoxes.push({lat:ll.lat,lon:ll.lon,phase,encounter:true});return true;}const ice=iceTypeAt(x,y);if(ice==='marginal'||ice==='cracked'||ice==='packed'){const mode=ice==='marginal'?'floe':'local-pack';if(roll<.2)iceWildlife.push({type:'bear',mode,lat:pos.lat,lon:pos.lon,phase,encounter:true});else if(roll<.34)iceWildlife.push({type:'walrus',species:'WALRUS',mode,lat:pos.lat,lon:pos.lon,phase,encounter:true});else iceWildlife.push({type:'seal',species:regionalSeal(pos.lon),mode,lat:pos.lat,lon:pos.lon,phase,encounter:true});return true;}if(summerWildlifeVisible()&&roll<.2){const species=regionalBird(pos.lon),color=species.includes('TERN')?'#e7ece8':species.includes('GOOSE')?'#555052':species.includes('MURRE')?'#272f33':'#465d62';summerBirds.push({species,lat:pos.lat,lon:pos.lon,phase,color,encounter:true});return true;}if(roll<.65){const species=regionalWhale(pos.lon),colors={BOWHEAD:'#263f52',BELUGA:'#e8f1ed','GRAY WHALE':'#667981',NARWHAL:'#7d929b',HUMPBACK:'#304d61'};whales.push({species,color:colors[species],x,y,angle:a+Math.PI*.6,phase,encounter:true});return true;}const species=regionalFish(pos.lon),style=FISH_STYLES[species];fishSchools.push({species,count:10+Math.floor(Math.random()*7),x,y,homeX:x,homeY:y,angle:a+Math.PI*.4,phase,speed:.7+Math.random()*.3,ready:true,encounter:true,color:style.color});return true;}return false;}
  function updateWildlifeEncounters(dt){wildlifeEncounterClock+=dt;if(wildlifeEncounterClock<1.35)return;wildlifeEncounterClock=0;retireDistantEncounters();const local=localWildlifeCount();if(local<7)spawnWildlifeEncounter();if(local<4)spawnWildlifeEncounter();}
  const sealSwimming=animal=>(animal.type==='seal'||animal.type==='walrus')&&((state.seasonDay+animal.phase*1.7)%9)>(animal.type==='walrus'?7.7:7.2);
  function iceAnimalWorld(animal){let w;if(animal.mode==='local-pack'){const lon=animal.lon+Math.sin(state.seasonDay*.22+animal.phase)*.16,lat=animal.lat+Math.cos(state.seasonDay*.18+animal.phase)*.025;w=polar(lat,lon);return isLand(w.x,w.y)?polar(animal.lat,animal.lon):w;}if(animal.mode==='pack'||animal.mode==='gyre-floe'){const lon=animal.lon+state.seasonDay*4.7+Math.sin(state.seasonDay*.2+animal.phase)*2,swimming=sealSwimming(animal),lat=animal.mode==='gyre-floe'?packIceEdge(lon)-(.75+Math.sin(animal.phase)*.2):packIceEdge(lon)+(swimming?-.45:(animal.depth??(animal.type==='bear'?.45:.04)));w=polar(lat,lon);return nearestOpenWater(w.x,w.y,animal.phase);}const anchor=polar(animal.lat,animal.lon),swimming=sealSwimming(animal),a=state.seasonDay*(swimming?.95:animal.mode==='floe'?.42:.18)+animal.phase,r=swimming?18:animal.mode==='floe'?12:2;w={x:anchor.x+Math.cos(a)*r,y:anchor.y+Math.sin(a)*r};if((animal.type==='seal'||animal.type==='walrus')&&animal.mode==='coast'&&!swimming)return nearestLand(w.x,w.y,animal.phase);return nearestOpenWater(w.x,w.y,animal.phase);}
  function forEachWildlifeVisual(callback){for(const whale of whales)callback(whale,whale.species,'whale',whale);for(const school of fishSchools)callback(school,school.species,'fish',school);for(const animal of iceWildlife)callback(animal,animal.type==='bear'?'POLAR BEAR':animal.species,animal.type==='bear'?'mammal':animal.type==='walrus'?'walrus':'seal',iceAnimalWorld(animal));for(const fox of arcticFoxes)callback(fox,'ARCTIC FOX','mammal',foxWorld(fox));for(const animal of landWildlife)callback(animal,animal.species,'mammal',landAnimalWorld(animal));if(summerWildlifeVisible())for(const bird of summerBirds)callback(bird,bird.species,'bird',summerBirdWorld(bird));}
  function wildlifeAtScreenPoint(clientX,clientY){let result=null,best=30;forEachWildlifeVisual((entity,species,category,w)=>{if(!wildlifeClearOfPorts(w.x,w.y))return;const p=worldToScreen(w.x,w.y);if(p.x<-35||p.x>width+35||p.y<72||p.y>height+35)return;const hit=Math.hypot(p.x-clientX,p.y-clientY);if(hit<best){best=hit;result={species,category,world:w,individualId:ensureWildlifeId(entity),entity};}});return result;}
  function wildlifeObservationAvailable(id){return!!id&&!observedWildlifeFallback.has(id)&&!research?.isWildlifeObserved?.(id);}
  function drawWildlifeIcons(){
    const weather=currentWeather();
    ctx.save();
    forEachWildlifeVisual((entity,species,category,w)=>{
      if(!wildlifeClearOfPorts(w.x,w.y))return;
      const fog=wildlifeFogFactor(w.x,w.y,weather); if(fog<=.03)return;
      const p=worldToScreen(w.x,w.y); if(p.x<-40||p.x>width+40||p.y<70||p.y>height+40)return;
      ctx.save(); ctx.translate(p.x,p.y); ctx.globalAlpha=.92*fog; ctx.lineWidth=1.4; ctx.strokeStyle='rgba(239,252,252,.9)';
      if(category==='whale'){
        ctx.rotate((entity.angle||0)+Math.PI/2);ctx.fillStyle=entity.color||'#355a6d';ctx.beginPath();ctx.ellipse(0,0,12,5.5,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(0,-5);ctx.quadraticCurveTo(-2,-10,1,-12);ctx.quadraticCurveTo(4,-9,3,-5);ctx.fill();ctx.beginPath();ctx.moveTo(-11,0);ctx.lineTo(-17,-5);ctx.lineTo(-16,0);ctx.lineTo(-17,5);ctx.closePath();ctx.fill();
      }else if(category==='seal'||category==='walrus'){
        ctx.fillStyle=category==='walrus'?'#8c684d':'#697d83';ctx.beginPath();ctx.ellipse(0,1,9,5.5,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.arc(7,-1,3.8,0,Math.PI*2);ctx.fill();ctx.stroke();if(category==='walrus'){ctx.strokeStyle='#f0dfbd';ctx.beginPath();ctx.moveTo(9,1);ctx.lineTo(10,6);ctx.moveTo(7.5,1);ctx.lineTo(8,6);ctx.stroke();}
      }else if(category==='bird'){
        ctx.strokeStyle='#eef9fa';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-8,2);ctx.quadraticCurveTo(-3,-5,0,0);ctx.quadraticCurveTo(3,-5,8,2);ctx.stroke();
      }else if(category==='mammal'){
        ctx.fillStyle='#d7e8df';ctx.beginPath();ctx.arc(0,0,6,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#173f50';ctx.fillRect(-1,-7,2,14);
      }
      ctx.restore();
    });
    ctx.restore();
  }
  function wildlifeFogFactor(x,y,weather=currentWeather()){if(weather.type!=='fog'||weather.amount<.04)return 1;const visibility=weather.visibilityKm+(vesselModifiers().visibilityBonusKm||0),distance=Math.hypot(x-state.x,y-state.y);if(distance<=visibility*.55)return 1;if(distance>=visibility*1.2)return 0;return Math.max(0,1-(distance-visibility*.55)/(visibility*.65));}
  function drawWildlifeObservationRings(){const pulse=.5+.5*Math.sin(performance.now()/320),weather=currentWeather();ctx.save();forEachWildlifeVisual((entity,species,category,w)=>{const id=ensureWildlifeId(entity);if(!wildlifeObservationAvailable(id)||!wildlifeClearOfPorts(w.x,w.y))return;const fog=wildlifeFogFactor(w.x,w.y,weather);if(fog<=.03)return;const ice=category==='fish'&&iceTypeAt(w.x,w.y);if(category==='fish'&&(ice==='packed'||ice==='cracked'||ice==='fast'||isLand(w.x,w.y)))return;const p=worldToScreen(w.x,w.y);if(p.x<-45||p.x>width+45||p.y<70||p.y>height+45)return;const radius=(category==='fish'?25:20)+pulse*4;ctx.globalAlpha=fog;ctx.strokeStyle=`rgba(255,225,94,${.5+pulse*.3})`;ctx.shadowColor='#ffe25e';ctx.shadowBlur=(8+pulse*6)*fog;ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,radius,0,Math.PI*2);ctx.stroke();ctx.globalAlpha=1;});ctx.restore();}
  function drawAnimalLabel(label,x,y){ctx.save();ctx.font='800 8px system-ui';ctx.textAlign='center';ctx.textBaseline='bottom';ctx.strokeStyle='rgba(4,28,42,.9)';ctx.lineWidth=3;ctx.strokeText(String(label||'').toUpperCase(),x,y-14);ctx.fillStyle='#eefcff';ctx.fillText(String(label||'').toUpperCase(),x,y-14);ctx.restore();}
  function drawWildlifeLabels(){ctx.save();for(const whale of whales){if(!wildlifeClearOfPorts(whale.x,whale.y))continue;const p=worldToScreen(whale.x,whale.y);if(p.x>-45&&p.x<width+45&&p.y>75&&p.y<height+35)drawAnimalLabel(whale.species,p.x,p.y);}for(const animal of iceWildlife){const w=iceAnimalWorld(animal);if(!wildlifeClearOfPorts(w.x,w.y))continue;const p=worldToScreen(w.x,w.y);if(p.x>-35&&p.x<width+35&&p.y>75&&p.y<height+30)drawAnimalLabel(animal.type==='bear'?'POLAR BEAR':animal.species,p.x,p.y);}for(const fox of arcticFoxes){const w=foxWorld(fox);if(!wildlifeClearOfPorts(w.x,w.y))continue;const p=worldToScreen(w.x,w.y);if(p.x>-30&&p.x<width+30&&p.y>75&&p.y<height+25)drawAnimalLabel('ARCTIC FOX',p.x,p.y);}for(const animal of landWildlife){const w=landAnimalWorld(animal);if(!wildlifeClearOfPorts(w.x,w.y))continue;const p=worldToScreen(w.x,w.y);if(p.x>-35&&p.x<width+35&&p.y>75&&p.y<height+30)drawAnimalLabel(animal.species,p.x,p.y);}if(summerWildlifeVisible())for(const bird of summerBirds){const w=summerBirdWorld(bird);if(!wildlifeClearOfPorts(w.x,w.y))continue;const p=worldToScreen(w.x,w.y);if(p.x>-45&&p.x<width+45&&p.y>75&&p.y<height+35)drawAnimalLabel(bird.species,p.x,p.y);}ctx.restore();}
  function whaleCourseClear(x,y,angle,distance=24){for(let d=4;d<=distance;d+=4){const cx=x+Math.cos(angle)*d,cy=y+Math.sin(angle)*d,type=iceTypeAt(cx,cy);if(unpolar(cx,cy).lat<MIN_LAT||isLand(cx,cy)||!wildlifeClearOfPorts(cx,cy)||type==='packed'||type==='fast'||type==='cracked')return false;}return true;}
  function safeWhaleWater(x,y,phase=0){const currentType=iceTypeAt(x,y);if(!isLand(x,y)&&wildlifeClearOfPorts(x,y)&&coastDistance(x,y,18)>10&&currentType!=='packed'&&currentType!=='fast'&&currentType!=='cracked')return{x,y};const pos=unpolar(x,y),edge=polar(packIceEdge(pos.lon)-1.35,pos.lon),edgeType=iceTypeAt(edge.x,edge.y);if(!isLand(edge.x,edge.y)&&wildlifeClearOfPorts(edge.x,edge.y)&&edgeType!=='packed'&&edgeType!=='fast'&&edgeType!=='cracked')return{x:edge.x,y:edge.y};for(let radius=12;radius<=1000;radius+=12){for(let i=0;i<24;i++){const a=phase+i*Math.PI/12,cx=x+Math.cos(a)*radius,cy=y+Math.sin(a)*radius,type=iceTypeAt(cx,cy);if(!isLand(cx,cy)&&wildlifeClearOfPorts(cx,cy)&&coastDistance(cx,cy,18)>10&&type!=='packed'&&type!=='fast'&&type!=='cracked')return{x:cx,y:cy};}}return nearestOpenWater(x,y,phase);}
  function chooseWhaleCourse(whale){if(whaleCourseClear(whale.x,whale.y,whale.angle))return whale.angle;for(let step=1;step<=15;step++){for(const sign of[1,-1]){const candidate=whale.angle+sign*step*Math.PI/12;if(whaleCourseClear(whale.x,whale.y,candidate,28))return candidate;}}return whale.angle+Math.PI*.5;}
  function updateFishSchools(dt){for(const school of fishSchools){if(!school.ready){const safe=nearestOpenWater(school.homeX,school.homeY,school.phase);school.x=safe.x;school.y=safe.y;school.homeX=safe.x;school.homeY=safe.y;school.ready=true;}const hx=school.homeX-school.x,hy=school.homeY-school.y,homeDistance=Math.hypot(hx,hy),wander=school.angle+Math.sin(state.seasonDay*.31+school.phase)*.035,desired=homeDistance>72?Math.atan2(hy,hx):wander,turn=((desired-school.angle+Math.PI*3)%(Math.PI*2))-Math.PI;school.angle+=Math.max(-.045,Math.min(.045,turn));const flow=currentAt(school.x,school.y,false),vx=Math.cos(school.angle)*school.speed+flow.vx*.035,vy=Math.sin(school.angle)*school.speed+flow.vy*.035,nx=school.x+vx*dt,ny=school.y+vy*dt;if(unpolar(nx,ny).lat<MIN_LAT||isLand(nx,ny)||!wildlifeClearOfPorts(nx,ny)){school.angle+=Math.PI*.72;}else{school.x=nx;school.y=ny;}}}
  function updateWildlife(dt){for(const whale of whales){const habitat=iceTypeAt(whale.x,whale.y);if(isLand(whale.x,whale.y)||!wildlifeClearOfPorts(whale.x,whale.y)||coastDistance(whale.x,whale.y,10)<2||habitat==='packed'||habitat==='fast'||habitat==='cracked'){const safe=safeWhaleWater(whale.x,whale.y,whale.phase);whale.x=safe.x;whale.y=safe.y;}const desired=chooseWhaleCourse(whale),turn=((desired-whale.angle+Math.PI*3)%(Math.PI*2))-Math.PI;whale.angle+=Math.max(-.055,Math.min(.055,turn))+Math.sin(state.seasonDay*.8+whale.phase)*.002;const flow=currentAt(whale.x,whale.y,false),swim=5.5,vx=Math.cos(whale.angle)*swim+flow.vx*.22,vy=Math.sin(whale.angle)*swim+flow.vy*.22,nx=whale.x+vx*dt,ny=whale.y+vy*dt,type=iceTypeAt(nx,ny),pos=unpolar(nx,ny);if(pos.lat<MIN_LAT||isLand(nx,ny)||!wildlifeClearOfPorts(nx,ny)||type==='packed'||type==='fast'||type==='cracked'){const safe=safeWhaleWater(whale.x,whale.y,whale.phase);whale.x=safe.x;whale.y=safe.y;whale.angle=chooseWhaleCourse(whale);}else{whale.x=nx;whale.y=ny;}}}
  const npcActive=npc=>!npc.seasonal||summerWildlifeVisible();
  function npcAllowedAt(npc,x,y){const pos=unpolar(x,y);if(pos.lat<MIN_LAT+.03||isBlocked(x,y))return false;const ice=iceTypeAt(x,y);return ice!=='packed'&&ice!=='fast'&&ice!=='cracked'&&(!npc.avoidMarginal||ice!=='marginal');}
  function safeNpcPosition(npc,x=npc.x,y=npc.y){if(npcAllowedAt(npc,x,y))return{x,y};for(let radius=8;radius<=180;radius+=8)for(let index=0;index<20;index++){const angle=npc.angle+index*Math.PI/10,cx=x+Math.cos(angle)*radius,cy=y+Math.sin(angle)*radius;if(npcAllowedAt(npc,cx,cy))return{x:cx,y:cy};}return null;}
  function npcCourseAllowed(npc,x,y){for(const fraction of[.25,.5,.75,1])if(!npcAllowedAt(npc,npc.x+(x-npc.x)*fraction,npc.y+(y-npc.y)*fraction))return false;return true;}
  function updateNpcVessels(dt){npcUpdateAccumulator+=dt;if(npcUpdateAccumulator<.045)return;const stepTime=Math.min(.12,npcUpdateAccumulator);npcUpdateAccumulator=0;for(const npc of npcVessels){if(!npcActive(npc))continue;if(!npc.ready){const safe=safeNpcPosition(npc);if(safe){npc.x=safe.x;npc.y=safe.y;}npc.ready=true;}const goal=npc.route[npc.routeIndex%npc.route.length],dx=goal.x-npc.x,dy=goal.y-npc.y,distance=Math.hypot(dx,dy);if(distance<16){npc.routeIndex=(npc.routeIndex+1)%npc.route.length;continue;}const desired=Math.atan2(dy,dx),turn=((desired-npc.angle+Math.PI*3)%(Math.PI*2))-Math.PI;npc.angle+=Math.max(-.028,Math.min(.028,turn));const distanceStep=Math.min(distance,npc.speed*KNOT_TO_WORLD_SPEED*stepTime*.24),nx=npc.x+Math.cos(npc.angle)*distanceStep,ny=npc.y+Math.sin(npc.angle)*distanceStep;if(npcCourseAllowed(npc,nx,ny)){npc.x=nx;npc.y=ny;}else{npc.routeIndex=(npc.routeIndex+1)%npc.route.length;npc.angle+=Math.PI*.45;const safe=safeNpcPosition(npc);if(safe){npc.x=safe.x;npc.y=safe.y;}}}}
  function drawNpcIcon(npc){ctx.strokeStyle='rgba(236,251,252,.95)';ctx.lineWidth=1.2;if(npc.kind==='canoe'){ctx.fillStyle='#7b432b';ctx.beginPath();ctx.moveTo(0,-10);ctx.quadraticCurveTo(7,1,0,11);ctx.quadraticCurveTo(-7,1,0,-10);ctx.fill();ctx.stroke();ctx.strokeStyle='#e7d39f';ctx.beginPath();ctx.moveTo(-8,-7);ctx.lineTo(8,8);ctx.stroke();return;}if(npc.kind==='sailing'){ctx.fillStyle='#f7f1da';ctx.beginPath();ctx.moveTo(0,-15);ctx.lineTo(0,7);ctx.lineTo(12,5);ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle='#745641';ctx.fillRect(-2,-10,3,22);return;}ctx.fillStyle=npc.kind==='research'?'#f5cf55':npc.kind==='cruise'?'#f5f1df':'#d8684f';ctx.beginPath();ctx.moveTo(0,-13);ctx.quadraticCurveTo(8,-4,7,11);ctx.quadraticCurveTo(0,15,-7,11);ctx.quadraticCurveTo(-8,-4,0,-13);ctx.fill();ctx.stroke();if(npc.kind==='cruise'){ctx.fillStyle='#eef7f5';ctx.fillRect(-6,-5,12,9);ctx.fillStyle='#24536b';for(const x of[-4,0,4])ctx.fillRect(x,-3,2,2);}else if(npc.kind==='research'){ctx.fillStyle='#edf7f3';ctx.fillRect(-5,-3,10,7);ctx.strokeStyle='#153e52';ctx.beginPath();ctx.moveTo(-7,4);ctx.lineTo(7,4);ctx.moveTo(0,-10);ctx.lineTo(0,-17);ctx.stroke();}else{ctx.fillStyle='#173f50';ctx.fillRect(-4,-2,8,5);}}
  function drawNpcVessels(){ctx.save();ctx.textAlign='center';ctx.textBaseline='bottom';for(const npc of npcVessels){if(!npcActive(npc)||!npc.ready)continue;const p=worldToScreen(npc.x,npc.y);if(p.x<-45||p.x>width+45||p.y<70||p.y>height+45)continue;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(npc.angle+Math.PI/2);drawNpcIcon(npc);ctx.restore();if(zoomLevel>=.75||Math.hypot(npc.x-state.x,npc.y-state.y)<90){ctx.font='800 8px system-ui';ctx.lineWidth=3;ctx.strokeStyle='rgba(4,28,42,.9)';ctx.strokeText(npc.name,p.x,p.y-18);ctx.fillStyle='#f4fdff';ctx.fillText(npc.name,p.x,p.y-18);}}ctx.restore();}
  function nearbyNpcVesselAt(clientX,clientY){let match=null,best=27;for(const npc of npcVessels){if(!npcActive(npc)||!npc.ready)continue;const p=worldToScreen(npc.x,npc.y),hit=Math.hypot(p.x-clientX,p.y-clientY);if(hit<best){best=hit;match={npc,p,distance:Math.hypot(npc.x-state.x,npc.y-state.y)};}}return match;}
  function openNpcVessel(encounter){if(!encounter?.npc)return false;const npc=encounter.npc;return!!research?.openNpcVessel?.({id:npc.id,name:npc.name,classId:npc.classId,type:npc.kind,typeLabel:npc.typeLabel,mission:npc.mission,description:`${npc.name} is working independently in Arctic waters.`,captainName:npc.captainName,captainRole:npc.captainRole,captainPortrait:npc.captainPortrait,image:npc.image,distanceKm:encounter.distance,canAssist:npc.kind==='research'});}
  function drawVessel(){const x=width/2,y=height/2;ctx.save();ctx.translate(x,y);ctx.rotate(state.angle);if(state.moving){ctx.fillStyle='rgba(235,251,255,.42)';ctx.beginPath();ctx.moveTo(-8,15);ctx.quadraticCurveTo(-25,45,-7,70);ctx.lineTo(0,28);ctx.lineTo(7,70);ctx.quadraticCurveTo(25,45,8,15);ctx.fill();}ctx.shadowColor='rgba(0,25,40,.4)';ctx.shadowBlur=12;ctx.shadowOffsetY=5;ctx.fillStyle='#f7f1dc';ctx.beginPath();ctx.moveTo(0,-24);ctx.quadraticCurveTo(13,-10,11,19);ctx.quadraticCurveTo(0,27,-11,19);ctx.quadraticCurveTo(-13,-10,0,-24);ctx.fill();ctx.shadowColor='transparent';ctx.fillStyle='#e85d4c';ctx.fillRect(-9,-5,18,10);ctx.fillStyle='#123c50';ctx.fillRect(-5,-13,10,8);ctx.fillStyle='#f6d365';ctx.fillRect(-1,-29,2,15);ctx.restore();ctx.strokeStyle='rgba(255,255,255,.42)';ctx.lineWidth=1;ctx.beginPath();ctx.arc(x,y,38,0,Math.PI*2);ctx.stroke();}
  function updateCompass(){const length=Math.hypot(state.x,state.y)||1,ux=-state.x/length,uy=-state.y/length,rotation=Math.atan2(uy,ux)+Math.PI/2;compassNeedle.style.transform=`translateY(4px) rotate(${rotation}rad)`;compassNorth.style.left=(27.5+ux*20)+'px';compassNorth.style.top=(27.5+uy*20)+'px';}

  function clearDisplacement(x,y,tx,ty){const dx=tx-x,dy=ty-y,dist=Math.hypot(dx,dy);for(let d=3;d<=dist;d+=3){const cx=x+dx*d/dist,cy=y+dy*d/dist;if(isBlocked(cx,cy)||iceTypeAt(cx,cy)==='fast')return false;}return true;}
  function pushOutOfAdvancingPack(dt){let best=null,bestScore=Infinity;const radius0=Math.hypot(state.x,state.y);for(let radius=8;radius<=180;radius+=8)for(let i=0;i<36;i++){const a=i*Math.PI/18,x=state.x+Math.cos(a)*radius,y=state.y+Math.sin(a)*radius,pos=unpolar(x,y),type=iceTypeAt(x,y);if(pos.lat<MIN_LAT||isBlocked(x,y)||type==='packed'||type==='fast'||!clearDisplacement(state.x,state.y,x,y))continue;const radialGain=Math.hypot(x,y)-radius0,score=radius-Math.max(0,radialGain)*.45;if(score<bestScore){best={x,y};bestScore=score;}}if(!best)return false;const dx=best.x-state.x,dy=best.y-state.y,dist=Math.hypot(dx,dy),step=Math.min(dist,95*dt/zoomLevel),nx=state.x+dx/dist*step,ny=state.y+dy/dist*step;if(isBlocked(nx,ny)||iceTypeAt(nx,ny)==='fast')return false;state.x=nx;state.y=ny;state.tx=state.x;state.ty=state.y;state.moving=false;state.commandActive=false;state.portDestination=null;return true;}
  function showToast(message,duration=1200){if(!message)return;clearTimeout(toastTimer);ui.toast.classList.remove('frozen');ui.toast.textContent=message;ui.toast.classList.add('show');toastTimer=setTimeout(()=>ui.toast.classList.remove('show'),duration);}
  function updateResourceWarning(vessel=vesselModifiers()){
    const previousFuel=resourceAlertState.fuel,previousFood=resourceAlertState.food;
    resourceAlertState.fuel=vessel.nuclearFuel?false:previousFuel?state.fuel<24:state.fuel<20;
    resourceAlertState.food=previousFood?state.food<24:state.food<20;
    if(state.started&&!previousFuel&&resourceAlertState.fuel)showToast('LOW FUEL · LESS THAN 20% REMAINING · RETURN TO PORT',3600);
    if(state.started&&!previousFood&&resourceAlertState.food)showToast('LOW FOOD · LESS THAN 20% REMAINING · RETURN TO PORT',3600);
    const warnings=[];if(resourceAlertState.fuel)warnings.push(`LOW FUEL ${Math.ceil(state.fuel)}%`);if(resourceAlertState.food)warnings.push(`LOW FOOD ${Math.ceil(state.food)}%`);
    if(ui.resourceWarning){ui.resourceWarning.textContent=warnings.length?`${warnings.join(' · ')} · RETURN TO PORT`:'';ui.resourceWarning.classList.toggle('show',warnings.length>0&&!state.gameOver);}
    document.querySelector('.fuel-status')?.classList.toggle('low',resourceAlertState.fuel);document.querySelector('.food-status')?.classList.toggle('low',resourceAlertState.food);
  }
  function freezeIn(){if(state.frozen)return;if(pushOutOfAdvancingPack(.025))return;clearTimeout(toastTimer);state.frozen=true;state.tx=state.x;state.ty=state.y;state.moving=false;state.commandActive=false;ui.speed.textContent='0.0 KN';ui.toast.textContent='FROZEN IN — SURROUNDED BY PACK ICE · TIME ×100';ui.toast.classList.add('show','frozen');}
  function releaseFromIce(){state.frozen=false;ui.toast.classList.remove('frozen');showToast('SPRING THAW — VESSEL FREE TO MOVE',2800);}
  function departWithCheck(proceed){const depart=()=>{if(currentPortCity){research?.leavePort?.();state.dockedPort=null;currentPortCity=null;}proceed();};const warned=!!currentPortCity&&!!research?.confirmDeparture?.({fuel:state.fuel,food:state.food},depart);if(!warned)depart();}
  function setWorldDestination(tx,ty){if(state.frozen){freezeIn();return;}const targetPos=unpolar(tx,ty);if(targetPos.lat<MIN_LAT){showToast('MAP BOUNDARY - TURN NORTH');return;}const targetOnLand=isLand(tx,ty),ice=iceTypeAt(tx,ty);if(!targetOnLand&&ice==='fast'){showToast('FAST ICE - IMPASSABLE');return;}departWithCheck(()=>{state.portDestination=null;state.tx=tx;state.ty=ty;state.moving=true;state.commandActive=true;state.targetOnLand=targetOnLand;state.ramming=!targetOnLand&&ice==='cracked';state.ramClock=0;ui.welcome.classList.add('hidden');if(!targetOnLand&&ice==='marginal')showToast('MARGINAL ICE — SPEED REDUCED');});}
  function setDestination(clientX,clientY){pendingResearchTargetId=null;setWorldDestination(state.x+(clientX-width/2)/scale,state.y+(clientY-height/2)/scale);}
  function navigateFromMiniMap(event){const rect=miniCanvas.getBoundingClientRect(),size=miniCanvas.clientWidth,c=size/2,dx=event.clientX-rect.left-c,dy=event.clientY-rect.top-c,radius=size*.45;if(Math.hypot(dx,dy)>radius)return;const geometry=miniMapGeometry();pendingResearchTargetId=null;setWorldDestination(geometry.centerX+dx/radius*geometry.worldRadius,geometry.centerY+dy/radius*geometry.worldRadius);}
  function startPortApproach(portItem){const approach=findPortApproach(portItem.city);if(!approach){showToast('PORT APPROACH BLOCKED BY LAND OR ICE');return;}if(Math.hypot(approach.x-state.x,approach.y-state.y)<=5){enterPort(portItem.city);return;}departWithCheck(()=>{pendingResearchTargetId=null;state.portDestination=portItem.city;state.tx=approach.x;state.ty=approach.y;state.moving=true;state.commandActive=true;state.targetOnLand=false;state.ramming=false;ui.welcome.classList.add('hidden');showToast(`PORT APPROACH — ${portItem.city.name}`,1800);});}
  function handleMapPointer(clientX,clientY){const portItem=nearbyCityAt(clientX,clientY);if(portItem){if(state.dockedPort===portItem.city.name&&currentPortCity){currentPortCity=portItem.city;research?.enterPort?.(portItem.city,{resume:true});}else startPortApproach(portItem);return;}const site=nearbyResearchTargetAt(clientX,clientY);if(site){research?.selectTarget?.(site.target.id);if(site.distance<=RESEARCH_INTERACTION_KM)research?.openTarget?.(site.target.id,{distanceKm:site.distance,atSite:true,target:site.target});else navigateToResearchTarget(site.target);return;}const vesselEncounter=nearbyNpcVesselAt(clientX,clientY);if(vesselEncounter&&openNpcVessel(vesselEncounter))return;const animal=wildlifeAtScreenPoint(clientX,clientY);if(animal&&research?.openWildlife){const pos=unpolar(animal.world.x,animal.world.y);observedWildlifeFallback.add(animal.individualId);research.openWildlife(animal.species,{individualId:animal.individualId,category:animal.category,lat:pos.lat,lon:pos.lon,dataValue:2});return;}setDestination(clientX,clientY);}
  function locationName(lat,lon){const river=riverAt(state.x,state.y,5);if(river)return river.name.toUpperCase();if(Math.hypot(state.x-home.x,state.y-home.y)<90)return'SVALBARD';if(lat>88)return'NORTH POLE';if(lon>-30&&lon<20&&lat>72)return'GREENLAND SEA';if(lon>=20&&lon<60&&lat>68)return'BARENTS SEA';if(lon>=60&&lon<140&&lat>70)return'KARA / LAPTEV SEA';if((lon>=140||lon<-160)&&lat>68)return'EAST SIBERIAN SEA';if(lon>=-160&&lon<-120&&lat>68)return'BEAUFORT SEA';return'ARCTIC OCEAN';}
  function courseBlockedAhead(x,y,angle,distance){for(let d=6;d<=distance;d+=6){const cx=x+Math.cos(angle)*d,cy=y+Math.sin(angle)*d,pos=unpolar(cx,cy),ice=iceTypeAt(cx,cy);if(pos.lat<MIN_LAT||isBlocked(cx,cy)||ice==='fast'||ice==='packed')return true;}return false;}
  function coastBlockedAhead(x,y,angle,distance){for(let d=6;d<=distance;d+=6){const cx=x+Math.cos(angle)*d,cy=y+Math.sin(angle)*d,pos=unpolar(cx,cy),ice=iceTypeAt(cx,cy);if(pos.lat<MIN_LAT||isBlocked(cx,cy)||ice==='fast')return true;}return false;}
  function fracturedIceAhead(x,y,angle,distance=60){for(let d=4;d<=distance;d+=4){const cx=x+Math.cos(angle)*d,cy=y+Math.sin(angle)*d;if(isCrackedIceAt(cx,cy))return true;const ice=iceTypeAt(cx,cy);if(isBlocked(cx,cy)||ice==='fast'||ice==='packed')return false;}return false;}
  function shorelineSlide(x,y,vx,vy,motionDt,targetX,targetY){const speed=Math.hypot(vx,vy);if(speed<.01)return null;const base=Math.atan2(vy,vx),tdx=targetX-x,tdy=targetY-y,tlen=Math.hypot(tdx,tdy)||1,lookAhead=Math.max(30,speed*motionDt*10);let best=null,bestScore=-Infinity;for(const clearance of[lookAhead,18,9,0]){for(const fraction of[1,.78,.56,.36]){for(let step=1;step<=35;step++){for(const sign of[-1,1]){const offset=sign*step*Math.PI/36,a=base+offset;if(clearance&&courseBlockedAhead(x,y,a,clearance*fraction))continue;const cx=x+Math.cos(a)*speed*motionDt*fraction,cy=y+Math.sin(a)*speed*motionDt*fraction,pos=unpolar(cx,cy),ice=iceTypeAt(cx,cy);if(pos.lat<MIN_LAT||isBlocked(cx,cy)||ice==='fast'||ice==='packed')continue;const probeX=x+Math.cos(a)*Math.max(5,speed*motionDt*2),probeY=y+Math.sin(a)*Math.max(5,speed*motionDt*2);if(isBlocked(probeX,probeY))continue;const progress=((cx-x)*tdx+(cy-y)*tdy)/tlen,score=progress-Math.abs(offset)*.18+fraction*.3+clearance*.025;if(score>bestScore){bestScore=score;best={x:cx,y:cy,vx:(cx-x)/motionDt,vy:(cy-y)/motionDt};}}}}if(best)return best;}return null;}
  function ramCycleSpeed(dt,normalCruise){
    // 3.2 seconds: snap astern briefly, pause, accelerate rapidly to full
    // power, then lose speed progressively while crushing the fractured pack.
    // The backing stroke is one-fifth its former duration and distance.
    state.ramClock=(state.ramClock+dt)%3.2;const p=state.ramClock;
    if(p<.2)return-normalCruise*(.4*Math.PI/2)*Math.sin(Math.PI*p/.2);
    if(p<.4)return 0;
    if(p<.55)return normalCruise*(p-.4)/.15;
    if(p<2)return normalCruise*(1-(p-.55)/1.45);
    return 0;
  }
  const packedBoundaryValue=(x,y)=>{const p=unpolar(x,y);return p.lat-packIceEdge(p.lon);};
  function slideAlongPackedEdge(x,y,vx,vy){const e=2,gx=(packedBoundaryValue(x+e,y)-packedBoundaryValue(x-e,y))/(2*e),gy=(packedBoundaryValue(x,y+e)-packedBoundaryValue(x,y-e))/(2*e),g2=gx*gx+gy*gy;if(g2<1e-8)return{vx:0,vy:0};const inward=(vx*gx+vy*gy)/g2;if(inward>0){vx-=gx*inward;vy-=gy*inward;}const gl=Math.sqrt(g2);vx-=gx/gl*.12;vy-=gy/gl*.12;return{vx,vy};}
  function vesselModifiers(){const item=research?.getVesselModifiers?.()||{};return{cruiseKnots:item.cruiseKnots??item.speedKnots??8,maxKnots:item.maxKnots??item.cruiseKnots??item.speedKnots??8,fuelEnduranceDays:item.fuelEnduranceDays??5,foodEnduranceDays:item.foodEnduranceDays??5,nuclearFuel:!!item.nuclearFuel,crackedIceFactor:item.crackedIceFactor??.1,minZoom:item.minZoom??.3,visibilityBonusKm:item.visibilityBonusKm??0,name:item.name??'RV AURORA',image:item.image??'assets/vessels/base-vessel.png'};}
  function updateVesselButton(item=vesselModifiers()){if(ui.vesselButtonImage&&ui.vesselButtonImage.getAttribute('src')!==item.image)ui.vesselButtonImage.setAttribute('src',item.image);ui.vesselButton?.setAttribute('aria-label',`Open ${item.name} information`);}
  function advanceGameDays(days){if(!Number.isFinite(days)||days<=0)return;state.seasonDay+=days;state.fogClearDays=Math.max(0,state.fogClearDays-days);while(state.seasonDay>=365){state.seasonDay-=365;state.year++;}const vessel=vesselModifiers();state.food=Math.max(0,state.food-days*100/vessel.foodEnduranceDays);research?.tickDays?.(days,{position:unpolar(state.x,state.y),source:'station'});}
  function updateCalendar(dt){const effectiveTimeScale=1/zoomLevel,stationBusy=!!research?.isBusy?.(),elapsedDays=state.started&&!stationBusy?dt*.2*(state.frozen?100:effectiveTimeScale):0;state.seasonDay+=elapsedDays;state.fogClearDays=Math.max(0,state.fogClearDays-elapsedDays);if(state.seasonDay>=365){state.seasonDay-=365;state.year++;}const date=new Date(Date.UTC(state.year,8,1+Math.floor(state.seasonDay))),months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];ui.calendarDate.textContent=String(date.getUTCDate()).padStart(2,'0')+' '+months[date.getUTCMonth()]+' '+date.getUTCFullYear();ui.seasonProgress.style.left=(state.seasonDay/365*100)+'%';const growth=iceGrowth();ui.seasonNote.textContent=state.frozen?'FROZEN IN · TIME ×100':growth<.08?'SEA ICE MINIMUM':growth>.92?'SEA ICE MAXIMUM':state.seasonDay<182.5?'ICE ADVANCING':'ICE RETREATING';ui.timeSpeed.textContent=stationBusy?'PAUSED':state.frozen?'×100':'×'+Number(effectiveTimeScale.toFixed(1));return elapsedDays;}
  function update(dt){if(state.gameOver)return;const elapsedDays=updateCalendar(dt),vessel=vesselModifiers(),weather=currentWeather();brandShip.textContent=`${vessel.name.toUpperCase()} · RESEARCH EDITION`;updateVesselButton(vessel);state.food=Math.max(0,state.food-elapsedDays*100/vessel.foodEnduranceDays);research?.tickDays?.(elapsedDays,{position:unpolar(state.x,state.y),source:'sailing'});researchOpportunityClock+=elapsedDays;const opportunityEnv=researchEnvironment(weather),opportunityInterval=opportunityEnv.fjord?.7:opportunityEnv.iceEdge?.9:opportunityEnv.coastal?1.05:1.8;if(researchOpportunityClock>=opportunityInterval){researchOpportunityClock=0;research?.maybeSpawnOpportunity?.(opportunityEnv);}if(state.food<=0){ui.foodValue.textContent='0%';ui.foodLevel.style.width='0%';endGame('OUT OF FOOD','The expedition has exhausted its provisions. Return to port before supplies run out.');return;}let currentIce=iceTypeAt(state.x,state.y);if(!state.frozen&&currentIce==='packed')freezeIn();else if(state.frozen&&currentIce!=='packed'){releaseFromIce();currentIce=iceTypeAt(state.x,state.y);}const iceSpeed=currentIce==='marginal'?1/3:1;ui.iceCondition.textContent=state.frozen?'FROZEN IN':state.ramming?'RAMMING FRACTURED PACK':currentIce==='fast'?'FAST ICE':currentIce==='packed'?'PACKED ICE':currentIce==='cracked'?'FRACTURED PACK':currentIce==='marginal'?'MARGINAL ICE':'OPEN WATER';ui.fuelValue.textContent=vessel.nuclearFuel?'∞':Math.ceil(state.fuel)+'%';ui.fuelLevel.style.width=(vessel.nuclearFuel?100:state.fuel)+'%';ui.fuelLevel.style.background=state.fuel<20&&!vessel.nuclearFuel?'#f97367':'#f6d365';ui.foodValue.textContent=Math.ceil(state.food)+'%';ui.foodLevel.style.width=state.food+'%';ui.foodLevel.style.background=state.food<20?'#f97367':'#73d6a1';const dx=state.tx-state.x,dy=state.ty-state.y,dist=Math.hypot(dx,dy),flow=state.dockedPort&&!state.commandActive?{vx:0,vy:0}:currentAt(state.x,state.y);if(state.ramming&&state.ramClock>=2&&!isCrackedIceAt(state.x,state.y)&&dist>0&&!fracturedIceAhead(state.x,state.y,Math.atan2(dy,dx)))state.ramming=false;if(currentIce==='fast'){state.moving=false;state.commandActive=false;state.ramming=false;state.tx=state.x;state.ty=state.y;ui.speed.textContent='0.0 KN';}else if(state.frozen){state.moving=false;ui.speed.textContent='0.0 KN';}else if(!vessel.nuclearFuel&&state.fuel<=0){ui.fuelValue.textContent='0%';ui.fuelLevel.style.width='0%';endGame('OUT OF FUEL','The vessel is stranded and the expedition cannot continue. Plan a shorter route between ports.');return;}else{
      const arrivalRadius=Math.max(2,3/zoomLevel);
      const courseRadial=dist>0?(dx*state.x+dy*state.y)/dist:0,propulsionFactor=currentIce==='cracked'?(courseRadial<0?.1:1/3):iceSpeed;
      const normalCruise=Math.max(vessel.cruiseKnots*KNOT_TO_WORLD_SPEED,Math.min(vessel.maxKnots*KNOT_TO_WORLD_SPEED,dist*1.1+30));
      let commanded=state.commandActive&&dist>arrivalRadius,cruise=commanded?normalCruise*propulsionFactor:0;
      if(commanded&&currentIce==='cracked'&&!state.ramming){state.ramming=true;state.ramClock=0;}
      if(commanded&&!vessel.nuclearFuel)state.fuel=Math.max(0,state.fuel-elapsedDays*(200/vessel.fuelEnduranceDays)*(state.ramming?3.5:1));
      if(commanded&&state.ramming)cruise=ramCycleSpeed(dt,normalCruise*(vessel.crackedIceFactor/.1));
      if(commanded&&!state.ramming){const currentTowardTarget=(flow.vx*dx+flow.vy*dy)/dist;if(cruise+currentTowardTarget<=.5){commanded=false;cruise=0;state.commandActive=false;state.moving=false;state.tx=state.x;state.ty=state.y;state.portDestination=null;}}
      // Simple set-and-drift model: engine velocity through the water plus the
      // current vector gives the vessel's velocity over the ground.
      let throughX=commanded?dx/dist*cruise:0,throughY=commanded?dy/dist*cruise:0;const through=Math.abs(cruise);
      if(commanded&&!state.ramming&&cruise>0){const steerX=throughX-flow.vx,steerY=throughY-flow.vy,steerLength=Math.hypot(steerX,steerY)||1;throughX=steerX/steerLength*cruise;throughY=steerY/steerLength*cruise;}
      const motionDt=dt/zoomLevel;let groundX=throughX+flow.vx,groundY=throughY+flow.vy,nx=state.x+groundX*motionDt,ny=state.y+groundY*motionDt,nextPos=unpolar(nx,ny),nextIce=iceTypeAt(nx,ny),groundStep=Math.hypot(groundX,groundY)*motionDt;
      if(!commanded&&nextIce==='packed'){const edgeMotion=slideAlongPackedEdge(state.x,state.y,groundX,groundY);groundX=edgeMotion.vx;groundY=edgeMotion.vy;nx=state.x+groundX*motionDt;ny=state.y+groundY*motionDt;nextPos=unpolar(nx,ny);nextIce=iceTypeAt(nx,ny);if(nextIce==='packed'){groundX=0;groundY=0;nx=state.x;ny=state.y;nextPos=unpolar(nx,ny);nextIce=iceTypeAt(nx,ny);}groundStep=Math.hypot(groundX,groundY)*motionDt;}
      const obstructionDistance=commanded?Math.min(38,dist):30,directAngle=Math.atan2(groundY,groundX);
      if(!state.targetOnLand&&(isBlocked(nx,ny)||(commanded&&coastBlockedAhead(state.x,state.y,directAngle,obstructionDistance)))&&nextPos.lat>=MIN_LAT&&nextIce!=='fast'){const slip=shorelineSlide(state.x,state.y,groundX,groundY,motionDt,state.tx,state.ty);if(slip){nx=slip.x;ny=slip.y;groundX=slip.vx;groundY=slip.vy;nextPos=unpolar(nx,ny);nextIce=iceTypeAt(nx,ny);groundStep=Math.hypot(nx-state.x,ny-state.y);}}
      if(nextPos.lat<MIN_LAT||nextIce==='fast'||isBlocked(nx,ny)){if(commanded){state.tx=state.x;state.ty=state.y;state.portDestination=null;}state.moving=false;state.commandActive=false;state.ramming=false;state.targetOnLand=false;ui.speed.textContent='0.0 KN';}
      else if(nextIce==='packed'){state.moving=false;state.commandActive=false;state.ramming=false;state.tx=state.x;state.ty=state.y;ui.speed.textContent='0.0 KN';}
      else{state.x=nx;state.y=ny;if(commanded){if(state.ramming&&cruise>0)addBrokenIce(state.x,state.y);state.travelled+=groundStep;const headingX=state.ramming?dx/dist:groundX,headingY=state.ramming?dy/dist:groundY,target=Math.atan2(headingY,headingX)+Math.PI/2;let da=((target-state.angle+Math.PI*3)%(Math.PI*2))-Math.PI;state.angle+=da*Math.min(1,dt*5);state.moving=through>.02;ui.speed.textContent=through<.02?'0.0 KN':(through/KNOT_TO_WORLD_SPEED).toFixed(1)+(cruise<0?' KN ASTERN':state.ramming?' KN RAM':' KN');}else{const driftKnots=Math.hypot(groundX,groundY)/KNOT_TO_WORLD_SPEED;state.moving=false;state.commandActive=false;state.ramming=false;ui.speed.textContent=driftKnots<.05?'0.0 KN':driftKnots.toFixed(1)+' KN DRIFT';if(state.portDestination)enterPort(state.portDestination);}}
    }const pos=unpolar(state.x,state.y),ew=pos.lon<0?'W':'E';ui.position.textContent=`${pos.lat.toFixed(2)}\u00B0N ${Math.abs(pos.lon).toFixed(2)}\u00B0${ew}`;ui.miniLocation.textContent=locationName(pos.lat,pos.lon);ui.progress.style.width=Math.min(100,8+state.travelled/18)+'%';}
  function updateIceReadout(){if(state.frozen)return;if(state.ramming){ui.iceCondition.textContent='RAMMING FRACTURED PACK';return;}const type=iceTypeAt(state.x,state.y);if(type==='cracked')ui.iceCondition.textContent='FRACTURED PACK';else if(type==='packed')ui.iceCondition.textContent=iceThicknessAt(state.x,state.y)+' M PACK ICE';}
  function setZoom(change,silent=false){
    const previousZoom=zoomLevel,minZoom=vesselModifiers().minZoom,steps=[.3,.4,.7,1.1,1.45,1.8,2.3,2.8].filter(value=>value>=minZoom-.001),direction=change>0?1:change<0?-1:0;let index=steps.reduce((best,value,i)=>Math.abs(value-zoomLevel)<Math.abs(steps[best]-zoomLevel)?i:best,0);if(direction)index=Math.max(0,Math.min(steps.length-1,index+direction));else index=Math.max(0,steps.findIndex(value=>value>=minZoom-.001));zoomLevel=steps[index]??minZoom;scale=baseScale*zoomLevel;if(zoomLevel!==previousZoom)iceFloes.length=0;ui.zoomLevel.textContent=Math.round(zoomLevel*100)+'%';ui.scaleDistance.textContent=Math.max(2,Math.round(15/zoomLevel))+' km';ui.zoomIn.disabled=index>=steps.length-1;ui.zoomOut.disabled=index<=0;if(!silent)showToast(zoomLevel>1?'CHART DETAIL '+Math.round(zoomLevel*100)+'%':'CHART OVERVIEW '+Math.round(zoomLevel*100)+'%');
  }
  function frame(now){const dt=Math.min(.04,(now-last)/1000);last=now;sound.update();const paused=state.gameOver||menuOpen||!!research?.isBusy?.();let weather;if(!paused){updateBrokenIceDrift(dt/zoomLevel);serviceNearbyPort();update(dt);weather=updateWeatherAnnouncement();updateIceReadout();updateCompass();if(now-lastResearchNavigation>250){lastResearchNavigation=now;updateResearchNavigation();}}else{updateCalendar(0);weather=currentWeather();ui.weatherValue.textContent=weather.type==='clear'?'CLEAR':`${weather.label} ${weather.rating}/10 · ${weather.visibilityKm} KM`;updateIceReadout();updateCompass();}const margin=60/scale,minX=state.x-width/scale/2-margin,maxX=state.x+width/scale/2+margin,minY=state.y-height/scale/2-margin,maxY=state.y+height/scale/2+margin;if(!paused){updateFloes(dt/zoomLevel,minX,maxX,minY,maxY);updateWakeFloes(dt/zoomLevel);updateWildlifeEncounters(dt);updateFishSchools(dt/zoomLevel);updateWildlife(dt/zoomLevel);updateNpcVessels(dt/zoomLevel);}updateResourceWarning();drawMap();drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);drawWildlifeLabels();drawResearchGuidance();drawMiniMap();drawVessel();requestAnimationFrame(frame);}
  research?.initialize?.({
    wildlifeCatalog:window.ARCTIC_WILDLIFE_CATALOG||{},
    isResearchSiteSuitable,
    findResearchSite,
    getResources:()=>({fuel:state.fuel,food:state.food}),
    setResources:resources=>{if(Number.isFinite(resources?.fuel))state.fuel=clampResource(resources.fuel);if(Number.isFinite(resources?.food))state.food=clampResource(resources.food);ui.fuelLevel.style.width=state.fuel+'%';ui.foodLevel.style.width=state.food+'%';updateResourceWarning();if(currentPortCity)saveCheckpoint(currentPortCity);},
    estimateMissionResources,
    onNavigate:navigateToResearchTarget,
    onResearchStart:()=>{state.tx=state.x;state.ty=state.y;state.commandActive=false;state.moving=false;state.ramming=false;state.portDestination=null;},
    onAdvanceTime:advanceGameDays,
    onVesselChanged:item=>{zoomLevel=(item||vesselModifiers()).minZoom;setZoom(0,true);updateVesselButton(item||vesselModifiers());},
    onCharacterReady:beginExpedition,
    onToast:showToast,
    onSound:type=>sound.play(type),
    onStateChange:()=>{if(currentPortCity)saveCheckpoint(currentPortCity);semanticAnalytics();if(!autosaveSuspended)scheduleAutosave();}
  });
  if(research?.maybeSpawnOpportunity){const spawnOpportunity=research.maybeSpawnOpportunity.bind(research);research.maybeSpawnOpportunity=payload=>spawnOpportunity({...researchEnvironment(payload?.weather),...payload});}
  setZoom(0,true);
  function clampResource(value){return Math.max(0,Math.min(100,value));}
  function beginExpedition(){if(state.started)return;startFlowPending=false;state.started=true;menuOpen=false;ui.welcome.classList.add('hidden');if(currentPortCity)enterPort(currentPortCity);analytics.track('game_started');scheduleAutosave(800);}
  function requestExpeditionStart(){menuOpen=false;ui.welcome.classList.add('hidden');if(research?.openCharacterSetup){startFlowPending=true;const opened=research.openCharacterSetup();if(opened)return;}beginExpedition();}
  canvas.addEventListener('pointerdown',e=>{sound.unlock();analytics.track('map_interaction',{map_area:'main',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});handleMapPointer(e.clientX,e.clientY);});
  miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});navigateFromMiniMap(e);});
  canvas.addEventListener('pointermove',e=>{canvas.style.cursor=wildlifeAtScreenPoint(e.clientX,e.clientY)||nearbyNpcVesselAt(e.clientX,e.clientY)||nearbyResearchTargetAt(e.clientX,e.clientY)||nearbyCityAt(e.clientX,e.clientY)?'pointer':'crosshair';});
  document.getElementById('start-button').addEventListener('click',()=>{sound.unlock();startNewGame();});
  document.getElementById('help-start-button').addEventListener('click',()=>{sound.unlock();state.started?resumeGame():startNewGame();});
  document.getElementById('continue-button').addEventListener('click',()=>{sound.unlock();const save=readSave('auto');if(save)restoreGameSave(save,'auto');});
  document.getElementById('load-button').addEventListener('click',()=>{showTitlePane('title-load');refreshMenu();analytics.track('load_menu_opened');});
  document.getElementById('save-button').addEventListener('click',()=>{showTitlePane('title-save');refreshMenu();analytics.track('save_menu_opened');});
  document.getElementById('how-button').addEventListener('click',()=>{showTitlePane('title-help');analytics.track('how_to_play_opened');});
  document.getElementById('resume-button').addEventListener('click',resumeGame);
  document.getElementById('game-menu-button').addEventListener('click',()=>{sound.unlock();openGameMenu();});
  ui.welcome.addEventListener('click',event=>{
    if(event.target.closest('[data-title-back]')){showTitlePane('title-main');refreshMenu();return;}
    const load=event.target.closest('[data-load-slot]');if(load){const slot=load.dataset.loadSlot,save=readSave(slot);if(save)restoreGameSave(save,slot);return;}
    const save=event.target.closest('[data-save-slot]');if(save){const slot=save.dataset.saveSlot;if(saveGame(slot,'manual')){showToast(`GAME SAVED — SLOT ${slot.slice(-1)}`,1800);showTitlePane('title-main');refreshMenu();}return;}
  });
  document.addEventListener('click',event=>{
    const action=event.target.closest?.('[data-arx-action]');if(action){const name=action.dataset.arxAction||'',id=action.dataset.id||'',rs=research?.getState?.()||{};analytics.track('research_ui_action',{ui_action:name,item_id:id});if(name==='complete-target'){const target=(rs.targets||[]).find(item=>item.id===id)||{};autosaveSuspended=true;analytics.track('mission_started',{mission_id:id,mission_title:target.shortTitle||target.title||'',mission_kind:target.kind||'',reward:target.reward||0});}if(name==='acknowledge-research'){autosaveSuspended=false;setTimeout(()=>saveGame('auto','mission_complete'),50);}if(name==='accept'){const offer=(rs.offers||[]).find(item=>item.id===id)||{};analytics.track('grant_accept_clicked',{grant_id:id,grant_title:offer.shortTitle||offer.title||'',reward:offer.reward||0});}if(name==='drop-grant')analytics.track('grant_dropped',{grant_id:id});if(name==='hire'){const person=(rs.candidates||[]).find(item=>item.id===id)||{};analytics.track('scientist_hire_clicked',{scientist_id:id,career:person.career||'',specialty:person.specialty||''});}if(name==='release')analytics.track('scientist_release_clicked',{scientist_id:id});if(name==='equipment')analytics.track('equipment_purchase_clicked',{equipment_id:id});if(name==='sell-equipment')analytics.track('equipment_sell_clicked',{equipment_id:id});if(name==='vessel')analytics.track('vessel_purchase_clicked',{vessel_id_clicked:id});if(['fuel','food','supplies','resupply-all'].includes(name))analytics.track('resupply_clicked',{resource_type:name});if(name==='publish')analytics.track('publication_submitted',{science_data:rs.data||0,publish_attempt:(rs.publishAttempts||0)+1});}
    const tab=event.target.closest?.('[data-arx-tab]');if(tab)analytics.track('port_tab_viewed',{port_tab:tab.dataset.arxTab||''});
  },true);
  ui.zoomIn.addEventListener('click',()=>{analytics.track('zoom_changed',{zoom_direction:'in'});setZoom(.1);});
  ui.zoomOut.addEventListener('click',()=>{analytics.track('zoom_changed',{zoom_direction:'out'});setZoom(-.1);});
  document.getElementById('restart-button').addEventListener('click',()=>{analytics.track('checkpoint_restore');restoreCheckpoint();});
  ui.vesselButton.addEventListener('click',()=>research?.openVessel?.());
  addEventListener('keydown',e=>{if(e.key==='Escape'&&state.started&&!menuOpen){openGameMenu();return;}const d=180/scale;if(e.key==='ArrowUp')setDestination(width/2,height/2-d);if(e.key==='ArrowDown')setDestination(width/2,height/2+d);if(e.key==='ArrowLeft')setDestination(width/2-d,height/2);if(e.key==='ArrowRight')setDestination(width/2+d,height/2);});
  document.addEventListener('visibilitychange',()=>{updateActiveClock();if(document.visibilityState==='hidden'){if(!autosaveSuspended)saveGame('auto','visibility');analytics.track('session_pause',{active_seconds:activeSeconds()});}});
  addEventListener('pagehide',()=>{updateActiveClock();if(!autosaveSuspended)saveGame('auto','pagehide');analytics.track('session_summary',{active_seconds:activeSeconds()});});
  setInterval(()=>{if(state.started&&!menuOpen&&!autosaveSuspended)saveGame('auto','interval');},30000);
  addEventListener('resize',resize);resize();lastResearchAnalytics=research?.getState?.()||null;refreshMenu();analytics.track('game_open',{analytics_enabled:analytics.isEnabled()?1:0});
  try{if(sessionStorage.getItem(AUTO_NEW_KEY)==='1'){sessionStorage.removeItem(AUTO_NEW_KEY);setTimeout(startNewGame,0);}}catch(error){}
  requestAnimationFrame(frame);
})();
