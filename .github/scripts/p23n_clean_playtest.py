from pathlib import Path
import re


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, got {count}")
    return text.replace(old, new, 1)


def rex(text, pattern, replacement, label, flags=re.S):
    out, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 regex match, got {count}")
    return out


exp_path = Path('expedition.js')
game_path = Path('game.js')
index_path = Path('index.html')
exp = exp_path.read_text()
game = game_path.read_text()
index = index_path.read_text()

# ---------------------------------------------------------------------------
# 1. Photographic media only in research/equipment cards.
# ---------------------------------------------------------------------------
media_block = r'''  const MEDIA = {
    local: {src:'assets/research/arctic-small-boat.webp', alt:'Small survey boat operating in Arctic water', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    river: {src:'assets/research/river-plume.webp', alt:'Sediment-rich Mackenzie River water entering the Beaufort Sea', credit:'NASA Earth Observatory / Lauren Dauphin', source:'https://earthobservatory.nasa.gov/images/146813/breakup-along-the-mackenzie-river'},
    ice: {src:'assets/research/sea-ice-station.webp', alt:'Researchers working on Arctic sea ice', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    aerial: {src:'assets/research/aerial-survey.webp', alt:'Aerial survey over Arctic sea ice', credit:'NOAA Fisheries', source:'https://www.fisheries.noaa.gov/feature-story/us-and-russian-scientists-partner-study-polar-bear-and-seal-populations'},
    storm: {src:'assets/research/storm-sea.webp', alt:'Research vessel in high Arctic seas', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    xbt: {src:'assets/equipment/xbt.webp', alt:'XBT oceanographic field equipment', credit:'Oceanographic equipment photograph', source:''},
    argo: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Argo%20float%20deployed%20from%20research%20vessel.jpg', alt:'Argo profiling float being deployed from a research vessel', credit:'NOAA GOMO / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Argo_float_deployed_from_research_vessel.jpg'},
    hydrophone: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Hydrophone%20arrays%20on%20the%20deck%20of%20the%20USNS%20Kane.jpg', alt:'Hydrophone arrays laid out on a research vessel deck', credit:'NOAA / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Hydrophone_arrays_on_the_deck_of_the_USNS_Kane.jpg'},
    sonobuoy: {src:'assets/equipment/sonobuoy.webp', alt:'Oceanographic sonobuoy equipment', credit:'Oceanographic equipment photograph', source:''},
    ctd: {src:'assets/equipment/ctd-rosette.webp', alt:'CTD rosette aboard NOAA Ship Okeanos Explorer', credit:'NOAA Ocean Exploration', source:'https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-ex2101-features-ctd-media-rosette/'},
    rov: {src:'assets/equipment/work-rov.webp', alt:'ROV Deep Discoverer on a research vessel deck', credit:'NOAA Ocean Exploration', source:'https://oceanexplorer.noaa.gov/multimedia/rov-deep-discoverer/'},
    radar: {src:'assets/equipment/cloud-radar.webp', alt:'NOAA W-band research radar', credit:'Ken Moran / NOAA CIRES', source:'https://psl.noaa.gov/technology/w-band-radar/'},
    balloon: {src:'assets/equipment/radiosonde.webp', alt:'Weather balloon carrying atmospheric instruments', credit:'NOAA NCEI', source:'https://www.ncei.noaa.gov/products/weather-balloon'},
    aerostat: {src:'assets/equipment/aerostat.webp', alt:'Research aerostat field system', credit:'Research equipment photograph', source:''},
    drone: {src:'assets/equipment/large-drone.webp', alt:'Large fixed-wing scientific drone prepared for shipboard operations', credit:'Research aircraft photograph', source:''},
    drifter: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Argo%20float%20deployed%20from%20research%20vessel.jpg', alt:'Autonomous ocean observing float during deployment', credit:'NOAA GOMO / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Argo_float_deployed_from_research_vessel.jpg'},
    starlink: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Starlink%20Dish%2020250111%20101122.jpg', alt:'Flat Starlink terminal installed on a ship', credit:'Ka23 13 / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Starlink_Dish_20250111_101122.jpg'},
    winch: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/1991%20windenleitstand%20hg.jpg', alt:'Oceanographic winch operations on the research vessel Polarstern', credit:'Hannes Grobe / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:1991_windenleitstand_hg.jpg'},
    hullSensor: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Sondeur%20transducteur.jpg', alt:'Echo sounder transducer', credit:'Clipper / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Sondeur_transducteur.jpg'},
    serviceTools: {src:'assets/research/arctic-small-boat.webp', alt:'Small Arctic field boat prepared for coastal servicing', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    handheldWater: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Researchers%20using%20Niskin%20bottle%20to%20collect%20water%20sample%20%C2%B7%20DN-SD-01-00282.JPEG', alt:'Researchers collecting an Arctic water sample with oceanographic equipment', credit:'U.S. Navy / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Researchers_using_Niskin_bottle_to_collect_water_sample_%C2%B7_DN-SD-01-00282.JPEG'},
    iceCorer: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/ACFEL%20ice%20auger%20in%20test%20block%20of%20ice.jpg', alt:'Scientific ice auger drilling into ice', credit:'U.S. Government / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:ACFEL_ice_auger_in_test_block_of_ice.jpg'},
    miniRov: {src:'assets/equipment/work-rov.webp', alt:'Scientific ROV on a research vessel deck', credit:'NOAA Ocean Exploration', source:'https://oceanexplorer.noaa.gov/multimedia/rov-deep-discoverer/'},
    shallowAdcp: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Deployment%20of%20acoustic%20doppler%20current%20profiler.jpg', alt:'Acoustic Doppler current profiler being deployed', credit:'USGS / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Deployment_of_acoustic_doppler_current_profiler.jpg'},
    shelfAdcp: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Mission%20AWA%20-%20Mise%20en%20%C5%93uvre%20de%20l%27ADCP%20%28Acoustic%20Doppler%20Current%20Profiler%29%20depuis%20la%20Thalassa%20%28Ifremer%2000562-67430%20-%2041954%29.jpg', alt:'ADCP being deployed from an oceanographic vessel', credit:'Ifremer / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Mission_AWA_-_Mise_en_%C5%93uvre_de_l%27ADCP_(Acoustic_Doppler_Current_Profiler)_depuis_la_Thalassa_(Ifremer_00562-67430_-_41954).jpg'},
    deepAdcp: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Acoustic%20Doppler%20Current%20Profiler.jpg', alt:'Deep-ocean acoustic Doppler current profiler', credit:'Wusel007 / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Acoustic_Doppler_Current_Profiler.jpg'},
    ek80: {src:'assets/vessels/noaa-rv-brown.webp', alt:'Oceanographic research vessel carrying scientific acoustic systems', credit:'Wade Blake / NOAA', source:'https://oceanexplorer.noaa.gov/technology/noaa-ship-brown/'},
    cameraTelephoto: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Sigma%20150-500mm%2002.jpg', alt:'DSLR camera fitted with an extra-large telephoto lens', credit:'Gerwin Sturm / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Sigma_150-500mm_02.jpg'},
    bongoDetailed: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Projet%20BioCotEs%20-%20Filet%20%C3%A0%20plancton%20%22Bongo%22%20%28Ifremer%2000810-92149%29.jpg', alt:'Paired Bongo plankton net system', credit:'Ifremer / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Projet_BioCotEs_-_Filet_%C3%A0_plancton_%22Bongo%22_(Ifremer_00810-92149).jpg'},
    ednaKit: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Manual%20pump%20used%20to%20move%20water%20through%20a%20filter%20for%20eDNA%20testing.%20%28c0fad0b1-d569-4d79-9fb7-1edcfb989389%29.JPG', alt:'Manual filtration pump used for eDNA field sampling', credit:'National Park Service / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Manual_pump_used_to_move_water_through_a_filter_for_eDNA_testing._(c0fad0b1-d569-4d79-9fb7-1edcfb989389).JPG'},
    fieldKit: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Arthropod%20field%20collection%20kit.png', alt:'Scientific field collection kit with GPS, notebook and sample containers', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Arthropod_field_collection_kit.png'},
    shoreDebris: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Collected%20Beach%20Litter%20at%20Scabbacombe%20Sands.jpg', alt:'Marine debris collected during a shoreline survey', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Collected_Beach_Litter_at_Scabbacombe_Sands.jpg'},
    shallowCorer: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Giant-box-corer%20hg.jpg', alt:'Scientific sediment corer being deployed from a research vessel', credit:'Hannes Grobe / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Giant-box-corer_hg.jpg'},
    surfaceNet: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Plankton%20Net%20%2808010639%29%20%2846940308932%29.jpg', alt:'Scientific plankton net', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Plankton_Net_(08010639)_(46940308932).jpg'},
    verticalNet: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Plankton%20Net%20%2808010639%29%20%2846940308932%29.jpg', alt:'Scientific plankton net prepared for sampling', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Plankton_Net_(08010639)_(46940308932).jpg'},
    bongoNet: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Projet%20BioCotEs%20-%20Filet%20%C3%A0%20plancton%20%22Bongo%22%20%28Ifremer%2000810-92149%29.jpg', alt:'Paired Bongo plankton net system', credit:'Ifremer / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Projet_BioCotEs_-_Filet_%C3%A0_plancton_%22Bongo%22_(Ifremer_00810-92149).jpg'},
    sedimentCorer: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Giant-box-corer%20hg.jpg', alt:'Large scientific box corer during research-vessel operations', credit:'Hannes Grobe / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Giant-box-corer_hg.jpg'},
    coastalAFrame: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Stern%20of%20the%20Kilo%20Moana.jpg', alt:'Research vessel stern with a large oceanographic A-frame', credit:'NOAA / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Stern_of_the_Kilo_Moana.jpg'},
    vessel: {src:'assets/vessels/noaa-rv-brown.webp', alt:'NOAA Ship Ronald H. Brown underway', credit:'Wade Blake / NOAA', source:'https://oceanexplorer.noaa.gov/technology/noaa-ship-brown/'}
  };'''
