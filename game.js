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

  const loadSprite=src=>{const img=new Image();img.decoding='async';img.src=src;return img;};
  const ICEBREAKER_MAP_SVG='data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 220"><defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f66a52"/><stop offset="1" stop-color="#9b2528"/></linearGradient></defs><path d="M60 5C79 18 92 48 96 92l8 87-18 28H34l-18-28 8-87C28 48 41 18 60 5Z" fill="url(#h)" stroke="#701a21" stroke-width="5"/><path d="M38 49h44l8 70H30Z" fill="#f4f8f7" stroke="#6f9eab" stroke-width="4"/><path d="M42 60h36v30H42Z" fill="#dcecee"/><g fill="#2c718d"><rect x="45" y="64" width="8" height="10" rx="2"/><rect x="56" y="64" width="8" height="10" rx="2"/><rect x="67" y="64" width="8" height="10" rx="2"/></g><path d="M60 48V25M60 30h23" stroke="#e7f3f5" stroke-width="5" stroke-linecap="round"/><circle cx="60" cy="154" r="22" fill="#dfe9e9" stroke="#56b49d" stroke-width="5"/><path d="M44 154h32M60 138v32" stroke="#56b49d" stroke-width="4"/><rect x="38" y="104" width="18" height="15" rx="3" fill="#d79d43"/><rect x="64" y="104" width="18" height="15" rx="3" fill="#5f9ab1"/><path d="M28 126h64" stroke="#f6d365" stroke-width="4" stroke-linecap="round"/></svg>`);
  const NUCLEAR_MAP_SVG='data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 132 236"><defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ef5544"/><stop offset="1" stop-color="#861d26"/></linearGradient></defs><path d="M66 4C88 18 103 50 108 98l9 94-20 32H35l-20-32 9-94C29 50 44 18 66 4Z" fill="url(#h)" stroke="#651520" stroke-width="5"/><path d="M40 43h52l10 82H30Z" fill="#f6faf9" stroke="#6f9eab" stroke-width="4"/><path d="M44 54h44v35H44Z" fill="#dcecee"/><g fill="#286d89"><rect x="47" y="59" width="8" height="11" rx="2"/><rect x="58" y="59" width="8" height="11" rx="2"/><rect x="69" y="59" width="8" height="11" rx="2"/><rect x="80" y="59" width="8" height="11" rx="2"/></g><path d="M66 43V18M66 24h30M85 24V10" stroke="#e8f4f5" stroke-width="5" stroke-linecap="round"/><circle cx="50" cy="165" r="20" fill="#dfe9e9" stroke="#56b49d" stroke-width="5"/><circle cx="84" cy="165" r="20" fill="#dfe9e9" stroke="#56b49d" stroke-width="5"/><path d="M36 165h28M50 151v28M70 165h28M84 151v28" stroke="#56b49d" stroke-width="3.5"/><rect x="41" y="107" width="19" height="16" rx="3" fill="#d79d43"/><rect x="65" y="107" width="19" height="16" rx="3" fill="#5f9ab1"/><path d="M28 133h76" stroke="#f6d365" stroke-width="4" stroke-linecap="round"/></svg>`);
  const wholeSprite=src=>({image:loadSprite(src),sx:null,sy:null,sw:null,sh:null});
  const SPRITE_ATLAS=loadSprite(window.AR_MAP_SPRITE_ATLAS_DATA||'assets/map-sprites-atlas.svg');
  const atlasSprite=(sx,sy,sw,sh)=>({image:SPRITE_ATLAS,sx,sy,sw,sh});
  const SPRITES={
    vessels:{
      fishing:atlasSprite(6,6,33,64),
      trawler:atlasSprite(6,6,33,64),
      coastal:atlasSprite(45,6,33,64),
      global:atlasSprite(84,6,37,64),
      icebreaker:wholeSprite(ICEBREAKER_MAP_SVG),
      nuclear:wholeSprite(NUCLEAR_MAP_SVG)
    },
    wildlife:{
      whale:atlasSprite(6,76,64,64),
      seal:atlasSprite(76,76,40,64),
      walrus:atlasSprite(122,76,64,63),
      polarBear:atlasSprite(6,146,48,64),
      birds:atlasSprite(60,146,64,39),
      narwhal:atlasSprite(130,146,64,50)
    }
  };
  const spriteReady=sprite=>!!(sprite?.image&&sprite.image.complete&&sprite.image.naturalWidth>0);
  const loadTextureImage=src=>{const img=new Image();img.decoding='async';img.src=src;return img;};
  const ICE_TEXTURE_DATA=window.AR_ICE_TEXTURE_DATA||{};
  const ICE_TEXTURE_IMAGES={
    marginal:loadTextureImage(ICE_TEXTURE_DATA.marginal||'arctic_ice_floes_on_deep_blue_water.png'),
    pack:loadTextureImage(ICE_TEXTURE_DATA.pack||'fractured_arctic_sea_ice_floes.png'),
    solid:loadTextureImage(ICE_TEXTURE_DATA.solid||'frozen_sea_ice_mosaic.png'),
    channel:loadTextureImage(ICE_TEXTURE_DATA.channel||'arctic_ice_floes_and_dark_waterway.png')
  };
  const icePatternCache=new Map();
  function textureImageReady(img){return !!(img&&img.complete&&img.naturalWidth>0);}
  function getIceTexturePattern(key,context=ctx){
    const img=ICE_TEXTURE_IMAGES[key];
    if(!textureImageReady(img))return null;
    const cacheKey=`${key}:${context===light?'light':'main'}`;
    if(icePatternCache.has(cacheKey))return icePatternCache.get(cacheKey);
    const tile=document.createElement('canvas');tile.width=256;tile.height=256;
    const t=tile.getContext('2d');
    t.clearRect(0,0,256,256);
    if(key==='marginal'){t.globalAlpha=.92;t.drawImage(img,0,0,256,256);}
    else if(key==='pack'){t.globalAlpha=.96;t.drawImage(img,0,0,256,256);t.fillStyle='rgba(222,241,245,.14)';t.fillRect(0,0,256,256);}
    else if(key==='solid'){t.globalAlpha=.98;t.drawImage(img,0,0,256,256);t.fillStyle='rgba(240,247,250,.10)';t.fillRect(0,0,256,256);}
    else if(key==='channel'){t.globalAlpha=.94;t.drawImage(img,0,0,256,256);}
    const pattern=context.createPattern(tile,'repeat');
    icePatternCache.set(cacheKey,pattern);
    return pattern;
  }
  function applyPatternTransform(pattern,dx=0,dy=0,scaleFactor=1,rotation=0){
    if(!pattern||typeof DOMMatrix==='undefined'||!pattern.setTransform)return pattern;
    const m=new DOMMatrix();
    m.translateSelf(dx,dy);
    if(rotation)m.rotateSelf(rotation*180/Math.PI);
    m.scaleSelf(scaleFactor,scaleFactor);
    pattern.setTransform(m);
    return pattern;
  }
  function withPatternFill(context,pattern,alpha,draw){
    if(!pattern)return false;
    context.save();
    context.globalAlpha=alpha;
    context.fillStyle=pattern;
    draw();
    context.fill();
    context.restore();
    return true;
  }

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
  terrainTexture.onerror=()=>{terrainTextureReady=false;if(!terrainTextureFallbackTried){terrainTextureFallbackTried=true;terrainTexture.src=TERRAIN_FALLBACK_URL;()}};
  terrainTexture.src=TERRAIN_PRIMARY_URL;

  // WGS 84 / IBCAO Polar Stereographic (EPSG:3996), expressed in km in the
  // game world. Keeping the game in the same projection as IBCAO removes the
  // small radial mismatch that was visible when the raster was laid over the
  // older approximate Arctic geometry. Game +y is opposite EPSG northing so
  // longitude orientation remains the same as the original chart code.
  const PS_A=6378137,PS_F=1/298.257223563,PS_E=Math.sqrt(PS_F*(2-PS_F));
  const psT=phi=>Math.tan(Math.PI/4-phi/2)/Math.pow((1-PS_E*Math.sin(phi))/(1+PS_E*Math.sin(phi)),PS_E/2);
  const PS_MC=Math.cos(PS_LAT_TS)/Math.sqrt(1-PS_E*PS_E*Math.sin(PS_LAT_TS)**2),PS_TC=psT(PS_LAT_TS);
  const polar=(lat,lon)=>{if(lat>=89.999999)return{x:0,y:0,lat,lon};const phi=lat*Math.PI/180,a=lon*Math.PI/180,r=PS_A*PS_MC*psT(phi)/PS_TC/1000;return{x:r*Math.sin(a),y:r*Math.cos(a),lat,lon};};
  const unpolar=(x,y)=>{const rho=Math.hypot(x,y)*1000;if(rho<1e-7)return{lat:90,lon:0};const t=rho*PS_TC/(PS_A*PS_MC),let phi=Math.PI/2-2*Math.atan(t);for(let i=0;i<7;i++)phi=Math.PI/2-2*Math.atan(t*Math.pow((1-PS_E*Math.sin(phi))/(1+PS_E*Math.sin(phi)),PS_E/2));return{lat:phi*180/Math.PI/lon:Math.atan2(x,y)*180/Math.PI};};
  const ll=points=>points.map(([lat,lon])=>polar(lat,lon));
  const home=polar