from pathlib import Path
import re


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


def regex_once(text, pattern, repl, label, flags=0):
    out, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return out


# ---------------- expedition.js ----------------
p = 'expedition.js'
s = read(p)

s = replace_once(
    s,
    "    aerial: {src:'assets/research/aerial-survey.webp', alt:'Aerial survey over Arctic sea ice', credit:'NOAA Fisheries', source:'https://www.fisheries.noaa.gov/feature-story/us-and-russian-scientists-partner-study-polar-bear-and-seal-populations'},",
    "    aerial: {src:'assets/research/aerial-survey.webp', alt:'Aerial survey over Arctic sea ice', credit:'NOAA Fisheries', source:'https://www.fisheries.noaa.gov/feature-story/us-and-russian-scientists-partner-study-polar-bear-and-seal-populations'},\n    helicopter: {src:'https://media.defense.gov/2016/Oct/27/2001659066/-1/-1/0/161026-G-AS999-011.JPG', alt:'MH-60 Jayhawk helicopter touching down on USCGC Healy during Arctic operations', credit:'U.S. Coast Guard / Petty Officer 1st Class Kelly Parker', source:'https://www.mycg.uscg.mil/About-Us/Our-Organization/Images/Mission_Images/igphoto/2001659066/'},",
    'helicopter media'
)

s = regex_once(
    s,
    r"('manned-helicopter': equipment\(\{.*?media:)MEDIA\.aerial(\}\),)",
    r"\1MEDIA.helicopter\2",
    'helicopter equipment image',
    re.S
)
s = regex_once(
    s,
    r"(mission\(\{id:'helicopter-axctd'.*?media:)MEDIA\.aerial(, description:)",
    r"\1MEDIA.helicopter\2",
    'AXCTD helicopter image',
    re.S
)
s = regex_once(
    s,
    r"(mission\(\{id:'helicopter-field-team'.*?media:)MEDIA\.aerial(, description:)",
    r"\1MEDIA.helicopter\2",
    'ice camp helicopter image',
    re.S
)