exp = rex(exp, r"  const MEDIA = \{.*?\n  \};\n\n  const SPECIALTIES =", media_block + "\n\n  const SPECIALTIES =", 'photographic MEDIA block')

# Use representative real photographs for vessel cards too.
new_vessel_images = r'''  const VESSEL_IMAGES = {
    coastal:'assets/vessels/fishing-trawler.webp',
    global:'assets/vessels/noaa-rv-brown.webp',
    icebreaker:'https://commons.wikimedia.org/wiki/Special:FilePath/Polarforskningssekretariatet%20IMG%202551%20Oden%20Hjorthfjellet.jpg',
    nuclear:'https://commons.wikimedia.org/wiki/Special:FilePath/50%20Let%20Pobedy.jpg'
  };'''
exp = rex(exp, r"  const VESSEL_IMAGES = \{.*?\n  \};", new_vessel_images, 'photographic vessel images')

# ---------------------------------------------------------------------------
# 2. Publication tiers: simple Letter / Article / Book + first-unlock explainer.
# ---------------------------------------------------------------------------
old_papers = """  const PAPER_LEVELS = [
    {id:'local',threshold:100,next:1000,label:'Arctic Field Research Note',journal:'Svalbard Science Bulletin',award:30000,initialCitations:10,potential:90},
    {id:'national',threshold:1000,next:10000,label:'Peer-Reviewed Research Article',journal:'Nordic Polar Research Review',award:350000,initialCitations:130,potential:1400},
    {id:'international',threshold:10000,next:null,label:'Landmark International Paper',journal:'International Journal of Polar Systems',award:4000000,initialCitations:1700,potential:18000}
  ];"""
new_papers = """  const PAPER_LEVELS = [
    {id:'local',threshold:100,next:1000,label:'Letter',journal:'Svalbard Science Bulletin',award:30000,initialCitations:10,potential:90},
    {id:'national',threshold:1000,next:10000,label:'Article',journal:'Nordic Polar Research Review',award:350000,initialCitations:130,potential:1400},
    {id:'international',threshold:10000,next:null,label:'Book',journal:'Arctic Research Monographs',award:4000000,initialCitations:1700,potential:18000}
  ];"""
exp = once(exp, old_papers, new_papers, 'paper tier labels')
exp = once(exp,
    "observed:[], observedIndividuals:[], claimedGroups:[], papers:[], publicationCooldown:0, publishAttempts:0, lastPublicationRejected:false,",
    "observed:[], observedIndividuals:[], claimedGroups:[], papers:[], publicationCooldown:0, publishAttempts:0, lastPublicationRejected:false, publicationIntroShown:false,",
    'publication intro state')
exp = once(exp,
    "state.data+=amount; callbacks.onSound?.('data',{amount});",
    "state.data+=amount; callbacks.onSound?.('data',{amount}); if(state.data>=PUBLISH_MIN&&!state.publicationIntroShown)setTimeout(maybePublicationIntro,0);",
    'publication intro trigger')