steps_helper = r'''  function missionSpecificSteps(target={}) {
    const raw=`${target.title||''} ${target.shortTitle||''}`.toLowerCase(),name=String(target.shortTitle||target.title||'research program').replace(/^event:\s*/i,'').trim();
    const gearNames=[...new Set(target.equipment||[])].map(id=>EQUIPMENT[id]?.name).filter(Boolean),gear=gearNames.slice(0,2).join(' and ');
    if(/fram.*strait|strait.*exchange/.test(raw))return ['Set the cross-strait station line from Greenland to Svalbard','Profile Atlantic and Polar Water at each occupied station','Measure current shear through the exchange layer','Close the heat and freshwater transport across the section','Assemble the Fram Strait transport estimate'];
    if(/lomonosov|ridge|abyss|deep[- ]water/.test(raw))return ['Locate the ridge flank and deep-water interface','Run full-depth profiles across the topographic gradient','Resolve water-mass boundaries and deep current shear','Compare stations on both sides of the ridge crest','Build the deep-water transect section'];
    if(/beaufort.*gyre|gyre.*freshwater/.test(raw))return ['Map the Beaufort Gyre halocline along the survey line','Profile salinity through the freshwater lens','Measure geostrophic shear beneath the halocline','Calculate freshwater content at each station','Close the regional freshwater-storage estimate'];
    if(/halocline/.test(raw))return ['Find the cold-halocline transition in the first profile','Resolve temperature, salinity and shear across the interface','Repeat profiles where the halocline is actively mixing','Quantify ventilation and vertical exchange','Assemble the halocline mixing budget'];
    if(/atlantic.*water|boundary current|heat[- ]flux/.test(raw))return ['Locate the Atlantic Water core with the opening profile','Run the section across the boundary current','Resolve temperature, salinity and velocity structure','Integrate heat transport through the current','Compare the section with upstream Atlantic Water properties'];
    if(/moor|time[- ]series|time series/.test(raw))return ['Confirm bottom depth and mooring coordinates','Lay out the anchor, release and sensor line on deck','Deploy the mooring under controlled wire tension','Range the acoustic release and verify sensor telemetry','Document the final time-series position and configuration'];
    if(/plankton|bloom|food[- ]web|food web|zooplankton/.test(raw))return ['Map the biological layer before the first net station','Sample the target depth interval with the selected nets','Preserve depth-resolved plankton fractions','Match catches to fluorescence and hydrography','Build the abundance and food-web section'];
    if(/acoustic|sound|sonobuoy|propagation|hydrophone/.test(raw))return ['Establish a quiet-ship acoustic baseline','Measure the sound-speed structure through the water column','Deploy and synchronize the acoustic receivers','Record the planned source or ambient-noise sequence','Compare observed propagation with the predicted sound field'];
    if(/mammal|whale|seal|walrus|wildlife/.test(raw))return ['Set the visual and acoustic survey track','Log effort, visibility and sea state continuously','Classify each sighting or call with position and time','Cross-check detections against habitat and ice conditions','Build the encounter-rate and distribution product'];
    if(/fish|fisher|ek80|trawl/.test(raw))return ['Calibrate the scientific echosounder for the survey band','Map fish schools along the assigned transect','Select verification stations from the acoustic record','Collect biological samples at representative schools','Convert backscatter and catches into the abundance estimate'];
    if(/ice|floe|under[- ]ice|snow/.test(raw))return ['Select a safe representative floe for the program','Lay out the snow and ice sampling transect','Measure ice thickness, structure and surface state','Collect the required cores or under-ice observations','Relate the station measurements to floe drift and ice conditions'];
    if(/fog|cloud|aerosol|atmos|boundary layer|flux|weather/.test(raw))return ['Establish the surface meteorology and flux baseline','Profile the lower atmosphere through the target layer','Track cloud, aerosol or visibility changes during the station','Match remote sensors to the in-situ profile','Assemble the boundary-layer evolution record'];
    if(/benthic|sediment|seafloor|rov|bottom/.test(raw))return ['Map the seafloor target before lowering equipment','Lower the camera or sampler under controlled wire tension','Document bottom type and benthic habitat along the station','Recover and section the sediment or imagery record','Merge seafloor observations into the site interpretation'];
    if(/carbon|biogeochem|nutrient|oxygen|edna|chemistry/.test(raw))return ['Resolve the hydrographic layers for targeted water sampling','Collect clean samples at the selected depths','Process nutrients, oxygen, carbon or DNA fractions aboard','Check blanks, replicates and sensor agreement','Build the vertical biogeochemical profile'];
    if(/fjord|coastal|shelf|river|plume/.test(raw))return ['Lay out the cross-shore or cross-fjord station line','Occupy stations from the nearshore end member offshore','Resolve the salinity and current gradient across the feature','Collect the project-specific biological or chemical samples','Build the coastal exchange section'];
    return [`Lay out the ${name} observing pattern`,gear?`Stage ${gear} for the ${name} stations`:`Prepare the science team for the ${name} stations`,`Collect the core observations that define ${name}`,`Cross-check the ${name} record for spatial and instrument consistency`,`Assemble the ${name} sponsor data product`];
  }

'''
s = replace_once(s, '  function careerFallbackTemplate(', steps_helper + '  function careerFallbackTemplate(', 'specific research steps helper')

s = replace_once(
    s,
    "    const media=equipment.map(id=>EQUIPMENT[id]?.media).find(Boolean)||(level>=3?MEDIA.ctd:level===2?MEDIA.winch:MEDIA.local);",
    "    const media=equipment.map(id=>EQUIPMENT[id]?.media).find(Boolean)||(level>=3?MEDIA.ctd:level===2?MEDIA.winch:MEDIA.local),steps=missionSpecificSteps({title:project.title,shortTitle:project.short||project.shortTitle||'',specialties:[specialty],equipment});",
    'fallback specific steps'
)
s = replace_once(s, "steps:['Frame the process hypothesis','Calibrate and stage the required instruments','Execute the observing pattern','Integrate the multidisciplinary record','Deliver the sponsor science synthesis']", 'steps', 'professor fallback steps')
s = replace_once(s, "steps:['Define the process hypothesis','Calibrate the required instruments','Collect the regional observations','Resolve the spatial or temporal gradient','Prepare the sponsor synthesis']", 'steps', 'postdoc fallback steps')
s = replace_once(s, "steps:['Define the local observation plan','Collect a repeatable field record','Check metadata and position','Preserve samples or imagery','Transmit the sponsor summary']", 'steps', 'grad fallback steps')