intro_function = r'''  function maybePublicationIntro() {
    if(state.publicationIntroShown||state.data<PUBLISH_MIN||!root||activeOperation)return false;
    if(root.querySelector('.arx-modal.open'))return false;
    state.publicationIntroShown=true;
    const modal=root.querySelector('#arx-publish-modal');if(!modal)return false;
    modal.innerHTML=`<div class="arx-modal-card arx-result-card arx-publication-intro"><button class="arx-close" data-arx-action="close-publication-intro">×</button><small>PUBLICATION UNLOCKED</small><h2>Your first publication is ready</h2><p>Field work produces <b>publication data</b>. Crossing a publication threshold lets you submit the corresponding work. Accepted publications then earn citations; citations are what drive your scientific reputation and career progression.</p><div class="arx-publication-tier-guide"><span><b>LETTER</b><small>100 data</small><em>Short, focused result from a compact field program.</em></span><span><b>ARTICLE</b><small>1,000 data</small><em>A full peer-reviewed study built from a much larger data set.</em></span><span><b>BOOK</b><small>10,000 data</small><em>A major Arctic synthesis. This top tier publishes automatically once ready.</em></span></div><p>You can keep collecting data beyond a threshold before submitting. For Letter and Article tiers, additional data improves the acceptance chance. Your first publication is guaranteed so the system is easy to learn.</p><button data-arx-action="close-publication-intro">GOT IT</button></div>`;
    modal.classList.add('open');callbacks.onStateChange?.();return true;
  }
'''
exp = once(exp, "  function maybeAutoPublish() {", intro_function + "  function maybeAutoPublish() {", 'publication intro function')

exp = once(exp,
    "!level?`${Math.ceil(PUBLISH_MIN-state.data)} more data for an Arctic Field Research Note`:level.next?`${level.label} ready · ${Math.round(chance*100)}% acceptance`:'Landmark paper threshold reached · automatic submission';",
    "!level?`${Math.ceil(PUBLISH_MIN-state.data)} more data for a Letter`:level.next?`${level.label} ready · ${Math.round(chance*100)}% acceptance`:'Book threshold reached · automatic publication';",
    'sidebar publication copy')
exp = once(exp,
    '<div class="arx-gauge-labels"><span>100 FIELD NOTE</span><span>1,000 RESEARCH ARTICLE</span><span>10,000 LANDMARK PAPER</span></div>',
    '<div class="arx-gauge-labels"><span>LETTER</span><span>ARTICLE</span><span>BOOK</span></div>',
    'sidebar simple tier labels')

# ---------------------------------------------------------------------------
# 3. Reward economy. Official port grants: 40-60k. Random: 10-15k.
#    Equipment (especially expendables), work, and official-grant distance
#    move the award within the range.
# ---------------------------------------------------------------------------
new_distance = r'''  function researchDistanceWindow(template,kind,options={}) {
    if(options.nearby){const max=options.iceThickness>=2?70:90;return{min:10,max};}
    const ranges={fishing:[5,48],trawler:[10,125],coastal:[28,330],global:[65,700],icebreaker:[95,1050],nuclear:[125,1450]}, range=ranges[state.currentVessel]||ranges.fishing;
    const progress=clamp(state.completed.length/12,0,1),localMax=state.currentVessel==='fishing'?28+progress*34:state.currentVessel==='trawler'?55+progress*55:range[1];
    const baseMin=template.minDistance??(kind==='opportunity'?Math.min(45,range[0]+15):range[0]),official=kind==='grant'||kind==='contract';
    const min=official&&!template.anywhere?Math.max(22,baseMin):baseMin;
    const requestedMax=min+(template.distanceRange??(kind==='opportunity'?range[1]*.45:range[1]-range[0]));
    return {min:Math.min(min,localMax-2),max:Math.max(min+2,Math.min(requestedMax,localMax))};
  }'''
exp = rex(exp, r"  function researchDistanceWindow\(template,kind,options=\{\}\) \{.*?\n  \}", new_distance, 'grant distance window')

reward_helpers = r'''  function missionRewardScore(template,distanceKm,kind) {
    const ids=[...(template.equipment||[]),...(template.consumables||[])],unique=[...new Set(ids)];
    let durable=0,disposable=0;
    for(const id of unique){const item=EQUIPMENT[id];if(!item)continue;if(item.consumable)disposable+=Math.max(0,item.price||0);else durable+=Math.max(0,item.price||0);}
    const durableScore=clamp(Math.log10(1+durable)/6,0,1),disposableScore=clamp(Math.log10(1+disposable*5)/5.5,0,1),workScore=clamp(((template.workHours||10)-8)/135,0,1);
    const official=kind==='grant'||kind==='contract';
    if(official){const distanceScore=clamp((Math.max(0,distanceKm||0)-20)/220,0,1);return clamp(.30*durableScore+.28*disposableScore+.27*workScore+.15*distanceScore,0,1);}
    return clamp(.35*durableScore+.35*disposableScore+.30*workScore,0,1);
  }
  function missionRewardAmount(template,kind,distanceKm,rng) {
    const official=kind==='grant'||kind==='contract',range=official?[40000,60000]:[10000,15000];
    const score=clamp(missionRewardScore(template,distanceKm,kind)+(rng()-.5)*.05,0,1);
    return Math.round((range[0]+(range[1]-range[0])*score)/500)*500;
  }
'''
exp = once(exp, "  function buildTarget(template, origin, rng, kind='grant', options={}) {", reward_helpers + "  function buildTarget(template, origin, rng, kind='grant', options={}) {", 'reward helpers')
exp = once(exp,
    "    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03), rewardScale=vesselRewardScale(),missionLevel=templateCareerLevel(template),careerRewardBoost=missionLevel<=2?3:1,sourceRewardBoost=kind==='grant'?(state.port?5:2):1;",
    "    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03);",
    'remove old reward multipliers')
exp = once(exp,
    "      data:Math.max(1,Math.round(template.data*scale*vesselScale*crewScale*iceValueMultiplier)), reward:Math.round(template.reward*scale*careerRewardBoost*sourceRewardBoost*iceValueMultiplier*rewardScale),",
    "      data:Math.max(1,Math.round(template.data*scale*vesselScale*crewScale*iceValueMultiplier)), reward:missionRewardAmount(template,kind,distance,rng),",
    'new reward amount')
exp = once(exp,
    "      upfront:kind==='grant'?Math.round(template.reward*scale*careerRewardBoost*sourceRewardBoost*iceValueMultiplier*rewardScale*.2):0, advancePaid:0, postdocOpportunity:!!template.postdocOpportunity,",
    "      upfront:0, advancePaid:0, postdocOpportunity:!!template.postdocOpportunity,",
    'remove upfront generation')

# ---------------------------------------------------------------------------
# 4. Port cards: no upfront and no locate/navigate button.
# ---------------------------------------------------------------------------
exp = once(exp,
    '<div class="arx-grant-advance"><span><small>TOTAL SPONSOR AWARD</small><b>${cash(item.reward)}</b></span><span><small>PAID UPFRONT ON ACCEPTANCE</small><b>${cash(item.upfront||0)}</b></span></div>',
    '<div class="arx-grant-advance"><span><small>PAYMENT ON COMPLETION</small><b>${cash(item.reward)}</b></span></div>',
    'offer payment display')
exp = once(exp,
    '<div class="arx-stats"><span>${item.data} data</span><span>Upfront paid ${cash(item.advancePaid||0)}</span>${item.iceValueMultiplier>1?`<span>ICE PREMIUM ×${item.iceValueMultiplier.toFixed(2)}</span>`:\'\'}<span>~${projection.days} field days</span><span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><div class="arx-grant-actions"><button data-arx-action="navigate-target" data-id="${item.id}">LOCATE / NAVIGATE</button><button class="danger" data-arx-action="drop-grant" data-id="${item.id}" ${recovery&&!teamPickup?\'disabled\':\'\'}>${recovery?(teamPickup?\'DROP RETURN PICKUP\':\'DEPLOYED EQUIPMENT MUST BE RECOVERED\'):\'DROP RESEARCH GRANT\'}</button></div>',
    '<div class="arx-stats"><span>${item.data} data</span><span>Payment ${cash(item.reward)} on completion</span>${item.iceValueMultiplier>1?`<span>ICE PREMIUM ×${item.iceValueMultiplier.toFixed(2)}</span>`:\'\'}<span>~${projection.days} field days</span><span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><div class="arx-grant-actions"><button class="danger" data-arx-action="drop-grant" data-id="${item.id}" ${recovery&&!teamPickup?\'disabled\':\'\'}>${recovery?(teamPickup?\'DROP RETURN PICKUP\':\'DEPLOYED EQUIPMENT MUST BE RECOVERED\'):\'DROP RESEARCH GRANT\'}</button></div>',
    'active grant no locate button')

# Unified research window has no navigation action and no upfront field.
exp = once(exp,
    "    const canNavigate=!target.anywhere&&!atSite&&!running&&!programFinished,canBegin=atSite&&readiness.ready&&!running&&!complete;",
    "    const canBegin=atSite&&readiness.ready&&!running&&!complete;",
    'remove modal navigation state')
exp = once(exp,
    '<span><small>UPFRONT</small><b>${cash(target.upfront||0)}${target.advancePaid?\' · PAID\':\'\'}</b></span>',
    '<span><small>PAYMENT</small><b>ON COMPLETION</b></span>',
    'research modal payment fact')