s = replace_once(
    s,
    "const progress=running?0:complete?100:0,steps=target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station'];",
    "const progress=running?0:complete?100:0,steps=target.steps?.length?target.steps:missionSpecificSteps(target);",
    'research window default steps'
)
s = replace_once(
    s,
    "activeOperation={targetId:id,startedAt:performance.now(),durationMs,workHours,days,stationIndex:target.stationIndex||0,participantIds,steps:target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station']};",
    "activeOperation={targetId:id,startedAt:performance.now(),durationMs,workHours,days,stationIndex:target.stationIndex||0,participantIds,steps:target.steps?.length?target.steps:missionSpecificSteps(target)};",
    'operation default steps'
)

# Keep the same touch-first research layout on phones and tablets.
s = replace_once(s, '@media(max-width:760px)', '@media(max-width:1200px)', 'research phone tablet layout')
write(p, s)


# ---------------- game.js ----------------
p = 'game.js'
s = read(p)

s = replace_once(s, 'const refreshMs=IS_COARSE_POINTER?420:280', 'const refreshMs=IS_COARSE_POINTER?95:80', 'smoother world cache')
s = replace_once(s, 'if(floeUpdateAccumulator>=.075)', 'if(floeUpdateAccumulator>=.035)', 'smoother floe physics')

label_pattern = r"if\(!afterFog&&\(zoomLevel>=\.55\|\|item\.distance<180\)\)\{const count=targetStationPoints\(target\)\.length,stationText=count\?` · \$\{Math\.min\(count,\(target\.stationIndex\|\|0\)\+1\)\}/\$\{count\}`:'',site=target\.siteName\?` · \$\{target\.siteName\}`:'',label=\(target\.shortTitle\|\|target\.title\|\|'RESEARCH SITE'\)\+stationText\+site;ctx\.font='800 9px system-ui';ctx\.textAlign='center';ctx\.strokeStyle='rgba\(4,31,49,\.94\)';ctx\.lineWidth=3;ctx\.strokeText\(label\.toUpperCase\(\),p\.x,p\.y-19\);ctx\.fillStyle=eligible\?'#f5fbfc':'#aebec2';ctx\.fillText\(label\.toUpperCase\(\),p\.x,p\.y-19\);\}"
s = regex_once(s, label_pattern, '', 'remove question-mark labels')