exp = rex(exp,
    r'\$\{decline\}<button data-arx-action="navigate-target" data-id="\$\{target\.id\}" \$\{canNavigate\?\'\':\'disabled\'\}>\$\{complete&&!programFinished\?\'NAVIGATE TO NEXT STATION\':\'NAVIGATE TO SITE\'\}</button><button data-arx-action="complete-target"',
    '${decline}<button data-arx-action="complete-target"',
    'remove research modal navigate button', flags=0)

# Pay everything when the work is actually completed/recovered.
exp = once(exp,
    "    const advance=Math.max(0,Number(target.advancePaid)||0),balance=Math.max(0,(Number(target.reward)||0)-advance);addData(dataGain);adjustMoney(balance);\n    return [{label:'DATA ARCHIVED',value:`+${dataGain}`},{label:'TOTAL AWARD',value:cash(target.reward)},{label:'UPFRONT PAID',value:cash(advance)},{label:'FINAL PAYMENT',value:cash(balance)}];",
    "    const payment=Math.max(0,Number(target.reward)||0);addData(dataGain);adjustMoney(payment);\n    return [{label:'DATA ARCHIVED',value:`+${dataGain}`},{label:'RESEARCH AWARD',value:cash(payment)},{label:'PAYMENT',value:'PAID ON COMPLETION'}];",
    'completion-only settlement')

# No acceptance cash injection.
exp = once(exp,
    "    state.targets.forEach(item=>item.selected=false);offer.selected=true;if((offer.upfront||0)>0&&!offer.advancePaid){offer.advancePaid=offer.upfront;adjustMoney(offer.upfront);}state.targets.push(offer);\n    state.offers=state.offers.filter(item=>item.id!==id);recordGrantUse(offer.templateId,offer);addLog(`Research grant accepted: ${offer.title}.${offer.advancePaid?` Upfront sponsor payment ${cash(offer.advancePaid)}.`:''}`);\n    toast(`RESEARCH GRANT ACCEPTED · ${offer.shortTitle}${offer.advancePaid?` · +${cash(offer.advancePaid)} UPFRONT`:''}`);changed();",
    "    state.targets.forEach(item=>item.selected=false);offer.selected=true;offer.upfront=0;offer.advancePaid=0;state.targets.push(offer);\n    state.offers=state.offers.filter(item=>item.id!==id);recordGrantUse(offer.templateId,offer);addLog(`Research grant accepted: ${offer.title}. Payment due on completion.`);\n    toast(`RESEARCH GRANT ACCEPTED · ${offer.shortTitle}`);changed();",
    'accept grant no upfront')
exp = once(exp,
    "else if (action==='accept-professor-grant'&&state.remoteOffer) { state.targets.forEach(item=>item.selected=false);state.remoteOffer.selected=true;if((state.remoteOffer.upfront||0)>0&&!state.remoteOffer.advancePaid){state.remoteOffer.advancePaid=state.remoteOffer.upfront;adjustMoney(state.remoteOffer.upfront);}state.targets.push(state.remoteOffer);addLog(`Professor-originated grant accepted: ${state.remoteOffer.title}.`);state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed(); }",
    "else if (action==='accept-professor-grant'&&state.remoteOffer) { state.targets.forEach(item=>item.selected=false);state.remoteOffer.selected=true;state.remoteOffer.upfront=0;state.remoteOffer.advancePaid=0;state.targets.push(state.remoteOffer);addLog(`Professor-originated grant accepted: ${state.remoteOffer.title}. Payment due on completion.`);state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed(); }",
    'professor grant no upfront')

# The sidebar's official navigation readout navigates directly; it no longer opens a pre-navigation card.
exp = once(exp,
    "  function openNavigationPrompt(id=state.navigation?.id) {\n    const target=state.targets.find(item=>item.id===id);if(!target)return false;const nav=state.navigation?.id===id?state.navigation:null;return openTarget(id,{distanceKm:nav?.distanceKm??Infinity,target});\n  }",
    "  function openNavigationPrompt(id=state.navigation?.id) {\n    const target=state.targets.find(item=>item.id===id);if(!target)return false;callbacks.onNavigate?.(target);return true;\n  }",
    'sidebar direct navigation')

# First publication explainer is shown after the research-result modal is acknowledged.
exp = once(exp,
    "else if (action==='acknowledge-research') { root.querySelector('#arx-target-modal').classList.remove('open'); showNextPromotion(); setTimeout(maybeAutoPublish,0); }",
    "else if (action==='acknowledge-research') { root.querySelector('#arx-target-modal').classList.remove('open'); if(!maybePublicationIntro()){showNextPromotion();setTimeout(maybeAutoPublish,0);} }",
    'publication intro after research')
exp = once(exp,
    "else if (action==='close-publish') { root.querySelector('#arx-publish-modal').classList.remove('open'); showNextPromotion(); }",
    "else if (action==='close-publish') { root.querySelector('#arx-publish-modal').classList.remove('open'); showNextPromotion(); }\n    else if (action==='close-publication-intro') { root.querySelector('#arx-publish-modal').classList.remove('open'); showNextPromotion(); setTimeout(maybeAutoPublish,0); }",
    'publication intro close action')

# iPhone portrait: top-align modals below the status-bar safe area with extra breathing room.
exp = once(exp,
    "@media(max-width:760px) and (orientation:portrait){.arx-modal{padding:calc(env(safe-area-inset-top) + 9px) 9px calc(env(safe-area-inset-bottom) + 9px)!important}.arx-modal-card{max-height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 18px)!important}",
    "@media(max-width:760px) and (orientation:portrait){.arx-modal.open{place-items:start center!important}.arx-modal{padding:calc(env(safe-area-inset-top) + 34px) 9px calc(env(safe-area-inset-bottom) + 10px)!important}.arx-modal-card{max-height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 44px)!important}",
    'portrait modal safe area')
exp = once(exp, ".arx-research-actions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-top:12px}", ".arx-research-actions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:12px}", 'research action columns')
exp = once(exp, ".arx-grant-advance{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:8px 0}", ".arx-grant-advance{display:grid;grid-template-columns:1fr;gap:6px;margin:8px 0}", 'grant payment columns')
exp = once(exp, ".arx-grant-actions{display:grid;grid-template-columns:1fr 1fr;gap:6px}", ".arx-grant-actions{display:grid;grid-template-columns:1fr;gap:6px}.arx-publication-tier-guide{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:16px 0;text-align:left}.arx-publication-tier-guide span{padding:11px;border:1px solid rgba(125,211,252,.2);border-radius:8px;background:rgba(30,79,96,.42)}.arx-publication-tier-guide b,.arx-publication-tier-guide small,.arx-publication-tier-guide em{display:block}.arx-publication-tier-guide b{color:#f6d365;font:900 14px system-ui}.arx-publication-tier-guide small{margin-top:3px;color:#7dd3fc;font-size:8px;font-weight:900}.arx-publication-tier-guide em{margin-top:7px;color:#a9cbd4;font-size:8px;font-style:normal;line-height:1.4}.arx-gauge-labels{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px;color:#91bac4;font-size:7px;font-weight:900;letter-spacing:.08em;text-align:center}@media(max-width:760px){.arx-publication-tier-guide{grid-template-columns:1fr}}", 'grant actions and publication guide')

# ---------------------------------------------------------------------------
# 5. Map behavior: official grants clear the port; arrows/minimap official only;
#    tapping a ? navigates first and opens the card only on arrival.
# ---------------------------------------------------------------------------
game = once(game,
    "    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<38;}))return false;",
    "    if((context.kind==='opportunity'||context.kind==='weather-opportunity')&&cityLabels.some(city=>{const w=polar(city.lat,city.lon);return Math.hypot(w.x-site.x,w.y-site.y)<38;}))return false;\n    if((context.kind==='grant'||context.kind==='contract')&&Number.isFinite(context.origin?.lat)&&Number.isFinite(context.origin?.lon)){const origin=polar(context.origin.lat,context.origin.lon);if(Math.hypot(origin.x-site.x,origin.y-site.y)<20)return false;}",
    'official grant port clearance')

game = once(game,
    "for(const target of researchTargets()){const w=polar(target.lat,target.lon),raw=project(w.x,w.y),dx=raw.x-c,dy=raw.y-c,d=Math.hypot(dx,dy),official=target.kind==='grant'||target.kind==='contract';",
    "for(const target of researchTargets().filter(target=>target.kind==='grant'||target.kind==='contract'||target.kind==='recovery')){const w=polar(target.lat,target.lon),raw=project(w.x,w.y),dx=raw.x-c,dy=raw.y-c,d=Math.hypot(dx,dy),official=true;",
    'minimap official targets only')
game = once(game,
    "targets=researchTargets().map(target=>({target,...researchTargetWorld(target)})).filter(item=>item.p.x<=35||item.p.x>=width-35||item.p.y<=95||item.p.y>=height-35)",
    "targets=researchTargets().filter(target=>target.kind==='grant'||target.kind==='contract'||target.kind==='recovery').map(target=>({target,...researchTargetWorld(target)})).filter(item=>item.p.x<=35||item.p.x>=width-35||item.p.y<=95||item.p.y>=height-35)",
    'official arrows only')