s = replace_once(
    s,
    'let ac=null,waveSource=null,waveGain=null,lastCrack=0,lastAnimal=0,unlockChimed=false,unlockPromise=null;',
    'let ac=null,waveSource=null,waveGain=null,ambientWindGain=null,ambientPadGain=null,ambientPadOsc=[],lastCrack=0,lastAnimal=0,unlockChimed=false,unlockPromise=null,nextBird=0,nextBell=0;',
    'ambient audio state'
)
ambient_setup = r'''    // SEASONAL ARCTIC AMBIENCE: deliberately subtle; wind, a low tonal bed and sparse seasonal details.
    const setupAmbience=c=>{if(ambientWindGain)return;const seconds=8,b=c.createBuffer(1,c.sampleRate*seconds,c.sampleRate),d=b.getChannelData(0);for(let i=0;i<d.length;i++){const slow=Math.sin(i/9200)*.22+Math.sin(i/31000)*.14;d[i]=(Math.random()*2-1)*(.45+slow);}const src=c.createBufferSource(),windFilter=c.createBiquadFilter();src.buffer=b;src.loop=true;windFilter.type='bandpass';windFilter.frequency.value=310;windFilter.Q.value=.42;ambientWindGain=c.createGain();ambientWindGain.gain.value=0;src.connect(windFilter).connect(ambientWindGain).connect(c.destination);src.start();const padFilter=c.createBiquadFilter();padFilter.type='lowpass';padFilter.frequency.value=360;ambientPadGain=c.createGain();ambientPadGain.gain.value=.0001;padFilter.connect(ambientPadGain).connect(c.destination);for(const freq of[82.4,123.6]){const o=c.createOscillator(),g=c.createGain();o.type='sine';o.frequency.value=freq;g.gain.value=freq<100?.7:.38;o.connect(g).connect(padFilter);o.start();ambientPadOsc.push(o);}};
'''
s = replace_once(s, '    const ensure=()=>{', ambient_setup + '    const ensure=()=>{', 'ambient setup function')
s = replace_once(s, 'waveSource.start();}catch(e){}return ac;};', 'waveSource.start();setupAmbience(ac);}catch(e){}return ac;};', 'start ambience graph')

old_update = "    const update=paused=>{if(!ac)return;const now=performance.now();if(waveGain)waveGain.gain.setTargetAtTime((!paused&&state.moving&&!state.ramming)?0.05:0,ac.currentTime,.22);if(!paused&&state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};"
new_update = r'''    const update=paused=>{if(!ac)return;const now=performance.now(),day=((state.seasonDay%365)+365)%365,season=day<91?'autumn':day<213?'winter':day<274?'spring':'summer';if(waveGain)waveGain.gain.setTargetAtTime((!paused&&state.moving&&!state.ramming)?0.045:0,ac.currentTime,.22);if(ambientWindGain){const wind=paused?0:{autumn:.008,winter:.018,spring:.007,summer:.004}[season];ambientWindGain.gain.setTargetAtTime(wind,ac.currentTime,.8);}if(ambientPadGain){const pad=paused?0:{autumn:.0023,winter:.0015,spring:.0027,summer:.0021}[season];ambientPadGain.gain.setTargetAtTime(pad,ac.currentTime,1.3);}if(!paused&&ac.state==='running'){if(!nextBird)nextBird=now+9000+Math.random()*8000;if(!nextBell)nextBell=now+18000+Math.random()*14000;if(season==='summer'&&now>=nextBird){tone(1780,.10,.008,0,'sine');tone(2240,.08,.007,.11,'sine');tone(1960,.09,.006,.23,'sine');nextBird=now+13000+Math.random()*18000;}else if(season!=='summer'&&now>=nextBird)nextBird=now+12000;if(now>=nextBell){const base={autumn:196,winter:146.8,spring:220,summer:246.9}[season];tone(base,1.7,.0045,0,'sine');tone(base*1.5,1.3,.003,.24,'sine');nextBell=now+26000+Math.random()*26000;}}if(!paused&&state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};'''
s = replace_once(s, old_update, new_update, 'seasonal ambient update')

# Phone/tablet: one touch layout family, not separate tablet controls.
s = replace_once(s, '((pointer:coarse) and (max-width:900px))', '((pointer:coarse) and (max-width:1200px))', 'touch layout family') if '((pointer:coarse) and (max-width:900px))' in s else s
write(p, s)


# ---------------- style.css ----------------
p = 'style.css'
s = read(p)
s = replace_once(s, '@media (max-width: 760px)', '@media (max-width: 1200px)', 'title phone tablet layout')
s = replace_once(s, '((pointer:coarse) and (max-width:900px))', '((pointer:coarse) and (max-width:1200px))', 'HUD phone tablet layout')
write(p, s)


# ---------------- index.html cache bust ----------------
p = 'index.html'
s = read(p)
s = s.replace('expedition-23af-audio-rewards-journal-map', 'expedition-23ag-smooth-ambient-specific')
if 'expedition-23ag-smooth-ambient-specific' not in s:
    raise SystemExit('cache bust failed')
write(p, s)