old_pointer_prefix = r'''  function handleMapPointer(clientX,clientY){const guidance=researchGuidanceAt(clientX,clientY);if(guidance){const target=researchTargets().find(item=>item.id===guidance.targetId);if(target){const item=researchTargetWorld(target);research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,target});}return;}const site=nearbyResearchTargetAt(clientX,clientY);if(site){research?.selectTarget?.(site.target.id);research?.openTarget?.(site.target.id,{distanceKm:site.distance,atSite:site.distance<=RESEARCH_INTERACTION_KM,target:site.target});return;}const portItem='''
new_pointer_prefix = r'''  function handleMapPointer(clientX,clientY){const guidance=researchGuidanceAt(clientX,clientY);if(guidance){const target=researchTargets().find(item=>item.id===guidance.targetId);if(target){const item=researchTargetWorld(target);if(item.distance<=RESEARCH_INTERACTION_KM){research?.selectTarget?.(target.id);research?.openTarget?.(target.id,{distanceKm:item.distance,atSite:true,target});}else navigateToResearchTarget(target);}return;}const site=nearbyResearchTargetAt(clientX,clientY);if(site){if(site.distance<=RESEARCH_INTERACTION_KM){research?.selectTarget?.(site.target.id);research?.openTarget?.(site.target.id,{distanceKm:site.distance,atSite:true,target:site.target});}else navigateToResearchTarget(site.target);return;}const portItem='''
game = once(game, old_pointer_prefix, new_pointer_prefix, 'tap question mark direct navigation')

# Replace the last explicitly cartoon-drawn NPC vessel photo with an existing photographic vessel asset.
game = rex(game, r"  const SMALL_PASSENGER_SVG='data:image/svg\+xml.*?;\n\n  const loadSprite", "  const SMALL_PASSENGER_SVG='assets/vessels/fishing-trawler.webp';\n\n  const loadSprite", 'passenger vessel photograph')

# ---------------------------------------------------------------------------
# 6. Clean playtest saves: every build bump erases all saves from older builds.
# ---------------------------------------------------------------------------
game = once(game, "const GAME_VERSION='expedition-22c-visuals',SAVE_VERSION=1;", "const GAME_VERSION='expedition-23n-clean-playtest',SAVE_VERSION=1;", 'game version')
game = once(game,
    "  const AUTO_NEW_KEY='arctic-research-start-new-v1';\n  let menuOpen=true,autosaveSuspended=false,autosaveTimer=0,lastResearchAnalytics=null;",
    "  const AUTO_NEW_KEY='arctic-research-start-new-v1';\n  const PLAYTEST_BUILD_KEY='arctic-research-playtest-build';\n  try{const previousBuild=localStorage.getItem(PLAYTEST_BUILD_KEY);if(previousBuild!==GAME_VERSION){Object.values(SAVE_KEYS).forEach(key=>localStorage.removeItem(key));localStorage.removeItem(AUTO_NEW_KEY);localStorage.setItem(PLAYTEST_BUILD_KEY,GAME_VERSION);}}catch(error){}\n  let menuOpen=true,autosaveSuspended=false,autosaveTimer=0,lastResearchAnalytics=null;",
    'playtest build save purge')
game = once(game,
    "const readSave=slot=>{try{const raw=localStorage.getItem(SAVE_KEYS[slot]);if(!raw)return null;const parsed=JSON.parse(raw);return parsed?.version===SAVE_VERSION?parsed:null;}catch(error){return null;}};",
    "const readSave=slot=>{try{const raw=localStorage.getItem(SAVE_KEYS[slot]);if(!raw)return null;const parsed=JSON.parse(raw);return parsed?.version===SAVE_VERSION&&parsed?.gameVersion===GAME_VERSION?parsed:null;}catch(error){return null;}};",
    'reject old-build saves')
game = once(game, "url.searchParams.set('build','23h');", "url.searchParams.set('build','23n');", 'new game build query')

# Cache bust both changing runtime files.
index = once(index, 'expedition.js?v=expedition-23m-research-program', 'expedition.js?v=expedition-23n-clean-playtest', 'expedition cache bust')
index = once(index, 'game.js?v=expedition-23m-research-program', 'game.js?v=expedition-23n-clean-playtest', 'game cache bust')

exp_path.write_text(exp)
game_path.write_text(game)
index_path.write_text(index)
print('p23n patch applied')
