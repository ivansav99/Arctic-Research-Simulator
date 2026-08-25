(() => {
  'use strict';

  const cash = value => new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0
  }).format(Math.round(value || 0));
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const clone = value => value == null ? value : JSON.parse(JSON.stringify(value));
  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
  const slug = value => String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const hash = text => {
    let value = 2166136261;
    for (const char of String(text)) {
      value ^= char.charCodeAt(0);
      value = Math.imul(value, 16777619);
    }
    return value >>> 0;
  };
  const seeded = seed => {
    let value = hash(seed) || 1;
    return () => {
      value ^= value << 13;
      value ^= value >>> 17;
      value ^= value << 5;
      return (value >>> 0) / 4294967296;
    };
  };

  const IVAN_PHOTO_ATLAS='assets/equipment/ivan-photo-atlas.webp';
  const atlasMedia=(col,row,alt)=>({src:IVAN_PHOTO_ATLAS,atlas:[col,row],alt,credit:'Field photograph supplied for Arctic Research Simulator',source:''});
  const MEDIA = {
    local: {src:'assets/research/arctic-small-boat.webp', alt:'Small survey boat operating in Arctic water', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    river: {src:'assets/research/river-plume.webp', alt:'Sediment-rich Mackenzie River water entering the Beaufort Sea', credit:'NASA Earth Observatory / Lauren Dauphin', source:'https://earthobservatory.nasa.gov/images/146813/breakup-along-the-mackenzie-river'},
    ice: {src:'assets/research/sea-ice-station.webp', alt:'Researchers working on Arctic sea ice', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    aerial: {src:'assets/research/aerial-survey.webp', alt:'Aerial survey over Arctic sea ice', credit:'NOAA Fisheries', source:'https://www.fisheries.noaa.gov/feature-story/us-and-russian-scientists-partner-study-polar-bear-and-seal-populations'},
    storm: {src:'assets/research/storm-sea.webp', alt:'Research vessel in high Arctic seas', credit:'NOAA', source:'https://response.restoration.noaa.gov/evaluating-oil-spill-response-technologies-arctic'},
    xbt: {src:'assets/equipment/xbt-kit.webp', alt:'XBT probe case and shipboard launcher equipment', credit:'ARS photo archive', source:''},
    argo: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Argo%20float%20deployed%20from%20research%20vessel.jpg', alt:'Argo profiling float being deployed from a research vessel', credit:'NOAA GOMO / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Argo_float_deployed_from_research_vessel.jpg'},
    hydrophone: {src:'assets/equipment/hydrophone-array-face-free.webp', alt:'Hydrophone array and cable equipment laid out for deployment', credit:'ARS photo archive', source:''},
    sonobuoy: {src:'assets/equipment/sonobuoy-pack.webp', alt:'Scientific sonobuoy pack prepared for deployment', credit:'ARS photo archive', source:''},
    ctd: {src:'assets/equipment/ctd-rosette.webp', alt:'CTD rosette aboard NOAA Ship Okeanos Explorer', credit:'NOAA Ocean Exploration', source:'https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-ex2101-features-ctd-media-rosette/'},
    rov: {src:'assets/equipment/work-rov.webp', alt:'ROV Deep Discoverer on a research vessel deck', credit:'NOAA Ocean Exploration', source:'https://oceanexplorer.noaa.gov/multimedia/rov-deep-discoverer/'},
    radar: {src:'assets/equipment/cloud-radar.webp', alt:'NOAA W-band research radar', credit:'Ken Moran / NOAA CIRES', source:'https://psl.noaa.gov/technology/w-band-radar/'},
    balloon: {src:'assets/equipment/radiosonde.webp', alt:'Weather balloon carrying atmospheric instruments', credit:'NOAA NCEI', source:'https://www.ncei.noaa.gov/products/weather-balloon'},
    aerostat: {src:'assets/equipment/aerostat-face-free.webp', alt:'Tethered research aerostat and field system', credit:'ARS photo archive', source:''},
    drone: {src:'assets/equipment/large-drone-face-free.webp', alt:'Large fixed-wing scientific UAS prepared for shipboard operations', credit:'ARS photo archive', source:''},
    drifter: {src:'assets/equipment/surface-drifter-pair.webp', alt:'Surface drifter instruments prepared for deployment', credit:'ARS photo archive', source:''},
    starlink: {src:'assets/equipment/starlink-terminal.webp', alt:'Flat satellite terminal installed for shipboard communications', credit:'ARS photo archive', source:''},
    winch: {src:'assets/equipment/medium-science-winch.webp', alt:'Medium oceanographic science winch', credit:'ARS photo archive', source:''},
    hullSensor: {src:'assets/equipment/hull-echosounder-sensor.webp', alt:'Hull echosounder transducer and sensor hardware', credit:'ARS photo archive', source:''},
    serviceTools: {src:'assets/equipment/coastal-service-toolkit.webp', alt:'Coastal service tools and deck hardware', credit:'ARS photo archive', source:''},
    handheldWater: {src:'assets/equipment/handheld-water-lab.webp', alt:'Portable multiparameter water-quality field laboratory', credit:'ARS photo archive', source:''},
    iceCorer: {src:'assets/equipment/ice-corer-auger.webp', alt:'Sea-ice corer and powered auger equipment', credit:'ARS photo archive', source:''},
    miniRov: {src:'assets/equipment/mini-rov.webp', alt:'Compact observation ROV for shallow-water surveys', credit:'ARS photo archive', source:''},
    shallowAdcp: {src:'assets/equipment/shallow-adcp.webp', alt:'Portable shallow-water ADCP system', credit:'ARS photo archive', source:''},
    shelfAdcp: {src:'assets/equipment/shelf-adcp.webp', alt:'Vessel-mounted shelf ADCP system', credit:'ARS photo archive', source:''},
    deepAdcp: {src:'assets/equipment/deep-adcp.webp', alt:'Deep-water current profiling ADCP system', credit:'ARS photo archive', source:''},
    ek80: {src:'assets/equipment/ek80-scientific-echosounder.webp', alt:'Scientific echosounder system used for fisheries and water-column acoustics', credit:'Scientific echosounder equipment photograph', source:''},
    cameraTelephoto: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Sigma%20150-500mm%2002.jpg', alt:'DSLR camera fitted with an extra-large telephoto lens', credit:'Gerwin Sturm / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Sigma_150-500mm_02.jpg'},
    bongoDetailed: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Projet%20BioCotEs%20-%20Filet%20%C3%A0%20plancton%20%22Bongo%22%20%28Ifremer%2000810-92149%29.jpg', alt:'Paired Bongo plankton net system', credit:'Ifremer / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Projet_BioCotEs_-_Filet_%C3%A0_plancton_%22Bongo%22_(Ifremer_00810-92149).jpg'},
    ednaKit: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Using%20the%20peristaltic%20pump%20to%20pass%20water%20through%20a%20filter.%20%28d88f9813-525c-4630-95ff-ff011ade9a36%29.png', alt:'Peristaltic pump and filtration apparatus for eDNA water sampling', credit:'National Park Service / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Using_the_peristaltic_pump_to_pass_water_through_a_filter._(d88f9813-525c-4630-95ff-ff011ade9a36).png'},
    fieldKit: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Arthropod%20field%20collection%20kit.png', alt:'Scientific field collection kit with GPS, notebook and sample containers', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Arthropod_field_collection_kit.png'},
    shoreDebris: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Collected%20Beach%20Litter%20at%20Scabbacombe%20Sands.jpg', alt:'Marine debris collected during a shoreline survey', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Collected_Beach_Litter_at_Scabbacombe_Sands.jpg'},
    shallowCorer: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Giant-box-corer%20hg.jpg', alt:'Medium-duty box corer being deployed from a research vessel', credit:'Hannes Grobe / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Giant-box-corer_hg.jpg'},
    surfaceNet: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/A%20simple%20plankton%20net.jpg', alt:'Simple scientific plankton net', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:A_simple_plankton_net.jpg'},
    verticalNet: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/A%20simple%20plankton%20net.jpg', alt:'Scientific plankton net prepared for vertical sampling', credit:'Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:A_simple_plankton_net.jpg'},
    bongoNet: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Projet%20BioCotEs%20-%20Filet%20%C3%A0%20plancton%20%22Bongo%22%20%28Ifremer%2000810-92149%29.jpg', alt:'Paired Bongo plankton net system', credit:'Ifremer / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Projet_BioCotEs_-_Filet_%C3%A0_plancton_%22Bongo%22_(Ifremer_00810-92149).jpg'},
    sedimentCorer: {src:'assets/equipment/box-corer.webp', alt:'Deep box corer and bottom-camera package for heavy research-vessel operations', credit:'ARS photo archive', source:''},
    coastalAFrame: {src:'assets/equipment/coastal-a-frame.webp', alt:'Oceanographic stern A-frame and deployment hardware', credit:'ARS photo archive', source:''},
    deepCtd: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/CTD%20rosette%20%28OOI%20401%29.jpg', alt:'Full-size oceanographic CTD rosette', credit:'Ocean Observatories Initiative / NSF / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:CTD_rosette_(OOI_401).jpg'},
    iceHoleSampling: {src:'https://commons.wikimedia.org/wiki/Special:FilePath/Researchers%20using%20Niskin%20bottle%20to%20collect%20water%20sample%20%C2%B7%20DN-SD-01-00282.JPEG', alt:'Water-sampling instrument lowered through a drilled sea-ice hole', credit:'U.S. Navy / Wikimedia Commons', source:'https://commons.wikimedia.org/wiki/File:Researchers_using_Niskin_bottle_to_collect_water_sample_%C2%B7_DN-SD-01-00282.JPEG'},
    swiftBuoy: atlasMedia(0,0,'SWIFT buoy instrument cropped to the instrument itself'),
    mooringAdcp: atlasMedia(1,0,'ADCP prepared as a mooring component'),
    mooringCtd: atlasMedia(2,0,'CTD sensor array element used as a mooring component'),
    sedimentTrap: atlasMedia(3,0,'Sediment trap used in an oceanographic mooring'),
    mammothMik: atlasMedia(0,1,'Heavy-duty Mammoth MIK plankton net'),
    heavyMultinet: atlasMedia(1,1,'Heavy-duty depth-stratified Multinet'),
    heavyWinch: atlasMedia(2,1,'Heavy-duty oceanographic science winch'),
    mooringAnchor: atlasMedia(3,1,'Bottom anchor for an oceanographic mooring'),
    acousticRelease: atlasMedia(0,2,'Acoustic release used in an oceanographic mooring'),
    oceanOptics: atlasMedia(1,2,'Ocean optics profiling instrument'),
    livePlankton: atlasMedia(2,2,'Live plankton samples collected during field work'),
    vessel: {src:'assets/vessels/noaa-rv-brown.webp', alt:'NOAA Ship Ronald H. Brown underway', credit:'Wade Blake / NOAA', source:'https://oceanexplorer.noaa.gov/technology/noaa-ship-brown/'}
  };

  const SPECIALTIES = [
    {id:'physical', name:'Physical Oceanographer', icon:'≈', description:'Water masses, currents, CTD casts and turbulence.'},
    {id:'biogeochemistry', name:'Marine Biogeochemist', icon:'◌', description:'Nutrients, carbon, oxygen and water chemistry.'},
    {id:'sea-ice-physics', name:'Sea-Ice Physicist', icon:'◇', description:'Ice thickness, snow, melt ponds and ice mechanics.'},
    {id:'sea-ice-ecology', name:'Sea-Ice Ecologist', icon:'❄', description:'Ice algae, microbes and under-ice ecosystems.'},
    {id:'plankton', name:'Plankton Ecologist', icon:'✣', description:'Plankton imaging, nets and food-web structure.'},
    {id:'fisheries', name:'Fisheries Scientist', icon:'◁', description:'Fish acoustics, trawls and population surveys.'},
    {id:'marine-mammals', name:'Marine Mammal Biologist', icon:'◒', description:'Visual surveys, population ecology and passive acoustics.'},
    {id:'naval-acoustics', name:'Underwater Acoustician', icon:'∿', description:'Sound-speed structure, propagation, scattering and ambient noise.'},
    {id:'benthic', name:'Benthic Ecologist / Geologist', icon:'△', description:'Seafloor imagery, sediment and deep benthos.'},
    {id:'atmosphere', name:'Atmospheric Scientist', icon:'☁', description:'Fog, clouds, aerosols, storms and soundings.'},
    {id:'moorings', name:'Mooring Engineer', icon:'⚓', description:'Autonomous buoys, moorings and time-series systems.'},
    {id:'coastal-oceanography', name:'Coastal Oceanographer', icon:'≋', description:'Nearshore circulation, tides and river plumes.'},
    {id:'coastal-ecology', name:'Coastal Ecologist', icon:'⌁', description:'Estuaries, kelp, shore communities and eDNA.'}
  ];
  const specialtyById = Object.fromEntries(SPECIALTIES.map(item => [item.id, item]));

  const CAREERS = {
    grad: {id:'grad', name:'Graduate Student', short:'Grad Student', level:1, minCitations:0, salary:300, quality:.88, productivity:1, color:'#8ef0cf', next:'postdoc', promotion:{papers:2,citations:100}},
    postdoc: {id:'postdoc', name:'Postdoctoral Researcher', short:'Postdoc', level:2, minCitations:100, salary:800, quality:1.12, productivity:1.35, color:'#7dd3fc', next:'professor', promotion:{papers:0,citations:2000}},
    professor: {id:'professor', name:'Professor', short:'Professor', level:3, minCitations:1000, salary:1900, quality:1.42, productivity:1.8, color:'#f6d365', next:null, promotion:null}
  };
  const SLOT_TYPES = ['light', 'medium', 'heavy'];
  const EQUIPMENT_RESALE_RATE = 1;
  const VESSEL_TRADE_IN_RATE = 1;
  const RELOCATION_COST = 10000;
  const RESEARCH_INTERACTION_KM = 10;
  // StoreKit-ready consumable funding packs. The web build uses a simulated
  // purchase adapter; an iOS wrapper can provide window.ArcticResearchIAP.purchase(productId).
  const PRIVATE_FUNDING_PACKAGES = [
    {id:'funding-1m',productId:'ars.private_funding.1m',gameCash:1000000,price:'$0.99',label:'$1 MILLION'},
    {id:'funding-10m',productId:'ars.private_funding.10m',gameCash:10000000,price:'$4.99',label:'$10 MILLION'},
    {id:'funding-50m',productId:'ars.private_funding.50m',gameCash:50000000,price:'$9.99',label:'$50 MILLION'}
  ];
  const PAPER_LEVELS = [
    {id:'local',threshold:100,next:1000,label:'Letter',journal:'Svalbard Science Bulletin',award:30000,initialCitations:10,potential:90},
    {id:'national',threshold:1000,next:10000,label:'Article',journal:'Nordic Polar Research Review',award:350000,initialCitations:130,potential:1400},
    {id:'international',threshold:10000,next:null,label:'Book',journal:'Arctic Research Monographs',award:4000000,initialCitations:1700,potential:18000}
  ];
  const PUBLISH_MIN = PAPER_LEVELS[0].threshold;
  const DATA_GAUGE_MAX = PAPER_LEVELS.at(-1).threshold;
  const DATA_SCALE_BY_VESSEL = {fishing:3,trawler:5,coastal:12,global:40,icebreaker:100,nuclear:180};

  const VESSEL_IMAGES = {
    coastal:'assets/vessels/coastal-rv.webp',
    global:'assets/vessels/noaa-rv-brown.webp',
    icebreaker:'https://commons.wikimedia.org/wiki/Special:FilePath/Polarforskningssekretariatet%20IMG%202551%20Oden%20Hjorthfjellet.jpg',
    nuclear:'assets/vessels/nuclear-icebreaker.webp'
  };
  const VESSELS = {
    fishing: {
      id:'fishing', name:'Small Fishing Vessel', shipName:'F/V Isfjord', className:'LOCAL CLASS', price:0, marketPrice:120000, berths:3, image:'assets/vessels/fishing-vessel.webp',
      slots:{light:3, medium:0, heavy:0}, helidecks:0, minZoom:1.8,
      supplyCapacity:75, fuelCapacity:5000, foodCapacity:400, fuelEnduranceDays:5, foodEnduranceDays:5,
      cruiseKnots:8, maxKnots:9, fuelUnitCost:1.15, foodUnitCost:4,
      standardEquipment:['hull-echosounder'], upgradeGate:null,
      description:'A compact local platform with a hull echosounder, three berths and three light portable science mounts.'
    },
    trawler: {
      id:'trawler', name:'Larger Fishing Trawler', shipName:'F/V Nordlys', className:'EXPEDITION TRAWLER', price:350000, berths:5, image:'assets/vessels/fishing-trawler.webp',
      slots:{light:8, medium:0, heavy:0}, helidecks:0, minZoom:1.45,
      supplyCapacity:140, fuelCapacity:15000, foodCapacity:1200, fuelEnduranceDays:8, foodEnduranceDays:8,
      cruiseKnots:9.5, maxKnots:11, fuelUnitCost:1.14, foodUnitCost:3.9,
      standardEquipment:['hull-echosounder'], upgradeGate:null,
      description:'A working trawler refit with five berths, expanded stores and eight light-equipment deck positions.'
    },
    coastal: {
      id:'coastal', name:'Coastal-Class Research Vessel', shipName:'R/V Kongsfjord', className:'COASTAL CLASS', price:750000, berths:10, image:VESSEL_IMAGES.coastal,
      slots:{light:8, medium:5, heavy:0}, helidecks:0, minZoom:.7,
      supplyCapacity:250, fuelCapacity:50000, foodCapacity:4000, fuelEnduranceDays:15, foodEnduranceDays:15,
      cruiseKnots:11, maxKnots:13, fuelUnitCost:1.12, foodUnitCost:3.8,
      standardEquipment:['hull-echosounder'], upgradeGate:{career:'postdoc', count:1, label:'Chief Scientist must be a postdoc'},
      description:'A regional vessel with ten berths and room for several medium winches, labs and communications systems.'
    },
    global: {
      id:'global', name:'Global-Class Research Vessel', shipName:'R/V Aurora', className:'GLOBAL CLASS', price:8000000, berths:20, image:VESSEL_IMAGES.global,
      slots:{light:12, medium:10, heavy:6}, helidecks:0, minZoom:.7,
      supplyCapacity:600, fuelCapacity:500000, foodCapacity:40000, fuelEnduranceDays:30, foodEnduranceDays:30,
      cruiseKnots:14, maxKnots:17, fuelUnitCost:1.08, foodUnitCost:3.5,
      standardEquipment:['hull-echosounder'], upgradeGate:{career:'professor', count:1, label:'Chief Scientist must be a professor'},
      description:'An ocean-going multidisciplinary platform with deep winches, cranes and the first heavy science positions.'
    },
    icebreaker: {
      id:'icebreaker', name:'Icebreaker', shipName:'R/V Borealis', className:'ICEBREAKER', price:60000000, berths:30, image:VESSEL_IMAGES.icebreaker,
      slots:{light:16, medium:14, heavy:10}, helidecks:1, minZoom:.7,
      supplyCapacity:950, fuelCapacity:5000000, foodCapacity:400000, fuelEnduranceDays:60, foodEnduranceDays:60,
      cruiseKnots:12, maxKnots:15, fuelUnitCost:1.04, foodUnitCost:3.2, crackedIceFactor:.2,
      standardEquipment:['hull-echosounder'], upgradeGate:{career:'professor', count:1, label:'Chief Scientist must be a professor'},
      description:'A reinforced science deck, one helideck and enough handling gear for sustained operations in fractured pack.'
    },
    nuclear: {
      id:'nuclear', name:'Nuclear Icebreaker', shipName:'NS Polarnaya Zvezda', className:'NUCLEAR ICEBREAKER', price:650000000, berths:40, image:VESSEL_IMAGES.nuclear,
      slots:{light:20, medium:18, heavy:16}, helidecks:2, minZoom:.7,
      supplyCapacity:1500, fuelCapacity:null, foodCapacity:4000000, fuelEnduranceDays:Infinity, foodEnduranceDays:180,
      nuclearFuel:true, cruiseKnots:18, maxKnots:21, foodUnitCost:3, crackedIceFactor:.36,
      standardEquipment:['hull-echosounder'], upgradeGate:{career:'professor', count:1, label:'Chief Scientist must be a professor'},
      description:'Forty berths, two helidecks, the largest modular science deck and reactor-powered propulsion.'
    }
  };

  const equipment = item => item;
  const EQUIPMENT = {
    'hull-echosounder': equipment({id:'hull-echosounder', name:'Hull Echosounder', price:0, slotType:'light', slots:0, tier:1, builtIn:true, deckTag:'SONAR', media:MEDIA.hullSensor, specialties:['physical','coastal-oceanography','fisheries'], crew:[], description:'Compact through-hull acoustic sensor for safe navigation and modest harbor bathymetry.', specs:['Single acoustic transducer beneath the hull','Continuous depth beneath keel','Standard on every vessel class']}),
    'field-optics': equipment({id:'field-optics', name:'Field Optics & Camera Kit', price:2500, slotType:'light', slots:1, tier:1, specialties:['coastal-ecology','marine-mammals'], crew:[], description:'Binoculars, stabilized camera and shoreline counting kit.', specs:['Visual wildlife transects','Geotagged photography','Light portable case'], media:MEDIA.cameraTelephoto}),
    'service-toolkit': equipment({id:'service-toolkit', name:'Coastal Service Toolkit', price:4000, slotType:'light', slots:1, tier:1, specialties:['moorings','atmosphere'], crew:[], description:'Calibration standards, standard boat hand tools, deck hook, spare shackles and portable diagnostics.', specs:['Buoy retrieval and servicing','Coastal weather-station checks','No powered winch'], media:MEDIA.serviceTools}),
    'portable-water-lab': equipment({id:'portable-water-lab', name:'Portable Water Lab', price:12000, slotType:'light', slots:1, tier:1, specialties:['coastal-oceanography','physical','biogeochemistry','coastal-ecology'], crew:[{specialties:['coastal-oceanography','physical','biogeochemistry','coastal-ecology'], minCareer:'grad', count:1}], description:'Rugged handheld multiparameter meter, probe cable, sample bottles and basic nearshore chemistry.', specs:['Temperature, salinity, oxygen, pH and turbidity','Handheld sonde cable for shallow profiles','Graduate-level operator'], media:MEDIA.handheldWater}),
    'surface-plankton-net': equipment({id:'surface-plankton-net', name:'Surface Plankton Ring Net', price:6500, slotType:'light', slots:1, tier:1, specialties:['plankton','coastal-ecology'], crew:[{specialties:['plankton','coastal-ecology'], minCareer:'grad', count:1}], description:'Compact hand-towed net for surface and upper-water-column plankton collections.', specs:['63–200 µm interchangeable mesh','Surface and short oblique tows','Biomass, microscopy and university-return samples'], media:MEDIA.surfaceNet}),
    'bongo-plankton-net': equipment({id:'bongo-plankton-net', name:'Bongo Plankton Net', price:11000, slotType:'light', slots:1, tier:1, specialties:['plankton','fisheries'], crew:[{specialties:['plankton','fisheries'], minCareer:'grad', count:1}], description:'Paired small nets for replicated zooplankton and ichthyoplankton sampling.', specs:['Two simultaneous mesh sizes','Upper 50–100 m oblique tows','Predator-prey and larval-fish samples'], media:MEDIA.bongoDetailed}),
    'vertical-plankton-net': equipment({id:'vertical-plankton-net', name:'Vertical Plankton Net', price:8500, slotType:'light', slots:1, tier:1, specialties:['plankton','coastal-ecology'], crew:[{specialties:['plankton','coastal-ecology'], minCareer:'grad', count:1}], description:'Weighted closing net for simple vertical hauls in sheltered fjords.', specs:['Depth-stratified vertical hauls','Simple hand-line deployment','Graduate training instrument'], media:MEDIA.verticalNet}),
    'portable-fluorometer': equipment({id:'portable-fluorometer', name:'Portable Chlorophyll Fluorometer', price:14500, slotType:'light', slots:1, tier:1, specialties:['plankton','biogeochemistry'], crew:[{specialties:['plankton','biogeochemistry'], minCareer:'grad', count:1}], description:'Rugged fluorometer for chlorophyll and bloom-intensity measurements alongside net sampling.', specs:['Chlorophyll fluorescence','Surface mapping and bottle samples','Pairs with light plankton nets'], media:MEDIA.handheldWater}),
    'edna-field-kit': equipment({id:'edna-field-kit', name:'Portable eDNA Filtration Kit', price:18000, slotType:'light', slots:1, tier:1, specialties:['plankton','coastal-ecology','biogeochemistry'], crew:[{specialties:['plankton','coastal-ecology','biogeochemistry'], minCareer:'grad', count:1}], description:'Portable sterile filtration and preservation gear for DNA, bacterial and viral analysis back at the university.', specs:['Sterile filters and blanks','Cold-preserved sample cartridges','Analysis completed ashore'], media:MEDIA.ednaKit}),
    'all-sky-camera': equipment({id:'all-sky-camera', name:'All-Sky Aurora Camera', price:16000, slotType:'light', slots:1, tier:1, specialties:['atmosphere'], crew:[{specialties:['atmosphere'], minCareer:'grad', count:1}], description:'Low-light all-sky camera and magnetometer logger for auroral arcs and geomagnetic-event observations.', specs:['Wide-angle low-light imager','Time-synchronized magnetometer','Graduate-level aurora monitoring'], media:MEDIA.aerial}),
    'shallow-adcp': equipment({id:'shallow-adcp', name:'1200 kHz Shallow-Water ADCP', price:28000, slotType:'light', slots:1, tier:1, deckTag:'ADCP', specialties:['coastal-oceanography','physical'], crew:[{specialties:['coastal-oceanography','physical'], minCareer:'grad', count:1}], description:'Portable high-frequency four-beam current profiler for harbors, rivers and very shallow fjords.', specs:['1200 kHz current profiles','Best for roughly the upper 20 m','Small-boat frame and bottom tracking'], media:MEDIA.shallowAdcp}),
    'mini-rov': equipment({id:'mini-rov', name:'Compact Observation ROV', price:24000, slotType:'light', slots:2, tier:1, deckTag:'MINI ROV', specialties:['coastal-ecology','benthic'], crew:[], description:'Small tethered camera vehicle for kelp, dock, seabed and shallow-habitat observations.', specs:['150 m tether reel','HD camera and scaling lasers','Any graduate scientist can operate it'], media:MEDIA.miniRov}),
    'shallow-coring-kit': equipment({id:'shallow-coring-kit', name:'Coastal Box Corer & Sample Kit', price:85000, slotType:'medium', slots:2, tier:2, deckTag:'BOX CORER', requiresEquipment:['coastal-a-frame'], specialties:['benthic','coastal-ecology'], crew:[{specialties:['benthic','coastal-ecology'], minCareer:'postdoc', count:1}], description:'Medium-duty box corer and sectioning kit for undisturbed fjord and shelf sediment.', specs:['Undisturbed box sediment sample','Coastal A-frame deployment','Postdoc-level deck lead'], media:MEDIA.shallowCorer}),
    'ice-core-system': equipment({id:'ice-core-system', name:'Sea-Ice Field System', price:32000, slotType:'light', slots:2, tier:1, specialties:['sea-ice-physics','sea-ice-ecology'], crew:[{specialties:['sea-ice-physics','sea-ice-ecology'], minCareer:'grad', count:1}], description:'Portable ice corer, powered auger, snow probe, light sensors and field safety equipment.', specs:['Visible corer and auger hardware','Thickness transects, ice cores and snow depth','Floe safety gear'], media:MEDIA.iceCorer}),
    'xbt-pack': equipment({id:'xbt-pack', name:'XBT Probe Case', price:9000, consumable:true, units:6, maxUnits:24, tier:1, specialties:['physical','naval-acoustics'], description:'Six expendable temperature probes for underway profiles and sound-speed correction.', specs:['6 ship-launched profiles','Temperature versus depth','One probe consumed per mission'], media:MEDIA.xbt}),
    'surface-drifters': equipment({id:'surface-drifters', name:'Surface Drifter Pair', price:16000, consumable:true, units:2, maxUnits:12, tier:1, specialties:['physical','coastal-oceanography','moorings'], description:'Two satellite-tracked buoys for surface current, wave and temperature observations.', specs:['2 autonomous drifters','Telemetry for several weeks','May strand or leave the chart'], media:MEDIA.swiftBuoy}),
    'radiosonde-pack': equipment({id:'radiosonde-pack', name:'Radiosonde Flight Pack', price:7500, consumable:true, units:6, maxUnits:24, tier:1, specialties:['atmosphere'], description:'Six expendable weather balloons and sensor packages for vertical profiles.', specs:['Pressure, temperature, humidity and wind','One flight consumed per launch','Useful during storms, rain, snow or fog'], media:MEDIA.balloon}),
    'sonobuoy-pack': equipment({id:'sonobuoy-pack', name:'Scientific Sonobuoy Pack', price:18000, consumable:true, units:4, maxUnits:16, tier:1, specialties:['marine-mammals','naval-acoustics'], description:'Four short-lived passive-acoustic buoys for whale calls and propagation experiments.', specs:['4 expendable listening buoys','VHF telemetry to vessel','Hours of listening per deployment'], media:MEDIA.sonobuoy}),
    'starlink-terminal': equipment({id:'starlink-terminal', name:'Starlink Science Terminal', price:45000, slotType:'medium', slots:1, tier:2, deckTag:'SATCOM', specialties:[], crew:[], description:'High-throughput satellite communications for collaboration, backups and manuscript work.', specs:['+12% manuscript acceptance chance','25% shorter submission cooldown','Faster remote collaboration'], media:MEDIA.starlink}),
    'medium-winch': equipment({id:'medium-winch', name:'Medium Science Winch', price:65000, slotType:'medium', slots:1, tier:2, deckTag:'WINCH', specialties:['physical','plankton','fisheries'], crew:[{specialties:['physical','plankton','fisheries','coastal-oceanography'], minCareer:'postdoc', count:1}], description:'Powered conducting winch for nets, profilers and modest towed payloads.', specs:['1,500 m steel instrument wire','Medium payload rating','Postdoc-level operator'], media:MEDIA.winch}),
    'aux-medium-winch': equipment({id:'aux-medium-winch', name:'Auxiliary Medium Winch', price:72000, slotType:'medium', slots:1, tier:2, deckTag:'AUX WINCH', specialties:['physical','plankton','fisheries','moorings'], crew:[{specialties:['physical','plankton','fisheries','moorings'], minCareer:'postdoc', count:1}], description:'A second independently operated winch that lets larger ships keep another payload rigged and ready.', specs:['Independent 1,200 m steel wire','Adds parallel payload-handling capacity','Postdoc-level operator'], media:MEDIA.winch}),
    'coastal-suite': equipment({id:'coastal-suite', name:'600 kHz Coastal ADCP Suite', price:55000, slotType:'medium', slots:1, tier:2, deckTag:'COASTAL ADCP', specialties:['coastal-oceanography'], crew:[{specialties:['coastal-oceanography'], minCareer:'postdoc', count:1}], description:'Coastal current profiler with turbidity, salinity and river-plume sensors.', specs:['600 kHz current profiles','Coastal range around 70 m','Nearshore navigation and plume package'], media:MEDIA.shallowAdcp}),
    'shelf-adcp': equipment({id:'shelf-adcp', name:'300 kHz Shelf ADCP', price:98000, slotType:'medium', slots:1, tier:2, deckTag:'SHELF ADCP', specialties:['physical','coastal-oceanography'], crew:[{specialties:['physical','coastal-oceanography'], minCareer:'postdoc', count:1}], description:'Vessel-mounted current profiler for long sections across fjords and continental shelves.', specs:['300 kHz broadband profiling','Shelf-depth range around 160 m','Underway bottom tracking'], media:MEDIA.shelfAdcp}),
    'coastal-a-frame': equipment({id:'coastal-a-frame', name:'Coastal Stern A-Frame', price:85000, slotType:'medium', slots:2, tier:2, deckTag:'A-FRAME', specialties:['moorings','coastal-oceanography','benthic'], crew:[{specialties:['moorings','coastal-oceanography','benthic'], minCareer:'postdoc', count:1}], description:'Compact powered stern frame for shallow moorings, small corers and instrument packages.', specs:['Available from coastal-class vessels','Shallow over-the-stern deployment','Postdoc-level deck lead'], media:MEDIA.coastalAFrame}),
    'shallow-mooring-kit': equipment({id:'shallow-mooring-kit', name:'Recoverable Shallow Mooring Kit', price:120000, slotType:'medium', slots:1, tier:2, deckTag:'MOORING', deploymentAsset:true, requiresEquipment:['coastal-a-frame'], specialties:['moorings','coastal-oceanography'], crew:[{specialties:['moorings','coastal-oceanography'], minCareer:'postdoc', count:1}], description:'Reusable coastal mooring with current meter, temperature loggers and acoustic release.', specs:['Deployment followed by later recovery','7-30 day coastal time series','Requires Coastal Stern A-Frame'], media:MEDIA.mooringAdcp}),
    'edna-lab': equipment({id:'edna-lab', name:'eDNA & Coastal Ecology Lab', price:65000, slotType:'medium', slots:1, tier:2, specialties:['coastal-ecology','sea-ice-ecology'], crew:[{specialties:['coastal-ecology','sea-ice-ecology'], minCareer:'postdoc', count:1}], description:'Filtration and preservation system for biodiversity surveys.', specs:['Sterile filtration bench','Field blanks and freezer','Postdoc-level lab lead'], media:MEDIA.ednaKit}),
    'plankton-winch': equipment({id:'plankton-winch', name:'Plankton Net & Imaging Winch', price:45000, slotType:'medium', slots:1, tier:2, specialties:['plankton'], crew:[{specialties:['plankton'], minCareer:'postdoc', count:1}], description:'Collects and images plankton through the upper water column.', specs:['Multiple net mesh sizes','Imaging flow cell','Medium winch included'], media:MEDIA.heavyMultinet}),
    'fish-acoustics': equipment({id:'fish-acoustics', name:'EK80 Scientific Echosounder & Trawl', price:110000, slotType:'medium', slots:2, tier:2, deckTag:'EK80', specialties:['fisheries'], crew:[{specialties:['fisheries'], minCareer:'postdoc', count:1}], description:'Portable multi-frequency scientific echosounder for fish counting, species discrimination and targeted scientific trawls.', specs:['38 and 200 kHz split-beam channels','Small-boat and vessel survey operation','Postdoc fisheries survey lead'], media:MEDIA.ek80}),
    'towed-hydrophone': equipment({id:'towed-hydrophone', name:'Towed Hydrophone Array', price:125000, slotType:'medium', slots:2, tier:2, deckTag:'ACOUSTICS', specialties:['marine-mammals','naval-acoustics'], crew:[{specialties:['marine-mammals','naval-acoustics'], minCareer:'postdoc', count:1}], description:'Multi-element passive-acoustic array for marine mammals, ambient noise and source localization.', specs:['Broadband passive acoustics','300 m tow cable','Marine mammal or acoustics postdoc'], media:MEDIA.hydrophone}),
    'atmospheric-suite': equipment({id:'atmospheric-suite', name:'Atmospheric Observatory', price:90000, slotType:'medium', slots:1, tier:2, specialties:['atmosphere'], crew:[{specialties:['atmosphere'], minCareer:'postdoc', count:1}], description:'Cloud, aerosol, precipitation and surface-flux instruments.', specs:['Aerosol and precipitation sensors','Air-sea flux station','Postdoc atmospheric lead'], media:MEDIA.radar}),
    'profiling-aerostat': equipment({id:'profiling-aerostat', name:'Tethered Profiling Aerostat', price:180000, slotType:'medium', slots:2, tier:2, deckTag:'AEROSTAT', specialties:['atmosphere'], crew:[{specialties:['atmosphere'], minCareer:'postdoc', count:1}], description:'A compact blimp and instrument tether for boundary-layer profiles and overhead imaging.', specs:['Temperature, humidity and aerosol payload','Local aerial imagery in fog','Grounded by high wind or severe icing'], media:MEDIA.aerostat}),
    'argo-float': equipment({id:'argo-float', name:'Polar Profiling Float', price:38000, consumable:true, units:1, maxUnits:4, tier:2, specialties:['physical','biogeochemistry'], description:'One autonomous profiling float that cycles through the upper 2,000 m and telemeters data.', specs:['One multi-year autonomous float','10-day profiling cycle','Ice-sensing polar firmware'], media:MEDIA.argo}),
    'ice-tethered-profiler': equipment({id:'ice-tethered-profiler', name:'Ice-Tethered Profiler Package', price:165000, consumable:true, units:1, maxUnits:3, tier:2, specialties:['physical','sea-ice-physics','moorings'], description:'One autonomous ice-floe surface package, tether and crawling ocean profiler.', specs:['Repeated under-ice profiles','Moves with its host floe','Possible early loss when ice fails'], media:MEDIA.ice}),
    'heavy-winch': equipment({id:'heavy-winch', name:'Deep-Ocean Traction Winch', price:420000, slotType:'heavy', slots:2, tier:3, deckTag:'DEEP WINCH', specialties:['physical','moorings','benthic'], crew:[{specialties:['physical','moorings','benthic'], minCareer:'professor', count:1},{specialties:['physical','moorings','benthic'], minCareer:'grad', count:1}], description:'Full-ocean-depth wire handling for CTDs, corers and mooring components.', specs:['Full-ocean-depth wire','Active tension monitoring','Professor plus science assistant'], media:MEDIA.heavyWinch}),
    'deep-adcp': equipment({id:'deep-adcp', name:'75 kHz Deep-Water ADCP', price:390000, slotType:'heavy', slots:1, tier:3, deckTag:'DEEP ADCP', specialties:['physical'], crew:[{specialties:['physical'], minCareer:'professor', count:1},{specialties:['physical','coastal-oceanography'], minCareer:'grad', count:1}], description:'Low-frequency vessel-mounted current profiler for basin and boundary-current sections.', specs:['75 kHz deep current profiling','Long-range underway sections','Professor plus science assistant'], media:MEDIA.deepAdcp}),
    'heavy-deck-crane': equipment({id:'heavy-deck-crane', name:'Heavy Science Deck Crane', price:360000, slotType:'heavy', slots:2, tier:3, deckTag:'SCIENCE CRANE', specialties:['moorings','benthic','physical'], crew:[{specialties:['moorings','benthic','physical'], minCareer:'professor', count:1}], description:'A knuckle-boom crane for moving large mooring packages, vehicles and container laboratories around the working deck.', specs:['High-capacity articulated boom','Expands simultaneous payload staging','Heavy-slot vessel and professor lead'], media:MEDIA.vessel}),
    'stern-a-frame': equipment({id:'stern-a-frame', name:'Heavy Stern A-Frame', price:520000, slotType:'heavy', slots:2, tier:3, deckTag:'A-FRAME', specialties:['moorings','benthic'], crew:[{specialties:['moorings','benthic'], minCareer:'professor', count:1}], description:'Over-the-stern launch and recovery frame for deep moorings and large packages.', specs:['Large overboard payloads','Mooring buoy handling','Heavy-slot vessel required'], media:MEDIA.coastalAFrame}),
    'ctd-rosette': equipment({id:'ctd-rosette', name:'Deep CTD Rosette', price:320000, slotType:'heavy', slots:1, tier:3, deckTag:'CTD', requiresEquipment:['heavy-winch'], specialties:['physical','biogeochemistry'], crew:[{specialties:['physical','biogeochemistry'], minCareer:'professor', count:1},{specialties:['physical','biogeochemistry'], minCareer:'grad', count:1}], description:'Full-depth profiling rosette with water-sampling bottles.', specs:['Conductivity, temperature and pressure','12 Niskin bottles','Needs deep winch and professor'], media:MEDIA.deepCtd}),
    'deep-mooring-payload': equipment({id:'deep-mooring-payload', name:'Composite Deep Mooring Payload', price:720000, slotType:'heavy', slots:2, tier:3, deckTag:'MOORING', requiresEquipment:['heavy-winch','stern-a-frame'], specialties:['moorings','physical','naval-acoustics'], crew:[{specialties:['moorings'], minCareer:'professor', count:1},{specialties:['moorings','physical','naval-acoustics'], minCareer:'postdoc', count:1},{specialties:['moorings','physical','naval-acoustics'], minCareer:'grad', count:1}], description:'Configurable long-term line with CTDs, current meter, hydrophone, ice-draft sonar and acoustic release.', specs:['Deployment then later recovery','Full data only after recovery','Composite physical/acoustic payload'], media:MEDIA.mooringCtd}),
    'box-corer': equipment({id:'box-corer', name:'Deep Box Corer & Bottom Camera', price:420000, slotType:'heavy', slots:2, tier:3, deckTag:'CORER', requiresEquipment:['heavy-winch','stern-a-frame'], specialties:['benthic'], crew:[{specialties:['benthic'], minCareer:'professor', count:1},{specialties:['benthic'], minCareer:'grad', count:1}], description:'Samples deep sediment and returns bottom imagery.', specs:['Visible open-jaw box corer','Undisturbed sediment box','Deep winch and A-frame required'], media:MEDIA.sedimentCorer}),
    'work-rov': equipment({id:'work-rov', name:'Work-Class ROV System', price:1800000, slotType:'heavy', slots:3, tier:3, deckTag:'ROV', requiresEquipment:['stern-a-frame'], specialties:['benthic','physical'], crew:[{specialties:['benthic'], minCareer:'professor', count:1},{specialties:['physical'], minCareer:'professor', count:1},{specialties:['benthic','physical'], minCareer:'grad', count:1}], description:'Deep remotely operated vehicle with imaging, sensors and manipulators.', specs:['6,000 m class operations','HD video and sample collection','Two professors plus assistant'], media:MEDIA.rov}),
    'research-radar': equipment({id:'research-radar', name:'W-Band Research Radar', price:950000, slotType:'heavy', slots:2, tier:3, deckTag:'CLOUD RADAR', specialties:['atmosphere'], crew:[{specialties:['atmosphere'], minCareer:'professor', count:1},{specialties:['atmosphere'], minCareer:'grad', count:1}], description:'Stabilized 95 GHz radar for fog, mist, cloud droplets and precipitation structure.', specs:['Cloud reflectivity and Doppler velocity','Continuous fog and cloud profiles','Adds 12 km instrument visibility'], media:MEDIA.radar}),
    'large-drone': equipment({id:'large-drone', name:'Long-Range Fixed-Wing Survey UAS', price:650000, slotType:'heavy', slots:1, tier:3, deckTag:'FIXED-WING UAS', minVesselClass:'global', specialties:['atmosphere','sea-ice-physics','marine-mammals'], crew:[{specialties:['atmosphere','sea-ice-physics','marine-mammals'], minCareer:'professor', count:1}], description:'Large deck-launched fixed-wing research aircraft for long ice, wildlife and atmospheric corridor surveys.', specs:['Global-class R/V or larger','Deck launch and recovery cradle','Thermal, visible and mapping payloads','Extends useful fog visibility by 10 km'], media:MEDIA.drone}),
    'manned-helicopter': equipment({id:'manned-helicopter', name:'Research Helicopter Detachment', price:3800000, slotType:'heavy', slots:2, tier:3, deckTag:'HELICOPTER', helideckUse:1, specialties:['atmosphere','sea-ice-physics','marine-mammals','physical'], crew:[{specialties:['atmosphere','sea-ice-physics','marine-mammals','physical'], minCareer:'professor', count:1}], description:'Crewed helicopter and science payload package for wide-area aerial work and AXCTD drops.', specs:['Requires one helideck','Wide-area surveys and AXCTD deployment','Extends useful fog visibility by 18 km'], media:MEDIA.aerial}),
    'axctd-pack': equipment({id:'axctd-pack', name:'AXCTD Air-Drop Case', price:55000, consumable:true, units:6, maxUnits:24, tier:3, requiresEquipment:['manned-helicopter'], specialties:['physical','naval-acoustics'], description:'Six airborne expendable conductivity-temperature-depth probes.', specs:['6 air-dropped profiles','Requires the research helicopter detachment','Temperature, salinity and sound speed'], media:MEDIA.xbt})
  };

  const mission = item => item;
  const TEMPLATES = [
    mission({id:'harbor-soundings', tier:'local', title:'Harbor Sounding Lines', shortTitle:'HARBOR SOUNDINGS', specialties:['coastal-oceanography','physical'], equipment:['hull-echosounder'], data:7, reward:4800, supplies:1, workHours:18, minDistance:6, distanceRange:18, media:MEDIA.hullSensor, description:'Run careful echosounder lines across a small harbor and clean the depth fixes for a local chart correction.', steps:['Plan closely spaced harbor lines','Check sounder draft and clock','Run the first sounding line','Repeat the cross-lines','Clean depth fixes and deliver the plot']}),
    mission({id:'nostoc-delivery', tier:'local', title:'Deliver Instruments to Petuniabukta', shortTitle:'NOSTOC DELIVERY', anyScientist:true, equipment:[], data:4, reward:4200, supplies:1, workHours:10, fixedDestination:{lat:78.69,lon:16.42}, onlyPorts:['longyearbyen'], unlockAfter:1, coastal:true, stationDelivery:true, media:MEDIA.local, description:'Carry calibration cases and environmental loggers to the Czech Arctic Research Station field base in Petuniabukta.', steps:['Check the station cargo manifest','Protect the logger cases from spray','Cross Isfjorden to Petuniabukta','Transfer equipment at the shore landing','Return the signed custody sheet']}),
    mission({id:'sverdrup-delivery', tier:'local', title:'Supply Ny-Ålesund Sverdrup Station', shortTitle:'SVERDRUP SUPPLY', anyScientist:true, equipment:[], data:5, reward:5800, supplies:1, workHours:14, fixedDestination:{lat:78.93,lon:11.62}, onlyPorts:['longyearbyen'], unlockAfter:2, coastal:true, stationDelivery:true, media:MEDIA.ice, description:'Deliver a protected instrument case to the Norwegian Polar Institute team at Ny-Ålesund Research Station – Sverdrup in Kongsfjorden.', steps:['Verify the Sverdrup delivery note','Secure the instrument case','Navigate to Kongsfjorden','Transfer cargo at Ny-Ålesund quay','Obtain the station receipt']}),
    mission({id:'hornsund-delivery', tier:'local', title:'Hornsund Monitoring Equipment Run', shortTitle:'HORNSUND RUN', anyScientist:true, equipment:[], data:6, reward:8200, supplies:2, workHours:18, fixedDestination:{lat:76.99,lon:15.12}, onlyPorts:['longyearbyen'], unlockAfter:5, coastal:true, stationDelivery:true, media:MEDIA.storm, description:'Carry replacement meteorological and geophysical instruments to the Polish Polar Station in Isbjørnhamna, Hornsund.', steps:['Inventory the Hornsund cargo','Weatherproof the sensor crates','Make the southbound coastal passage','Transfer crates in Isbjørnhamna','Close the station logistics record']}),
    mission({id:'shellfish-run', tier:'local', title:'Shellfish Sample Errand', shortTitle:'SHELLFISH RUN', anyScientist:true, equipment:[], data:3, reward:2200, supplies:1, workHours:8, minDistance:5, distanceRange:15, media:MEDIA.local, description:'Pick up a carefully labeled shellfish sample for a professor in Longyearbyen. It is humble work, but it pays.', steps:['Confirm the sample list','Reach the sheltered collection cove','Collect and label specimens','Keep the cooler at temperature','Deliver the sample log']}),
    mission({id:'duck-count', tier:'local', title:'Spitsbergen Duck Count', shortTitle:'DUCK COUNT', anyScientist:true, equipment:['field-optics'], data:4, reward:3000, supplies:1, workHours:12, minDistance:8, distanceRange:25, coastal:true, transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:6,icebreaker:7,nuclear:8}, stationSpacingKm:4, media:MEDIA.cameraTelephoto, description:'Count summer waterfowl along a short Spitsbergen shoreline transect using stabilized field optics.', steps:['Review identification sheet','Set a slow shoreline track','Count birds by transect segment','Photograph uncertain groups','Submit the observation sheet']}),
    mission({id:'buoy-retrieval', tier:'local', title:'Retrieve a Service Buoy', shortTitle:'BUOY PICKUP', anyScientist:true, equipment:['service-toolkit'], data:5, reward:3900, supplies:1, workHours:13, minDistance:10, distanceRange:30, media:MEDIA.drifter, description:'Bring a small coastal buoy back to Longyearbyen so the university workshop can replace its batteries.', steps:['Load the recovery hook','Locate the buoy signal','Approach from downwind','Bring the buoy aboard','Secure it for the port return']}),
    mission({id:'met-station-check', tier:'local', title:'Coastal Met Station Check', shortTitle:'MET STATION', anyScientist:true, equipment:['service-toolkit'], data:4, reward:3400, supplies:1, workHours:10, minDistance:9, distanceRange:26, coastal:true, media:MEDIA.storm, description:'Check the calibration flag and photograph icing at a small automated weather station on the far side of the fjord.', steps:['Review last telemetry packet','Reach the station landing','Inspect sensors and mast','Run a reference check','Transmit the service note']}),
    mission({id:'shoreline-litter', tier:'local', shore:true, title:'Shoreline Debris Transect', shortTitle:'SHORE TRANSECT', anyScientist:true, equipment:[], data:4, reward:2800, supplies:1, workHours:11, minDistance:7, distanceRange:22, media:MEDIA.shoreDebris, description:'Photograph and classify debris along a short beach transect for a graduate methods class.', steps:['Mark the transect endpoints','Photograph the wrack line','Classify visible debris','Record substrate and weather','Upload the field sheet']}),
    mission({id:'glacier-photo', tier:'local', glacier:true, shore:true, title:'Repeat Glacier Photograph', shortTitle:'GLACIER PHOTO', anyScientist:true, equipment:[], data:4, reward:3100, supplies:1, workHours:9, minDistance:12, distanceRange:28, media:MEDIA.ice, description:'Repeat a fixed-point photograph of a glacier front and record the exact viewing geometry.', steps:['Load last year’s reference','Navigate to the photo station','Match bearing and framing','Record weather and ice','Archive the repeat image']}),
    mission({id:'tide-gauge', tier:'local', shore:true, title:'Tide-Gauge Service Check', shortTitle:'TIDE GAUGE', anyScientist:true, equipment:['service-toolkit'], data:4, reward:3300, supplies:1, workHours:10, minDistance:7, distanceRange:24, coastal:true, media:MEDIA.local, description:'Visit a small fjord tide gauge, compare its staff reading and report whether the logger clock has drifted.', steps:['Download the last service sheet','Read the tide staff','Check logger time and battery','Photograph the installation','Submit the calibration note']}),
    mission({id:'sample-cooler', tier:'local', title:'Deliver Archived Sample Coolers', shortTitle:'COOLER DELIVERY', anyScientist:true, equipment:[], data:3, reward:2500, supplies:1, workHours:8, minDistance:6, distanceRange:20, media:MEDIA.local, description:'Carry labeled sample coolers between two fjord field teams and keep the temperature log intact.', steps:['Verify labels and custody form','Load the insulated coolers','Make the sheltered fjord crossing','Check arrival temperature','Obtain the receiving signature']}),
    mission({id:'camera-recovery', tier:'local', glacier:true, shore:true, title:'Recover a Shore Time-Lapse Camera', shortTitle:'CAMERA RECOVERY', anyScientist:true, equipment:[], data:5, reward:3900, supplies:1, workHours:12, minDistance:9, distanceRange:27, media:MEDIA.ice, description:'Retrieve a small time-lapse camera overlooking a glacier front before its battery is exhausted.', steps:['Confirm the camera coordinates','Land at the marked shoreline','Inspect and power down the unit','Copy the memory card','Secure the camera aboard']}),
    mission({id:'fjord-secchi', tier:'local', title:'Fjord Water-Clarity Transect', shortTitle:'WATER CLARITY', anyScientist:true, equipment:[], data:5, reward:3600, supplies:1, workHours:14, minDistance:8, distanceRange:30, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:6,icebreaker:7,nuclear:8}, stationSpacingKm:4, media:MEDIA.river, description:'Lower a simple Secchi disk at several sheltered stations and record water color for a student monitoring program.', steps:['Mark the short station line','Lower the disk on the shaded side','Record disappearance depth','Repeat the observation','Deliver the station sheet']}),
    mission({id:'harbor-buoys', tier:'local', title:'Harbor Marker Inventory', shortTitle:'MARKER CHECK', anyScientist:true, equipment:['service-toolkit'], data:4, reward:3000, supplies:1, workHours:11, minDistance:5, distanceRange:22, coastal:true, media:MEDIA.drifter, description:'Check which small navigation and research markers survived the last storm and photograph any damaged fittings.', steps:['Load the marker inventory','Follow the harbor circuit','Record each marker position','Photograph damage or icing','Return the updated inventory']}),
    mission({id:'shallow-water-samples', tier:'local', title:'Shallow Fjord Water Samples', shortTitle:'WATER SAMPLES', anyScientist:true, equipment:[], data:6, reward:5200, supplies:3, workHours:16, minDistance:7, distanceRange:28, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:3,trawler:3,coastal:4,global:5,icebreaker:6,nuclear:7}, stationSpacingKm:4, media:MEDIA.handheldWater, description:'Collect carefully labeled shallow-water bottles for later chemical and biological analysis at the university.', steps:['Prepare clean sample bottles','Record the nearshore station','Collect surface and near-bottom water','Label and chill every bottle','Return the custody sheet']}),
    mission({id:'kelp-mini-rov', tier:'local', shore:true, title:'Kelp Forest Mini-ROV Survey', shortTitle:'KELP ROV', anyScientist:true, equipment:['mini-rov'], data:13, reward:12800, supplies:3, workHours:24, minDistance:8, distanceRange:34, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:6,icebreaker:7,nuclear:8}, stationSpacingKm:3, media:MEDIA.miniRov, description:'Fly a compact observation ROV over several shallow kelp patches and deliver a geotagged habitat video survey.', steps:['Test camera, tether and lasers','Launch at the first kelp patch','Fly the habitat video line','Record cover and visible animals','Recover and back up the footage']}),
    mission({id:'terrestrial-team', tier:'local', shore:true, terrestrial:true, title:'Deliver Terrestrial Ecologists to a Remote Coast', shortTitle:'FIELD TEAM', anyScientist:true, equipment:[], berthReserve:2, data:7, reward:9200, supplies:2, workHours:12, minDistance:12, distanceRange:42, coastal:true, fjordPreferred:true, missionMode:'staged-deploy', recoveryAfterDays:5, recoveryTitle:'Pick Up the Terrestrial Ecology Team', recoveryShortTitle:'FIELD PICKUP', recoveryDescription:'The shore team has completed its tundra transects. Return to the landing and bring the ecologists, samples and field notes safely aboard.', media:MEDIA.local, description:'Land a small terrestrial ecology team at a remote Svalbard coast, then return several days later to collect them and their samples.', steps:['Review the shore-party plan','Load tents and sample cases','Approach the remote landing','Put the team safely ashore','Confirm the scheduled pickup']}),
    mission({id:'fjord-plankton-ring', tier:'local', title:'Fjord Surface Plankton Biomass Tow', shortTitle:'PLANKTON TOW', specialties:['plankton','coastal-ecology'], equipment:['surface-plankton-net'], data:9, reward:9000, supplies:2, workHours:15, minDistance:4, distanceRange:22, coastal:true, fjordPreferred:true, media:MEDIA.local, description:'Tow a small ring net through a sheltered fjord, measure simple biomass and preserve representative samples for the university.', steps:['Choose a sheltered tow line','Rinse and rig the ring net','Tow at constant speed','Estimate wet biomass','Preserve and label the university sample']}),
    mission({id:'fjord-bongo-predation', tier:'local', title:'Fjord Predator–Prey Bongo-Net Survey', shortTitle:'BONGO SURVEY', specialties:['plankton','fisheries'], equipment:['bongo-plankton-net'], data:13, reward:14000, supplies:3, workHours:22, minDistance:5, distanceRange:28, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:2,trawler:3,coastal:4,global:5,icebreaker:6,nuclear:7}, stationSpacingKm:3, media:MEDIA.bongoDetailed, description:'Use paired mesh sizes to compare zooplankton and larval-fish communities along a fjord transect.', steps:['Rig both bongo cod ends','Record tow depth and speed','Tow the paired nets','Split and preserve samples','Log predator-prey size classes']}),
    mission({id:'fjord-vertical-plankton', tier:'local', title:'Vertical Fjord Plankton Profile', shortTitle:'VERTICAL NET', specialties:['plankton','coastal-ecology'], equipment:['vertical-plankton-net'], data:11, reward:11500, supplies:2, workHours:18, minDistance:4, distanceRange:24, coastal:true, fjordPreferred:true, media:MEDIA.local, description:'Make repeated vertical net hauls in a protected fjord to compare near-surface and deeper plankton communities.', steps:['Measure local water depth','Lower the weighted net','Haul at constant speed','Rinse organisms into the cod end','Preserve the depth-profile samples']}),
    mission({id:'fjord-edna-plankton', tier:'local', title:'Plankton eDNA Sample Collection', shortTitle:'eDNA PLANKTON', specialties:['plankton','coastal-ecology','biogeochemistry'], equipment:['surface-plankton-net','edna-field-kit'], data:15, reward:17000, supplies:4, workHours:23, minDistance:5, distanceRange:28, coastal:true, fjordPreferred:true, media:MEDIA.ednaKit, description:'Collect a plankton tow and sterile filtered-water samples for bacterial, viral and community DNA analysis back at the university.', steps:['Prepare sterile filtration blanks','Collect the plankton tow','Filter replicate water samples','Preserve filters and subsamples','Seal the university return shipment']}),
    mission({id:'fjord-bloom-fluoro', tier:'local', title:'Fjord Bloom Mapping & Net Tow', shortTitle:'BLOOM MAPPING', specialties:['plankton','biogeochemistry'], equipment:['surface-plankton-net','portable-fluorometer'], data:14, reward:15500, supplies:3, workHours:20, minDistance:5, distanceRange:30, coastal:true, fjordPreferred:true, media:MEDIA.local, description:'Map chlorophyll fluorescence through a fjord and collect a small net tow at the strongest bloom signal.', steps:['Zero the fluorometer','Map surface fluorescence','Select the bloom maximum','Tow the ring net','Preserve microscopy samples']}),
    mission({id:'postdoc-depth-plankton', title:'Depth-Stratified Plankton Food-Web Survey', shortTitle:'DEEP PLANKTON', specialties:['plankton'], equipment:['medium-winch','plankton-winch'], data:42, reward:52000, supplies:12, workHours:62, coastal:true, fjordPreferred:true, description:'A postdoctoral plankton program resolves vertical community structure, grazing pressure and predator-prey coupling through the fjord water column.', steps:['Calibrate the winch depth counter','Plan depth-stratified tows','Sample each target layer','Image and split subsamples','Build the vertical food-web profile']}),
    mission({id:'postdoc-edna-foodweb', title:'Plankton Metabarcoding & Microbial Food-Web Survey', shortTitle:'PLANKTON DNA', specialties:['plankton','coastal-ecology'], equipment:['plankton-winch','edna-lab'], data:48, reward:60000, supplies:14, workHours:68, coastal:true, fjordPreferred:true, description:'Combine depth-resolved plankton collections with eDNA filtration to resolve community composition from metazoans to bacteria and viruses.', steps:['Plan sterile station sequence','Collect depth-resolved plankton','Filter paired water samples','Preserve DNA and microscopy fractions','Complete chain-of-custody metadata']}),
    mission({id:'postdoc-frontogenesis',postdocOpportunity:true,title:'Fjord Frontogenesis & Turbulent Exchange Experiment',shortTitle:'FRONT DYNAMICS',specialties:['physical','coastal-oceanography'],equipment:['medium-winch','coastal-suite'],transect:true,stationCounts:{coastal:5,global:7,icebreaker:9,nuclear:11},stationSpacingKm:8,data:58,reward:76000,supplies:15,workHours:78,coastal:true,fjordPreferred:true,media:MEDIA.winch,description:'Resolve lateral density gradients, ageostrophic exchange and frontal sharpening across a rapidly evolving Arctic fjord front.',steps:['Map the frontal density gradient','Repeat velocity sections across the front','Profile stratification and shear','Resolve cross-front exchange','Synthesize the frontal energy budget']}),
    mission({id:'postdoc-acoustic-inversion',postdocOpportunity:true,title:'Coupled Acoustic Scattering & Plankton Community Inversion',shortTitle:'ACOUSTIC INVERSION',specialties:['fisheries','plankton'],equipment:['fish-acoustics','plankton-winch'],transect:true,stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10},stationSpacingKm:14,data:62,reward:82000,supplies:17,workHours:84,media:MEDIA.mammothMik,description:'Combine multi-frequency acoustic backscatter with depth-resolved net samples to invert scattering layers into biological size and community structure.',steps:['Calibrate the acoustic frequencies','Map vertically migrating scattering layers','Collect depth-matched net samples','Fit taxon-specific scattering models','Invert the section for community structure']}),
    mission({id:'postdoc-carbon-edna',postdocOpportunity:true,title:'Mesoscale Carbon Export & eDNA Coupling Survey',shortTitle:'CARBON COUPLING',specialties:['biogeochemistry','plankton','coastal-ecology'],equipment:['edna-lab','plankton-winch','portable-water-lab'],transect:true,stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10},stationSpacingKm:12,data:66,reward:88000,supplies:19,workHours:88,coastal:true,media:MEDIA.sedimentTrap,description:'Couple particulate export, hydrographic structure and metabarcoding across a mesoscale feature to identify the organisms driving carbon transfer.',steps:['Map the hydrographic feature','Collect depth-resolved water and plankton','Filter paired eDNA replicates','Quantify particle and biomass gradients','Assemble the coupled carbon-community section']}),
    mission({id:'postdoc-underice-biooptics',postdocOpportunity:true,title:'Under-Ice Bio-Optical Coupling Experiment',shortTitle:'UNDER-ICE OPTICS',specialties:['sea-ice-physics','sea-ice-ecology'],equipment:['ice-core-system','edna-lab'],data:60,reward:80000,supplies:18,workHours:82,iceAllowed:true,media:MEDIA.oceanOptics,description:'Link snow and ice structure to transmitted light, under-ice biological communities and eDNA across a drifting floe.',steps:['Survey snow and ice thickness','Measure transmitted spectral light','Collect stratified ice cores','Filter under-ice eDNA samples','Relate optical habitat to community structure']}),
    mission({id:'fjord-water', tier:'local', title:'Fjord Water Sample Transect', shortTitle:'FJORD WATER', specialties:['coastal-oceanography','physical','biogeochemistry'], equipment:['portable-water-lab'], data:11, reward:8500, supplies:3, workHours:22, minDistance:12, distanceRange:38, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:6,icebreaker:7,nuclear:8}, stationSpacingKm:5, media:MEDIA.handheldWater, description:'Collect temperature, salinity, oxygen and water samples across a fjord gradient with a handheld multiparameter sonde.', steps:['Lay out the fjord stations','Calibrate the handheld sonde','Profile the inner station','Collect outer-fjord bottles','Preserve samples and metadata']}),
    mission({id:'harbor-adcp', tier:'local', title:'Harbor Tidal-Current Transect', shortTitle:'SHALLOW ADCP', specialties:['coastal-oceanography','physical'], equipment:['shallow-adcp'], data:14, reward:13500, supplies:3, workHours:26, minDistance:7, distanceRange:34, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:4,trawler:5,coastal:6,global:7,icebreaker:8,nuclear:9}, stationSpacingKm:3, media:MEDIA.shallowAdcp, description:'Run a portable 1200 kHz ADCP through a tidal cycle to map shallow harbor and fjord currents.', steps:['Mount and align the ADCP','Run the first cross-channel line','Repeat near tidal reversal','Check bottom-track quality','Archive velocity sections']}),
    mission({id:'fjord-sediment', tier:'local', title:'Fjord Box-Corer Sediment Gradient', shortTitle:'BOX CORES', specialties:['benthic','coastal-ecology'], equipment:['shallow-coring-kit'], data:15, reward:14800, supplies:5, workHours:30, minDistance:9, distanceRange:34, coastal:true, fjordPreferred:true, transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:6,icebreaker:7,nuclear:8}, stationSpacingKm:4, media:MEDIA.shallowCorer, description:'Recover undisturbed sediment boxes from the inner fjord to the shelf and document the change in grain size and benthic material.', steps:['Prepare clean sample trays','Rig the coastal box corer','Recover an undisturbed sediment box','Section and label sediment','Clean the corer for the next station']}),
    mission({id:'xbt-transect', title:'Underway XBT Section', shortTitle:'XBT SECTION', specialties:['physical','naval-acoustics'], equipment:['xbt-pack'], consumables:['xbt-pack'], consumablePerStation:{'xbt-pack':1}, transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:7,icebreaker:9,nuclear:12}, stationSpacingKm:18, data:18, reward:18000, supplies:3, workHours:22, media:MEDIA.xbt, description:'Launch an expendable temperature probe at each numbered station and build a sound-speed-corrected upper-ocean section.', steps:['Inspect launcher and probe','Enter station position and metadata','Launch the XBT while underway','Check the temperature trace','Advance to the next section station']}),
    mission({id:'water-column', title:'Shelf Water-Column Section', shortTitle:'WATER COLUMN', specialties:['physical','biogeochemistry','coastal-oceanography'], equipment:['portable-water-lab'], transect:true, stationCounts:{fishing:3,trawler:4,coastal:5,global:7,icebreaker:9,nuclear:12}, stationSpacingKm:12, data:24, reward:24000, supplies:8, workHours:42, media:MEDIA.handheldWater, description:'Profile the upper shelf and collect a compact set of water samples along a numbered section.', steps:['Hold station and check weather','Calibrate the portable sonde','Lower bottles through the surface layer','Preserve samples and verify metadata','Advance to the next station']}),
    mission({id:'river-plume', title:'River Plume Transect', shortTitle:'RIVER PLUME', specialties:['coastal-oceanography'], equipment:['portable-water-lab','coastal-suite'], transect:true, stationCounts:{coastal:5,global:7,icebreaker:9,nuclear:11}, stationSpacingKm:7, data:28, reward:34000, supplies:9, workHours:48, media:MEDIA.river, coastal:true, fjordPreferred:true, description:'Measure salinity, temperature, currents and suspended material across a coastal freshwater plume.', steps:['Lay out the cross-plume transect','Calibrate salinity sensors','Sample the plume front','Repeat the nearshore station','Advance across the plume']}),
    mission({id:'shelf-profiler', title:'Shelf Profiler Section', shortTitle:'WINCH SECTION', specialties:['physical','coastal-oceanography'], equipment:['medium-winch','portable-water-lab'], transect:true, stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10}, stationSpacingKm:18, data:34, reward:44000, supplies:9, workHours:56, media:MEDIA.winch, description:'Use the medium science winch to repeat upper-ocean profiler casts across a shelf section.', steps:['Inspect the winch and steel wire','Rig the profiler and deck lead','Lower through the target layer','Recover and verify the cast','Advance to the next station']}),
    mission({id:'coastal-adcp', title:'Fjord-to-Shelf 600 kHz ADCP Transect', shortTitle:'COASTAL ADCP', specialties:['coastal-oceanography'], equipment:['coastal-suite'], transect:true, stationCounts:{coastal:5,global:7,icebreaker:9,nuclear:11}, stationSpacingKm:10, data:32, reward:41000, supplies:7, workHours:48, coastal:true, fjordPreferred:true, media:MEDIA.shallowAdcp, description:'Map the evolving current structure from a sheltered fjord mouth onto the shallow shelf.', steps:['Align the 600 kHz ADCP','Run the cross-channel line','Check bottom-track and heading','Repeat the outward leg','Archive the gridded current field']}),
    mission({id:'shelf-adcp-section', title:'Shelf-Break 300 kHz Current Section', shortTitle:'SHELF CURRENT', specialties:['physical','coastal-oceanography'], equipment:['shelf-adcp'], transect:true, stationCounts:{coastal:6,global:8,icebreaker:10,nuclear:13}, stationSpacingKm:24, data:42, reward:59000, supplies:8, workHours:64, media:MEDIA.shelfAdcp, description:'Run a long vessel-mounted ADCP section across the shelf break and resolve the boundary current.', steps:['Verify heading and transducer offsets','Start the numbered section','Monitor profiling range','Repeat the shelf-break crossing','Quality-control the velocity field']}),
    mission({id:'shallow-mooring-deploy', title:'Deploy a Shallow Coastal Mooring', shortTitle:'COASTAL MOORING', specialties:['moorings','coastal-oceanography'], equipment:['shallow-mooring-kit','coastal-a-frame'], data:38, reward:62000, supplies:10, workHours:54, missionMode:'mooring-deploy', recoveryAfterDays:14, coastal:true, media:MEDIA.mooringAdcp, description:'Deploy a recoverable coastal mooring for a short current and temperature time series, then return after two weeks.', steps:['Inspect releases and sensors','Rig the coastal A-frame','Stream the mooring line','Set the anchor on position','Range the release and log deployment']}),
    mission({id:'paired-hydrography', title:'Paired Plankton & Hydrography Section', shortTitle:'DUAL WINCH', specialties:['physical','plankton'], equipment:['medium-winch','aux-medium-winch','plankton-winch'], transect:true, stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10}, stationSpacingKm:16, data:48, reward:69000, supplies:14, workHours:72, media:MEDIA.winch, description:'Keep a profiler and plankton system rigged simultaneously to sample the same shelf feature efficiently.', steps:['Rig both independent winches','Profile the water column','Tow the plankton net','Match samples to hydrography','Advance with both systems ready']}),
    mission({id:'coastal-ecosystem', title:'Nearshore Biodiversity Survey', shortTitle:'COASTAL ECOLOGY', specialties:['coastal-ecology'], equipment:['edna-lab'], data:30, reward:36000, supplies:10, workHours:52, media:MEDIA.ednaKit, coastal:true, description:'Combine eDNA, shoreline observations and habitat samples in a nearshore ecosystem.', steps:['Document shoreline habitat','Prepare sterile filtration gear','Collect replicate eDNA samples','Preserve filters and field blanks','Complete the biodiversity log']}),
    mission({id:'ice-physics', title:'Drifting Ice-Floe Station', shortTitle:'ICE STATION', specialties:['sea-ice-physics','sea-ice-ecology'], equipment:['ice-core-system'], data:34, reward:42000, supplies:12, workHours:66, media:MEDIA.iceHoleSampling, iceAllowed:true, description:'Characterize sea ice, snow and the under-ice environment from a suitable floe.', steps:['Assess floe safety and drift','Lay out the ice transect','Drill thickness and snow stations','Collect ice cores and light readings','Return equipment and samples aboard']}),
    mission({id:'plankton-bloom', title:'Plankton Bloom Survey', shortTitle:'PLANKTON BLOOM', specialties:['plankton'], equipment:['plankton-winch'], data:34, reward:39000, supplies:10, workHours:54, media:MEDIA.livePlankton, description:'Sample a concentrated plankton feature and connect it to the surrounding water column.', steps:['Map fluorescence around the bloom','Prepare nets and imaging system','Tow through the target layer','Image and preserve subsamples','Clean the net and close the station']}),
    mission({id:'fish-school', title:'EK80 Arctic Fish Biomass Transect', shortTitle:'EK80 FISH', specialties:['fisheries'], equipment:['fish-acoustics'], transect:true, stationCounts:{coastal:5,global:7,icebreaker:9,nuclear:12}, stationSpacingKm:20, data:38, reward:47000, supplies:12, workHours:60, media:MEDIA.ek80, description:'Use multi-frequency EK80 acoustics to map and identify Arctic fish schools along a numbered biomass transect.', steps:['Calibrate the split-beam channels','Run the acoustic survey leg','Classify the target school','Sample a verification trawl','Advance to the next leg']}),
    mission({id:'ek80-discrimination', title:'Fish-Plankton Acoustic Discrimination', shortTitle:'EK80 SPECIES', specialties:['fisheries','plankton'], equipment:['fish-acoustics','plankton-winch'], transect:true, stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10}, stationSpacingKm:18, data:52, reward:68000, supplies:15, workHours:76, media:MEDIA.ek80, description:'Combine 38 and 200 kHz acoustic returns with net samples to distinguish fish from plankton layers.', steps:['Calibrate both EK80 frequencies','Map the scattering layers','Tow the verification net','Match catch to acoustic targets','Advance along the section']}),
    mission({id:'marine-mammal-acoustics', title:'Marine Mammal Acoustic Transect', shortTitle:'WHALE ACOUSTICS', specialties:['marine-mammals'], equipment:['towed-hydrophone'], transect:true, stationCounts:{coastal:4,global:6,icebreaker:8,nuclear:10}, stationSpacingKm:28, data:40, reward:52000, supplies:9, workHours:64, media:MEDIA.hydrophone, description:'Tow a hydrophone array through numbered listening legs to detect, classify and localize Arctic whale calls.', steps:['Quiet the ship and stream the array','Calibrate channels and GPS feed','Run the listening leg','Classify detections','Advance with the array streamed']}),
    mission({id:'sound-propagation', title:'Underwater Sound Propagation Trial', shortTitle:'SOUND SPEED', specialties:['naval-acoustics','physical'], equipment:['towed-hydrophone','xbt-pack'], consumables:['xbt-pack'], data:46, reward:68000, supplies:11, workHours:70, media:MEDIA.sonobuoy, description:'Pair acoustic receptions with a measured temperature profile to study Arctic propagation and scattering.', steps:['Establish the acoustic geometry','Deploy the receiver array','Launch an XBT profile','Run calibrated transmissions','Model propagation loss']}),
    mission({id:'drifter-deploy', title:'Autonomous Surface Drifter Study', shortTitle:'DRIFTER ARRAY', specialties:['physical','coastal-oceanography','moorings'], equipment:['surface-drifters'], consumables:['surface-drifters'], data:34, reward:46000, supplies:4, workHours:20, missionMode:'autonomous', deploymentDays:28, media:MEDIA.drifter, description:'Deploy a satellite drifter that will report currents and temperature until it leaves the region or expires.', steps:['Program the telemetry interval','Record the deployment metadata','Lower the drifter clear of the wake','Confirm the first satellite fix','Release the platform to the current']}),
    mission({id:'argo-deploy', title:'Polar Profiling Float Mission', shortTitle:'POLAR FLOAT', specialties:['physical','biogeochemistry'], equipment:['argo-float'], consumables:['argo-float'], data:54, reward:82000, supplies:5, workHours:28, missionMode:'autonomous', deploymentDays:50, media:MEDIA.argo, description:'Deploy an autonomous profiling float and receive a sequence of under-ice and open-water profiles.', steps:['Register the float metadata','Run final sensor checks','Program the polar mission','Deploy clear of the ship','Confirm the first telemetry']}),
    mission({id:'itp-deploy', title:'Ice-Tethered Profiler Deployment', shortTitle:'ICE PROFILER', specialties:['physical','sea-ice-physics','moorings'], equipment:['ice-tethered-profiler'], consumables:['ice-tethered-profiler'], data:62, reward:98000, supplies:10, workHours:52, missionMode:'autonomous', deploymentDays:65, media:MEDIA.ice, iceAllowed:true, description:'Install an autonomous profiler through a suitable floe and let it drift with the pack.', steps:['Select and survey a stable floe','Drill the deployment hole','Lower the weighted tether','Install and program the profiler','Confirm GPS and satellite telemetry']}),
    mission({id:'sonobuoy-survey', title:'Arctic Sonobuoy Listening Station', shortTitle:'SONOBUOY', specialties:['marine-mammals','naval-acoustics'], equipment:['sonobuoy-pack'], consumables:['sonobuoy-pack'], data:22, reward:26000, supplies:3, workHours:24, media:MEDIA.sonobuoy, description:'Deploy a short-lived passive acoustic buoy to localize whale calls and characterize ambient sound.', steps:['Program listening depth and channel','Deploy the sonobuoy','Acquire the VHF signal','Classify calls and noise','Close the expendable station']}),
    mission({id:'routine-sounding', title:'Routine Arctic Atmosphere Sounding', shortTitle:'RADIOSONDE', specialties:['atmosphere'], equipment:['radiosonde-pack'], consumables:['radiosonde-pack'], data:18, reward:22000, supplies:2, workHours:15, media:MEDIA.balloon, description:'Launch a routine radiosonde away from a major weather event to strengthen the expedition atmosphere record.', steps:['Log surface meteorology','Prepare the radiosonde','Launch clear of the vessel','Track the full ascent','Transmit the quality-controlled profile']}),
    mission({id:'deep-ctd', title:'Deep Arctic CTD Section', shortTitle:'DEEP CTD', specialties:['physical','biogeochemistry'], equipment:['ctd-rosette','heavy-winch'], transect:true, stationCounts:{global:4,icebreaker:6,nuclear:9}, stationSpacingKm:45, data:58, reward:88000, supplies:18, workHours:92, media:MEDIA.deepCtd, description:'Run full-depth rosette casts at numbered stations to resolve deep water masses and chemistry.', steps:['Position over the deep station','Test winch, sensors and bottles','Lower the rosette to full depth','Fire bottles on the upcast','Recover and advance to the next cast']}),
    mission({id:'deep-adcp-section', title:'Deep Boundary-Current ADCP Section', shortTitle:'DEEP CURRENT', specialties:['physical'], equipment:['deep-adcp'], transect:true, stationCounts:{global:6,icebreaker:9,nuclear:13}, stationSpacingKm:55, data:62, reward:98000, supplies:12, workHours:92, media:MEDIA.deepAdcp, description:'Use a low-frequency deep-water ADCP to resolve the velocity structure of an Arctic basin boundary current.', steps:['Verify deep-ADCP alignment','Begin the long section leg','Monitor range and interference','Cross the boundary current core','Quality-control the deep velocity field']}),
    mission({id:'seafloor', title:'Deep Ridge Sediment Station', shortTitle:'SEAFLOOR CORE', specialties:['benthic'], equipment:['box-corer','heavy-winch','stern-a-frame'], data:64, reward:112000, supplies:20, workHours:110, media:MEDIA.sedimentCorer, description:'Image the seafloor and recover sediment from a deep bathymetric feature.', steps:['Survey the bottom approach','Prepare box corer and camera','Lower to the deep seafloor','Recover and section the core','Catalogue imagery and sediment samples']}),
    mission({id:'rov-survey', title:'Deep-Sea ROV Transect', shortTitle:'ROV DIVE', specialties:['benthic','physical'], equipment:['work-rov','stern-a-frame'], transect:true, stationCounts:{global:3,icebreaker:4,nuclear:6}, stationSpacingKm:24, data:82, reward:185000, supplies:28, workHours:148, media:MEDIA.rov, description:'Pilot a work-class ROV across a connected series of deep Arctic seafloor sites.', steps:['Complete the dive safety brief','Launch and descend the ROV','Run the imaging transect','Collect targeted samples','Recover before the next dive']}),
    mission({id:'large-buoy-recovery', title:'Recover a Large Arctic Observatory Buoy', shortTitle:'BUOY RECOVERY', specialties:['moorings','physical'], equipment:['heavy-deck-crane','heavy-winch'], data:58, reward:106000, supplies:16, workHours:96, media:MEDIA.drifter, description:'Recover a large autonomous observatory and its submerged instrument train using the heavy science crane.', steps:['Establish contact with the buoy','Secure the lifting pendant','Recover the submerged line','Crane the observatory aboard','Download and inventory all sensors']}),
    mission({id:'mooring-deploy', title:'Deploy Long-Term Arctic Mooring', shortTitle:'MOORING DEPLOY', specialties:['moorings','physical','naval-acoustics'], equipment:['deep-mooring-payload','heavy-winch','stern-a-frame'], data:78, reward:155000, supplies:24, workHours:132, missionMode:'mooring-deploy', recoveryAfterDays:70, recoveryAfterDaysByVessel:{global:70,icebreaker:180,nuclear:365}, media:MEDIA.mooringAnchor, description:'Deploy a composite physical and acoustic mooring. The full time series and contract value arrive only after a later recovery.', steps:['Inspect releases and payload stack','Stream the instrument line astern','Lower flotation and sensors','Drop the anchor on position','Range the release and log deployment']}),
    mission({id:'cloud-radar', title:'Shipborne Cloud Radar Program', shortTitle:'CLOUD RADAR', specialties:['atmosphere'], equipment:['research-radar'], data:58, reward:92000, supplies:12, workHours:96, media:MEDIA.radar, description:'Operate stabilized W-band radar through a cloud transition to resolve droplets, snow and vertical motion.', steps:['Level and stabilize the radar','Record surface flux conditions','Acquire the cloud transition','Check Doppler and attenuation','Archive calibrated radar moments']}),
    mission({id:'aerostat-profile', title:'Tethered Aerostat Profile', shortTitle:'AEROSTAT', specialties:['atmosphere'], equipment:['profiling-aerostat'], data:40, reward:58000, supplies:8, workHours:58, media:MEDIA.aerostat, description:'Raise a tethered blimp through the Arctic boundary layer for meteorology, aerosols and overhead imagery.', steps:['Check wind and icing limits','Prepare tether and payload','Climb through profile levels','Hold at the inversion top','Recover and inspect the aerostat']}),
    mission({id:'routine-atmosphere', title:'Shipborne Atmosphere Observatory Day', shortTitle:'ATMOSPHERE', specialties:['atmosphere'], equipment:['atmospheric-suite'], data:34, reward:46000, supplies:6, workHours:44, media:MEDIA.radar, description:'Run a coordinated clear-weather day of aerosol, precipitation and surface-flux observations.', steps:['Zero and inspect the sensors','Record the air-sea flux station','Sample aerosol size spectra','Check precipitation channels','Archive the coordinated day']}),
    mission({id:'starlink-collaboration', title:'Real-Time Forecast Assimilation', shortTitle:'LIVE FORECAST', specialties:['atmosphere','sea-ice-physics','physical'], equipment:['starlink-terminal'], anywhere:true, data:18, reward:26000, supplies:2, workHours:18, media:MEDIA.starlink, description:'Stream live observations to shore-side collaborators and assimilate them into a rapid Arctic forecast while still at sea.', steps:['Open the secure science link','Package recent observations','Stream data to the forecast team','Review the updated forecast','Archive the collaboration record']}),
    mission({id:'aerial-wildlife', title:'Aerial Ice & Wildlife Survey', shortTitle:'AERIAL SURVEY', specialties:['marine-mammals','sea-ice-physics'], equipment:['large-drone'], transect:true, stationCounts:{global:4,icebreaker:5,nuclear:8}, stationSpacingKm:45, data:52, reward:84000, supplies:10, workHours:84, media:MEDIA.drone, description:'Fly thermal and visible cameras across connected ice-habitat corridors to map wildlife and surface conditions.', steps:['File the survey corridor','Check aircraft and payload','Launch from the deck cradle','Fly the thermal-image leg','Recover to the deck system']}),
    mission({id:'drone-ice-edge', title:'Long-Range Drone Ice-Edge Reconnaissance', shortTitle:'ICE RECON', specialties:['sea-ice-physics','atmosphere'], equipment:['large-drone'], transect:true, stationCounts:{global:4,icebreaker:5,nuclear:9}, stationSpacingKm:55, data:56, reward:91000, supplies:9, workHours:78, iceAllowed:true, media:MEDIA.drone, description:'Map leads, ridging and low-cloud structure along a long ice-edge corridor with a deck-launched drone.', steps:['Plan the ice-edge flight','Inspect airframe and sensors','Launch from the deck cradle','Map leads and cloud base','Recover and mosaic the imagery']}),
    mission({id:'helicopter-axctd', title:'Helicopter AXCTD Section', shortTitle:'AIR-DROP CTD', specialties:['physical','naval-acoustics'], equipment:['manned-helicopter','axctd-pack'], consumables:['axctd-pack'], consumablePerStation:{'axctd-pack':1}, transect:true, stationCounts:{icebreaker:6,nuclear:12}, stationSpacingKm:70, data:72, reward:132000, supplies:12, workHours:98, media:MEDIA.aerial, description:'Use a research helicopter to drop a wide-area numbered section of expendable temperature and salinity probes.', steps:['Brief flight and science crews','Load and verify AXCTD probes','Fly to the numbered station','Drop and receive the probe','Continue or recover the aircraft']}),
    mission({id:'helicopter-field-team', title:'Remote Ice-Camp Team Deployment', shortTitle:'ICE CAMP', specialties:['sea-ice-physics','atmosphere'], equipment:['manned-helicopter'], berthReserve:2, data:48, reward:98000, supplies:14, workHours:54, missionMode:'staged-deploy', recoveryAfterDays:30, recoveryTitle:'Recover the Remote Ice-Camp Team', recoveryShortTitle:'ICE CAMP PICKUP', recoveryDescription:'The remote team has completed its month-long ice and atmosphere program. Return by helicopter and recover the scientists, samples and autonomous recorders.', iceAllowed:true, media:MEDIA.aerial, description:'Fly a small field team and instrument cases to a remote ice camp, then return a month later for recovery.', steps:['Brief flight and camp teams','Load people and instrument cases','Fly to the selected floe','Establish the remote camp','Confirm the recovery window']}),
    mission({id:'basic-fog-log', weather:'fog', anywhere:true, anyScientist:true, title:'Event: Fog Visibility Log', shortTitle:'FOG LOG', equipment:[], data:8, reward:9000, supplies:1, workHours:6, media:MEDIA.storm, description:'Any scientist can document visibility, sea state and surface conditions during this fog event.', steps:['Record visibility every ten minutes','Log sea state and wind','Photograph the horizon reference','Note condensation and icing','Archive the event log']}),
    mission({id:'basic-wind-watch', weather:'high-wind', anywhere:true, anyScientist:true, title:'Event: Gale Observation Watch', shortTitle:'GALE WATCH', equipment:[], data:10, reward:11000, supplies:1, workHours:7, media:MEDIA.storm, description:'Any scientist can keep a structured watch of wind, waves and ship response during the gale.', steps:['Log wind and gusts','Estimate wave state','Record ship response','Photograph spray and whitecaps','Archive the event watch']}),
    mission({id:'basic-snow-watch', weather:'snow', anywhere:true, anyScientist:true, title:'Event: Snowfall Observation Log', shortTitle:'SNOW LOG', equipment:[], data:9, reward:10000, supplies:1, workHours:6, media:MEDIA.storm, description:'Any scientist can document snowfall intensity, visibility and accumulation during the event.', steps:['Log snowfall intensity','Record visibility','Measure deck accumulation','Photograph snow habit','Archive the event log']}),
    mission({id:'basic-rain-watch', weather:'rain', anywhere:true, anyScientist:true, title:'Event: Arctic Rain Observation', shortTitle:'RAIN LOG', equipment:[], data:9, reward:10000, supplies:1, workHours:6, media:MEDIA.storm, description:'Any scientist can record rain rate, surface temperature and sea-state changes during this unusual Arctic rain.', steps:['Log rain intensity','Record air and sea temperature','Track visibility','Photograph the sea surface','Archive the event log']}),
    mission({id:'fog-sounding', weather:'fog', anywhere:true, title:'Event: Fog Boundary-Layer Sounding', shortTitle:'FOG SOUNDING', specialties:['atmosphere'], equipment:['radiosonde-pack'], consumables:['radiosonde-pack'], data:20, reward:28000, supplies:2, workHours:16, media:MEDIA.balloon, description:'A live fog event makes a vertical temperature and humidity profile unusually valuable right here.', steps:['Log fog intensity and visibility','Prepare the radiosonde','Launch into the fog layer','Track the inversion profile','Transmit the rapid event report']}),
    mission({id:'basic-aurora-log', weather:'aurora', anywhere:true, anyScientist:true, title:'Event: Aurora Observation Log', shortTitle:'AURORA LOG', equipment:[], data:8, reward:9000, supplies:1, workHours:6, media:MEDIA.aerial, description:'Any scientist can document auroral structure, timing and sky conditions during a strong Arctic aurora.', steps:['Record first visible arc','Photograph the sky every five minutes','Log cloud and moon conditions','Note arc motion and color','Archive the event timeline']}),
    mission({id:'aurora-allsky', weather:'aurora', anywhere:true, title:'Event: Aurora All-Sky Imaging', shortTitle:'AURORA CAMERA', specialties:['atmosphere'], equipment:['all-sky-camera'], data:22, reward:30000, supplies:2, workHours:16, media:MEDIA.aerial, description:'An atmospheric scientist can exploit a strong auroral event with synchronized all-sky imagery and magnetic-field logging.', steps:['Level and orient the all-sky camera','Synchronize camera and magnetometer clocks','Record the evolving auroral arcs','Annotate cloud contamination','Transmit the event data set']}),
    mission({id:'wind-flux', weather:'high-wind', anywhere:true, title:'Event: High-Wind Air-Sea Flux Station', shortTitle:'GALE FLUX', specialties:['atmosphere','physical'], equipment:['atmospheric-suite'], data:30, reward:42000, supplies:5, workHours:30, media:MEDIA.storm, description:'A strong-wind event opens a brief chance to measure turbulent exchange over the Arctic Ocean.', steps:['Secure the science deck','Verify flux sensors','Acquire the rising wind','Sample the event peak','Close the station safely']}),
    mission({id:'snow-profile', weather:'snow', anywhere:true, title:'Event: Arctic Snow Microphysics', shortTitle:'SNOW EVENT', specialties:['atmosphere'], equipment:['research-radar'], data:34, reward:48000, supplies:5, workHours:34, media:MEDIA.radar, description:'Falling snow is crossing the vessel. Use cloud radar to resolve particle layers and vertical motion.', steps:['Start calibrated radar scans','Log surface snow habit','Track the main snow band','Verify attenuation correction','Archive the event volume']}),
    mission({id:'rain-profile', weather:'rain', anywhere:true, title:'Event: Arctic Rain-on-Ocean Profile', shortTitle:'RAIN EVENT', specialties:['atmosphere'], equipment:['radiosonde-pack'], consumables:['radiosonde-pack'], data:22, reward:30000, supplies:3, workHours:18, media:MEDIA.balloon, description:'A short rain event offers a rare warm-season thermodynamic profile opportunity at the vessel.', steps:['Record rain rate and surface flux','Prepare the radiosonde','Launch through the rain layer','Track freezing level and wind','Send the rapid event dataset']})
  ];

  const SCIENTIST_PROFILES = [
    ['maya-chen','Maya Chen','coastal-oceanography'],['noah-okafor','Noah Okafor','physical'],['elena-morozova','Elena Morozova','sea-ice-physics','russian'],['aputi-ivalu','Aputi Ivalu','sea-ice-ecology'],
    ['sofia-lindgren','Sofia Lindgren','plankton'],['amara-singh','Amara Singh','biogeochemistry'],['jonas-berg','Jonas Berg','moorings'],['leila-haddad','Leila Haddad','atmosphere'],
    ['mateo-alvarez','Mateo Álvarez','fisheries'],['nuka-petersen','Nuka Petersen','coastal-ecology'],['priya-raman','Priya Raman','benthic'],['daniel-kim','Daniel Kim','physical'],
    ['ingrid-nilsen','Ingrid Nilsen','sea-ice-physics'],['ariq-kalluk','Ariq Kalluk','coastal-oceanography'],['fatima-el-sayed','Fatima El-Sayed','biogeochemistry'],['lucas-tremblay','Lucas Tremblay','moorings'],
    ['mei-tanaka','Mei Tanaka','plankton'],['elias-korhonen','Elias Korhonen','atmosphere'],['anika-patel','Anika Patel','coastal-ecology'],['oskar-dahl','Oskar Dahl','benthic'],
    ['hana-suzuki','Hana Suzuki','physical'],['malik-mensah','Malik Mensah','fisheries'],['claire-rousseau','Claire Rousseau','sea-ice-ecology'],['diego-navarro','Diego Navarro','coastal-oceanography'],
    ['aisha-khan','Aisha Khan','atmosphere'],['erik-johansen','Erik Johansen','moorings'],['nadia-petrova','Nadia Petrova','sea-ice-physics','russian'],['tane-kauri','Tane Kauri','benthic'],
    ['kavya-menon','Kavya Menon','biogeochemistry'],['thomas-greene','Thomas Greene','plankton'],['selma-qajaq','Selma Qajaq','coastal-ecology'],['owen-clarke','Owen Clarke','naval-acoustics'],
    ['zuri-mbatha','Zuri Mbatha','marine-mammals'],['lucia-torres','Lucía Torres','sea-ice-ecology'],['martin-fischer','Martin Fischer','moorings'],['aya-nakamura','Aya Nakamura','atmosphere'],
    ['jukka-laine','Jukka Laine','sea-ice-physics'],['samira-el-amin','Samira El-Amin','marine-mammals'],['victor-lebedev','Victor Lebedev','naval-acoustics','russian'],['emma-walsh','Emma Walsh','coastal-oceanography']
  ].map(([id,name,specialty,recruitmentPool='international']) => ({id,name,specialty,recruitmentPool,portrait:`assets/scientists/${id}.webp`}));
  const profileById = Object.fromEntries(SCIENTIST_PROFILES.map(item => [item.id, item]));
  const GROUP_REWARDS = {'Arctic Pinniped Survey':50000,'Arctic Seal Survey':45000,'Arctic Whales':38000,'Arctic Summer Birds':42000,'Arctic Fish Survey':40000,'Tundra & Ice Mammals':32000};
  const PLAYER_AVATARS = [
    {id:'chief-1',src:'assets/scientists/maya-chen.webp'},
    {id:'chief-2',src:'assets/scientists/noah-okafor.webp'},
    {id:'chief-3',src:'assets/scientists/amara-singh.webp'},
    {id:'chief-4',src:'assets/scientists/nuka-petersen.webp'},
    {id:'chief-5',src:'assets/scientists/hana-suzuki.webp'},
    {id:'chief-6',src:'assets/scientists/owen-clarke.webp'}
  ];

  const initialScientist = {id:'player', profileId:null, name:'Chief Scientist', role:'Chief Scientist', specialty:'coastal-oceanography', career:'grad', portrait:PLAYER_AVATARS[0].src, isPlayer:true, recruitmentPool:'player', hiredAt:-1, missions:0, papers:0};
  const state = {
    money:185000, citations:0, data:0, supplies:35, currentVessel:'fishing', ownedVessels:['fishing'], homePortId:'longyearbyen',
    scientists:[initialScientist], playerConfigured:false, installedEquipment:[], inventory:{}, port:null, portVisits:0,
    candidates:[], offers:[], targets:[], completed:[], deployments:[], weatherEventsSeen:[], droppedGrantTemplates:[],
    observed:[], observedIndividuals:[], claimedGroups:[], papers:[], publicationCooldown:0, publishAttempts:0, lastPublicationRejected:false, publicationIntroShown:false,
    economyDays:0, elapsedDays:0, log:['Expedition commissioned in Longyearbyen.'], navigation:null, lastTargetContext:null,
    scientistRecords:{}, promotions:[], recentGrantTemplates:[], recentGrantSites:[], recentOpportunityTemplates:[], lastOpportunitySpawnPosition:null, grantCooldowns:{}, grantMarketReady:{}, assistedByVessels:[], bridgeSupportNotice:null, lastPortId:null, lastProfessorGrantDay:-999, remoteOffer:null, helicopterFoodReminderShown:false
  };

  let callbacks = {};
  let catalog = {};
  let root = null;
  let portOpen = false;
  let activePortTab = 'vessel';
  let portScrollTop = 0;
  let portTabsScrollLeft = 0;
  let activeOperation = null;
  let operationFrame = 0;
  let pendingDeparture = null;
  let openStoreDetail = null;
  let promotionQueue = [];
  let pendingCandidateId = null;
  let characterDraft = {avatar:PLAYER_AVATARS[0].id,specialty:'coastal-oceanography',name:''};
  let activeNpcEncounter = null;
  let cashAnimation = null;
  let devCareerOverride = null;
  let relocationPortCache = {key:null,ports:[]};

  function vessel() { return VESSELS[state.currentVessel]; }
  function profileFor(item) { return item?.portrait?{portrait:item.portrait,recruitmentPool:item.recruitmentPool||'player'}:profileById[item?.profileId] || profileById[slug(item?.name)] || SCIENTIST_PROFILES[0]; }
  function careerLevel(id) { return CAREERS[id]?.level || 0; }
  function playerScientist() { return state.scientists.find(item=>item.isPlayer)||state.scientists[0]; }
  function playerCareerLevel() { return careerLevel(playerScientist()?.career); }
  function hiredCareerCount(id) { return state.scientists.filter(item=>!item.isPlayer&&item.career===id).length; }
  const CAREER_CITATION_COST={grad:10,postdoc:100,professor:1000};
  function citationCapacityUsed() {
    return state.scientists.filter(item=>!item.isPlayer).reduce((sum,item)=>sum+(CAREER_CITATION_COST[item.career]||0),0);
  }
  function careerHireStatus(id) {
    const cost=CAREER_CITATION_COST[id]||Infinity,total=Math.floor(state.citations),used=citationCapacityUsed(),playerReady=id==='grad'||playerCareerLevel()>=careerLevel(id);
    const stage=id==='grad'?'Graduate Student':id==='postdoc'?'Postdoc':'Professor';
    const gate=!playerReady?`Chief Scientist must become a ${id==='postdoc'?'postdoc':'professor'} first`:null;
    return {ready:playerReady&&used+cost<=total,label:gate||`Citation budget ${used}/${total} used · ${stage} requires ${cost.toLocaleString()} citations`};
  }
  function templateCareerLevel(template) {
    let level=1; for (const id of [...(template.equipment||[]),...(template.consumables||[])]) level=Math.max(level,EQUIPMENT[id]?.tier||1); return Math.min(3,level);
  }
  function missionMinCrew(template) {
    const title=String(template?.title||'').toLowerCase();
    if ((template?.berthReserve||0)>0 && (template?.stationDelivery||template?.anyScientist||/deliver|transport|supply|field team|team deployment/.test(title))) return 1;
    const explicit=Number(template?.minCrew); if(Number.isFinite(explicit)&&explicit>0)return Math.max(1,Math.round(explicit));
    const level=templateCareerLevel(template),bounds={1:[1,3],2:[3,10],3:[10,20]}[level]||[1,3];
    const rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level).map(item=>Number(item.reward)||0).filter(value=>value>0);
    const low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low,reward=Math.max(low,Number(template?.reward)||low),t=high>low?clamp((reward-low)/(high-low),0,1):0;
    return Math.round(bounds[0]+(bounds[1]-bounds[0])*t);
  }
  function templateRelativeReward(template) {
    const level=templateCareerLevel(template),rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level&&!item.weather).map(item=>Number(item.reward)||0).filter(Boolean),low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low;
    return high>low?clamp(((Number(template?.reward)||low)-low)/(high-low),0,1):0;
  }
  function missionSpecialistRequirements(template) {
    if(Array.isArray(template?.specialistRequirements))return clone(template.specialistRequirements);
    if(template?.anyScientist)return [];
    const level=templateCareerLevel(template),specialties=[...new Set(template?.specialties||[])];
    if(level<2||specialties.length<2)return [];
    const relative=templateRelativeReward(template),seed=[...String(template?.id||template?.title||'')].reduce((sum,ch)=>(sum*31+ch.charCodeAt(0))>>>0,17),interdisciplinary=relative>=.42&&(seed%100)<(level>=3?62:42);
    if(!interdisciplinary)return [];
    const count=level>=3&&specialties.length>=3&&relative>=.7&&(seed%3!==1)?3:2,minCareer=level>=3?'professor':'postdoc';
    return specialties.slice(0,count).map(specialty=>({specialties:[specialty],minCareer,count:1}));
  }
  function expandedSpecialistNeeds(template) {
    const needs=[];for(const requirement of missionSpecialistRequirements(template))for(let i=0;i<(requirement.count||1);i++)needs.push(requirement);return needs;
  }
  function specialistAssignment(template) {
    const needs=expandedSpecialistNeeds(template);if(!needs.length)return {missing:0,ids:[]};let best=[];
    const walk=(index,used,ids)=>{if(index>=needs.length){if(ids.length>best.length)best=[...ids];return;}walk(index+1,used,ids);const need=needs[index];for(const scientist of state.scientists){if(used.has(scientist.id)||careerLevel(scientist.career)<careerLevel(need.minCareer)||!(need.specialties||[]).includes(scientist.specialty))continue;used.add(scientist.id);ids.push(scientist.id);walk(index+1,used,ids);ids.pop();used.delete(scientist.id);}};walk(0,new Set(),[]);return {missing:Math.max(0,needs.length-best.length),ids:best};
  }
  function specialistRequirementsMet(template) { return specialistAssignment(template).missing===0; }
  function missionFitsCurrentVessel(template,ship=vessel()) { return missionMinCrew(template)+Math.max(0,Number(template?.berthReserve)||0)<=ship.berths; }
  function vesselRewardScale(ship=vessel()) {
    const starter=VESSELS.fishing,baseCapital=Math.max(1,vesselPurchasePrice(starter)||120000),capital=Math.max(baseCapital,vesselPurchasePrice(ship)||ship.marketPrice||baseCapital);
    const operatingCost=s=>Math.max(1,(s.nuclearFuel?0:s.fuelCapacity*s.fuelUnitCost)+s.foodCapacity*s.foodUnitCost+s.supplyCapacity*250),baseOperating=operatingCost(starter),operating=operatingCost(ship);
    const capitalIndex=1+Math.max(0,Math.log10(capital/baseCapital))*1.35,operatingIndex=1+Math.max(0,Math.log10(operating/baseOperating))*.9;
    return clamp(capitalIndex*.7+operatingIndex*.3,1,12);
  }
  function payroll() { return state.scientists.reduce((sum,item) => sum + (CAREERS[item.career]?.salary || 0), 0); }
  function normalizedPortId(port=state.port) { return port?.id || slug(port?.name || ''); }
  const RUSSIAN_PORTS = new Set(['murmansk','arkhangelsk','dikson','tiksi','pevek','anadyr']);
  function isRussianPort(port=state.port) { return RUSSIAN_PORTS.has(normalizedPortId(port)); }
  function activeGrants() {
    return state.targets.filter(item => (item.kind==='grant'||item.kind==='contract') && !['completed','failed','dropped'].includes(item.status));
  }
  function grantCapacity() { const level=playerCareerLevel();if(level<2)return Math.max(1,state.scientists.length);const postdocs=state.scientists.filter(item=>item.career==='postdoc').length,professors=state.scientists.filter(item=>item.career==='professor').length;return Math.max(2,postdocs*2+professors*3); }
  function grantLoad() {
    return activeGrants().length+(state.deployments||[]).filter(item=>item.originalKind==='grant'&&item.status==='collecting').length;
  }
  function vesselMarketUnlock(id) {
    if (id==='fishing'||id==='trawler') return true;
    if (id==='coastal') return playerCareerLevel()>=2;
    if (id==='global'||id==='icebreaker'||id==='nuclear') return playerCareerLevel()>=3;
    return false;
  }
  function vesselsForPort(port=state.port) {
    if (isRussianPort(port)) return [VESSELS.nuclear];
    return ['fishing','trawler','coastal','global','icebreaker'].map(id=>VESSELS[id]);
  }
  function vesselForSaleHere(id,port=state.port) {
    if (id==='nuclear') return isRussianPort(port);
    return !isRussianPort(port)&&['fishing','trawler','coastal','global','icebreaker'].includes(id);
  }
  function vesselScienceTier(ship=vessel()) { return ship.slots.heavy>0?3:ship.slots.medium>0?2:1; }
  function equipmentPossibleOnShip(item,ship=vessel()) {
    if (!item) return false;
    if (item.builtIn) return ship.standardEquipment.includes(item.id);
    if ((item.tier||1)>vesselScienceTier(ship)) return false;
    if(item.minVesselClass){const order=['fishing','trawler','coastal','global','icebreaker','nuclear'];if(order.indexOf(ship.id)<order.indexOf(item.minVesselClass))return false;}
    if (item.consumable) return true;
    if ((item.helideckUse||0)>ship.helidecks) return false;
    return (ship.slots[item.slotType]||0)>=(item.slots||0);
  }
  function equipmentForVessel(ship=vessel()) {
    return Object.values(EQUIPMENT).filter(item => equipmentPossibleOnShip(item,ship)||isInstalled(item.id,ship)).sort((a,b)=>{
      const aboard=item=>isInstalled(item.id,ship)||(item.consumable&&(state.inventory[item.id]||0)>0);
      const rank=item=>aboard(item)?0:equipmentPurchaseStatus(item,ship).ready?1:2;
      return rank(a)-rank(b)||a.name.localeCompare(b.name);
    });
  }
  function recordScientist(item) {
    if (!item?.profileId) return;
    state.scientistRecords[item.profileId]={career:item.career,missions:item.missions||0,papers:item.papers||0};
  }
  function showNextPromotion() {
    if (!root||!promotionQueue.length||root.querySelector('#arx-target-modal.open')||root.querySelector('#arx-publish-modal.open')) return;
    const promotion=promotionQueue.shift(), modal=root.querySelector('#arx-promotion-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-result-card accepted"><small>CAREER MILESTONE</small><h2>${escapeHtml(promotion.name)} is now a ${escapeHtml(CAREERS[promotion.career].name)}</h2><p>${escapeHtml(promotion.message)}</p><div class="arx-chance"><span>PUBLICATIONS ABOARD<b>${promotion.papers}</b></span><span>SPECIALTY MISSIONS<b>${promotion.missions}</b></span><span>NEW SALARY<b>${cash(CAREERS[promotion.career].salary)}/day</b></span></div><button data-arx-action="close-promotion">CONGRATULATIONS</button></div>`;
    modal.classList.add('open');
  }
  function checkPromotions() {
    if (devCareerOverride) return;
    const player=playerScientist();
    if (player?.career==='grad' && state.papers.length>=2 && state.citations>=100) {
      player.career='postdoc'; recordScientist(player); promotionQueue.push({name:'Chief Scientist',career:'postdoc',papers:state.papers.length,missions:player.missions||0,message:`Congratulations, you finally earned your PhD degree! You reached postdoc status with ${state.papers.length} published papers and ${Math.floor(state.citations)} citations. You may now hire postdocs (one per 100 citations), purchase medium-duty science systems, commission a coastal-class research vessel, relocate your expedition to ports around the Arctic, and receive much more sophisticated postdoc-level research programs.`}); addLog('Chief Scientist promoted to postdoc · coastal R/V and medium equipment unlocked.'); refreshProgressionOpportunities('career-promotion');
    }
    if (player?.career==='postdoc' && state.citations>=2000) {
      player.career='professor'; recordScientist(player); promotionQueue.push({name:'Chief Scientist',career:'professor',papers:state.papers.length,missions:player.missions||0,message:'Reaching 2,000 citations has earned professor status. There is no minimum publication-count requirement. Global research vessels, icebreakers and heavy equipment are unlocked. Professors lead the highest-complexity programs and can originate new grants while at sea.'}); addLog('Chief Scientist promoted to professor at 2,000 citations · global vessels, icebreakers and heavy equipment unlocked.'); refreshProgressionOpportunities('career-promotion');
    }
    if (promotionQueue.length) showNextPromotion();
  }
  function averageQuality() {
    if (!state.scientists.length) return .7;
    return state.scientists.reduce((sum,item) => sum + (CAREERS[item.career]?.quality || .7), 0) / state.scientists.length;
  }
  function isInstalled(id, ship=vessel()) {
    return ship.standardEquipment.includes(id) || state.installedEquipment.includes(id);
  }
  function slotUsage(ids=state.installedEquipment) {
    const used = {light:0,medium:0,heavy:0};
    for (const id of ids) {
      const item = EQUIPMENT[id];
      if (item && !item.consumable && !item.builtIn) used[item.slotType] += item.slots || 0;
    }
    return used;
  }
  function helideckUsage(ids=state.installedEquipment) {
    return ids.reduce((sum,id) => sum + (EQUIPMENT[id]?.helideckUse || 0), 0);
  }
  function equipmentFits(ship, extraId=null) {
    const ids = [...state.installedEquipment];
    const extra = EQUIPMENT[extraId];
    if (extraId && extra && !extra.consumable && !ids.includes(extraId)) ids.push(extraId);
    const used = slotUsage(ids);
    return SLOT_TYPES.every(type => used[type] <= (ship.slots[type] || 0)) && helideckUsage(ids) <= ship.helidecks;
  }
  function equipmentCrewRequirements(item) {
    if (Array.isArray(item?.crew)) return item.crew;
    if (!item?.specialties?.length) return [];
    const minCareer=item.tier>=3?'professor':item.tier>=2?'postdoc':'grad';
    return [{specialties:item.specialties,minCareer,count:1}];
  }
  function equipmentPurchaseStatus(item,ship=vessel()) {
    if (!item) return {ready:false,reason:'Equipment unavailable'};
    const inventory=state.inventory[item.id]||0,maxUnits=item.maxUnits??Infinity,loadUnits=item.consumable?Math.min(item.units||1,Math.max(0,maxUnits-inventory)):0,purchaseCost=item.consumable?Math.round(item.price*loadUnits/Math.max(1,item.units||1)):item.price,storageRoom=!item.consumable||loadUnits>0;
    const possible=equipmentPossibleOnShip(item,ship),capacity=item.consumable?storageRoom:(item.builtIn||equipmentFits(ship,item.id));
    const playerTierReady=(item.tier||1)<=playerCareerLevel(),crewReady=crewRequirementsMet(equipmentCrewRequirements(item)),prerequisites=(item.requiresEquipment||[]).every(id=>equipmentOperational(id));
    const support=playerTierReady&&crewReady&&prerequisites,affordable=state.money>=purchaseCost; let reason='Ready to purchase';
    if (!possible) reason='Not supported by this vessel class'; else if (!playerTierReady) reason=`Chief Scientist must reach ${item.tier===3?'professor':'postdoc'} level first`; else if (!storageRoom) reason=`Expendable storage full · ${inventory}/${maxUnits} units aboard`; else if (!capacity) reason=`No available ${item.helideckUse?'helideck or ':''}${item.slotType||'science'} capacity`; else if (!crewReady) reason=`Current crew cannot operate this ${item.tier===3?'professor':item.tier===2?'postdoc':'graduate'}-level system`; else if (!prerequisites) reason=`Requires ${item.requiresEquipment.map(id=>EQUIPMENT[id]?.name||id).join(' + ')}`; else if (!affordable) reason='Insufficient funds';
    return {ready:possible&&capacity&&support&&affordable,possible,capacity,crewReady,prerequisites,support,affordable,storageRoom,maxUnits,inventory,loadUnits,purchaseCost,reason};
  }
  function slotSummary(ship=vessel(), usage=slotUsage()) {
    const parts=SLOT_TYPES.filter(type=>(ship.slots[type]||0)>0).map(type=>`${type[0].toUpperCase()+type.slice(1)} ${usage[type]||0}/${ship.slots[type]}`);
    return `Equipment capacity: ${parts.join(' · ')}`;
  }
  function crewRequirementsMet(requirements=[]) {
    const needs = [];
    for (const requirement of requirements) {
      for (let count=0; count<(requirement.count || 1); count++) needs.push(requirement);
    }
    needs.sort((a,b) => careerLevel(b.minCareer) - careerLevel(a.minCareer));
    const assign = (index, used) => {
      if (index >= needs.length) return true;
      const need = needs[index];
      for (let i=0; i<state.scientists.length; i++) {
        const scientist = state.scientists[i];
        if (used.has(i) || careerLevel(scientist.career) < careerLevel(need.minCareer) || !need.specialties.includes(scientist.specialty)) continue;
        used.add(i);
        if (assign(index+1, used)) return true;
        used.delete(i);
      }
      return false;
    };
    return assign(0, new Set());
  }
  function equipmentOperational(id, trail=new Set()) {
    const item = EQUIPMENT[id];
    if (!item || trail.has(id)) return false;
    if (item.consumable && (state.inventory[id] || 0) <= 0) return false;
    if (!item.consumable && !isInstalled(id)) return false;
    if (item.deploymentAsset&&state.deployments.some(deployment=>deployment.recoveryRequired&&deployment.status!=='recovered'&&(deployment.equipment||[]).includes(id))) return false;
    if (id==='deep-mooring-payload'&&state.deployments.some(deployment=>deployment.recoveryRequired&&deployment.status!=='recovered')) return false;
    if ((item.helideckUse || 0) > vessel().helidecks) return false;
    const nextTrail = new Set(trail); nextTrail.add(id);
    if ((item.requiresEquipment || []).some(required => !equipmentOperational(required, nextTrail))) return false;
    return crewRequirementsMet(equipmentCrewRequirements(item));
  }
  function hasSpecialty(template) {
    if (template.anyScientist) return state.scientists.length > 0;
    return (template.specialties || []).some(id => state.scientists.some(scientist => scientist.specialty === id));
  }
  function eligible(template, weather=null) {
    if (!hasSpecialty(template)) return false;
    if (!missionFitsCurrentVessel(template)) return false;
    if (!specialistRequirementsMet(template)) return false;
    if ((template.equipment || []).some(id => !equipmentOperational(id))) return false;
    if (state.scientists.length<missionMinCrew(template)) return false;
    if (template.weather && weather && template.weather !== weather.type) return false;
    return true;
  }
  function workRate(target) {
    const people = target.anyScientist ? state.scientists : state.scientists.filter(item => (target.specialties || []).includes(item.specialty));
    return Math.max(1, people.reduce((sum,item) => sum + (CAREERS[item.career]?.productivity || 1), 0));
  }
  function effectiveDays(target,hours=target.workHours) { return Math.max(.1, Number((hours / (8 * workRate(target))).toFixed(1))); }
  function pendingStations(target) {
    return (target.stations||[]).filter(station=>station.status!=='completed');
  }
  function currentStation(target) {
    return target.stations?.[target.stationIndex||0] || null;
  }
  function remainingWorkHours(target) {
    const stations=pendingStations(target);
    return stations.length?stations.reduce((sum,station)=>sum+(Number(station.workHours)||0),0):target.workHours;
  }
  function remainingSupplies(target) {
    const stations=pendingStations(target);
    return stations.length?Math.ceil(stations.reduce((sum,station)=>sum+(Number(station.supplies)||0),0)):target.supplies;
  }
  function operationWorkHours(target) { return currentStation(target)?.workHours || target.workHours; }
  function operationSupplies(target) { return Math.max(1,Math.ceil(currentStation(target)?.supplies || target.supplies)); }
  function remainingConsumableNeed(target,id) {
    const perStation=target.consumablePerStation?.[id];
    if (perStation) return perStation*Math.max(1,pendingStations(target).length);
    return (target.consumables||[]).includes(id)?1:0;
  }
  function requirementText(item) {
    const pieces = equipmentCrewRequirements(item).map(need => {
      const role = CAREERS[need.minCareer]?.name.replace('Postdoctoral Researcher','Postdoc').replace('Graduate Student','Grad student');
      const fields = need.specialties.map(id => specialtyById[id]?.name).filter(Boolean).join(' / ');
      return `${need.count || 1} × ${role} · ${fields}`;
    });
    if (item.requiresEquipment?.length) pieces.push(`Also needs ${item.requiresEquipment.map(id => EQUIPMENT[id]?.name).filter(Boolean).join(' + ')}`);
    if (item.helideckUse) pieces.push(`${item.helideckUse} helideck position`);
    return pieces.join(' + ') || 'No specialist operator requirement';
  }
  function formatCapacity(value, unit) {
    return value == null ? 'REACTOR · INDEFINITE' : `${new Intl.NumberFormat('en-US',{maximumFractionDigits:0}).format(Math.round(value))} ${unit}`;
  }
  function fuelStepCost(ship=vessel()) { return ship.nuclearFuel ? 0 : Math.round(ship.fuelCapacity * .1 * ship.fuelUnitCost); }
  function foodStepCost(ship=vessel()) { return Math.round(ship.foodCapacity * .1 * ship.foodUnitCost); }
  function toast(message) { callbacks.onToast?.(message); }
  function addLog(message) { state.log.unshift(message); state.log = state.log.slice(0,18); }
  function syncGlobalCash() { const node=document.getElementById('cash-balance'); if(node)node.textContent=cash(state.money); }
  function animateCashReadouts() {
    if (!cashAnimation||!root) return;
    const animation=cashAnimation; cashAnimation=null;
    const nodes=[...root.querySelectorAll('[data-arx-cash]')]; if (!nodes.length) return;
    const started=performance.now(), duration=1000;
    const frame=now=>{const t=clamp((now-started)/duration,0,1), eased=1-Math.pow(1-t,3), value=animation.from+(animation.to-animation.from)*eased; nodes.forEach(node=>node.textContent=cash(value)); if(t<1)requestAnimationFrame(frame);};
    requestAnimationFrame(frame);
  }
  function adjustMoney(delta,{sound=true}={}) {
    if (!Number.isFinite(delta)||!delta) return;
    const from=state.money; state.money+=delta; syncGlobalCash(); cashAnimation={from,to:state.money};
    if (sound) callbacks.onSound?.('cash',{amount:Math.abs(delta),direction:delta>0?'in':'out'});
  }
  function addData(amount) {
    amount=Math.max(0,Number(amount)||0); if (!amount) return;
    state.data+=amount; callbacks.onSound?.('data',{amount}); if(state.data>=PUBLISH_MIN&&!state.publicationIntroShown)setTimeout(maybePublicationIntro,0);
  }
  function currentPaperLevel() { return [...PAPER_LEVELS].reverse().find(level=>state.data>=level.threshold)||null; }
  function dataGaugePercent(data=state.data) {
    data=Math.max(0,data);
    if (data<=100) return data/100*12;
    if (data<=1000) return 12+(data-100)/900*38;
    return Math.min(100,50+(data-1000)/9000*50);
  }
  function publicationChance(level=currentPaperLevel(),data=state.data) {
    if (!level) return 0; if (!level.next) return 1;
    const halfway=level.threshold+(level.next-level.threshold)/2;
    return clamp(.5+.5*(data-level.threshold)/Math.max(1,halfway-level.threshold),.5,1);
  }
  function maybePublicationIntro() {
    if(state.publicationIntroShown||state.data<PUBLISH_MIN||!root||activeOperation)return false;
    if(root.querySelector('.arx-modal.open'))return false;
    state.publicationIntroShown=true;
    const modal=root.querySelector('#arx-publish-modal');if(!modal)return false;
    modal.innerHTML=`<div class="arx-modal-card arx-result-card arx-publication-intro"><button class="arx-close" data-arx-action="close-publication-intro">×</button><small>PUBLICATION UNLOCKED</small><h2>Your first publication is ready</h2><p>Field work produces <b>publication data</b>. Crossing a publication threshold lets you submit the corresponding work. Accepted publications then earn citations; citations are what drive your scientific reputation and career progression.</p><div class="arx-publication-tier-guide"><span><b>LETTER</b><small>100 data</small><em>Short, focused result from a compact field program.</em></span><span><b>ARTICLE</b><small>1,000 data</small><em>A full peer-reviewed study built from a much larger data set.</em></span><span><b>BOOK</b><small>10,000 data</small><em>A major Arctic synthesis. This top tier publishes automatically once ready.</em></span></div><p>You can keep collecting data beyond a threshold before submitting. For Letter and Article tiers, additional data improves the acceptance chance. Your first publication is guaranteed so the system is easy to learn.</p><button data-arx-action="close-publication-intro">GOT IT</button></div>`;
    modal.classList.add('open');callbacks.onStateChange?.();return true;
  }
  function maybeAutoPublish() {
    const level=currentPaperLevel(); if (!level||level.next||state.publicationCooldown>0||activeOperation) return false;
    if (root?.querySelector('.arx-modal.open')) return false;
    publishPaper(true); return true;
  }
  function changed({port=true}={}) {
    renderSidebar();
    if (port && portOpen) renderPort();
    animateCashReadouts(); callbacks.onStateChange?.();
  }

  function destination(lat, lon, distanceKm, bearingDeg) {
    const radius=6371, bearing=bearingDeg*Math.PI/180, phi1=lat*Math.PI/180, lambda1=lon*Math.PI/180, delta=distanceKm/radius;
    const phi2=Math.asin(Math.sin(phi1)*Math.cos(delta)+Math.cos(phi1)*Math.sin(delta)*Math.cos(bearing));
    const lambda2=lambda1+Math.atan2(Math.sin(bearing)*Math.sin(delta)*Math.cos(phi1),Math.cos(delta)-Math.sin(phi1)*Math.sin(phi2));
    return {lat:phi2*180/Math.PI, lon:((lambda2*180/Math.PI+540)%360)-180};
  }
  function geoDistance(a,b) {
    const toRad=Math.PI/180,lat1=a.lat*toRad,lat2=b.lat*toRad,dLat=(b.lat-a.lat)*toRad,dLon=(b.lon-a.lon)*toRad;
    const h=Math.sin(dLat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
    return 6371*2*Math.atan2(Math.sqrt(h),Math.sqrt(Math.max(0,1-h)));
  }
  function researchDistanceWindow(template,kind,options={}) {
    const vesselId=state.currentVessel,official=kind==='grant'||kind==='contract',field=kind==='opportunity'||kind==='weather-opportunity',career=playerCareerLevel();
    const grantRanges={fishing:[30,105],trawler:[240,650],coastal:[900,1600],global:[1100,2000],icebreaker:[1300,2350],nuclear:[1500,2800]};
    const fieldRanges={fishing:[25,90],trawler:[110,300],coastal:[240,680],global:[360,920],icebreaker:[470,1180],nuclear:[580,1450]};
    const base=(official?grantRanges:fieldRanges)[vesselId]||(official?grantRanges.fishing:fieldRanges.fishing);
    let min=base[0],max=base[1];
    const careerBonus=career>=3?120:career===2?55:0;min+=careerBonus;max+=careerBonus;
    if(Number.isFinite(template.minDistance))min=Math.max(min,template.minDistance);
    if(options.nearby&&field){min=Math.max(35,min*.72);max=Math.max(min+40,max*.82);}
    if(vesselId==='fishing'&&Number.isFinite(template.distanceRange))max=Math.min(max,min+Math.max(35,template.distanceRange*2.2));
    if(vesselId==='trawler'&&Number.isFinite(template.distanceRange))max=Math.min(max,min+Math.max(120,template.distanceRange*4));
    return{min:Math.max(5,min),max:Math.max(min+20,max)};
  }
  function targetSpacingKm() {
    return {fishing:18,trawler:45,coastal:110,global:180,icebreaker:240,nuclear:300}[state.currentVessel]||18;
  }
  function missionRewardScore(template,distanceKm,kind,actualWorkHours=template.workHours) {
    const ids=[...(template.equipment||[]),...(template.consumables||[])],unique=[...new Set(ids)];
    let durable=0,disposable=0;
    for(const id of unique){const item=EQUIPMENT[id];if(!item)continue;if(item.consumable)disposable+=Math.max(0,item.price||0);else durable+=Math.max(0,item.price||0);}
    const durableScore=clamp(Math.log10(1+durable)/6,0,1),disposableScore=clamp(Math.log10(1+disposable*5)/5.5,0,1),workScore=clamp(((actualWorkHours||10)-8)/135,0,1);
    const official=kind==='grant'||kind==='contract';
    if(official){const distanceScore=clamp((Math.max(0,distanceKm||0)-20)/220,0,1);return clamp(.30*durableScore+.28*disposableScore+.27*workScore+.15*distanceScore,0,1);}
    return clamp(.35*durableScore+.35*disposableScore+.30*workScore,0,1);
  }
  function missionRewardAmount(template,kind,distanceKm,rng,actualWorkHours=template.workHours) {
    const official=kind==='grant'||kind==='contract',base=official?[40000,60000]:[10000,15000];
    const score=clamp(missionRewardScore(template,distanceKm,kind,actualWorkHours)+(rng()-.5)*.05,0,1);
    const careerFactor=playerCareerLevel()>=3?2.4:playerCareerLevel()===2?1.55:1;
    const vesselFactor={fishing:1,trawler:1.25,coastal:1.8,global:3,icebreaker:4.5,nuclear:6}[state.currentVessel]||1;
    const templateFactor=1+Math.max(0,templateCareerLevel(template)-1)*.18;
    const value=(base[0]+(base[1]-base[0])*score)*careerFactor*vesselFactor*templateFactor;
    return Math.round(value/500)*500;
  }
  function buildTarget(template, origin, rng, kind='grant', options={}) {
    if(!missionFitsCurrentVessel(template))return null;
    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03);
    const window=researchDistanceWindow(template,kind,options);
    const validator=callbacks.isResearchSiteSuitable;
    const avoidPoints=[...state.targets,...state.offers,...(state.recentGrantSites||[])].filter(item=>item.status!=='completed');
    let point=template.fixedDestination ? {...template.fixedDestination} : null;
    let distance=0, bearing=0;
    const spacing=options.nearby?18:targetSpacingKm(),context=()=>({template,origin,kind,distanceKm:distance,bearingDeg:bearing,distanceWindow:window,avoidPoints,minimumSpacingKm:spacing,preferred:template.fixedDestination||null,...options});
    if (point) {
      distance=geoDistance(origin,point);
      if (!pointIsSpaced(point,avoidPoints,spacing) || (validator&&!validator(point,context()))) point=null;
    }
    if (!point && template.fixedDestination) {
      for (let radius=3; radius<=30&&!point; radius+=3) for (let angle=0; angle<360; angle+=20) {
        const candidate=destination(template.fixedDestination.lat,template.fixedDestination.lon,radius,angle);
        distance=geoDistance(origin,candidate); bearing=angle;
        if (pointIsSpaced(candidate,avoidPoints,spacing) && (!validator||validator(candidate,context()))) { point=candidate; break; }
      }
    }
    if (!point && !template.fixedDestination) {
      for (let attempt=0; attempt<96; attempt++) {
        distance=window.min+rng()*(window.max-window.min); bearing=rng()*360;
        const candidate=destination(origin.lat,origin.lon,distance,bearing);
        if (pointIsSpaced(candidate,avoidPoints,spacing) && (!validator || validator(candidate,context()))) { point=candidate; break; }
      }
    }
    if (!point) {
      const fallback=callbacks.findResearchSite?.(context());
      if (fallback&&Number.isFinite(fallback.lat)&&Number.isFinite(fallback.lon)&&(!template.fixedDestination||geoDistance(fallback,template.fixedDestination)<=35)&&pointIsSpaced(fallback,avoidPoints,spacing)&&(!validator||validator(fallback,context()))) point=fallback;
    }
    if (!point) return null;
    const iceValueMultiplier=Math.max(1,Number(callbacks.researchSiteValueMultiplier?.(point,template)||1));
    const target={
      id:`${kind}-${template.id}-${Date.now()}-${Math.floor(rng()*1e6)}`,
      templateId:template.id, title:template.title, shortTitle:template.shortTitle, description:template.description,
      specialties:[...(template.specialties || [])], anyScientist:!!template.anyScientist,
      equipment:[...(template.equipment || [])], consumables:[...(template.consumables || [])], minCrew:missionMinCrew(template), specialistRequirements:missionSpecialistRequirements(template),
      steps:[...(template.steps || [])], media:clone(template.media), lat:point.lat, lon:point.lon,
      data:Math.max(1,Math.round(template.data*scale*vesselScale*crewScale*iceValueMultiplier)), reward:missionRewardAmount(template,kind,distance,rng,template.workHours*scale),
      supplies:Math.max(1,Math.round(template.supplies*scale)), workHours:Math.max(4,Math.round(template.workHours*scale)),
      missionMode:template.missionMode || 'immediate', deploymentDays:template.deploymentDays || 0,
      recoveryAfterDays:template.recoveryAfterDays || 0, weather:template.weather || null,
      anywhere:!!template.anywhere, stationDelivery:!!template.stationDelivery, berthReserve:template.berthReserve||0, shore:!!template.shore, glacier:!!template.glacier, terrestrial:!!template.terrestrial, fjordPreferred:!!template.fjordPreferred, siteName:point.siteName||null, iceValueMultiplier, status:'active', kind, selected:false, discoveredAtDay:state.elapsedDays, expiresAtDay:kind==='weather-opportunity'?state.elapsedDays+2.25:kind==='opportunity'?state.elapsedDays+3+rng()*2:null, weatherEventId:options.weatherEventId||null,
      upfront:0, advancePaid:0, postdocOpportunity:!!template.postdocOpportunity,
      sourcePortId:normalizedPortId(origin), recoveryTitle:template.recoveryTitle||null,recoveryShortTitle:template.recoveryShortTitle||null,
      recoveryDescription:template.recoveryDescription||null,recoveryAfterDaysByVessel:clone(template.recoveryAfterDaysByVessel||{}),
      consumablePerStation:clone(template.consumablePerStation||{})
    };
    const stations=buildStations(template,point,rng,validator,context());
    if (template.transect&&stationCountFor(template)>1&&!stations) return null;
    if (stations) {
      for (const station of stations) { station.workHours=target.workHours/stations.length; station.supplies=target.supplies/stations.length; }
      target.stations=stations; target.stationIndex=0; target.lat=stations[0].lat; target.lon=stations[0].lon;
    }
    return target;
  }

  function recordGrantUse(templateId,point,portId=null) {
    if (!templateId) return;
    state.recentGrantTemplates=[templateId,...(state.recentGrantTemplates||[]).filter(id=>id!==templateId)].slice(0,8);
    state.grantCooldowns=state.grantCooldowns||{};
    const source=portId||point?.sourcePortId||normalizedPortId(state.port)||'field';
    const key=`${source}:${templateId}`;
    state.grantCooldowns[key]=Math.max(state.grantCooldowns[key]||0,state.elapsedDays+14);
    if (point&&Number.isFinite(point.lat)&&Number.isFinite(point.lon)) {
      state.recentGrantSites=[{lat:point.lat,lon:point.lon,templateId,day:state.elapsedDays},...(state.recentGrantSites||[])].slice(0,18);
    }
  }

  function generateCandidates(port) {
    const rng=seeded(`${normalizedPortId(port)}-${state.portVisits}-crew`), stages=['grad','grad','postdoc','postdoc','professor','professor'];
    const aboard=new Set(state.scientists.map(item => item.profileId || slug(item.name)));
    const shuffle=list=>{for(let i=list.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[list[i],list[j]]=[list[j],list[i]];}return list;};
    const available=SCIENTIST_PROFILES.filter(profile => !aboard.has(profile.id));
    const pool=isRussianPort(port)
      ? [...shuffle(available.filter(profile=>profile.recruitmentPool==='russian')),...shuffle(available.filter(profile=>profile.recruitmentPool!=='russian'))]
      : shuffle(available.filter(profile=>profile.recruitmentPool!=='russian'));
    const careerOrder=shuffle([...stages]);
    state.candidates=careerOrder.slice(0,pool.length).map((career,index) => {
      const profile=pool[index], record=state.scientistRecords[profile.id]||{};
      return {id:`candidate-${state.portVisits}-${profile.id}`,profileId:profile.id,name:profile.name,specialty:profile.specialty,recruitmentPool:profile.recruitmentPool,career:record.career||career,missions:record.missions||0,papers:record.papers||0};
    });
  }
  function compatibleFallbackTemplate() {
    const scientist=state.scientists[0],specialty=scientist?.specialty||'physical',spec=specialtyById[specialty]?.name||'Arctic';
    return mission({id:`fallback-${specialty}`,tier:'local',title:`${spec} Field Reconnaissance`,shortTitle:'FIELD RECON',specialties:[specialty],equipment:[],data:7,reward:7500,supplies:1,workHours:10,anywhere:true,coastal:['coastal-oceanography','coastal-ecology','plankton','fisheries'].includes(specialty),fjordPreferred:true,media:MEDIA.local,description:`A flexible sponsor call that matches the expertise currently aboard.`,steps:['Define the local observation plan','Collect a repeatable field record','Check metadata and position','Preserve samples or imagery','Transmit the sponsor summary']});
  }
  const GRANT_MEDIA_POOL=[MEDIA.river,MEDIA.ice,MEDIA.storm,MEDIA.ctd,MEDIA.rov,MEDIA.radar,MEDIA.balloon,MEDIA.aerostat,MEDIA.drone,MEDIA.drifter,MEDIA.winch,MEDIA.handheldWater,MEDIA.iceCorer,MEDIA.miniRov,MEDIA.shallowAdcp,MEDIA.surfaceNet,MEDIA.verticalNet,MEDIA.bongoDetailed,MEDIA.ednaKit,MEDIA.fieldKit,MEDIA.shallowCorer,MEDIA.vessel].filter(Boolean);
  function canonicalMissionMedia(item){const template=TEMPLATES.find(template=>template.id===item?.templateId);return template?.media||item?.media||MEDIA.fieldKit||MEDIA.local;}
  function giveGrantUniqueMedia(target,used,rng){
    const template=TEMPLATES.find(item=>item.id===target.templateId),gear=[...(target.equipment||[]),...(target.consumables||[])].map(id=>EQUIPMENT[id]?.media).find(media=>media?.src),media=template?.media||gear||target.media||MEDIA.fieldKit||MEDIA.local;
    target.media=clone(media);if(used&&media?.src)used.add(media.src);return !!media?.src;
  }
  function generateOffers(port,{fresh=false}={}) {
    if(!port)return; const portId=normalizedPortId(port),cycle=`${portId}:${state.portVisits}`; if(!fresh&&state.grantOfferCycle===cycle)return; state.grantOfferCycle=cycle;
    const rng=seeded(`${portId}-${state.portVisits}-grants-v6-${playerScientist()?.career||'grad'}-${state.currentVessel}`),activeTemplates=new Set(activeGrants().map(item=>item.templateId));
    const careerFloor=playerCareerLevel(),available=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)<=careerFloor&&templateSupportedByVessel(item)&&hasSpecialty(item)&&(eligible(item)||teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item))&&!activeTemplates.has(item.id)&&!(state.droppedGrantTemplates||[]).includes(item.id)&&(item.unlockAfter||0)<=state.completed.length&&(!item.onlyPorts||item.onlyPorts.includes(portId))&&(state.grantCooldowns?.[`${portId}:${item.id}`]||0)<=state.elapsedDays);
    const teamLevel=playerCareerLevel(),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length,weighted=[];
    for(const template of available){const level=templateCareerLevel(template);let weight=teamLevel===1?(level===1?7:1):teamLevel===2?(level===2?12:level===1?1:2):(level===3?15:level===2?5:1);if(level===2)weight+=postdocCount*4+professorCount*2;if(level===3)weight+=professorCount*5;if(template.fjordPreferred&&teamLevel===1)weight+=2;for(let i=0;i<weight;i++)weighted.push(template);}
    for(let i=weighted.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[weighted[i],weighted[j]]=[weighted[j],weighted[i]];} const pool=[],seen=new Set(); for(const item of weighted)if(!seen.has(item.id)){seen.add(item.id);pool.push(item);}
    if(state.completed.length===0&&teamLevel===1){const harbor=pool.find(item=>item.id==='harbor-soundings');if(harbor){pool.splice(pool.indexOf(harbor),1);pool.unshift(harbor);}}
    const chiefCareer=playerScientist()?.career||'grad',sameLevel=state.scientists.filter(item=>item.career===chiefCareer),offerLimit=Math.min(12,Math.max(3,2+sameLevel.length*2));
    const priority=[],priorityIds=new Set();
    for(const scientist of [...sameLevel,...state.scientists.filter(item=>item.career!==chiefCareer)]){
      const match=pool.find(template=>!priorityIds.has(template.id)&&(template.specialties||[]).includes(scientist.specialty));
      if(match){priority.push(match);priorityIds.add(match.id);}
    }
    const ordered=[...priority,...pool.filter(item=>!priorityIds.has(item.id))];
    state.offers=[];const usedPictures=new Set();let attempts=0;
    for(const template of ordered){if(state.offers.length>=offerLimit||attempts>=offerLimit*4)break;attempts++;const target=buildTarget(template,port,rng,'grant');if(!target)continue;if(!giveGrantUniqueMedia(target,usedPictures,rng))continue;state.offers.push(target);}
    if(!state.offers.length){const fallback=buildTarget(compatibleFallbackTemplate(),port,rng,'grant');if(fallback){giveGrantUniqueMedia(fallback,usedPictures,rng);state.offers.push(fallback);}}
  }

  function mediaMarkup(item, className='') {
    const media=item?.templateId?canonicalMissionMedia(item):item?.media;
    if (!media?.src) return '';
    const alt=escapeHtml(media.alt || item.name || item.title);
    let visual;
    if (Array.isArray(media.atlas)) {
      const col=Number(media.atlas[0])||0,row=Number(media.atlas[1])||0;
      const x=(col/3*100).toFixed(3),y=(row/2*100).toFixed(3);
      visual='<div class="arx-atlas-photo" role="img" aria-label="'+alt+'" style="width:100%;aspect-ratio:4/3;border-radius:6px;background-color:#0f1d24;background-image:url(&quot;'+escapeHtml(media.src)+'&quot;);background-size:400% 300%;background-position:'+x+'% '+y+'%;background-repeat:no-repeat"></div>';
    } else visual='<img src="'+escapeHtml(media.src)+'" alt="'+alt+'">';
    return '<figure class="arx-media '+className+'">'+visual+'<figcaption>'+escapeHtml(media.credit || '')+(media.source?' · <a href="'+escapeHtml(media.source)+'" target="_blank" rel="noopener">source</a>':'')+'</figcaption></figure>';
  }
  function scientistCard(item,candidate=false) {
    const spec=specialtyById[item.specialty]||{name:item.specialty,description:''},career=CAREERS[item.career],profile=profileFor(item),hireStatus=careerHireStatus(item.career),locked=candidate&&!hireStatus.ready,full=state.scientists.length>=vessel().berths;
    const capability=career.level===1?'LIGHT EQUIPMENT':career.level===2?'LIGHT + MEDIUM EQUIPMENT':'LIGHT + MEDIUM + HEAVY EQUIPMENT',selected=candidate&&pendingCandidateId===item.id,citationUse=item.career==='grad'?10:item.career==='postdoc'?100:1000; let action;
    if(candidate) action=locked?`<button disabled>${escapeHtml(hireStatus.label)}</button>`:full?`<button data-arx-action="select-recruit" data-id="${item.id}">${selected?'SELECTED · CHOOSE A CREW MEMBER':'SELECT TO REPLACE CREW'}</button>`:`<button data-arx-action="hire" data-id="${item.id}">HIRE · ${citationUse.toLocaleString()} CITATION CAPACITY · ${cash(career.salary)}/DAY</button>`;
    else if(item.isPlayer) action='<button disabled>Chief Scientist · permanent berth</button>'; else if(pendingCandidateId&&full) action=`<button data-arx-action="replace-scientist" data-id="${item.id}">REPLACE WITH SELECTED RECRUIT</button>`; else action=`<button class="ghost" data-arx-action="release" data-id="${item.id}">Release at port</button>`;
    let progress='Senior career stage'; if(item.isPlayer&&item.career==='grad') progress=`Chief Scientist progression · ${state.papers.length}/2 papers · ${Math.floor(state.citations)}/100 citations`; else if(item.isPlayer&&item.career==='postdoc') progress=`Chief Scientist progression · ${state.papers.length}/10 papers · ${Math.floor(state.citations)}/1,000 citations`; else if(candidate&&item.career!=='grad') progress=hireStatus.label;
    const origin=profile.recruitmentPool==='russian'?'<span>RUSSIAN PORT RECRUIT</span>':'';
    return `<article class="arx-card scientist ${locked?'locked':''} ${selected?'selected':''}"><div class="arx-card-head"><img class="arx-portrait" src="${escapeHtml(profile.portrait)}" alt="Cartoon portrait of ${escapeHtml(item.name)}"><div><b>${escapeHtml(item.name)}</b><small>${item.isPlayer?'CHIEF SCIENTIST · ':''}${career.short} · ${escapeHtml(spec.name)}</small></div><em style="--career:${career.color}">${cash(career.salary)}/day</em></div><p>${escapeHtml(spec.description)}</p><div class="arx-stats">${origin}<span>${escapeHtml(progress)}</span></div><div class="arx-qualification">${capability}</div>${action}</article>`;
  }
  function gateStatus(ship,scientists=state.scientists) {
    const gate=ship.upgradeGate; if (!gate) return {ready:true,label:'Career requirement met'};
    const ready=playerCareerLevel()>=careerLevel(gate.career); return {ready,label:ready?`${gate.label} · unlocked`:gate.label};
  }
  function crewPreviewForVessel(ship) {
    const kept=[...state.scientists], removed=[];
    while (kept.length>ship.berths) {
      const newest=kept.filter(item=>!item.isPlayer).sort((a,b)=>(b.hiredAt??0)-(a.hiredAt??0))[0];
      if (!newest) break;
      kept.splice(kept.indexOf(newest),1); removed.push(newest);
    }
    return {kept,removed};
  }
  function deployedTradeAsset() {
    const ids=new Set((state.deployments||[]).filter(item=>item.recoveryRequired&&!['recovered','complete'].includes(item.status)).flatMap(item=>item.equipment||[]));
    return state.installedEquipment.find(id=>ids.has(id))||null;
  }
  function vesselPurchasePrice(ship) { return ship?.id==='fishing'?(ship.marketPrice||120000):(ship?.price||0); }
  function equipmentFitsIds(ship,ids) {
    const used=slotUsage(ids);return SLOT_TYPES.every(type=>used[type]<=(ship.slots[type]||0))&&helideckUsage(ids)<=ship.helidecks;
  }
  function vesselTransferPlan(next) {
    const kept=[],sold=[];
    for(const id of state.installedEquipment){const item=EQUIPMENT[id];if(item&&equipmentPossibleOnShip(item,next)&&equipmentFitsIds(next,[...kept,id]))kept.push(id);else sold.push(id);}
    const keptInventory={},soldInventory={};
    for(const [id,count] of Object.entries(state.inventory||{})){const item=EQUIPMENT[id];if(item&&equipmentPossibleOnShip(item,next))keptInventory[id]=count;else soldInventory[id]=count;}
    const installedCredit=sold.reduce((sum,id)=>sum+Math.round((EQUIPMENT[id]?.price||0)*EQUIPMENT_RESALE_RATE),0);
    const inventoryCredit=Object.entries(soldInventory).reduce((sum,[id,count])=>{const item=EQUIPMENT[id];return sum+(item?Math.round(item.price/Math.max(1,item.units||1)*count*EQUIPMENT_RESALE_RATE):0);},0);
    return {kept,sold,keptInventory,soldInventory,resaleCredit:installedCredit+inventoryCredit};
  }
  function vesselTradeInValue(ship=vessel(),next=null) {
    const hull=Math.round(vesselPurchasePrice(ship)*VESSEL_TRADE_IN_RATE);
    if(next)return hull+vesselTransferPlan(next).resaleCredit;
    const installed=state.installedEquipment.reduce((sum,id)=>sum+Math.round((EQUIPMENT[id]?.price||0)*EQUIPMENT_RESALE_RATE),0);
    const inventory=Object.entries(state.inventory).reduce((sum,[id,count])=>{const item=EQUIPMENT[id]; return sum+(item?Math.round(item.price/Math.max(1,item.units||1)*count*EQUIPMENT_RESALE_RATE):0);},0);
    return hull+installed+inventory;
  }
  function vesselCommissioningCost(ship){return fullResupplyCost(ship);}
  function vesselIceCapabilityText(item) {
    if(['fishing','trawler','coastal'].includes(item.id))return'Open water only · cannot enter marginal ice';
    if(item.id==='global')return'Marginal ice only · 33% speed';
    if(item.id==='icebreaker')return'Marginal 60% · fractured 1 m 30% RAM · solid 1 m 10% RAM · 2 m blocked';
    if(item.id==='nuclear')return'Marginal 100% · 1 m 60% RAM · 2 m 30–60% RAM · fractured 3 m 30% RAM';
    return'Open water';
  }
  function vesselPurchaseReady(item) {
    if(!item||item.id===state.currentVessel)return false;
    if(!vesselMarketUnlock(item.id)||!vesselForSaleHere(item.id))return false;
    const preview=crewPreviewForVessel(item),gate=gateStatus(item,preview.kept),blockedAsset=deployedTradeAsset(),credit=vesselTradeInValue(vessel(),item),commissioning=vesselCommissioningCost(item),due=Math.max(0,vesselPurchasePrice(item)+commissioning-credit),grantBlocked=grantLoad()>Math.max(1,preview.kept.length);
    return !blockedAsset&&gate.ready&&!grantBlocked&&state.money>=due;
  }
  function vesselCard(item) {
    const active=state.currentVessel===item.id,unlocked=vesselMarketUnlock(item.id),forSale=vesselForSaleHere(item.id),preview=crewPreviewForVessel(item),gate=gateStatus(item,preview.kept),blockedAsset=deployedTradeAsset(),transfer=vesselTransferPlan(item),credit=vesselTradeInValue(vessel(),item),listPrice=vesselPurchasePrice(item),commissioning=vesselCommissioningCost(item),net=listPrice+commissioning-credit,due=Math.max(0,net),refund=Math.max(0,-net),grantBlocked=grantLoad()>Math.max(1,preview.kept.length),fuel=item.nuclearFuel?'REACTOR · ∞':formatCapacity(item.fuelCapacity,'L');
    const careerNeed=item.id==='coastal'?'Postdoc Chief Scientist':(['global','icebreaker','nuclear'].includes(item.id)?'Professor Chief Scientist':'No career gate');
    const transferText=active?'Current equipment remains aboard':transfer.sold.length?`${transfer.kept.length} systems transfer · ${transfer.sold.length} excess systems sold`:`${transfer.kept.length} installed systems transfer automatically`;
    const checks=[{ok:active||unlocked,text:active?'Currently equipped vessel':unlocked?`${careerNeed} requirement met`:careerNeed},{ok:active||forSale,text:forSale?'Sold at this port':item.id==='nuclear'?'Sold in Russian Arctic ports':'Conventional vessels sold at non-Russian Arctic ports'},{ok:active||!blockedAsset,text:blockedAsset?`Recover ${EQUIPMENT[blockedAsset]?.name||'deployed equipment'}`:'No deployed trade-blocking equipment'},{ok:active||gate.ready,text:gate.label},{ok:active||!grantBlocked,text:grantBlocked?'Reduce active grants before downsizing crew':'Active grants fit retained crew'},{ok:true,text:transferText},{ok:active||state.money>=due,text:refund>0?`Trade-in credit exceeds fully supplied purchase cost by ${cash(refund)}`:`Available cash ${cash(state.money)} · total due ${cash(due)}`}];
    const disabled=active||checks.some(check=>!check.ok),image=item.image||'assets/vessels/base-vessel.png',reason=active?'EQUIPPED':disabled?'PURCHASE UNAVAILABLE':refund>0?`PURCHASE FULLY SUPPLIED · RECEIVE ${cash(refund)} CREDIT`:`PURCHASE FULLY SUPPLIED · ${cash(due)}`,badge=active?'EQUIPPED':(listPrice?cash(listPrice):'STARTER VESSEL'),tradeName=vessel().shipName||vessel().name;
    return `<details class="arx-card arx-store-details ${active?'selected':''}" data-arx-store-details="vessel-${item.id}"><summary><span><b>${escapeHtml(item.shipName||item.name)}</b><small>${escapeHtml(item.name)} · ${item.className} · ${item.berths} BERTHS</small></span><em class="${disabled&&!active?'price-locked':''}">${badge}</em></summary><div class="arx-detail-split"><figure class="arx-media compact"><img src="${escapeHtml(image)}" alt="Side view of ${escapeHtml(item.shipName||item.name)}"></figure><div><p>${escapeHtml(item.description)}</p><ul class="arx-spec-list arx-vessel-specs"><li>${item.cruiseKnots} kn cruise · ${item.maxKnots} kn maximum</li><li>${escapeHtml(vesselIceCapabilityText(item))}</li><li>${fuel} fuel · ${item.foodEnduranceDays} d provisions</li><li>${item.helidecks} helideck${item.helidecks===1?'':'s'}</li><li>${slotSummary(item,{light:0,medium:0,heavy:0})}</li><li>${item.berths} total berths</li></ul><div class="arx-vessel-purchase-breakdown"><span><small>HULL PRICE</small><b>${cash(listPrice)}</b></span><span><small>FULL FUEL / FOOD / LAB STORES</small><b>+ ${cash(commissioning)}</b></span><span><small>TRADE-IN + EXCESS SALE · ${escapeHtml(tradeName)}</small><b>− ${cash(credit)}</b></span><span><small>TOTAL DUE</small><b>${refund?`CREDIT ${cash(refund)}`:cash(due)}</b></span></div><div class="arx-requirement-checklist">${checks.map(check=>`<div class="${check.ok?'ready':'missing'}"><i>${check.ok?'✓':'!'}</i><span>${escapeHtml(check.text)}</span></div>`).join('')}</div><button data-arx-action="vessel" data-id="${item.id}" ${disabled?'disabled':''}>${reason}</button></div></div></details>`;
  }
  function missionsForEquipment(id) {
    return TEMPLATES.filter(template=>(template.equipment||[]).includes(id)||(template.consumables||[]).includes(id)).map(template=>template.title);
  }
  function equipmentCard(item) {
    const ship=vessel(), inventory=state.inventory[item.id]||0, installed=isInstalled(item.id), ready=equipmentOperational(item.id), purchase=equipmentPurchaseStatus(item,ship);
    const supportReady=crewRequirementsMet(equipmentCrewRequirements(item))&&(item.requiresEquipment||[]).every(required=>equipmentOperational(required));
    const tier=['','Grad Student','POSTDOC','PROFESSOR'][item.tier] || 'FIELD';
    const priceLabel=item.consumable?`${cash(item.price)} / ${item.units} unit${item.units===1?'':'s'} · max ${item.maxUnits??'∞'}`:item.builtIn?'STANDARD':cash(item.price);
    let actionLabel, disabled=false;
    if (item.builtIn) { actionLabel='Standard vessel equipment'; disabled=true; }
    else if (item.consumable) { actionLabel=purchase.ready?`Buy ${purchase.loadUnits} · ${cash(purchase.purchaseCost)}`:purchase.reason; disabled=!purchase.ready; }
    else if (installed) { actionLabel=`Sell equipment · ${cash(item.price*EQUIPMENT_RESALE_RATE)}`; }
    else { actionLabel=purchase.ready?'Purchase & install':purchase.reason; disabled=!purchase.ready; }
    const details=(item.specs||[]).map(value=>`<li>${escapeHtml(value)}</li>`).join('');
    const action=installed&&!item.builtIn&&!item.consumable?'sell-equipment':'equipment';
    const status=ready?'OPERATIONAL WITH CURRENT CREW':item.consumable&&inventory<=0?(supportReady?'CURRENT CREW READY · NO UNITS ABOARD':`CURRENT CREW CANNOT OPERATE · ${tier} SUPPORT NEEDED`):installed?`NOT OPERABLE · ${tier}-LEVEL SUPPORT NEEDED`:supportReady?'CURRENT CREW CAN OPERATE':'CURRENT CREW CANNOT OPERATE';
    const purchasable=item.builtIn||installed||purchase.ready, missions=missionsForEquipment(item.id);
    return `<details class="arx-card arx-store-details equipment ${installed||inventory?'selected':''} ${installed&&!ready?'inoperable':''} ${purchasable?'':'locked'}" data-arx-store-details="equipment-${item.id}"><summary><span><b>${escapeHtml(item.name)}</b><small>${item.consumable?`EXPENDABLE · ${inventory}/${item.maxUnits??'∞'} ABOARD`:`${item.slots||0} ${(item.slotType||'light').toUpperCase()} SLOT${item.slots===1?'':'S'} · TIER ${item.tier}`} · ${status}</small></span><em ${purchasable?'':'style="color:#f97367"'}>${priceLabel}</em></summary><div class="arx-detail-split">${mediaMarkup(item,'compact')}<div><p>${escapeHtml(item.description)}</p><ul class="arx-spec-list">${details}</ul><div class="arx-requirement ${ready||(!installed&&supportReady)?'ready':''}"><b>${status}</b><span>${escapeHtml(requirementText(item))}</span></div><div class="arx-requirement ready"><b>RESEARCH PROGRAMS UNLOCKED</b><span>${escapeHtml(missions.slice(0,5).join(' · ')||'Field support and opportunistic observations')}</span></div><button class="${action==='sell-equipment'?'danger':''}" data-arx-action="${action}" data-id="${item.id}" ${disabled?'disabled':''}>${actionLabel}</button></div></div></details>`;
  }
  function emptySlotMarkup(ship=vessel()) {
    const usage=slotUsage(), tiles=[];
    for (const type of SLOT_TYPES) {
      const free=Math.max(0,(ship.slots[type]||0)-(usage[type]||0));
      for (let i=0;i<Math.min(free,12);i++) tiles.push(`<div class="arx-empty-slot ${type}"><b>＋</b><span>EMPTY ${type.toUpperCase()} SLOT</span></div>`);
      if (free>12) tiles.push(`<div class="arx-empty-slot ${type}"><b>+${free-12}</b><span>MORE ${type.toUpperCase()} SLOTS</span></div>`);
    }
    return tiles.join('')||'<div class="arx-empty-slot full"><b>✓</b><span>ALL SCIENCE SLOTS OCCUPIED</span></div>';
  }
  function equipmentCategory(item) {
    const text=`${item?.id||''} ${item?.name||''} ${(item?.specialties||[]).join(' ')}`.toLowerCase();
    if(item?.consumable)return 'Consumables & Sample Supplies';
    if(/drone|aerostat|atmos|weather|radar|radiometer|lidar|starlink|satellite/.test(text))return 'Atmosphere, Remote Sensing & Communications';
    if(/mooring|glider|float|auv|rov|autonomous|drifter/.test(text))return 'Autonomous Platforms & Moorings';
    if(/plankton|fish|fisher|edna|biology|ecology|mammal|hydrophone|net/.test(text))return 'Biology & Ecology';
    if(/ice|snow|sediment|core|magnet|geophys|seafloor/.test(text))return 'Sea Ice, Seafloor & Geophysics';
    if(/ctd|adcp|xbt|winch|current|salin|echo|sonar|hydrograph|water/.test(text))return 'Oceanography & Hydrography';
    return 'General Science Systems';
  }
  function categorizedEquipmentMarkup(items) {
    const order=['Oceanography & Hydrography','Biology & Ecology','Sea Ice, Seafloor & Geophysics','Atmosphere, Remote Sensing & Communications','Autonomous Platforms & Moorings','Consumables & Sample Supplies','General Science Systems'],groups=new Map();
    for(const item of items){const category=equipmentCategory(item);if(!groups.has(category))groups.set(category,[]);groups.get(category).push(item);}
    return order.filter(category=>groups.has(category)).map(category=>`<section class="arx-equipment-category"><h3 style="margin-top:18px">${escapeHtml(category)}</h3><div class="arx-grid arx-store-list">${groups.get(category).map(equipmentCard).join('')}</div></section>`).join('');
  }
  function equipmentCatalogMarkup(ship=vessel()) {
    const items=equipmentForVessel(ship), aboard=items.filter(item=>isInstalled(item.id)||(item.consumable&&(state.inventory[item.id]||0)>0)), available=items.filter(item=>!aboard.includes(item)), usage=slotUsage();
    return `<div class="arx-slot-banner"><b>SCIENCE DECK</b><span>${slotSummary(ship,usage)} · helidecks ${helideckUsage()}/${ship.helidecks}</span><small>Trade-in value is 100% of purchase price, so swapping equipment is encouraged.</small></div><h3>Already aboard</h3><div class="arx-grid arx-store-list">${aboard.map(equipmentCard).join('')||'<div class="arx-empty"><b>No portable science equipment aboard.</b></div>'}</div><div class="arx-empty-slots">${emptySlotMarkup(ship)}</div><h3 style="margin-top:22px">Available equipment by category</h3>${categorizedEquipmentMarkup(available)||'<div class="arx-empty"><b>No further compatible equipment at this port.</b></div>'}`;
  }
  function missionFoodProjection(item) {
    const resources=callbacks.getResources?.()||{fuel:100,food:100}, hours=remainingWorkHours(item), days=effectiveDays(item,hours);
    const estimate=callbacks.estimateMissionResources?.(item,{workDays:days,workHours:hours})||{};
    const remaining=Number.isFinite(estimate.foodAfter)?estimate.foodAfter:resources.food-days*100/vessel().foodEnduranceDays;
    const fuelRemaining=Number.isFinite(estimate.fuelAfter)?estimate.fuelAfter:resources.fuel;
    return {days,remaining,fuelRemaining,travelDays:estimate.travelDays||0,returnKm:estimate.returnKm||0};
  }
  function missionReadiness(target) {
    const projection=missionFoodProjection(target), rows=[],player=playerScientist();
    const teamReady=hasSpecialty(target);
    rows.push({label:'Qualified science team',ready:teamReady,detail:target.anyScientist?`${player?.name||'You'} · Chief Scientist qualifies`:target.specialties.map(id=>specialtyById[id]?.name||id).join(' / ')});
    const requirements=missionSpecialistRequirements(target);
    if(requirements.length){const assignment=specialistAssignment(target),names=requirements.map(requirement=>`${CAREERS[requirement.minCareer]?.name||requirement.minCareer}: ${(requirement.specialties||[]).map(id=>specialtyById[id]?.name||id).join(' / ')}`);rows.push({label:`Interdisciplinary specialists · ${requirements.length}`,ready:assignment.missing===0,detail:assignment.missing?`${assignment.missing} specialist position${assignment.missing===1?'':'s'} still missing · ${names.join(' + ')}`:names.join(' + ')});}
    const minCrew=target.minCrew||missionMinCrew(target);
    rows.push({label:'Minimum expedition team',ready:state.scientists.length>=minCrew,detail:`${state.scientists.length} aboard · ${minCrew} required`});
    if (target.berthReserve) {
      const free=Math.max(0,vessel().berths-state.scientists.length);
      rows.push({label:'Berths for visiting field team',ready:free>=target.berthReserve,detail:`${free} free · ${target.berthReserve} required`});
    }
    for (const id of target.equipment||[]) {
      const item=EQUIPMENT[id], ready=equipmentOperational(id);
      rows.push({label:item?.name||id,ready,detail:ready?'Aboard and operable':isInstalled(id)||state.inventory[id]?'Aboard, but the required operator or support system is missing':'Not aboard'});
    }
    rows.push({label:'Food reserve',ready:projection.remaining>=5,detail:`Projected ${Math.round(projection.remaining)}% after mission`});
    if(!vessel().nuclearFuel)rows.push({label:'Fuel reserve',ready:projection.fuelRemaining>=3,detail:`Projected ${Math.round(projection.fuelRemaining)}% after mission`});
    return {ready:rows.every(row=>row.ready),rows,projection};
  }
  function readinessMarkup(readiness) {
    return `<div class="arx-readiness">${readiness.rows.map(row=>`<div class="${row.ready?'ready':'missing'}"><i>${row.ready?'✓':'!'}</i><span><b>${escapeHtml(row.label)}</b><small>${escapeHtml(row.detail)}</small></span></div>`).join('')}</div>`;
  }
  function missingMissionEquipmentIds(target) {
    const missing=[],seen=new Set();
    const visit=id=>{if(!id||seen.has(id))return;seen.add(id);const item=EQUIPMENT[id];if(!item)return;for(const required of item.requiresEquipment||[])visit(required);const aboard=item.consumable?(state.inventory[id]||0)>0:isInstalled(id);if(!aboard)missing.push(id);};
    [...new Set([...(target.equipment||[]),...(target.consumables||[])])].forEach(visit);
    return missing;
  }
  function missingEquipmentShopMarkup(target) {
    const ids=missingMissionEquipmentIds(target);if(!ids.length)return'';
    return `<div class="arx-missing-equipment-links">${ids.map(id=>`<button data-arx-action="shop-equipment" data-id="${escapeHtml(id)}">EQUIPMENT SHOP · ${escapeHtml(EQUIPMENT[id]?.name||id)}</button>`).join('')}</div>`;
  }
  function offerCard(item) {
    const specialty=item.anyScientist?'Any scientist aboard':item.specialties.map(id=>specialtyById[id]?.name).filter(Boolean).join(' / '),media=canonicalMissionMedia(item);
    const readiness=missionReadiness(item),missing=readiness.rows.find(row=>!row.ready),projection=missionFoodProjection(item),cap=grantLoad()>=grantCapacity(),foodUnsafe=projection.remaining<15,fuelUnsafe=!vessel().nuclearFuel&&projection.fuelRemaining<10,blocked=!readiness.ready;
    const label=blocked?`MISSING · ${missing?.label||'REQUIRED CAPABILITY'}`:cap?`ACTIVE GRANT LIMIT ${grantLoad()}/${grantCapacity()}`:foodUnsafe?`INSUFFICIENT FOOD · PROJECTED ${Math.max(0,Math.floor(projection.remaining))}%`:fuelUnsafe?`INSUFFICIENT FUEL · PROJECTED ${Math.max(0,Math.floor(projection.fuelRemaining))}%`:'ACCEPT RESEARCH GRANT';
    const missingNote=blocked?`<div class="arx-requirement"><b>NOT READY</b><span>${escapeHtml(missing?.detail||missing?.label||'Purchase or restore the missing capability, then return to this grant.')}</span></div>${readinessMarkup(readiness)}${missingEquipmentShopMarkup(item)}`:'';
    return `<article class="arx-card offer research-offer ${blocked?'locked':''}"><div class="arx-offer-thumb"><img src="${escapeHtml(media?.src||MEDIA.fieldKit.src)}" alt="${escapeHtml(media?.alt||item.title)}"></div><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(specialty)}</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p>${missingNote}<div class="arx-grant-advance"><span><small>PAYMENT ON COMPLETION</small><b>${cash(item.reward)}</b></span></div><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class="arx-mini-label">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class="arx-stats"><span>+${item.data} data</span><span>${item.minCrew||missionMinCrew(item)} people minimum</span><span>${item.supplies} supplies</span><span>${item.workHours} person-hours</span><span>~${projection.days} field days</span>${item.iceValueMultiplier>1?`<span>ICE DATA VALUE ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>Food on return ~${Math.max(0,Math.floor(projection.remaining))}%</span><span>Fuel on return ~${Math.max(0,Math.floor(projection.fuelRemaining))}%</span></div><button data-arx-action="accept" data-id="${item.id}" ${blocked||cap||foodUnsafe||fuelUnsafe?'disabled':''}>${escapeHtml(label)}</button></article>`;
  }
  function activeGrantCard(item) {
    const missing=!eligible(item), projection=missionFoodProjection(item);
    const recovery=!!item.deploymentId,teamPickup=item.missionMode==='staged-recovery';
    return `<article class="arx-card grant"><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${recovery?'RETURN VISIT REQUIRED':missing?'CAPABILITY CURRENTLY MISSING':'READY'} · ${Math.round(item.workHours)} PERSON-HOURS</small></div><em>${cash(item.reward)}</em></div><p>${escapeHtml(item.description)}</p><h4 class="arx-mini-label">RESPONSIBLE SCIENTISTS</h4>${operationScientistsMarkup(item)}<h4 class="arx-mini-label">EQUIPMENT USED</h4>${operationEquipmentMarkup(item)}<div class="arx-stats"><span>${item.data} data</span><span>Payment ${cash(item.reward)} on completion</span>${item.iceValueMultiplier>1?`<span>ICE DATA VALUE ×${item.iceValueMultiplier.toFixed(2)}</span>`:''}<span>~${projection.days} field days</span><span>Projected food ${Math.max(0,Math.floor(projection.remaining))}%</span></div><div class="arx-grant-actions"><button class="danger" data-arx-action="drop-grant" data-id="${item.id}" ${recovery&&!teamPickup?'disabled':''}>${recovery?(teamPickup?'DROP RETURN PICKUP':'DEPLOYED EQUIPMENT MUST BE RECOVERED'):'DROP RESEARCH GRANT'}</button></div></article>`;
  }
  function collectingGrantCard(item) {
    const teamPickup=item.recoveryMode==='staged-recovery';
    return `<article class="arx-card grant"><div class="arx-card-head"><div><b>${escapeHtml(item.title)}</b><small>${teamPickup?'FIELD TEAM ASHORE · RETURN VISIT PENDING':'INSTRUMENT COLLECTING · RETURN VISIT PENDING'}</small></div><em>${Math.max(0,Math.ceil(item.remainingDays||0))} d</em></div><p>${teamPickup?'The shore party is working independently. You can return for them when ready, or hand their pickup to local logistics and drop the return visit.':'Autonomous observations are underway. This research grant continues to occupy one scientist-led grant slot until recovery.'}</p>${teamPickup?`<button class="danger" data-arx-action="abandon-deployment" data-id="${item.id}">DROP RETURN PICKUP</button>`:'<button disabled>RECOVERY WINDOW NOT OPEN YET</button>'}</article>`;
  }

  function relocationPorts(force=false) { const key=`${state.currentVessel}:${Math.floor((state.elapsedDays||0)*2)}`;if(!force&&relocationPortCache.key===key)return relocationPortCache.ports;const ports=(callbacks.getRelocationPorts?.()||[]).map(item=>({...item,id:item.id||slug(item.name)}));relocationPortCache={key,ports};return ports; }
  function emergencyRelocationAllowed() {
    if(playerCareerLevel()>=2||['icebreaker','nuclear'].includes(state.currentVessel))return false;
    const currentId=normalizedPortId(state.port),current=relocationPorts().find(item=>item.id===currentId);
    return !!current?.frozen;
  }
  function relocationUnlocked() { return playerCareerLevel()>=2||emergencyRelocationAllowed(); }
  function relocationPanelMarkup() {
    const ports=relocationPorts(),emergency=playerCareerLevel()<2&&emergencyRelocationAllowed();
    if (!relocationUnlocked()) return '<div class="arx-empty"><b>POSTDOCTORAL CAREER REQUIRED</b><p>Relocating the expedition home port unlocks when the Chief Scientist reaches postdoctoral status.</p></div>';
    const currentId=normalizedPortId(state.port),homeId=state.homePortId||'longyearbyen';
    return `<p class="arx-help">${emergency?'EMERGENCY RELOCATION · Your current port is frozen in, so relocation is temporarily available before postdoctoral status. ':''}Move the entire expedition and vessel to another Arctic home port for ${cash(RELOCATION_COST)}. Frozen destination ports remain selectable only aboard an icebreaker.</p><div class="arx-relocation-list">${ports.map(port=>{const current=port.id===currentId,home=port.id===homeId,frozen=!!port.frozen,available=port.relocationAvailable!==false,poor=state.money<RELOCATION_COST,blocked=frozen&&!available;return `<article class="arx-relocation-row ${blocked?'frozen':''}"><div><b>${escapeHtml(port.name)}</b><small>${escapeHtml(port.country||'Arctic')} ${home?'· CURRENT HOME PORT':''}</small></div><span>${frozen?`FROZEN IN · ${escapeHtml(port.iceLabel||'SEA ICE')}${available?' · ICEBREAKER ACCESS':''}`:escapeHtml(port.iceLabel||'OPEN')}</span><button data-arx-action="relocate-port" data-id="${escapeHtml(port.id)}" ${current||blocked||poor?'disabled':''}>${current?'CURRENT PORT':blocked?'UNAVAILABLE':poor?'INSUFFICIENT CASH':`RELOCATE · ${cash(RELOCATION_COST)}`}</button></article>`;}).join('')}</div>`;
  }
  function relocateHomePort(id) {
    if (!relocationUnlocked()) { toast('POSTDOCTORAL CAREER REQUIRED'); return; }
    const port=relocationPorts().find(item=>item.id===id); if(!port) return;
    if (port.frozen&&port.relocationAvailable===false) { toast(`${port.name.toUpperCase()} · PORT CURRENTLY FROZEN IN`); return; }
    if (state.money<RELOCATION_COST) { toast(`RELOCATION REQUIRES ${cash(RELOCATION_COST)}`); return; }
    const oldMoney=state.money; adjustMoney(-RELOCATION_COST); state.homePortId=id;
    closePort(); relocationPortCache={key:null,ports:[]};
    const moved=callbacks.relocateToPort?.(id);
    if (!moved) { state.money=oldMoney; cashAnimation={from:oldMoney-RELOCATION_COST,to:oldMoney}; toast('RELOCATION FAILED · PORT APPROACH UNAVAILABLE'); changed(); return; }
    addLog(`Home port relocated to ${port.name}, ${port.country||'Arctic'} · ${cash(RELOCATION_COST)}.`);
    toast(`HOME PORT RELOCATED · ${port.name.toUpperCase()}`); callbacks.onStateChange?.();
  }

  function capturePortView() {
    if (!root) return;
    const card=root.querySelector('.arx-port-card'), tabs=card?.querySelector('.arx-tabs');
    if (card) portScrollTop=card.scrollTop;
    if (tabs) portTabsScrollLeft=tabs.scrollLeft;
    const opened=card?.querySelector('[data-arx-store-details][open]');
    openStoreDetail=opened?.dataset.arxStoreDetails || null;
  }
  function resupplyAllQuote(resources,ship=vessel()) {
    const fuelMissing=ship.nuclearFuel?0:Math.max(0,100-resources.fuel);
    const foodMissing=Math.max(0,100-resources.food);
    const supplyMissing=Math.max(0,ship.supplyCapacity-state.supplies);
    return Math.round(fuelMissing/10*fuelStepCost(ship)+foodMissing/10*foodStepCost(ship)+supplyMissing/10*2500);
  }
  function portVesselDashboardMarkup(resources,ship,quote) {
    const installed=[...ship.standardEquipment,...state.installedEquipment].map(id=>EQUIPMENT[id]).filter(Boolean), usage=slotUsage();
    const scientistTiles=state.scientists.map(item=>{const profile=profileFor(item);return `<div class="arx-dashboard-thumb scientist"><img src="${escapeHtml(profile.portrait)}" alt=""><span>${escapeHtml(item.name)}</span></div>`;}).join('');
    const emptyBerths=Array.from({length:Math.min(8,Math.max(0,ship.berths-state.scientists.length))},()=>'<div class="arx-dashboard-thumb empty"><b>＋</b><span>EMPTY BERTH</span></div>').join('');
    const equipmentTiles=installed.map(item=>`<div class="arx-dashboard-thumb equipment ${equipmentOperational(item.id)?'':'inoperable'}"><img src="${escapeHtml(item.media?.src||MEDIA.local.src)}" alt=""><span>${escapeHtml(item.name)}</span></div>`).join('');
    const grantTiles=activeGrants().map(item=>`<div class="arx-dashboard-thumb grant"><img src="${escapeHtml(item.media?.src||MEDIA.local.src)}" alt=""><span>${escapeHtml(item.shortTitle||item.title)}</span></div>`).join('')||'<div class="arx-dashboard-thumb empty"><b>＋</b><span>NO ACTIVE GRANTS</span></div>';
    const fCost=fuelStepCost(ship), provisionCost=foodStepCost(ship), fuelAmount=ship.nuclearFuel?'REACTOR':formatCapacity(ship.fuelCapacity*resources.fuel/100,'L'), foodAmount=formatCapacity(ship.foodCapacity*resources.food/100,'kg');
    return `<div class="arx-resupply-block arx-resupply-top"><h3>Consumables & stores</h3><button class="arx-resupply-all" data-arx-action="resupply-all" ${quote<=0||state.money<quote?'disabled':''}>RESUPPLY ALL · ${cash(quote)}</button><div class="arx-resupply"><article><small>FUEL · ${Math.ceil(resources.fuel)}%</small><b>${fuelAmount}</b><span>${ship.nuclearFuel?'Indefinite reactor endurance':`${ship.fuelEnduranceDays} days at 50% cruise`}</span><button data-arx-action="fuel" ${ship.nuclearFuel||resources.fuel>=99||state.money<fCost?'disabled':''}>${ship.nuclearFuel?'NO REFUELING NEEDED':`+10% · ${cash(fCost)}`}</button></article><article><small>FOOD · ${Math.ceil(resources.food)}%</small><b>${foodAmount}</b><span>${ship.foodEnduranceDays} days from full</span><button data-arx-action="food" ${resources.food>=99||state.money<provisionCost?'disabled':''}>+10% · ${cash(provisionCost)}</button></article><article><small>LAB SUPPLIES</small><b>${state.supplies}/${ship.supplyCapacity}</b><span>Consumed by field stations</span><button data-arx-action="supplies" ${state.supplies>=ship.supplyCapacity||state.money<2500?'disabled':''}>+10 · ${cash(2500)}</button></article><article><small>DAILY PAYROLL</small><b>${cash(payroll())}</b><span>Includes your Chief Scientist salary</span></article></div></div><div class="arx-port-vessel-dashboard compact-dashboard"><section class="crew-orbit"><h3>Team · ${state.scientists.length}/${ship.berths}</h3><div class="arx-dashboard-thumbs">${scientistTiles}${emptyBerths}</div></section><div class="arx-dashboard-ship"><small>${escapeHtml(ship.className)}</small><h2>${escapeHtml(ship.shipName||ship.name)}</h2><img src="${escapeHtml(ship.image||'assets/vessels/base-vessel.png')}" alt=""><div class="arx-dashboard-stats"><span>${slotSummary(ship,usage)}</span><span>Payroll ${cash(payroll())}/day</span></div></div><section class="equipment-orbit"><h3>Equipment</h3><div class="arx-dashboard-thumbs">${equipmentTiles}${emptySlotMarkup(ship)}</div></section></div>`;
  }
  function openPrivateFunding() {
    if (!root||!state.port) return;
    const modal=root.querySelector('#arx-funding-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-funding-card"><button class="arx-close" data-arx-action="close-private-funding" aria-label="Close private funding">×</button><small>PRIVATE RESEARCH BACKING</small><h2>Apply for Private Funding</h2><p>Accelerate the expedition with an unrestricted private research contribution.</p><div class="arx-web-preview"><b>WEB PREVIEW · NO REAL CHARGE</b><span>Purchases are simulated in this browser build. In the iOS app, these same product IDs will be fulfilled through StoreKit.</span></div><div class="arx-funding-balance"><small>CURRENT EXPEDITION CASH</small><b data-arx-cash>${cash(state.money)}</b></div><div class="arx-funding-grid">${PRIVATE_FUNDING_PACKAGES.map((item,index)=>`<article class="${index===1?'featured':''}"><small>${index===0?'STARTER BACKING':index===1?'POPULAR':'MAJOR SPONSOR'}</small><b>${item.label}</b><span>game cash</span><button data-arx-action="buy-private-funding" data-id="${item.id}">${item.price}</button></article>`).join('')}</div><p class="arx-funding-note">Private funding is a consumable purchase: each successful transaction adds the selected amount to expedition cash and does not alter research progress, career level, or vessel requirements.</p></div>`;
    modal.classList.add('open');
  }
  async function purchasePrivateFunding(id,button) {
    const item=PRIVATE_FUNDING_PACKAGES.find(pack=>pack.id===id); if(!item)return;
    const originalLabel=button?.textContent||item.price;
    if(button){button.disabled=true;button.textContent='PROCESSING…';}
    let result={success:true,mode:'web-preview'};
    try {
      const adapter=window.ArcticResearchIAP;
      if(adapter&&typeof adapter.purchase==='function') {
        const response=await adapter.purchase(item.productId);
        if(response===false||response?.success===false) result={success:false,mode:'storekit',message:response?.message||'Purchase was not completed'};
        else result={success:true,mode:'storekit',transactionId:response?.transactionId||null};
      }
    } catch(error) {
      result={success:false,mode:'storekit',message:error?.message||'Purchase failed'};
    }
    if(!result.success){if(button){button.disabled=false;button.textContent=originalLabel;}toast((result.message||'PURCHASE NOT COMPLETED').toUpperCase());return;}
    adjustMoney(item.gameCash);
    addLog(`Private funding received: ${cash(item.gameCash)}${result.mode==='web-preview'?' · web preview transaction':''}.`);
    root.querySelector('#arx-funding-modal')?.classList.remove('open');
    toast(`PRIVATE FUNDING SECURED · ${cash(item.gameCash)}`); changed();
  }

  function updatePortTabHints(tabs) {
    if (!tabs) return;
    const viewport=tabs.closest('.arx-tabs-viewport'); if(!viewport) return;
    const left=viewport.querySelector('.arx-tab-hint.left'), right=viewport.querySelector('.arx-tab-hint.right');
    const max=Math.max(0,tabs.scrollWidth-tabs.clientWidth), epsilon=2;
    left?.classList.toggle('hidden',max<=epsilon||tabs.scrollLeft<=epsilon);
    right?.classList.toggle('hidden',max<=epsilon||tabs.scrollLeft>=max-epsilon);
  }

  let grantRefreshTimer=0;
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
  }
  function refreshProgressionOpportunities(reason='progression') {
    const removed=new Set(state.targets.filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!item.accepted&&item.status!=='completed').map(item=>item.id));
    if(removed.size){state.targets=state.targets.filter(item=>!removed.has(item.id));if(state.navigation&&removed.has(state.navigation.id))state.navigation=null;if(state.lastTargetContext&&removed.has(state.lastTargetContext.id))state.lastTargetContext=null;}
    state.grantOfferCycle=null;
    if(state.port){generateCandidates(state.port);refreshGrantOffersNow({render:true});}
    callbacks.onProgressionChanged?.({reason});
  }

  function portPanelMarkup(tab,resources,ship,quote,usage,collecting){
    if(tab==='vessel')return portVesselDashboardMarkup(resources,ship,quote);
    if(tab==='fleet')return `<h3>${isRussianPort()?'Russian Nuclear Shipyard':normalizedPortId()==='longyearbyen'?'Longyearbyen Vessel Broker':'Arctic Vessel Broker'}</h3><p class="arx-help">Every vessel class sold here is displayed from the start. Trade-in credit and the actual purchase amount are shown separately.</p><div class="arx-grid arx-store-list">${vesselsForPort().map(vesselCard).join('')||'<div class="arx-empty"><b>No vessels sold at this port.</b></div>'}</div>`;
    if(tab==='crew')return `<p class="arx-help">Salaries are deducted daily for everyone aboard, including you. All hired scientists share one citation budget: 10 per graduate student, 100 per postdoc, and 1,000 per professor.</p><div class="arx-vessel-columns"><section><h3>Available to hire · ${citationCapacityUsed()}/${Math.floor(state.citations)} citations used</h3><div class="arx-grid arx-store-list">${state.candidates.map(item=>scientistCard(item,true)).join('')||'<div class="arx-empty"><b>No new candidates at this port.</b></div>'}</div></section><section><h3>Current crew · ${state.scientists.length}/${ship.berths}</h3><div class="arx-grid arx-store-list">${state.scientists.map(item=>scientistCard(item)).join('')}</div></section></div>`;
    if(tab==='equipment')return `<h3>Scientific instrumentation for ${escapeHtml(ship.shipName||ship.name)}</h3><p class="arx-help">${slotSummary(ship,usage)}${ship.helidecks?` · helidecks ${helideckUsage()}/${ship.helidecks}`:''}. Equipment that loses its qualified operator is marked in red until the team is restored.</p>${equipmentCatalogMarkup(ship)}`;
    if(tab==='contracts')return `<h3>Active research grants · ${grantLoad()}/${grantCapacity()}</h3><p class="arx-help">More scientific specialties aboard produce a broader grant board. A different port always has its own fresh market; only return visits to the same port use cooldowns. Ice-capable expeditions can produce especially valuable data in thicker pack ice.</p><div class="arx-grid">${[...activeGrants().map(activeGrantCard),...collecting.map(collectingGrantCard)].join('')||'<div class="arx-empty"><b>No active research grants.</b></div>'}</div><h3>New grant offers</h3><div class="arx-grid">${state.offers.map(offerCard).join('')||'<div class="arx-empty"><b>Building a compatible sponsor call…</b><p>Grant opportunities are generated after the port screen opens so port entry stays immediate.</p></div>'}</div>`;
    if(tab==='relocate'&&relocationUnlocked())return `<h3>Relocate home port</h3>${relocationPanelMarkup()}`;
    return portVesselDashboardMarkup(resources,ship,quote);
  }
  function renderPort() {
    if (!root) return;
    capturePortView();
    const modal=root.querySelector('#arx-port-modal'), resources=callbacks.getResources?.()||{fuel:100,food:100}, ship=vessel(), quote=resupplyAllQuote(resources,ship), usage=slotUsage();
    if(activePortTab==='relocate'&&!relocationUnlocked())activePortTab='vessel';
    const tab=(id,label,attention=false)=>`<button data-arx-tab="${id}" class="${activePortTab===id?'active':''} ${attention?'attention':''}">${label}</button>`;
    const collecting=(state.deployments||[]).filter(item=>item.originalKind==='grant'&&item.status==='collecting'), grantAttention=state.offers.length>0&&grantLoad()<grantCapacity();
    const crewAttention=state.scientists.length<ship.berths&&state.candidates.some(item=>careerHireStatus(item.career).ready);
    const vesselRanks={fishing:0,trawler:1,coastal:2,global:3,icebreaker:4,nuclear:5},currentRank=vesselRanks[state.currentVessel]??0;
    const fleetAttention=vesselsForPort().some(item=>(vesselRanks[item.id]??-1)>currentRank&&vesselPurchaseReady(item));
    const panelMarkup=portPanelMarkup(activePortTab,resources,ship,quote,usage,collecting);
    modal.innerHTML=`<div class="arx-modal-card arx-port-card"><button class="arx-close" data-arx-action="close-port" aria-label="Close port">×</button><header><small>PORT CALL · ${escapeHtml(state.port?.name||'ARCTIC PORT')}</small><h2>Expedition Services</h2></header><div class="arx-port-navrow"><div class="arx-tabs-viewport"><i class="arx-tab-hint left">‹</i><nav class="arx-tabs arx-tabs-top">${tab('vessel','Your Vessel')}${tab('fleet','Shipyard',fleetAttention)}${tab('crew','Scientists',crewAttention)}${tab('equipment','Equipment')}${tab('contracts','Research Grants',grantAttention)}${relocationUnlocked()?tab('relocate','Relocate Home Port'):''}</nav><i class="arx-tab-hint right">›</i></div><div class="arx-port-cash"><span><small>CASH</small><b data-arx-cash>${cash(state.money)}</b></span><button data-arx-action="open-private-funding">APPLY FOR PRIVATE FUNDING</button></div></div>${state.bridgeSupportNotice?`<div class="arx-bridge-support"><b>UNIVERSITY BRIDGE SUPPORT</b><span>${escapeHtml(state.bridgeSupportNotice)}</span></div>`:''}<section class="arx-tab active" data-arx-panel="${activePortTab}">${panelMarkup}</section></div>`;
    modal.classList.add('open'); portOpen=true;
    const card=modal.querySelector('.arx-port-card'), tabs=card.querySelector('.arx-tabs'); card.scrollTop=portScrollTop; tabs.scrollLeft=portTabsScrollLeft;
    const syncTabHints=()=>updatePortTabHints(tabs); tabs.addEventListener('scroll',syncTabHints,{passive:true}); requestAnimationFrame(syncTabHints);
    const detail=openStoreDetail&&card.querySelector(`[data-arx-store-details="${openStoreDetail}"]`); if (detail) detail.open=true;
    animateCashReadouts();
  }
  function deploymentSummary() {
    const active=state.deployments.filter(item=>item.status==='collecting'||item.status==='awaiting-recovery');
    if (!active.length) return '';
    return `<section class="arx-deployments"><small>AUTONOMOUS PROGRAMS</small>${active.slice(0,4).map(item=>`<div><span>${escapeHtml(item.title)}<em>${item.status==='awaiting-recovery'?'RECOVERY READY':`${Math.max(0,Math.ceil(item.remainingDays))} d remaining`}</em></span><b>${item.recoveryRequired?'MOORING':'TELEMETRY'}</b></div>`).join('')}</section>`;
  }
  function renderSidebar() {
    if (!root) return;
    const ship=vessel(), nav=state.navigation, readiness=dataGaugePercent(), level=currentPaperLevel();
    const next=PAPER_LEVELS.find(item=>state.data<item.threshold), chance=level?publicationChance(level):0;
    const cool=state.publicationCooldown>0?`${Math.ceil(state.publicationCooldown)} d submission cooldown`:!level?`${Math.ceil(PUBLISH_MIN-state.data)} more data for a Letter`:level.next?`${level.label} ready · ${Math.round(chance*100)}% acceptance`:'Book threshold reached · automatic publication';
    const papers=[...state.papers].reverse().slice(0,3), navOpportunity=nav?.target&&(nav.target.kind==='opportunity'||nav.target.kind==='weather-opportunity'), publishLabel=!level?'PUBLISH LETTER':level.id==='local'?'PUBLISH LETTER':level.id==='national'?'PUBLISH ARTICLE':'AUTO-PUBLISH BOOK';
    root.querySelector('#arx-sidebar').innerHTML=`<div class="arx-side-head"><div><small>RESEARCH PROGRAM</small><b data-arx-cash>${cash(state.money)}</b></div><button data-arx-action="toggle-side" aria-label="Close research panel">×</button></div><div class="arx-metrics"><span><small>CITATIONS</small><b>${Math.floor(state.citations)}</b><em>${state.papers.length} PAPER${state.papers.length===1?'':'S'}</em></span><span><small>LAB SUPPLIES</small><b>${state.supplies}/${ship.supplyCapacity}</b></span><span><small>GRANTS</small><b>${grantLoad()}/${grantCapacity()}</b></span></div><section class="arx-data"><div><small>PUBLICATION DATA</small><b>${Math.round(state.data)}</b></div><i class="arx-nonlinear-gauge"><em style="width:${readiness}%"></em><u style="left:12%"></u><u style="left:50%"></u></i><div class="arx-gauge-labels"><span>LETTER</span><span>ARTICLE</span><span>BOOK</span></div><p>${escapeHtml(cool)}${next?` · next threshold ${new Intl.NumberFormat().format(next.threshold)} data`:''}</p><button class="publish" data-arx-action="publish" ${!level||state.publicationCooldown>0||!level.next?'disabled':''}>${publishLabel}</button></section>${papers.length?`<section class="arx-papers"><small>PUBLICATIONS · CITATIONS GROW DAILY</small>${papers.map(paper=>`<div><span>${escapeHtml(paper.title)}<em>${escapeHtml(paper.journal)} · ${Math.floor(paper.ageDays||0)} d old</em></span><b>${paper.citations||0}</b></div>`).join('')}</section>`:''}${deploymentSummary()}${nav?`<button class="arx-nav ${navOpportunity?'opportunity':''}" data-arx-action="open-nav"><span class="arx-arrow" style="transform:rotate(${nav.bearingDeg}deg)">↑</span><div><small>${navOpportunity?'DISCOVERED RESEARCH OPPORTUNITY':'ACTIVE RESEARCH GRANT'}</small><b>${escapeHtml(nav.target?.shortTitle||nav.target?.title||'RESEARCH')}</b><em>${Math.round(nav.distanceKm)} km · ${Math.round(nav.bearingDeg)}°</em></div></button>`:'<div class="arx-nav empty"><span>＋</span><div><small>NO ACTIVE SITE</small><b>Explore or visit a port for grants</b></div></div>'}<div class="arx-side-actions"><button data-arx-action="field-guide">FIELD GUIDE · ${state.observed.length}/${Object.keys(catalog).length}</button><button data-arx-action="open-port" ${state.port?'':'disabled'}>PORT SERVICES</button></div><footer>${escapeHtml(ship.shipName||ship.name)} · ${state.scientists.length}/${ship.berths} berths · payroll ${cash(payroll())}/day</footer>`;
    const researchToggle=root.querySelector('#arx-mobile-toggle'),articleReady=level?.id==='national'&&state.publicationCooldown<=0;researchToggle?.classList.remove('attention');researchToggle?.classList.toggle('article-ready',articleReady);
    animateCashReadouts();
  }

  function fullResupplyCost(ship=vessel()) {
    return (ship.nuclearFuel?0:10*fuelStepCost(ship))+10*foodStepCost(ship)+Math.ceil(ship.supplyCapacity/10)*2500;
  }
  function enterPort(port,options={}) {
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
  function closePort() { capturePortView(); root?.querySelector('#arx-port-modal')?.classList.remove('open'); portOpen=false; }
  function leavePort() { state.port=null; closePort(); renderSidebar(); }

  function renderResearchWindow(target,{phase='ready',resultTitle='',resultBody='',resultStats=[]}={}) {
    const running=phase==='running',complete=phase==='complete',programFinished=complete&&target.status==='completed';
    const readiness=missionReadiness(target),projection=readiness.projection,station=currentStation(target),stationLabel=station?`${station.number} of ${target.stations.length}`:'Single station';
    const contextDistance=state.lastTargetContext?.id===target.id?state.lastTargetContext.distanceKm:null,navDistance=state.navigation?.id===target.id?state.navigation.distanceKm:null,distance=Number.isFinite(contextDistance)?contextDistance:Number.isFinite(navDistance)?navDistance:Infinity,atSite=target.anywhere||distance<=RESEARCH_INTERACTION_KM;
    const opportunity=target.kind==='opportunity'||target.kind==='weather-opportunity',accepted=!opportunity||target.accepted===true,missing=readiness.rows.find(row=>!row.ready),participants=participantIdsFor(target),rate=workRate(target),workHours=Math.round(running?(activeOperation?.workHours||operationWorkHours(target)):remainingWorkHours(target));
    const progress=running?0:complete?100:0,steps=target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station'];
    const canBegin=accepted&&atSite&&readiness.ready&&!running&&!complete;
    const primaryLabel=running?'RESEARCH IN PROGRESS':complete?'RESEARCH COMPLETE':!atSite&&!target.anywhere?'SAIL TO SITE FIRST':readiness.ready?'BEGIN RESEARCH':`CANNOT BEGIN · ${missing?.label||'MISSING CAPABILITY'}`;
    const decline=opportunity?`<button class="${accepted?'danger':'ghost'}" data-arx-action="cancel-opportunity" data-id="${target.id}" ${running||complete?'disabled':''}>${accepted?'ABANDON OPPORTUNITY':'DECLINE'}</button>`:(target.kind==='grant'||target.kind==='contract')?`<button class="danger" data-arx-action="drop-grant" data-id="${target.id}" ${running||programFinished||(target.deploymentId&&target.missionMode!=='staged-recovery')?'disabled':''}>${target.missionMode==='staged-recovery'?'DROP RETURN PICKUP':'DROP GRANT'}</button>`:'<button class="ghost" disabled>NO DROP ACTION</button>';
    const result=resultTitle||'Research result',modal=root.querySelector('#arx-target-modal');
    const workActions=complete?'<button data-arx-action="acknowledge-research">OKAY</button>':!atSite&&!target.anywhere?`${decline}<button data-arx-action="navigate-target" data-id="${target.id}">NAVIGATE TO SITE</button>`:`${decline}<button data-arx-action="complete-target" data-id="${target.id}" ${canBegin?'':'disabled'}>${escapeHtml(primaryLabel)}</button>`;

    if(!accepted){
      modal.innerHTML=`<div class="arx-modal-card arx-target-card arx-research-unified arx-research-review"><button class="arx-close" data-arx-action="close-target" aria-label="Close research opportunity">×</button><small>${target.weather?'LIVE WEATHER RESEARCH':'DISCOVERED RESEARCH OPPORTUNITY'}</small><h2>${escapeHtml(target.title)}</h2>${mediaMarkup(target,'hero')}<p>${escapeHtml(target.description)}</p><div class="arx-target-facts arx-research-facts"><span><small>STATION</small><b>${stationLabel}</b></span><span><small>WORK</small><b>${workHours} person-hours · team rate ${rate.toFixed(1)}×</b></span><span><small>CASH AWARD</small><b>${cash(target.reward||0)}</b></span><span><small>DATA AWARD</small><b>${['mooring-deploy','staged-deploy','autonomous'].includes(target.missionMode)?'Data after telemetry / recovery':`+${target.data} data`}</b></span><span><small>DISTANCE</small><b>${target.anywhere?'REMOTE / ONBOARD':Number.isFinite(distance)?`${Math.round(distance)} km`:'OFF-SCREEN SITE'}</b></span></div><h3 class="arx-operation-subhead">RESPONSIBLE SCIENTISTS</h3>${operationScientistsMarkup(target)}<h3 class="arx-operation-subhead">EQUIPMENT USED</h3>${operationEquipmentMarkup(target)}<h3 class="arx-check-title">MISSION READINESS</h3>${readinessMarkup(readiness)}<div class="arx-research-review-actions">${decline}<button data-arx-action="accept-opportunity" data-id="${target.id}" ${atSite?'':'disabled'}>${atSite?'ACCEPT OPPORTUNITY':'ARRIVE AT SITE FIRST'}</button></div></div>`;
      modal.classList.add('open');
      return;
    }

    modal.innerHTML=`<div class="arx-modal-card arx-target-card arx-operation arx-research-unified arx-research-work ${complete?'arx-complete':''}"><button class="arx-close" data-arx-action="close-target" aria-label="Close research site" ${running?'disabled':''}>×</button><div class="arx-operation-progress"><div><b id="arx-operation-percent">${progress}%</b><span><strong>${escapeHtml(target.shortTitle||target.title)}</strong> · ${workHours} person-hours · ~${projection.days} game days · ${participants.length||1} scientist${participants.length===1?'':'s'} assigned</span></div><i><em id="arx-operation-bar" style="width:${progress}%"></em></i></div>${!readiness.ready&&!running&&!complete?`<div class="arx-work-readiness">${readinessMarkup(readiness)}</div>`:''}<ol>${steps.map((step,index)=>`<li data-arx-step="${index}" class="${complete?'done':''}"><i>${complete?'✓':index+1}</i><b>${escapeHtml(step)}</b><span>${complete?'Complete':'Queued'}</span></li>`).join('')}</ol><div class="arx-operation-result-space">${complete?`<div class="arx-research-result"><small>${escapeHtml(result)}</small><p>${escapeHtml(resultBody)}</p>${resultStats.length?`<div class="arx-chance">${resultStats.map(item=>`<span>${escapeHtml(item.label)}<b>${escapeHtml(item.value)}</b></span>`).join('')}</div>`:''}</div>`:'<div class="arx-result-placeholder">Results will appear here without replacing this research card.</div>'}</div><div class="arx-research-actions ${complete?'single':''}">${workActions}</div></div>`;
    modal.classList.add('open');
  }
  function openTarget(id,context={}) {
    const target=state.targets.find(item=>item.id===id);if(!target)return false;
    if(activeOperation&&activeOperation.targetId!==id){toast('RESEARCH STATION ALREADY IN PROGRESS');return false;}
    const distance=context.distanceKm??(state.navigation?.id===id?state.navigation.distanceKm:Infinity);
    state.targets.forEach(item=>item.selected=item.id===id);state.lastTargetContext={...context,id,distanceKm:distance};
    if(!context.preview&&!target.anywhere&&distance>RESEARCH_INTERACTION_KM){callbacks.onNavigate?.(target);renderSidebar();return true;}
    renderResearchWindow(target,{phase:activeOperation?.targetId===id?'running':'ready'});renderSidebar();return true;
  }
  function operationEquipmentMarkup(target) {
    const ids=[...(target.equipment||[]),...(target.consumables||[])],items=[...new Set(ids)].map(id=>EQUIPMENT[id]).filter(Boolean);
    if(!items.length)return `<div class="arx-operation-equipment"><div class="arx-operation-gear field-kit"><img src="${escapeHtml(MEDIA.fieldKit.src)}" alt="${escapeHtml(MEDIA.fieldKit.alt)}"><span>General Arctic Field Kit</span></div></div>`;
    return `<div class="arx-operation-equipment">${items.map(item=>`<div class="arx-operation-gear"><img src="${escapeHtml(item.media?.src||MEDIA.fieldKit.src)}" alt="${escapeHtml(item.media?.alt||item.name)}"><span>${escapeHtml(item.name)}</span></div>`).join('')}</div>`;
  }
  function operationScientistsMarkup(target) {
    const ids=participantIdsFor(target),people=state.scientists.filter(item=>ids.includes(item.id));
    return `<div class="arx-operation-scientists">${people.map(item=>{const profile=profileFor(item);return`<div><img src="${escapeHtml(profile.portrait)}" alt=""><span><b>${escapeHtml(item.name)}</b><small>${escapeHtml(specialtyById[item.specialty]?.name||item.specialty)} · ${CAREERS[item.career]?.short||item.career}</small></span></div>`;}).join('')}</div>`;
  }
  function renderOperationShell(target) { renderResearchWindow(target,{phase:'running'}); }
  function participantIdsFor(target) {
    const player=playerScientist(),requiredLevel=templateCareerLevel(target);if(target?.anyScientist)return player?[player.id]:[];
    const specialistIds=specialistAssignment(target).ids||[],ids=[...specialistIds];
    const candidates=state.scientists.filter(item=>(target.specialties||[]).includes(item.specialty)&&careerLevel(item.career)>=requiredLevel).sort((a,b)=>careerLevel(b.career)-careerLevel(a.career));
    for(const item of candidates)if(!ids.includes(item.id))ids.push(item.id);
    return ids.length?ids:(player?[player.id]:[]);
  }
  function creditSpecialtyMission(target,participantIds) {
    if (!(target.specialties||[]).length) return;
    for (const scientist of state.scientists) {
      if (!participantIds.includes(scientist.id)||(target.specialties||[]).includes(scientist.specialty)===false) continue;
      scientist.missions=(scientist.missions||0)+1; recordScientist(scientist);
    }
  }
  function updateOperation(now) {
    if (!activeOperation) return;
    const target=state.targets.find(item=>item.id===activeOperation.targetId);
    if (!target) { activeOperation=null; operationFrame=0; root.querySelector('#arx-target-modal')?.classList.remove('open'); return; }
    const progress=clamp((now-activeOperation.startedAt)/activeOperation.durationMs,0,1), percent=Math.floor(progress*100), current=Math.min(activeOperation.steps.length-1,Math.floor(progress*activeOperation.steps.length));
    const modal=root.querySelector('#arx-target-modal'), bar=modal.querySelector('#arx-operation-bar'), readout=modal.querySelector('#arx-operation-percent');
    if (bar) bar.style.width=`${percent}%`; if (readout) readout.textContent=`${percent}%`;
    modal.querySelectorAll('[data-arx-step]').forEach((row,index)=>{
      row.classList.toggle('done',progress>=1||index<current); row.classList.toggle('active',progress<1&&index===current);
      const label=row.querySelector('span'); if (label) label.textContent=progress>=1||index<current?'Complete':index===current?'In progress':'Queued';
    });
    if (progress<1) { operationFrame=requestAnimationFrame(updateOperation); return; }
    finishOperation(target);
  }
  function completionModal(target,title,body,stats=[]) { renderResearchWindow(target,{phase:'complete',resultTitle:title,resultBody:body,resultStats:stats}); }
  function settleResearch(target,dataGain) {
    const payment=Math.max(0,Number(target.reward)||0);addData(dataGain);adjustMoney(payment);
    return [{label:'DATA ARCHIVED',value:`+${dataGain}`},{label:'RESEARCH AWARD',value:cash(payment)},{label:'PAYMENT',value:'PAID ON COMPLETION'}];
  }
  function finishOperation(target) {
    const operation=activeOperation||{}, participants=operation.participantIds||participantIdsFor(target);
    activeOperation=null; operationFrame=0;
    const days=operation.days||effectiveDays(target,operation.workHours||operationWorkHours(target));
    target.lastOperationHours=operation.workHours||operationWorkHours(target);
    callbacks.onAdvanceTime?.(days);
    const station=currentStation(target);
    if (station) {
      station.status='completed';
      const nextIndex=target.stations.findIndex(item=>item.status!=='completed');
      if (nextIndex>=0) {
        target.stationIndex=nextIndex; target.lat=target.stations[nextIndex].lat; target.lon=target.stations[nextIndex].lon; target.selected=true;
        state.lastTargetContext=null; state.navigation=null;
        const done=target.stations.filter(item=>item.status==='completed').length;
        addLog(`${target.shortTitle||target.title}: station ${done}/${target.stations.length} complete.`);
        completionModal(target,`Station ${done} complete`,`The station record is secure. Station ${target.stations[nextIndex].number} is now highlighted; sail there to continue the section.`,[
          {label:'SECTION PROGRESS',value:`${done}/${target.stations.length}`},{label:'NEXT STATION',value:`${target.stations[nextIndex].number}`}
        ]);
        renderSidebar(); callbacks.onStateChange?.(); return;
      }
    }
    const quality=averageQuality(), recoveryMode=['mooring-recovery','staged-recovery'].includes(target.missionMode);
    const dataGain=recoveryMode?Math.max(1,Math.round(target.data)):Math.max(1,Math.round(target.data*(.82+quality*.18)));
    target.status='completed'; target.selected=false;
    let title='Program complete', body='The team completed the assignment and archived the station record.', stats=[];
    if (['mooring-deploy','staged-deploy'].includes(target.missionMode)) {
      const baseWait=target.recoveryAfterDaysByVessel?.[state.currentVessel]||target.recoveryAfterDays||7;
      const wait=Math.max(1,Math.round(baseWait*(.92+seeded(target.id)()*.16)));
      const staged=target.missionMode==='staged-deploy';
      state.deployments.push({id:`deployment-${target.id}`,title:target.title.replace(/^(Deploy|Deliver) /,''),lat:target.lat,lon:target.lon,status:'collecting',remainingDays:wait,recoveryRequired:true,data:dataGain,reward:target.reward,upfront:target.upfront||0,advancePaid:target.advancePaid||0,equipment:[...target.equipment],specialties:[...target.specialties],anyScientist:target.anyScientist,berthReserve:target.berthReserve||0,workHours:Math.max(6,Math.round(target.workHours*.72)),supplies:Math.max(2,Math.round(target.supplies*.55)),media:clone(target.media),recoveryTargetId:null,originalKind:target.kind,templateId:target.templateId,recoveryMode:staged?'staged-recovery':'mooring-recovery',recoveryTitle:target.recoveryTitle,recoveryShortTitle:target.recoveryShortTitle,recoveryDescription:target.recoveryDescription});
      title=staged?'Field team deployed':'Mooring deployed'; body=`${staged?'The shore or ice team is working independently':'The array is collecting autonomously'}. Return in about ${wait} game days for recovery; the full data set and sponsor payment are released only after a safe pickup.`;
      stats=[{label:'RETURN WINDOW',value:`~${wait} days`},{label:'DATA STATUS',value:'AWAITING RECOVERY'}];
      addLog(`${target.title} completed; return visit pending.`);
    } else if (recoveryMode) {
      const deployment=state.deployments.find(item=>item.id===target.deploymentId);
      if (deployment) {
        deployment.status='recovered';
        deployment.remainingDays=0;
        deployment.recoveryTargetId=null;
      }
      stats=settleResearch(target,dataGain);
      title=target.missionMode==='staged-recovery'?'Team safely recovered':'Mooring recovered';
      body=target.missionMode==='staged-recovery'?'The field party, samples and recorders are safely aboard. Their complete field record has been released to the expedition archive.':'The full instrument line is safely aboard. The team downloaded the complete time series, verified the record and released the recovered-mooring data to the expedition archive.';
      addLog(`Recovery complete: ${target.title}. Full record archived.`);
    } else if (target.missionMode==='autonomous') {
      state.deployments.push({id:`deployment-${target.id}`,title:target.title,lat:target.lat,lon:target.lon,status:'collecting',remainingDays:target.deploymentDays,recoveryRequired:false,data:dataGain,reward:target.reward,upfront:target.upfront||0,advancePaid:target.advancePaid||0,equipment:[...target.equipment],specialties:[...target.specialties],media:clone(target.media)});
      title='Autonomous platform released'; body=`Telemetry will accumulate for roughly ${target.deploymentDays} game days. This instrument is treated as expendable and may sink or go silent at the end of its mission.`;
      stats=[{label:'TELEMETRY WINDOW',value:`${target.deploymentDays} days`},{label:'RECOVERY',value:'NOT REQUIRED'}];
      addLog(`${target.title} deployed; telemetry collection underway.`);
    } else {
      stats=settleResearch(target,dataGain);
      body='The assignment is complete, the data have been archived and the sponsor has released the contracted field payment.';
      addLog(`Assignment completed: ${target.title}. Field record archived.`);
    }
    state.completed.push({...target,completedAt:Date.now(),dataGain});
    recordGrantUse(target.templateId,target);
    creditSpecialtyMission(target,participants);
    state.targets=state.targets.filter(item=>item.id!==target.id);
    checkPromotions(); completionModal(target,title,body,stats); renderSidebar(); callbacks.onStateChange?.();
  }
  function completeTarget(id,context={}) {
    const target=state.targets.find(item=>item.id===id);
    if (!target||activeOperation) return false;
    const nav=state.navigation?.id===id?state.navigation:null;
    const distance=context.distanceKm??state.lastTargetContext?.distanceKm??nav?.distanceKm??Infinity;
    if (distance>RESEARCH_INTERACTION_KM&&!target.anywhere) { callbacks.onNavigate?.(target); return false; }
    const readiness=missionReadiness(target), missing=readiness.rows.find(row=>!row.ready);
    if (!readiness.ready) { toast(`MISSION NOT READY · ${missing?.label?.toUpperCase()||'MISSING CAPABILITY'}`); return false; }
    const stationSupplies=operationSupplies(target), station=currentStation(target);
    state.supplies=Math.max(0,state.supplies-stationSupplies);
    for (const consumableId of target.consumables || []) {
      const amount=target.consumablePerStation?.[consumableId]||(station?0:1);
      if (amount) state.inventory[consumableId]=Math.max(0,(state.inventory[consumableId]||0)-amount);
    }
    callbacks.onResearchStart?.(target,station);
    const workHours=operationWorkHours(target),days=effectiveDays(target,workHours),participantIds=participantIdsFor(target),productivity=Math.max(1,workRate(target)),challenge=1+(templateCareerLevel(target)-1)*.28,durationMs=clamp(2600+(workHours/productivity)*130*challenge,3400,22000);
    activeOperation={targetId:id,startedAt:performance.now(),durationMs,workHours,days,stationIndex:target.stationIndex||0,participantIds,steps:target.steps?.length?target.steps:['Hold the science station','Calibrate instruments','Collect observations','Check sample metadata','Secure the station']};
    renderOperationShell(target); operationFrame=requestAnimationFrame(updateOperation); renderSidebar(); callbacks.onStateChange?.(); return true;
  }

  function createRecoveryTarget(deployment) {
    const staged=deployment.recoveryMode==='staged-recovery';
    const target={
      id:`recovery-${deployment.id}`,templateId:deployment.templateId||'mooring-recovery',title:deployment.recoveryTitle||`${staged?'Pick up':'Recover'} ${deployment.title}`,shortTitle:deployment.recoveryShortTitle||(staged?'FIELD PICKUP':'MOORING RECOVERY'),
      description:deployment.recoveryDescription||(staged?'The field party is ready. Return to the landing, recover everyone and bring their samples and recorders safely aboard.':'The autonomous time series is ready. Trigger the acoustic release, recover every payload section and download the full record.'),
      specialties:[...deployment.specialties],anyScientist:!!deployment.anyScientist,equipment:deployment.equipment.filter(id=>id!=='deep-mooring-payload'&&!EQUIPMENT[id]?.deploymentAsset),consumables:[],
      steps:staged?['Confirm the pickup position','Approach the landing safely','Bring the field party aboard','Secure samples and recorders','Account for every person and case']:['Range the acoustic release','Command the anchor release','Recover flotation and instrument line','Bring the payload safely aboard','Download and verify the full time series'],
      media:staged?clone(deployment.media):clone(MEDIA.acousticRelease),lat:deployment.lat,lon:deployment.lon,data:deployment.data,reward:deployment.reward,upfront:deployment.upfront||0,advancePaid:deployment.advancePaid||0,
      supplies:deployment.supplies,workHours:deployment.workHours,missionMode:deployment.recoveryMode||'mooring-recovery',deploymentId:deployment.id,
      berthReserve:deployment.berthReserve||0,status:'active',kind:deployment.originalKind==='grant'?'grant':'recovery',selected:true
    };
    deployment.status='awaiting-recovery'; deployment.recoveryTargetId=target.id;
    state.targets.forEach(item=>item.selected=false);
    state.targets.push(target); toast(`${staged?'FIELD TEAM':'MOORING'} READY FOR RECOVERY · ${deployment.title}`); addLog(`${deployment.title} is ready for recovery.`);
  }

  function updateNavigation(nav) {
    const previous=state.navigation;
    if (!nav&&!previous) return;
    if (nav&&previous&&nav.id===previous.id&&Math.abs(nav.distanceKm-previous.distanceKm)<1&&Math.abs(nav.bearingDeg-previous.bearingDeg)<2) return;
    state.navigation=nav;
    if (nav?.id) state.targets.forEach(item=>item.selected=item.id===nav.id);
    renderSidebar();
  }
  function templateSupportedByVessel(template) {
    if (template.transect&&stationCountFor(template)<2) return false;
    if (!missionFitsCurrentVessel(template)) return false;
    return (template.equipment||[]).every(id=>equipmentPossibleOnShip(EQUIPMENT[id],vessel()));
  }
  function teamCouldDoWithEquipment(template) {
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&!eligible(template)&&(template.equipment||[]).some(id=>!equipmentOperational(id));
  }
  function teamCouldDoWithMoreCrew(template) {
    const specialistGap=specialistAssignment(template).missing;
    return hasSpecialty(template)&&templateSupportedByVessel(template)&&(template.equipment||[]).every(id=>equipmentOperational(id))&&((state.scientists.length<missionMinCrew(template))||(specialistGap>0&&specialistGap<=1));
  }
  function maybeOfferProfessorGrant(environment={}) {
    const professorCount=state.scientists.filter(item=>item.career==='professor').length,cooldown=Math.max(1.5,6/professorCount);if(!professorCount||state.port||state.remoteOffer||grantLoad()>=grantCapacity()||state.elapsedDays-(state.lastProfessorGrantDay||-999)<cooldown)return false;
    const candidates=TEMPLATES.filter(item=>!item.weather&&templateCareerLevel(item)>=2&&eligible(item)&&!(item.onlyPorts?.length)); if(!candidates.length)return false; const rng=seeded(`professor-${Math.floor(state.elapsedDays*10)}-${professorCount}`),weighted=candidates.flatMap(item=>Array(templateCareerLevel(item)>=3?1+professorCount*8:1+professorCount*3).fill(item)),template=weighted[Math.floor(rng()*weighted.length)],origin=environment.position||{lat:78,lon:15},target=buildTarget(template,origin,rng,'grant',{nearby:!!(environment.iceEdge||environment.iceThickness),iceThickness:Number(environment.iceThickness)||0}); if(!target)return false;
    state.remoteOffer=target;state.lastProfessorGrantDay=state.elapsedDays;const modal=root.querySelector('#arx-target-modal');modal.innerHTML=`<div class="arx-modal-card arx-target-card"><small>PROFESSOR-ORIGINATED PROPOSAL</small><h2>${escapeHtml(target.title)}</h2><p>A professor aboard has developed a fundable research idea from conditions observed at sea. Accept it and the site will receive normal grant navigation guidance.</p>${mediaMarkup(target,'hero')}<div class="arx-operation-actions"><button class="ghost" data-arx-action="decline-professor-grant">DECLINE</button><button data-arx-action="accept-professor-grant">ACCEPT GRANT</button></div></div>`;modal.classList.add('open');return true;
  }
  function activeFieldOpportunityCount(){return state.targets.filter(item=>item.kind==='opportunity'||item.kind==='weather-opportunity').length;}
  function opportunityMovementRequiredKm(){return{fishing:35,trawler:75,coastal:140,global:210,icebreaker:280,nuclear:350}[state.currentVessel]||35;}
  function rememberOpportunitySpawn(target,position){
    const templateId=target?.templateId||target?.id;if(templateId)state.recentOpportunityTemplates=[templateId,...(state.recentOpportunityTemplates||[]).filter(id=>id!==templateId)].slice(0,4);
    if(Number.isFinite(position?.lat)&&Number.isFinite(position?.lon))state.lastOpportunitySpawnPosition={lat:position.lat,lon:position.lon};
  }
  function enoughMovementForOpportunity(position){
    if(!state.lastOpportunitySpawnPosition)return true;
    return geoDistance(state.lastOpportunitySpawnPosition,position)>=opportunityMovementRequiredKm();
  }
  function maybeSpawnOpportunity(payload={}) {
    if(!payload.position)return null;
    if(maybeOfferProfessorGrant(payload))return null;
    const opportunityCap=2,weather=payload.weather;
    if(weather?.type&&weather.type!=='clear'&&weather.eventId&&!state.weatherEventsSeen.includes(weather.eventId)){
      const openSlots=Math.max(0,opportunityCap-activeFieldOpportunityCount()),careerFloor=playerCareerLevel(),weatherTemplates=TEMPLATES.filter(item=>item.weather===weather.type&&(careerFloor<2||templateCareerLevel(item)>=careerFloor)&&templateSupportedByVessel(item)),basic=careerFloor<2?weatherTemplates.find(item=>item.anyScientist):null,advanced=weatherTemplates.filter(item=>!item.anyScientist&&eligible(item,weather)),spawned=[];
      for(const template of [basic,...advanced].filter(Boolean).filter((item,index,array)=>array.findIndex(other=>other.id===item.id)===index).slice(0,openSlots)){
        const rng=seeded(`${weather.eventId}-${template.id}`),target=buildTarget(template,payload.position,rng,'weather-opportunity',{weatherEventId:weather.eventId,iceThickness:Number(payload.iceThickness)||0});
        if(target){target.selected=false;state.targets.push(target);rememberOpportunitySpawn(target,payload.position);spawned.push(target);}
      }
      state.weatherEventsSeen.push(weather.eventId);
      if(spawned.length){toast(`WEATHER RESEARCH AVAILABLE · ${spawned.map(item=>item.shortTitle).join(' + ')}`);changed({port:false});return spawned[0];}
      return null;
    }
    if(activeFieldOpportunityCount()>=opportunityCap||!enoughMovementForOpportunity(payload.position))return null;
    const coastal=payload.fjord||payload.fjordScore>.38||payload.coastal||payload.coastDistanceKm<30,iceEdge=!!payload.iceEdge||payload.ice==='marginal'||payload.ice==='fast',iceThickness=Math.max(0,Number(payload.iceThickness)||0),deepIce=payload.ice==='packed'||payload.ice==='cracked'||payload.ice==='fast',inIce=iceEdge||deepIce,teamLevel=Math.max(1,...state.scientists.map(item=>careerLevel(item.career))),postdocCount=state.scientists.filter(item=>item.career==='postdoc').length,professorCount=state.scientists.filter(item=>item.career==='professor').length;
    const rng=seeded(`${payload.position.lat.toFixed(2)}-${payload.position.lon.toFixed(2)}-${state.portVisits}-${state.completed.length}-${Math.floor(state.elapsedDays*4)}`),unlockCredit=teamLevel>=3?8:teamLevel>=2?3:0,recent=(state.recentOpportunityTemplates||[]).slice(0,3);
    const basePossible=TEMPLATES.filter(item=>!item.weather&&templateSupportedByVessel(item)&&(playerCareerLevel()<2||templateCareerLevel(item)>=playerCareerLevel())&&(item.unlockAfter||0)<=state.completed.length+unlockCredit);
    let possible=basePossible.filter(item=>!recent.includes(item.id));
    if(!possible.length)possible=basePossible.filter(item=>!recent.slice(0,2).includes(item.id));
    if(!possible.length)possible=basePossible.filter(item=>item.id!==recent[0]);
    if(inIce){const icePossible=possible.filter(item=>item.iceAllowed);if(icePossible.length)possible=icePossible;}
    if(!possible.length){
      if(playerCareerLevel()>=2)return null;
      const fallback=compatibleFallbackTemplate();fallback.anywhere=false;fallback.minDistance=35;fallback.distanceRange=80;const target=buildTarget(fallback,payload.position,rng,'opportunity',{nearby:false,iceThickness});
      if(!target)return null;target.selected=false;state.targets.push(target);rememberOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;
    }
    const weighted=possible.flatMap(template=>{let weight=1,level=templateCareerLevel(template);if(coastal&&(template.coastal||template.fjordPreferred||template.tier==='local'))weight+=payload.fjord?5:3;if(iceEdge&&template.iceAllowed)weight+=18;if(deepIce&&template.iceAllowed)weight+=30+iceThickness*18;if(inIce&&!template.iceAllowed)weight=1;if(teamLevel===2)weight+=level===2?18:level===1?1:0;if(teamLevel===2&&template.postdocOpportunity)weight+=34;if(teamLevel>=3)weight+=level===3?42:level===2?12:1;if(level===2)weight+=postdocCount*4+professorCount*3;if(level===3)weight+=professorCount*12;if(payload.ramming&&template.iceAllowed)weight+=25;if(!coastal&&template.tier!=='local')weight+=3;return Array(Math.max(1,Math.round(weight))).fill(template);});
    const ready=weighted.filter(item=>eligible(item)),aspirational=weighted.filter(item=>teamCouldDoWithEquipment(item)||teamCouldDoWithMoreCrew(item));let pool;
    if(!ready.length&&aspirational.length)pool=aspirational;
    else if(!ready.length)return null;
    else if(aspirational.length&&rng()<.25)pool=aspirational;
    else pool=ready;
    const template=pool[Math.floor(rng()*pool.length)];let target=buildTarget(template,payload.position,rng,'opportunity',{nearby:false,iceThickness});
    if(!target)return null;
    target.selected=false;state.targets.push(target);rememberOpportunitySpawn(target,payload.position);toast(`NEW RESEARCH OPPORTUNITY · ${target.shortTitle}`);changed({port:false});return target;
  }

  function publishPaper(automatic=false) {
    const level=currentPaperLevel(); if (!level||state.publicationCooldown>0) return;
    if (!automatic&&!level.next) automatic=true;
    const available=state.data, used=level.threshold, quality=averageQuality(), connected=equipmentOperational('starlink-terminal'), baseChance=publicationChance(level,available), guaranteed=state.papers.length===0||state.lastPublicationRejected===true, chance=guaranteed?1:baseChance, accepted=guaranteed||!level.next||Math.random()<chance;
    state.publishAttempts++; state.lastPublicationRejected=!accepted; state.publicationCooldown=accepted?0:4*(connected?.75:1);
    let heading,message,award=0,initialCitations=0;
    if (accepted) {
      const factor=(.85+quality*.25)*(connected?1.08:1), recent=state.completed.slice(-3).map(item=>item.shortTitle).filter(Boolean).join(', ');
      award=Math.round(level.award*factor); initialCitations=Math.max(1,Math.round(level.initialCitations*factor)); const potential=Math.max(initialCitations+1,Math.round(level.potential*factor));
      const paperTitle=recent?`${level.label}: ${recent}`:`${level.label}: Arctic Field Observations`;
      adjustMoney(award); state.citations+=initialCitations; state.data=Math.max(0,state.data-used);
      state.papers.push({id:`paper-${Date.now()}`,title:paperTitle,journal:level.journal,tier:level.label,data:used,award,initialCitations,potential,citations:initialCitations,ageDays:0,citationRemainder:0});
      for (const scientist of state.scientists) { scientist.papers=(scientist.papers||0)+1; recordScientist(scientist); }
      heading='Manuscript accepted'; message=`Published in ${level.journal}. ${new Intl.NumberFormat().format(state.data)} overflow data remain available for the next paper.`;
      addLog(`Article published in ${level.journal}; sponsor recognition received.`); callbacks.onSound?.('paper-accepted');
    } else {
      heading='Manuscript rejected'; message='Reviewers requested revision and resubmission.';
      addLog('Manuscript rejected; all data retained for revision.'); callbacks.onSound?.('paper-rejected');
    }
    const modal=root.querySelector('#arx-publish-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-result-card ${accepted?'accepted':'rejected'}"><button class="arx-close" data-arx-action="close-publish">×</button><small>${automatic?'AUTOMATIC TOP-TIER SUBMISSION':'EDITORIAL DECISION'}${accepted?' · ACCEPTED':''}</small><h2>${escapeHtml(heading)}</h2><div class="arx-chance"><span>DATA USED<b>${new Intl.NumberFormat().format(used)}</b></span><span>DATA RETAINED<b>${new Intl.NumberFormat().format(state.data)}</b></span><span>ACCEPTANCE CHANCE<b>${Math.round(chance*100)}%</b></span></div><p>${escapeHtml(message)}</p>${accepted?`<div class="arx-award"><span>${cash(award)}</span><small>SPONSOR RESEARCH AWARD · +${initialCitations} INITIAL CITATIONS</small></div>`:''}<button data-arx-action="close-publish">CONTINUE EXPEDITION</button></div>`;
    modal.classList.add('open'); checkPromotions(); changed();
  }

  function groupProgress(group) {
    const species=Object.entries(catalog).filter(([,item])=>item.group===group), seen=species.filter(([key])=>state.observed.includes(key));
    return {total:species.length,seen:seen.length,complete:species.length>0&&seen.length===species.length};
  }
  function openWildlife(species,context={}) {
    const rawKey=String(species).replace(/ SCHOOL$/,'').trim().toUpperCase(),aliases={'BOWHEAD WHALE':'BOWHEAD','BELUGA WHALE':'BELUGA','HUMPBACK WHALE':'HUMPBACK','GREY WHALE':'GRAY WHALE','POLAR BEAR':'POLAR BEAR'},key=aliases[rawKey]||rawKey;
    let item=catalog[key];if(!item){const compact=value=>String(value||'').toUpperCase().replace(/[^A-Z0-9]/g,'');item=Object.values(catalog).find(entry=>compact(entry.displayName)===compact(rawKey));}
    if(!item){item={displayName:String(species||'Arctic wildlife'),scientificName:'Field identification pending',group:'Arctic Wildlife Observation',photo:'assets/wildlife/polar-bear.jpg',credit:'Field observation record',source:'#',facts:['A wildlife observation was recorded from the expedition chart.','The individual has been removed from the active chart after observation.','Species reference details can be expanded in a future field-guide update.']};}
    const dataValue=Math.max(1,Math.round(Number(context.dataValue)||2));
    const individualId=String(context.individualId||context.id||`${key}:${Number(context.lat||0).toFixed(3)}:${Number(context.lon||0).toFixed(3)}`);
    const firstSpecies=!state.observed.includes(key), firstIndividual=!(state.observedIndividuals||[]).includes(individualId);
    if (firstSpecies) state.observed.push(key);
    if (firstIndividual) { state.observedIndividuals=state.observedIndividuals||[]; state.observedIndividuals.push(individualId); addData(dataValue); addLog(`${item.displayName} observation archived · +${dataValue} data.`); }
    const progress=groupProgress(item.group);
    if (progress.complete&&!state.claimedGroups.includes(item.group)) {
      state.claimedGroups.push(item.group); adjustMoney(GROUP_REWARDS[item.group]||30000); state.citations+=5;
      addLog(`Field assignment complete: ${item.group}. Illustrated article published in Northern Field Notes.`);
      toast(`${item.group.toUpperCase()} COMPLETE · NORTHERN FIELD NOTES PUBLISHED`);
    }
    const tone=item.photoTone==='dark'?'dark':'';
    const modal=root?.querySelector('#arx-wildlife-modal'); if(!modal)return false;
    modal.innerHTML=`<div class="arx-modal-card arx-wildlife-card"><button class="arx-close" data-arx-action="close-wildlife">×</button><div class="arx-photo ${item.photoFit==='contain'?'contain':''} ${tone}"><img src="${escapeHtml(item.photo)}" alt="${escapeHtml(item.displayName)}"><span>${firstIndividual?`OBSERVATION ARCHIVED · +${dataValue} DATA`:'THIS INDIVIDUAL ALREADY OBSERVED · +0 DATA'}</span></div><div class="arx-species"><small>${escapeHtml(item.group)} · ${progress.seen}/${progress.total}</small><h2>${escapeHtml(item.displayName)}</h2><em>${escapeHtml(item.scientificName)}</em>${firstIndividual?'':`<p class="arx-observation-note">This is the same animal or school already recorded during this expedition, so no additional data were added.</p>`}<ul>${item.facts.map(fact=>`<li>${escapeHtml(fact)}</li>`).join('')}</ul><a href="${escapeHtml(item.source)}" target="_blank" rel="noopener">${escapeHtml(item.credit)}</a><div class="arx-modal-actions"><button data-arx-action="field-guide">OPEN FIELD GUIDE</button><button class="ghost" data-arx-action="close-wildlife">DISMISS</button></div></div></div>`;
    modal.classList.add('open'); changed({port:false}); return true;
  }
  function openFieldGuide() {
    const groups=[...new Set(Object.values(catalog).map(item=>item.group))], modal=root.querySelector('#arx-guide-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-guide-card"><button class="arx-close" data-arx-action="close-guide">×</button><small>ARCTIC FIELD GUIDE</small><h2>Photographic Research Checklists</h2><p>Click wildlife on the chart to add a real photograph and species record. Completed assignments are celebrated in the field journal; their sponsor recognition is revealed at completion.</p>${groups.map(group=>{const progress=groupProgress(group);return`<section><header><div><b>${escapeHtml(group)}</b><small>${progress.seen}/${progress.total} observed</small></div><em>${state.claimedGroups.includes(group)?'PUBLISHED':'IN PROGRESS'}</em></header><div>${Object.entries(catalog).filter(([,item])=>item.group===group).map(([key,item])=>`<span class="${state.observed.includes(key)?'seen':''}">${state.observed.includes(key)?'✓':'○'} ${escapeHtml(item.displayName)}</span>`).join('')}</div></section>`;}).join('')}</div>`;
    modal.classList.add('open');
  }

  function accruePaperCitations(paper,days) {
    let remaining=days, age=Number(paper.ageDays)||0, remainder=Number(paper.citationRemainder)||0, gain=0;
    const potential=Math.max(Number(paper.potential)||0,Number(paper.citations)||0);
    while (remaining>1e-8) {
      let span=remaining, rate;
      if (age<7) { span=Math.min(span,7-age); rate=Math.max(.08,potential*.055); }
      else if (age<30) { span=Math.min(span,30-age); rate=Math.max(.025,potential*.008); }
      else rate=Math.max(.005,potential*.0015);
      remainder+=span*rate; age+=span; remaining-=span;
    }
    if ((paper.citations||0)<potential) { gain=Math.min(potential-(paper.citations||0),Math.floor(remainder)); paper.citations=(paper.citations||0)+gain; remainder-=gain; }
    else remainder=0;
    paper.ageDays=age; paper.citationRemainder=remainder; state.citations+=gain;
  }
  function tickDays(days,environment={}) {
    if (!Number.isFinite(days)||days<=0) return;
    state.elapsedDays=(Number(state.elapsedDays)||0)+days;
    state.recentGrantSites=(state.recentGrantSites||[]).filter(site=>state.elapsedDays-(site.day||0)<90).slice(0,18);
    const activeWeather=environment?.weather||null,expiredOpportunityIds=new Set();
    state.targets=state.targets.filter(target=>{if(target.kind!=='opportunity'&&target.kind!=='weather-opportunity')return true;const timedOut=Number.isFinite(target.expiresAtDay)&&state.elapsedDays>=target.expiresAtDay,weatherGone=target.kind==='weather-opportunity'&&activeWeather&&(activeWeather.type==='clear'||(target.weatherEventId&&activeWeather.eventId!==target.weatherEventId));if(timedOut||weatherGone){expiredOpportunityIds.add(target.id);return false;}return true;});
    if(state.navigation?.id&&expiredOpportunityIds.has(state.navigation.id))state.navigation=null;
    const cooldownBefore=Math.ceil(state.publicationCooldown), citationsBefore=Math.floor(state.citations), moneyBefore=Math.round(state.money);
    const total=state.economyDays+days, billable=Math.floor(total+1e-9); state.economyDays=total-billable;
    state.publicationCooldown=Math.max(0,state.publicationCooldown-days);
    if (billable>0) adjustMoney(-billable*payroll());
    for (const paper of state.papers) accruePaperCitations(paper,days);
    let deploymentChanged=false;
    for (const deployment of state.deployments) {
      if (deployment.status!=='collecting') continue;
      deployment.remainingDays-=days;
      if (deployment.remainingDays>0) continue;
      deploymentChanged=true;
      if (deployment.recoveryRequired) createRecoveryTarget(deployment);
      else {
        deployment.status='complete'; addData(deployment.data); adjustMoney(deployment.reward);
        addLog(`Autonomous program complete: ${deployment.title}. Telemetry archived.`);
        toast(`AUTONOMOUS DATA RECEIVED · +${deployment.data} DATA`);
      }
    }
    if (citationsBefore!==Math.floor(state.citations)) checkPromotions();
    if (cooldownBefore!==Math.ceil(state.publicationCooldown)||citationsBefore!==Math.floor(state.citations)||moneyBefore!==Math.round(state.money)||deploymentChanged) {
      renderSidebar(); animateCashReadouts(); callbacks.onStateChange?.();
    }
    if(environment?.source==='sailing')maybeOfferProfessorGrant(environment);
    maybeHelicopterFoodReminder();
    if (state.data>=DATA_GAUGE_MAX) setTimeout(maybeAutoPublish,0);
  }

  function buyResource(type) {
    const resources=callbacks.getResources?.()||{fuel:100,food:100}, ship=vessel();
    if (type==='fuel') {
      const cost=fuelStepCost(ship); if (ship.nuclearFuel||resources.fuel>=99||state.money<cost) return;
      adjustMoney(-cost); callbacks.setResources?.({fuel:clamp(resources.fuel+10,0,100),food:resources.food});
    } else if (type==='food') {
      const cost=foodStepCost(ship); if (resources.food>=99||state.money<cost) return;
      adjustMoney(-cost); callbacks.setResources?.({fuel:resources.fuel,food:clamp(resources.food+10,0,100)});
    } else if (type==='supplies') {
      if (state.supplies>=ship.supplyCapacity||state.money<2500) return;
      adjustMoney(-2500); state.supplies=Math.min(ship.supplyCapacity,state.supplies+10);
    }
    changed();
  }
  function resupplyAll() {
    const resources=callbacks.getResources?.()||{fuel:100,food:100}, ship=vessel(), quote=resupplyAllQuote(resources,ship);
    if (quote<=0||state.money<quote) return;
    adjustMoney(-quote); state.supplies=ship.supplyCapacity;
    callbacks.setResources?.({fuel:100,food:100}); addLog(`All stores topped up at ${state.port?.name||'port'}.`); changed();
  }
  function hire(id) {
    const item=state.candidates.find(candidate=>candidate.id===id); if (!item) return;
    const career=CAREERS[item.career];
    if (!careerHireStatus(item.career).ready) return;
    if (state.scientists.length>=vessel().berths) { pendingCandidateId=id; changed(); return; }
    state.scientists.push({...item,missions:item.missions||0,papers:item.papers||0,hiredAt:state.portVisits}); state.candidates=state.candidates.filter(candidate=>candidate.id!==id);
    pendingCandidateId=null; recordScientist(item); callbacks.onSound?.('cash');
    refreshProgressionOpportunities('team-change'); addLog(`${item.name} joined as ${career.name}.`); changed();
  }
  function selectRecruit(id) {
    const item=state.candidates.find(candidate=>candidate.id===id); if (!item||!careerHireStatus(item.career).ready) return;
    if (state.scientists.length<vessel().berths) { hire(id); return; }
    pendingCandidateId=pendingCandidateId===id?null:id; changed();
  }
  function replaceScientist(outgoingId) {
    const incoming=state.candidates.find(candidate=>candidate.id===pendingCandidateId), outgoing=state.scientists.find(item=>item.id===outgoingId);
    if (!incoming||!outgoing||outgoing.isPlayer||!careerHireStatus(incoming.career).ready) return;
    const next=state.scientists.map(item=>item.id===outgoingId?{...incoming,missions:incoming.missions||0,papers:incoming.papers||0,hiredAt:state.portVisits}:item);
    if (!gateStatus(vessel(),next).ready) { toast('CURRENT VESSEL REQUIRES THIS SENIOR COMMAND TEAM'); return; }
    recordScientist(outgoing); recordScientist(incoming);
    const returned={...outgoing,id:`candidate-${state.portVisits}-return-${outgoing.profileId||slug(outgoing.name)}`}; delete returned.hiredAt;
    state.scientists=next;
    state.candidates=state.candidates.filter(item=>item.id!==incoming.id&&item.profileId!==outgoing.profileId).concat(returned);
    pendingCandidateId=null; callbacks.onSound?.('cash'); scheduleGrantRefresh(); addLog(`${incoming.name} replaced ${outgoing.name}; ${outgoing.name} remains available during this port call.`); changed();
  }
  function release(id) {
    const item=state.scientists.find(scientist=>scientist.id===id); if (!item) return;
    if (item.isPlayer) { toast('THE CHIEF SCIENTIST CANNOT BE RELEASED'); return; }
    const remaining=state.scientists.filter(scientist=>scientist.id!==id);
    if (!gateStatus(vessel(),remaining).ready) { toast('CURRENT VESSEL REQUIRES THIS SENIOR COMMAND TEAM'); return; }
    recordScientist(item); state.scientists=remaining;
    const returned={...item,id:`candidate-${state.portVisits}-released-${item.profileId||slug(item.name)}`}; delete returned.hiredAt;
    if (!state.candidates.some(candidate=>candidate.profileId===returned.profileId)) state.candidates.push(returned);
    scheduleGrantRefresh(); addLog(`${item.name} left the expedition and remains available to rehire during this port call.`); changed();
  }
  function chooseVessel(id) {
    const next=VESSELS[id],previous=vessel(); if(!next||id===state.currentVessel||!vesselForSaleHere(id)||!vesselMarketUnlock(id))return;
    const blockedAsset=deployedTradeAsset();if(blockedAsset){toast(`RECOVER ${EQUIPMENT[blockedAsset]?.name||'DEPLOYED EQUIPMENT'} BEFORE TRADING HULLS`);return;}
    const preview=crewPreviewForVessel(next),gate=gateStatus(next,preview.kept),transfer=vesselTransferPlan(next),credit=vesselTradeInValue(previous,next),listPrice=vesselPurchasePrice(next),commissioning=vesselCommissioningCost(next),due=Math.max(0,listPrice+commissioning-credit);
    if(!gate.ready||grantLoad()>Math.max(1,preview.kept.length)||state.money<due)return;
    adjustMoney(credit-listPrice-commissioning);
    for(const scientist of preview.removed){recordScientist(scientist);const returned={...scientist,id:`candidate-${state.portVisits}-downsize-${scientist.profileId||slug(scientist.name)}`};delete returned.hiredAt;if(!state.candidates.some(item=>item.profileId===returned.profileId))state.candidates.push(returned);}
    state.scientists=preview.kept;state.installedEquipment=transfer.kept;state.inventory=transfer.keptInventory;state.ownedVessels=[id];pendingCandidateId=null;
    state.currentVessel=id;state.supplies=next.supplyCapacity;callbacks.setResources?.({fuel:100,food:100});
    const equipmentNote=transfer.sold.length?` ${transfer.kept.length} installed systems transferred; ${transfer.sold.length} excess systems sold automatically.`:` ${transfer.kept.length} installed systems transferred automatically.`;
    addLog(`${previous.shipName||previous.name} traded toward ${next.shipName||next.name}. New vessel commissioned with full fuel, food and lab stores for ${cash(commissioning)}.${equipmentNote}${preview.removed.length?` ${preview.removed.map(item=>item.name).join(', ')} remained ashore.`:''}`);
    callbacks.onVesselChanged?.(getVesselModifiers());refreshProgressionOpportunities('vessel-change');changed();
  }
  function buyEquipment(id) {
    const item=EQUIPMENT[id]; if (!item) return;
    const purchase=equipmentPurchaseStatus(item,vessel());
    if (!purchase.ready) { toast(purchase.reason.toUpperCase()); return; }
    if (item.consumable) {
      const current=state.inventory[id]||0,loaded=purchase.loadUnits||0; if(loaded<=0){toast('EXPENDABLE STORAGE LIMIT REACHED');return;} adjustMoney(-purchase.purchaseCost); state.inventory[id]=current+loaded; addLog(`${item.name} loaded · ${state.inventory[id]}/${item.maxUnits??'∞'} aboard.`);
    } else {
      if (item.builtIn||state.installedEquipment.includes(id)) return;
      adjustMoney(-item.price); state.installedEquipment.push(id); addLog(`${item.name} installed.`);
    }
    if(item.consumable)scheduleGrantRefresh();else refreshProgressionOpportunities('equipment-change'); changed();
  }
  function sellEquipment(id) {
    const item=EQUIPMENT[id];
    if (!item||item.builtIn||item.consumable||!state.installedEquipment.includes(id)) return;
    if (state.deployments.some(deployment=>deployment.recoveryRequired&&!['recovered','complete'].includes(deployment.status)&&(deployment.equipment||[]).includes(id))) { toast('RECOVER THE DEPLOYED RESEARCH SYSTEM BEFORE SELLING IT'); return; }
    const dependent=state.installedEquipment.map(other=>EQUIPMENT[other]).find(other=>other?.id!==id&&(other.requiresEquipment||[]).includes(id));
    if (dependent) { toast(`${dependent.name.toUpperCase()} DEPENDS ON THIS EQUIPMENT`); return; }
    state.installedEquipment=state.installedEquipment.filter(itemId=>itemId!==id); adjustMoney(Math.round(item.price*EQUIPMENT_RESALE_RATE));
    addLog(`${item.name} sold for ${cash(item.price*EQUIPMENT_RESALE_RATE)}.`); scheduleGrantRefresh(); changed();
  }
  function acceptOffer(id) {
    const offer=state.offers.find(item=>item.id===id); if (!offer) return;
    const readiness=missionReadiness(offer),missing=readiness.rows.find(row=>!row.ready);
    if(!readiness.ready){toast(`GRANT NOT READY · ${String(missing?.label||'MISSING CAPABILITY').toUpperCase()}`);return;}
    if (grantLoad()>=grantCapacity()) { toast(`ACTIVE RESEARCH GRANT LIMIT · ${grantLoad()}/${grantCapacity()}`); return; }
    const projection=missionFoodProjection(offer);
    if (projection.remaining<15) { toast('INSUFFICIENT FOOD SUPPLY ONBOARD TO COMPLETE THE WORK'); return; }
    if (!vessel().nuclearFuel&&projection.fuelRemaining<10) { toast('INSUFFICIENT FUEL TO COMPLETE THE WORK AND RETURN'); return; }
    state.targets.forEach(item=>item.selected=false);offer.selected=true;offer.upfront=0;offer.advancePaid=0;state.targets.push(offer);
    state.offers=state.offers.filter(item=>item.id!==id);recordGrantUse(offer.templateId,offer);addLog(`Research grant accepted: ${offer.title}. Payment due on completion.`);
    toast(`RESEARCH GRANT ACCEPTED · ${offer.shortTitle}`);changed();
  }
  function abandonDeployment(id){
  const deployment=state.deployments.find(item=>item.id===id);if(!deployment||deployment.recoveryMode!=='staged-recovery')return;
  deployment.status='abandoned';if(deployment.recoveryTargetId)state.targets=state.targets.filter(item=>item.id!==deployment.recoveryTargetId);deployment.recoveryTargetId=null;
  addLog(`Return pickup dropped for ${deployment.title}; local logistics assumed responsibility for the field party.`);toast('RETURN PICKUP DROPPED · LOCAL LOGISTICS WILL RECOVER THE TEAM');changed();
}
function dropGrant(id) {
  const grant=state.targets.find(item=>item.id===id&&(item.kind==='grant'||item.kind==='contract'));if(!grant||activeOperation?.targetId===id)return;
  if(grant.deploymentId&&grant.missionMode!=='staged-recovery'){toast('THIS RETURN VISIT IS REQUIRED TO RECOVER DEPLOYED EQUIPMENT');return;}
  if(grant.deploymentId&&grant.missionMode==='staged-recovery'){
    const deployment=state.deployments.find(item=>item.id===grant.deploymentId);if(deployment){deployment.status='abandoned';deployment.recoveryTargetId=null;}
    addLog(`Return pickup dropped for ${grant.title}; local logistics assumed responsibility for the field party.`);
  }else state.droppedGrantTemplates.push(grant.templateId);
  state.targets=state.targets.filter(item=>item.id!==id);if(state.navigation?.id===id)state.navigation=null;if(state.lastTargetContext?.id===id)state.lastTargetContext=null;
  root?.querySelector('#arx-target-modal')?.classList.remove('open');toast(grant.missionMode==='staged-recovery'?'RETURN PICKUP DROPPED':'RESEARCH GRANT DROPPED');changed();
}

function vesselOverlay() {
    const ship=vessel(), tags=[];
    for (let i=0;i<ship.helidecks;i++) tags.push({label:`HELIDECK ${i+1}`,kind:'helideck'});
    for (const id of state.installedEquipment) {
      const item=EQUIPMENT[id]; if (item?.deckTag) tags.push({label:item.deckTag,kind:item.helideckUse?'aircraft':'gear'});
    }
    return tags.map((tag,index)=>`<span class="arx-deck-module ${tag.kind}" style="--module-index:${index}">${escapeHtml(tag.label)}</span>`).join('');
  }
  function helicopterFoodStatus(){
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
  function vesselOverviewMarkup(inPort=false) {
    const baseShip=vessel(), ship={...baseShip,name:baseShip.shipName||baseShip.name}, usage=slotUsage(), resources=callbacks.getResources?.()||{fuel:100,food:100};
    const installed=[...ship.standardEquipment,...state.installedEquipment].map(id=>EQUIPMENT[id]).filter(Boolean), visibility=getVesselModifiers().visibilityBonusKm, image=ship.image||'assets/vessels/base-vessel.png';
    const equipmentTiles=installed.map(item=>`<div class="arx-dashboard-thumb equipment ${equipmentOperational(item.id)?'':'inoperable'}"><img src="${escapeHtml(item.media?.src||MEDIA.local.src)}" alt=""><span>${escapeHtml(item.name)}</span></div>`).join(''),heli=helicopterFoodStatus(),heliPanel=heli.available?`<div class="arx-heli-resupply"><span><b>HELICOPTER PROVISION RUN</b><small>Food delivered anywhere at 3× the normal port price.</small></span><button data-arx-action="helicopter-food" ${heli.steps<=0||state.money<heli.cost?'disabled':''}>${heli.steps<=0?'FOOD STORES FULL':`RESUPPLY FOOD TO 100% · ${cash(heli.cost)}`}</button></div>`:'';
    return `<div class="arx-vessel-overview"><header><small>${escapeHtml(ship.className)} · CURRENT VESSEL</small><h2>${escapeHtml(ship.name)}</h2><p>${escapeHtml(ship.description)}</p></header><div class="arx-vessel-figure ship-${ship.id}"><img src="${escapeHtml(image)}" alt="Side elevation of ${escapeHtml(ship.name)}"></div><div class="arx-vessel-facts"><span><small>STORES</small><b>Fuel ${ship.nuclearFuel?'∞':Math.ceil(resources.fuel)+'%'} · Food ${Math.ceil(resources.food)}% · Lab ${state.supplies}/${ship.supplyCapacity}</b></span><span><small>SCIENCE CAPACITY</small><b>${slotSummary(ship,usage)}${ship.helidecks?` · Helidecks ${helideckUsage()}/${ship.helidecks}`:''}</b></span><span><small>NAVIGATION</small><b>${ship.cruiseKnots} kn cruise · overview to ${Math.round(ship.minZoom*100)}% · fog extension ${visibility} km</b></span></div>${heliPanel}<div class="arx-vessel-columns"><section><h3>Scientists aboard · ${state.scientists.length}/${ship.berths}</h3><div class="arx-manifest">${state.scientists.map(item=>{const profile=profileFor(item),career=CAREERS[item.career];return`<div><img src="${escapeHtml(profile.portrait)}" alt=""><span><b>${escapeHtml(item.name)}</b><small>${career.short} · ${escapeHtml(specialtyById[item.specialty]?.name||item.specialty)}<br>${cash(career.salary)}/day</small></span></div>`;}).join('')}</div></section><section><h3>Installed equipment</h3><div class="arx-dashboard-thumbs">${equipmentTiles}${emptySlotMarkup(ship)}</div></section></div>${!inPort?`<details class="arx-journal-toggle"><summary>FIELD JOURNAL</summary><section class="arx-journal">${state.log.slice(0,8).map(entry=>`<p>${escapeHtml(entry)}</p>`).join('')}</section></details>`:''}<p class="arx-image-note">Vessel illustration and installed deck modules update with the current platform.</p></div>`;
  }
  function openVessel() {
    const modal=root.querySelector('#arx-vessel-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-vessel-card"><button class="arx-close" data-arx-action="close-vessel">×</button>${vesselOverviewMarkup(false)}</div>`;
    modal.classList.add('open');
  }

  function openCharacterSetup() {
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
  function openNpcVessel(info={}) {
    if (!info.id) return false;
    activeNpcEncounter={...info};
    const classOrder=['canoe','sailing','fishing','trawler','coastal','global','icebreaker','nuclear'], currentRank=classOrder.indexOf(state.currentVessel), otherRank=classOrder.indexOf(info.classId||info.type);
    const already=state.assistedByVessels.includes(info.id), canAssist=!!info.canAssist&&otherRank>currentRank&&!already;
    const modal=root.querySelector('#arx-npc-modal'), shipImage=info.image||VESSELS[info.classId]?.image||MEDIA.vessel.src, portrait=info.captainPortrait||SCIENTIST_PROFILES[0]?.portrait||PLAYER_AVATARS[1].src;
    modal.innerHTML=`<div class="arx-modal-card arx-npc-card"><button class="arx-close" data-arx-action="close-npc">×</button><figure class="arx-media compact"><img src="${escapeHtml(shipImage)}" alt="${escapeHtml(info.name||'Arctic vessel')}"></figure><div><small>VESSEL ENCOUNTER · ${escapeHtml(info.typeLabel||info.type||'WORKING VESSEL')}</small><h2>${escapeHtml(info.name||'Passing vessel')}</h2><p>${escapeHtml(info.description||'Another vessel working in the Arctic.')}</p><div class="arx-npc-person"><img src="${escapeHtml(portrait)}" alt="Cartoon portrait"><span><b>${escapeHtml(info.captainName||'Arctic mariner')}</b><small>${escapeHtml(info.captainRole||'Captain')}</small></span></div><div class="arx-target-facts compact"><span><small>VESSEL</small><b>${escapeHtml(info.typeLabel||info.classId||info.type||'Unknown')}</b></span><span><small>CURRENT MISSION</small><b>${escapeHtml(info.mission||'Regional operations')}</b></span><span><small>RANGE</small><b>${Math.max(0,Math.round(info.distanceKm||0))} km</b></span></div>${canAssist?'<p class="arx-aid-note">“We remember starting small. Take fuel and provisions from our spare stores, and keep the science going.”</p><button data-arx-action="accept-npc-aid">ACCEPT SHARED STORES</button>':already?'<p class="arx-aid-note">This vessel has already shared its spare stores during this expedition.</p>':''}</div></div>`;
    modal.classList.add('open'); return true;
  }
  function acceptNpcAid() {
    if (!activeNpcEncounter||state.assistedByVessels.includes(activeNpcEncounter.id)) return;
    state.assistedByVessels.push(activeNpcEncounter.id);
    const resources=callbacks.getResources?.()||{fuel:100,food:100};
    callbacks.setResources?.({fuel:100,food:100});
    addLog(`${activeNpcEncounter.name} shared fuel and provisions with the expedition.`); toast(`${activeNpcEncounter.name?.toUpperCase()||'RESEARCH VESSEL'} · FUEL AND FOOD TOPPED UP`);
    root.querySelector('#arx-npc-modal')?.classList.remove('open'); activeNpcEncounter=null; changed({port:false});
  }

  function devIsUnlocked() { try{return sessionStorage.getItem('arctic-research-dev-unlocked')==='1';}catch(error){return false;} }
  function unlockDevConsole() {
    if (devIsUnlocked()) return true;
    const password=window.prompt('Enter Arctic Research test password');
    if (password!=='1301') { if(password!=null) toast('TEST CONSOLE · INCORRECT PASSWORD'); return false; }
    try{sessionStorage.setItem('arctic-research-dev-unlocked','1');}catch(error){}
    const button=root?.querySelector('#arx-dev-toggle'); if(button)button.textContent='TEST';
    toast('TEST CONSOLE UNLOCKED'); return true;
  }
  function openDevConsole() {
    if (!unlockDevConsole()) return;
    const modal=root.querySelector('#arx-dev-modal'),player=playerScientist(),calendar=callbacks.getCalendarState?.()||{month:8},months=['January','February','March','April','May','June','July','August','September','October','November','December'];
    modal.innerHTML=`<div class="arx-modal-card arx-dev-card"><button class="arx-close" data-arx-action="close-dev">×</button><small>TEMPORARY DEVELOPMENT TOOL</small><h2>Test progression state</h2><p>Jump directly to a vessel, Chief Scientist career stage, and month of the Arctic season. The month control is intended for rapid sea-ice coverage testing.</p><label><span>VESSEL</span><select data-arx-dev-vessel>${Object.values(VESSELS).map(ship=>`<option value="${ship.id}" ${ship.id===state.currentVessel?'selected':''}>${escapeHtml(ship.name)}</option>`).join('')}</select></label><label><span>CAREER STAGE</span><select data-arx-dev-career>${Object.values(CAREERS).map(career=>`<option value="${career.id}" ${career.id===player?.career?'selected':''}>${escapeHtml(career.name)}</option>`).join('')}</select></label><label><span>MONTH / ICE COVERAGE</span><select data-arx-dev-month>${months.map((month,index)=>`<option value="${index}" ${index===calendar.month?'selected':''}>${month}</option>`).join('')}</select></label><div class="arx-dev-warning">TEST MODE can alter the current local save. Do not use this state as a production playthrough.</div><button data-arx-action="apply-dev-state">APPLY TEST STATE</button></div>`;
    modal.classList.add('open');
  }
  function applyDevState() {
    const modal=root.querySelector('#arx-dev-modal'),vesselId=modal.querySelector('[data-arx-dev-vessel]')?.value,careerId=modal.querySelector('[data-arx-dev-career]')?.value,monthIndex=Number(modal.querySelector('[data-arx-dev-month]')?.value);
    if(!VESSELS[vesselId]||!CAREERS[careerId]||!Number.isInteger(monthIndex)||monthIndex<0||monthIndex>11)return;
    const player=playerScientist(); if(player)player.career=careerId; devCareerOverride=careerId;
    state.currentVessel=vesselId; if(!state.ownedVessels.includes(vesselId))state.ownedVessels.push(vesselId);
    state.money=Math.max(state.money,1000000000); state.citations=Math.max(state.citations,careerId==='professor'?1000:careerId==='postdoc'?100:0);
    const ship=VESSELS[vesselId],months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']; state.installedEquipment=state.installedEquipment.filter(id=>equipmentPossibleOnShip(EQUIPMENT[id],ship)); while(!equipmentFits(ship)&&state.installedEquipment.length)state.installedEquipment.pop();
    state.supplies=ship.supplyCapacity; callbacks.setResources?.({fuel:100,food:100}); callbacks.setTestMonth?.(monthIndex); callbacks.onVesselChanged?.(getVesselModifiers()); recordScientist(player); addLog(`TEST MODE · ${CAREERS[careerId].name} aboard ${ship.name} · ${months[monthIndex]}.`);
    modal.classList.remove('open'); changed(); toast(`TEST STATE · ${ship.name.toUpperCase()} · ${CAREERS[careerId].short} · ${months[monthIndex]}`); callbacks.onStateChange?.();
  }

  function cancelOpportunity(id) {
    const target=state.targets.find(item=>item.id===id&&(item.kind==='opportunity'||item.kind==='weather-opportunity')); if(!target)return;
    state.targets=state.targets.filter(item=>item.id!==id);
    if(state.navigation?.id===id)state.navigation=null;
    if(state.lastTargetContext?.id===id)state.lastTargetContext=null;
    addLog(`Research opportunity declined: ${target.title}.`); root?.querySelector('#arx-target-modal')?.classList.remove('open'); toast('RESEARCH OPPORTUNITY DECLINED'); changed({port:false});
  }
  function openNavigationPrompt(id=state.navigation?.id) {
    const target=state.targets.find(item=>item.id===id);if(!target)return false;callbacks.onNavigate?.(target);return true;
  }

  function confirmDeparture(resources,proceed) {
    const ship=vessel(), supplyPercent=state.supplies/ship.supplyCapacity*100;
    const low=[];
    if (!ship.nuclearFuel&&resources.fuel<50) low.push({name:'Fuel',value:`${Math.ceil(resources.fuel)}%`});
    if (resources.food<50) low.push({name:'Food',value:`${Math.ceil(resources.food)}%`});
    if (supplyPercent<50) low.push({name:'Lab supplies',value:`${state.supplies}/${ship.supplyCapacity} · ${Math.ceil(supplyPercent)}%`});
    if (!state.port||!low.length) return false;
    pendingDeparture=proceed;
    const modal=root.querySelector('#arx-departure-modal');
    modal.innerHTML=`<div class="arx-modal-card arx-result-card"><small>BEFORE DEPARTURE</small><h2>Leave with low stores?</h2><p>One or more expedition stores are below 50%. You can return to port services now or accept the risk and depart.</p><div class="arx-store-warning">${low.map(item=>`<span><small>${escapeHtml(item.name)}</small><b>${escapeHtml(item.value)}</b></span>`).join('')}</div><div class="arx-modal-actions"><button class="ghost" data-arx-action="return-port">GO BACK TO PORT</button><button data-arx-action="depart-anyway">DEPART ANYWAY</button></div></div>`;
    modal.classList.add('open'); return true;
  }

  function handleAction(event) {
    const button=event.target.closest('[data-arx-action]'); if (!button) return;
    const action=button.dataset.arxAction, id=button.dataset.id;
    if (action==='close-port') closePort();
    else if (action==='dev-console') openDevConsole();
    else if (action==='close-dev') root.querySelector('#arx-dev-modal').classList.remove('open');
    else if (action==='apply-dev-state') applyDevState();
    else if (action==='close-target'&&!activeOperation) root.querySelector('#arx-target-modal').classList.remove('open');
    else if (action==='acknowledge-research') { root.querySelector('#arx-target-modal').classList.remove('open'); if(!maybePublicationIntro()){showNextPromotion();setTimeout(maybeAutoPublish,0);} }
    else if (action==='close-wildlife') { root.querySelector('#arx-wildlife-modal').classList.remove('open'); setTimeout(maybeAutoPublish,0); }
    else if (action==='close-guide') root.querySelector('#arx-guide-modal').classList.remove('open');
    else if (action==='close-publish') { root.querySelector('#arx-publish-modal').classList.remove('open'); showNextPromotion(); }
    else if (action==='close-publication-intro') { root.querySelector('#arx-publish-modal').classList.remove('open'); showNextPromotion(); setTimeout(maybeAutoPublish,0); }
    else if (action==='close-promotion') { root.querySelector('#arx-promotion-modal').classList.remove('open'); showNextPromotion(); }
    else if (action==='close-vessel') root.querySelector('#arx-vessel-modal').classList.remove('open');
    else if (action==='close-npc') { root.querySelector('#arx-npc-modal').classList.remove('open'); activeNpcEncounter=null; }
    else if (action==='choose-avatar') { characterDraft.specialty=root.querySelector('[data-arx-character-specialty]')?.value||characterDraft.specialty; characterDraft.name=root.querySelector('[data-arx-character-name]')?.value||characterDraft.name; characterDraft.avatar=id; openCharacterSetup(); }
    else if (action==='confirm-character') confirmCharacter();
    else if (action==='accept-npc-aid') acceptNpcAid();
    else if (action==='toggle-side') root.querySelector('#arx-sidebar').classList.remove('open');
    else if (action==='open-port'&&state.port) renderPort();
    else if (action==='open-private-funding'&&state.port) openPrivateFunding();
    else if (action==='close-private-funding') root.querySelector('#arx-funding-modal').classList.remove('open');
    else if (action==='buy-private-funding') purchasePrivateFunding(id,button);
    else if (action==='fuel'||action==='food'||action==='supplies') buyResource(action);
    else if (action==='helicopter-food') helicopterFoodRun();
    else if (action==='dismiss-helicopter-food') root.querySelector('#arx-vessel-modal')?.classList.remove('open');
    else if (action==='resupply-all') resupplyAll();
    else if (action==='relocate-port') relocateHomePort(id);
    else if (action==='hire') hire(id);
    else if (action==='select-recruit') selectRecruit(id);
    else if (action==='replace-scientist') replaceScientist(id);
    else if (action==='release') release(id);
    else if (action==='vessel') chooseVessel(id);
    else if (action==='equipment') buyEquipment(id);
    else if (action==='sell-equipment') sellEquipment(id);
    else if (action==='shop-equipment') { if(!state.port){toast('EQUIPMENT SHOP AVAILABLE IN PORT');return;} activePortTab='equipment';portScrollTop=0;openStoreDetail=id;renderPort(); }
    else if (action==='accept') acceptOffer(id);
    else if (action==='accept-opportunity') { const target=state.targets.find(item=>item.id===id); if(target&&(target.kind==='opportunity'||target.kind==='weather-opportunity')){target.accepted=true;target.expiresAtDay=null;target.selected=true;addLog(`Research opportunity accepted: ${target.title}.`);toast(`RESEARCH OPPORTUNITY ACCEPTED · ${target.shortTitle||target.title}`);renderResearchWindow(target,{phase:'ready'});changed({port:false});} }
    else if (action==='accept-professor-grant'&&state.remoteOffer) { state.targets.forEach(item=>item.selected=false);state.remoteOffer.selected=true;state.remoteOffer.upfront=0;state.remoteOffer.advancePaid=0;state.targets.push(state.remoteOffer);addLog(`Professor-originated grant accepted: ${state.remoteOffer.title}. Payment due on completion.`);state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');renderSidebar();changed(); }
    else if (action==='decline-professor-grant') { state.remoteOffer=null;root.querySelector('#arx-target-modal').classList.remove('open');changed(); }
    else if (action==='drop-grant') dropGrant(id);
    else if (action==='abandon-deployment') abandonDeployment(id);
    else if (action==='navigate-target') { const target=state.targets.find(item=>item.id===id);root.querySelector('#arx-target-modal')?.classList.remove('open');if(target)callbacks.onNavigate?.(target); }
    else if (action==='publish') publishPaper();
    else if (action==='field-guide') { root.querySelector('#arx-wildlife-modal').classList.remove('open'); openFieldGuide(); }
    else if (action==='open-nav'&&state.navigation) openNavigationPrompt();
    else if (action==='navigate-opportunity') { const target=state.targets.find(item=>item.id===id); root.querySelector('#arx-target-modal')?.classList.remove('open'); if(target)callbacks.onNavigate?.(target); }
    else if (action==='cancel-opportunity') cancelOpportunity(id);
    else if (action==='complete-target') completeTarget(id);
    else if (action==='return-port') { root.querySelector('#arx-departure-modal').classList.remove('open'); pendingDeparture=null; renderPort(); }
    else if (action==='depart-anyway') { const proceed=pendingDeparture; pendingDeparture=null; root.querySelector('#arx-departure-modal').classList.remove('open'); proceed?.(); }
  }
  function handleTabs(event) {
    const button=event.target.closest('[data-arx-tab]'); if (!button) return;
    const card=button.closest('.arx-port-card'),tabs=card.querySelector('.arx-tabs');
    activePortTab=button.dataset.arxTab; portScrollTop=0; portTabsScrollLeft=tabs.scrollLeft; openStoreDetail=null;
    if(activePortTab==='contracts'&&!state.offers.length)refreshGrantOffersNow({render:false});
    if(activePortTab==='crew'&&!state.candidates.length)generateCandidates(state.port);
    renderPort();
  }

  function ensureUI() {
    if (root) return;
    root=document.createElement('div'); root.id='arx-root';
    root.innerHTML=`<button id="arx-mobile-toggle" data-arx-action="mobile-toggle">RESEARCH</button><button id="arx-dev-toggle" data-arx-action="dev-console">${devIsUnlocked()?'TEST':'TEST 🔒'}</button><aside id="arx-sidebar" class="arx-sidebar" aria-label="Research program"></aside><div id="arx-port-modal" class="arx-modal"></div><div id="arx-target-modal" class="arx-modal"></div><div id="arx-wildlife-modal" class="arx-modal"></div><div id="arx-guide-modal" class="arx-modal"></div><div id="arx-publish-modal" class="arx-modal"></div><div id="arx-promotion-modal" class="arx-modal"></div><div id="arx-vessel-modal" class="arx-modal"></div><div id="arx-departure-modal" class="arx-modal"></div><div id="arx-character-modal" class="arx-modal"></div><div id="arx-npc-modal" class="arx-modal"></div><div id="arx-funding-modal" class="arx-modal"></div><div id="arx-dev-modal" class="arx-modal"></div>`;
    document.body.appendChild(root);
    syncGlobalCash();
    const style=document.createElement('style'); style.id='arx-expedition-style'; style.textContent=`
      #arx-root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#eafaff}#arx-root *{box-sizing:border-box}#arx-root button,#arx-root a{touch-action:manipulation}.arx-sidebar{position:fixed;z-index:5;left:16px;top:96px;width:270px;max-height:calc(100vh - 118px);padding:13px;overflow:auto;border:1px solid rgba(166,230,244,.28);border-radius:13px;background:rgba(4,31,49,.88);box-shadow:0 14px 40px rgba(0,17,28,.34);backdrop-filter:blur(14px)}.arx-side-head{display:flex;justify-content:space-between;gap:10px;align-items:start}.arx-side-head small,.arx-metrics small,.arx-data small,.arx-nav small,.arx-papers>small,.arx-deployments>small{display:block;color:#82b7c7;font-size:7px;font-weight:800;letter-spacing:.12em}.arx-side-head b{display:block;margin-top:3px;color:#f6d365;font-size:16px}.arx-side-head button{display:none;border:0;background:transparent;color:#9cc6d0;font-size:22px}.arx-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin:11px 0}.arx-metrics span{padding:7px 5px;border-radius:7px;background:rgba(62,113,131,.25);text-align:center}.arx-metrics b{display:block;margin-top:3px;font-size:10px}.arx-metrics em{display:block;margin-top:2px;color:#91bac4;font-size:7px;font-style:normal;font-weight:800}.arx-data{padding:10px;border:1px solid rgba(246,211,101,.2);border-radius:9px;background:rgba(13,55,72,.58)}.arx-data>div{display:flex;justify-content:space-between;align-items:end}.arx-data>div b{color:#fff4bd;font-size:20px}.arx-data>i{position:relative;display:block;height:7px;margin:8px 0;border-radius:5px;background:#214f63}.arx-data>i em{display:block;height:100%;border-radius:5px;background:linear-gradient(90deg,#7dd3fc,#f6d365)}.arx-data>i u{position:absolute;top:-3px;width:1px;height:13px;background:#fff}.arx-data p{margin:7px 0 9px;color:#9bc5d0;font-size:9px;line-height:1.35}.arx-data button,.arx-card button,.arx-modal-card>button:not(.arx-close),.arx-modal-actions button,.arx-species button,.arx-resupply-all{width:100%;padding:9px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:8px;font-weight:900;letter-spacing:.09em;cursor:pointer}.arx-data button:disabled,.arx-card button:disabled,.arx-modal-actions button:disabled,.arx-resupply-all:disabled{background:#315766;color:#7896a0;cursor:default}.arx-nav{display:flex;width:100%;gap:10px;align-items:center;margin-top:9px;padding:9px;border:1px solid rgba(125,211,252,.22);border-radius:9px;background:rgba(12,54,71,.62);color:#eafaff;text-align:left;cursor:pointer}.arx-nav.empty{cursor:default}.arx-nav>span{display:grid;place-items:center;flex:0 0 34px;height:34px;border:1px solid rgba(246,211,101,.55);border-radius:50%;color:#f6d365;font-size:22px}.arx-nav div{min-width:0}.arx-nav b,.arx-nav em{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.arx-nav b{margin-top:3px;font-size:10px}.arx-nav em{margin-top:3px;color:#8bc2d0;font-size:8px;font-style:normal}.arx-side-actions{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px}.arx-side-actions button{padding:7px 4px;border:1px solid rgba(166,230,244,.2);border-radius:6px;background:transparent;color:#a9d1dc;font-size:7px;font-weight:800;cursor:pointer}.arx-sidebar footer{margin-top:8px;color:#6f9eab;font-size:7px;text-align:center}.arx-papers,.arx-deployments{margin-top:9px;padding:9px;border:1px solid rgba(125,211,252,.16);border-radius:8px;background:rgba(12,54,71,.45)}.arx-papers>div,.arx-deployments>div{display:flex;justify-content:space-between;gap:8px;padding-top:7px}.arx-papers span,.arx-deployments span{min-width:0;color:#c7e3e9;font-size:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.arx-papers span em,.arx-deployments span em{display:block;margin-top:2px;color:#709daa;font-size:7px;font-style:normal}.arx-papers b,.arx-deployments b{color:#f6d365;font-size:8px}#arx-mobile-toggle{display:none;position:fixed;z-index:7;right:14px;bottom:16px;padding:10px 12px;border:1px solid rgba(246,211,101,.55);border-radius:8px;background:rgba(4,31,49,.92);color:#f6d365;font-size:8px;font-weight:900;letter-spacing:.12em}.arx-modal{display:none;position:fixed;z-index:12;inset:0;padding:24px;overflow:auto;background:rgba(0,13,22,.72);backdrop-filter:blur(7px);touch-action:pan-y}.arx-modal.open{display:grid;place-items:center}.arx-modal-card{position:relative;width:min(900px,100%);max-height:calc(100vh - 48px);padding:26px;overflow:auto;border:1px solid rgba(166,230,244,.3);border-radius:16px;background:linear-gradient(145deg,rgba(6,42,61,.985),rgba(4,25,40,.985));box-shadow:0 30px 80px rgba(0,0,0,.45);touch-action:pan-y}.arx-close{position:absolute;right:13px;top:10px;z-index:2;border:0;background:rgba(4,25,40,.6);border-radius:50%;color:#c1dde4;font-size:26px;cursor:pointer}.arx-modal-card>header>small,.arx-modal-card>small,.arx-guide-card>small,.arx-species>small{color:#7dd3fc;font-size:8px;font-weight:900;letter-spacing:.16em}.arx-modal-card h2{margin:7px 0 8px;color:#f4fbfc;font:800 30px/1.05 Georgia,serif}.arx-modal-card>header p,.arx-modal-card>p,.arx-guide-card>p{margin:0;color:#a9cbd4;font-size:11px;line-height:1.5}.arx-port-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:18px 0 13px}.arx-port-summary span{padding:9px;border-radius:8px;background:rgba(76,133,151,.18)}.arx-port-summary small{display:block;color:#7faebc;font-size:7px;letter-spacing:.1em}.arx-port-summary b{display:block;margin-top:4px;font-size:10px}.arx-tabs{display:flex;gap:5px;overflow:auto;border-bottom:1px solid rgba(166,230,244,.18)}.arx-tabs button{padding:9px 12px;border:0;border-bottom:2px solid transparent;background:transparent;color:#86adba;font-size:8px;font-weight:800;cursor:pointer}.arx-tabs button.active{border-color:#f6d365;color:#f6d365}.arx-tab{display:none;padding-top:16px}.arx-tab.active{display:block}.arx-tab h3,.arx-vessel-card h3{margin:0 0 6px;font:800 18px Georgia,serif}.arx-help{margin:0 0 13px;color:#8eb7c3;font-size:10px}.arx-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.arx-card{padding:12px;border:1px solid rgba(166,230,244,.17);border-radius:9px;background:rgba(23,67,83,.42)}.arx-card.selected{border-color:rgba(246,211,101,.55)}.arx-card.locked{opacity:.58}.arx-card-head{display:flex;justify-content:space-between;gap:8px;align-items:start}.arx-card-head>div{min-width:0}.arx-card-head b,.arx-card-head small{display:block}.arx-card-head b{font-size:11px}.arx-card-head small{margin-top:3px;color:#82afbc;font-size:7px;font-weight:800;letter-spacing:.06em}.arx-card-head em{flex:0 0 auto;color:#f6d365;font-size:8px;font-style:normal}.arx-card-head em[style]{padding-left:8px;border-left:3px solid var(--career)}.arx-card p{min-height:29px;margin:8px 0;color:#9fc3cd;font-size:9px;line-height:1.4}.arx-card .ghost,.arx-modal-actions .ghost{border:1px solid rgba(166,230,244,.25);background:transparent;color:#a9d2dc}.arx-stats{display:flex;flex-wrap:wrap;gap:4px;margin:7px 0}.arx-stats span{padding:3px 5px;border-radius:4px;background:rgba(125,211,252,.1);color:#a9ccd5;font-size:7px}.arx-portrait{display:block;flex:0 0 50px;width:50px;height:50px;border:2px solid rgba(166,230,244,.34);border-radius:12px;object-fit:cover;background:#176070}.scientist .arx-card-head{align-items:center}.scientist p{min-height:0}.arx-qualification{margin:-2px 0 8px;color:#7dd3fc;font-size:7px;font-weight:900;letter-spacing:.08em}.arx-requirement{margin:8px 0;padding:7px;border:1px solid rgba(249,115,103,.22);border-radius:6px;background:rgba(92,45,49,.16)}.arx-requirement.ready{border-color:rgba(142,240,207,.25);background:rgba(35,91,77,.15)}.arx-requirement b,.arx-requirement span{display:block}.arx-requirement b{color:#f2b3a8;font-size:7px;letter-spacing:.08em}.arx-requirement.ready b{color:#8ef0cf}.arx-requirement span{margin-top:4px;color:#9fc3cd;font-size:8px;line-height:1.35}.arx-card details{margin:8px 0;border-top:1px solid rgba(166,230,244,.12);border-bottom:1px solid rgba(166,230,244,.12)}.arx-card summary{padding:7px 0;color:#7dd3fc;font-size:7px;font-weight:900;letter-spacing:.09em;cursor:pointer}.arx-card details ul{padding-left:17px;color:#b5d0d6;font-size:8px;line-height:1.5}.arx-media{position:relative;margin:0;overflow:hidden;border-radius:9px;background:#0c3447}.arx-media img{display:block;width:100%;height:100%;object-fit:cover}.arx-media figcaption{position:absolute;left:0;right:0;bottom:0;padding:6px 8px;background:rgba(2,20,31,.82);color:#b8d7df;font-size:6px}.arx-media a{color:#7dd3fc}.arx-media.compact{height:155px}.arx-media.hero{height:210px;margin:-26px -26px 20px;border-radius:16px 16px 9px 9px}.arx-media.result{height:185px;margin:-26px -26px 20px;border-radius:16px 16px 9px 9px}.arx-offer-thumb{height:86px;margin:-12px -12px 10px;overflow:hidden;border-radius:9px 9px 4px 4px}.arx-offer-thumb img{width:100%;height:100%;object-fit:cover}.arx-resupply-all{margin:5px 0 10px}.arx-resupply{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:18px}.arx-resupply article{display:flex;flex-direction:column;padding:11px;border-radius:9px;background:rgba(23,67,83,.48)}.arx-resupply small,.arx-resupply b,.arx-resupply span{display:block}.arx-resupply small{color:#84afbc;font-size:7px}.arx-resupply b{margin:5px 0 8px;font-size:15px}.arx-resupply span{min-height:20px;color:#8fb5bf;font-size:8px;line-height:1.3}.arx-resupply button{width:100%;margin-top:auto;padding:7px;border:0;border-radius:6px;background:#f6d365;color:#17323b;font-size:7px;font-weight:900}.arx-resupply button:disabled{background:#315766;color:#7896a0}.arx-empty{grid-column:1/-1;padding:25px;border:1px dashed rgba(166,230,244,.25);border-radius:9px;text-align:center}.arx-empty p{color:#8eb5c0;font-size:10px}.arx-target-card{width:min(690px,100%)}.arx-target-facts{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:18px 0}.arx-target-facts span{padding:9px;border-radius:7px;background:rgba(30,79,96,.48)}.arx-target-facts small,.arx-target-facts b{display:block}.arx-target-facts small{color:#82adba;font-size:7px}.arx-target-facts b{margin-top:4px;font-size:9px}.arx-modal-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.arx-modal-actions.single{grid-template-columns:1fr}.arx-operation-progress{margin:18px 0 14px;padding:11px;border-radius:9px;background:rgba(23,67,83,.48)}.arx-operation-progress>div{display:flex;justify-content:space-between;align-items:end}.arx-operation-progress b{color:#f6d365;font-size:23px}.arx-operation-progress span{color:#8eb7c3;font-size:8px}.arx-operation-progress>i{display:block;height:8px;margin-top:8px;overflow:hidden;border-radius:8px;background:#214f63}.arx-operation-progress>i em{display:block;width:0;height:100%;border-radius:8px;background:linear-gradient(90deg,#7dd3fc,#8ef0cf,#f6d365)}.arx-operation ol{display:grid;gap:6px;margin:0;padding:0;list-style:none}.arx-operation li{display:grid;grid-template-columns:26px 1fr auto;gap:8px;align-items:center;padding:8px;border:1px solid rgba(166,230,244,.12);border-radius:7px;color:#789eaa;background:rgba(13,50,66,.35)}.arx-operation li>i{display:grid;place-items:center;width:23px;height:23px;border-radius:50%;background:#234f61;color:#88b5c0;font-size:8px;font-style:normal}.arx-operation li>b{font-size:9px}.arx-operation li>span{font-size:7px;font-weight:800;text-transform:uppercase}.arx-operation li.active{border-color:rgba(246,211,101,.42);color:#eff9fb}.arx-operation li.active>i{background:#f6d365;color:#17323b}.arx-operation li.active>span{color:#f6d365}.arx-operation li.done{color:#a8daca}.arx-operation li.done>i{background:#4eb691;color:#062f32}.arx-operation ol{grid-template-columns:1fr}.arx-operation li{grid-template-columns:26px minmax(0,1fr) 72px}.arx-operation-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}.arx-operation-actions button{width:100%}.arx-operation-result-space{min-height:54px}.arx-port-navrow{display:flex;align-items:stretch;gap:10px}.arx-port-navrow .arx-tabs{flex:1;min-width:0}.arx-port-cash{flex:0 0 auto;display:flex!important;align-items:center;gap:9px;margin:0!important;padding:0 12px!important;border-left:1px solid rgba(166,230,244,.18);white-space:nowrap}.arx-port-cash span{display:block}.arx-port-cash small,.arx-port-cash b{display:block;margin:0!important}.arx-port-cash button{padding:6px 8px;border:1px solid rgba(246,211,101,.42);border-radius:6px;background:rgba(246,211,101,.08);color:#f6d365;font-size:6px;font-weight:900;letter-spacing:.08em;cursor:pointer}.arx-funding-card{width:min(720px,100%)}.arx-web-preview{margin:17px 0;padding:10px 12px;border:1px solid rgba(125,211,252,.28);border-radius:8px;background:rgba(20,75,96,.38)}.arx-web-preview b,.arx-web-preview span{display:block}.arx-web-preview b{color:#7dd3fc;font-size:8px;letter-spacing:.1em}.arx-web-preview span{margin-top:4px;color:#9fc6d1;font-size:8px;line-height:1.4}.arx-funding-balance{margin:14px 0;text-align:center}.arx-funding-balance small,.arx-funding-balance b{display:block}.arx-funding-balance small{color:#82afbc;font-size:7px;letter-spacing:.12em}.arx-funding-balance b{margin-top:4px;color:#f6d365;font:800 25px Georgia,serif}.arx-funding-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:17px 0}.arx-funding-grid article{padding:16px 12px;border:1px solid rgba(166,230,244,.18);border-radius:10px;background:rgba(23,67,83,.46);text-align:center}.arx-funding-grid article.featured{border-color:rgba(246,211,101,.55);box-shadow:inset 0 0 0 1px rgba(246,211,101,.12)}.arx-funding-grid small,.arx-funding-grid b,.arx-funding-grid span{display:block}.arx-funding-grid small{color:#7dd3fc;font-size:7px;font-weight:900;letter-spacing:.1em}.arx-funding-grid b{margin:10px 0 2px;color:#fff4bd;font:800 23px Georgia,serif}.arx-funding-grid span{color:#8fb7c2;font-size:8px}.arx-funding-grid button{width:100%;margin-top:13px;padding:10px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:10px;font-weight:900;cursor:pointer}.arx-funding-grid button:disabled{background:#315766;color:#7896a0}.arx-funding-note{color:#789eaa!important;font-size:8px!important;text-align:center}.arx-resupply-block{margin:10px 0 16px}.arx-resupply-top{margin-top:14px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid rgba(166,230,244,.14)}.compact-dashboard{margin-bottom:6px}.arx-wildlife-card{display:grid;grid-template-columns:1.05fr 1fr;gap:22px;width:min(780px,100%)}.arx-photo{position:relative;min-height:330px;overflow:hidden;border-radius:11px;background:#123e51}.arx-photo img{width:100%;height:100%;min-height:330px;object-fit:cover}.arx-photo.contain{background:#edf4f3}.arx-photo.contain.dark{background:#03080b}.arx-photo.contain img{object-fit:contain!important;padding:16px}.arx-photo.contain.dark img{padding:10px}.arx-photo span{position:absolute;left:10px;bottom:10px;padding:6px 8px;border-radius:5px;background:rgba(3,26,39,.85);color:#f6d365;font-size:7px;font-weight:900}.arx-species{align-self:center}.arx-species>em{color:#8fc2ce;font:italic 13px Georgia,serif}.arx-species ul{padding-left:18px;color:#b6d2d9;font-size:11px;line-height:1.5}.arx-species a{display:block;margin:12px 0;color:#7dd3fc;font-size:8px}.arx-guide-card{width:min(720px,100%)}.arx-guide-card section{margin-top:12px;padding:12px;border:1px solid rgba(166,230,244,.16);border-radius:9px}.arx-guide-card section header{display:flex;justify-content:space-between}.arx-guide-card section small{color:#82afbb;font-size:8px}.arx-guide-card section em{color:#f6d365;font-size:8px;font-style:normal}.arx-guide-card section>div{display:grid;grid-template-columns:repeat(2,1fr);gap:5px;margin-top:9px}.arx-guide-card section span{color:#789eaa;font-size:9px}.arx-guide-card section span.seen{color:#8ef0cf}.arx-result-card{width:min(570px,100%);text-align:center}.arx-result-card.accepted{border-color:rgba(142,240,207,.45)}.arx-result-card.rejected{border-color:rgba(249,115,103,.45)}.arx-result-card p{margin:14px auto;max-width:470px}.arx-chance{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin:15px 0}.arx-chance span{padding:8px;border-radius:6px;background:rgba(42,91,106,.35);color:#8db6c0;font-size:7px}.arx-chance b{display:block;margin-top:4px;color:#eafaff;font-size:13px}.arx-award{margin:15px auto 20px}.arx-award span,.arx-award small{display:block}.arx-award span{color:#f6d365;font:800 31px Georgia,serif}.arx-award small{color:#91bac4;font-size:7px}.arx-store-warning{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:18px 0}.arx-store-warning span{padding:12px;border:1px solid rgba(249,115,103,.28);border-radius:8px;background:rgba(100,43,47,.18)}.arx-store-warning small,.arx-store-warning b{display:block}.arx-store-warning small{color:#f2b3a8;font-size:8px}.arx-store-warning b{margin-top:4px}.arx-vessel-card{width:min(1050px,100%)}.arx-vessel-figure{position:relative;height:310px;margin:18px 0;padding:20px;overflow:hidden;border:1px solid rgba(125,211,252,.18);border-radius:12px;background:radial-gradient(circle at 60% 90%,rgba(62,137,160,.35),transparent 55%),linear-gradient(#08283d,#0c4258)}.arx-vessel-figure>img{position:absolute;left:4%;right:4%;bottom:10px;width:92%;height:88%;object-fit:contain;transform-origin:right bottom}.ship-fishing>img{transform:scaleX(.68) scaleY(.78)}.ship-coastal>img{transform:scaleX(.8) scaleY(.85)}.ship-global>img{transform:scaleX(.92) scaleY(.94)}.ship-icebreaker>img{transform:scaleX(1) scaleY(1.02)}.ship-nuclear>img{transform:scaleX(1.08) scaleY(1.06)}.arx-deck-line{position:absolute;left:9%;right:41%;top:29%;height:62%}.arx-deck-module{position:absolute;left:calc(2% + var(--module-index)*12%);bottom:20%;min-width:58px;padding:7px 5px;border:2px solid #f6d365;border-radius:5px;background:rgba(8,39,55,.92);color:#fff2ac;font-size:7px;font-weight:900;text-align:center}.arx-deck-module.helideck{bottom:4%;border-radius:50%;border-color:#8ef0cf;color:#8ef0cf}.arx-deck-module.aircraft{bottom:36%;border-color:#f7a766;color:#ffd2a3}.arx-bow-label{display:none!important;position:absolute;right:6%;bottom:13%;color:#88bbc8;font-size:8px;font-weight:900}.arx-vessel-facts{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:13px 0}.arx-vessel-facts span{padding:10px;border-radius:8px;background:rgba(30,79,96,.48)}.arx-vessel-facts small,.arx-vessel-facts b{display:block}.arx-vessel-facts small{color:#82adba;font-size:7px}.arx-vessel-facts b{margin-top:4px;font-size:9px}.arx-vessel-columns{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}.arx-manifest{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}.arx-manifest>div{display:flex;gap:8px;align-items:center;padding:7px;border-radius:7px;background:rgba(30,79,96,.35)}.arx-manifest img{width:38px;height:38px;border-radius:9px;object-fit:cover}.arx-manifest b,.arx-manifest small{display:block}.arx-manifest b{font-size:9px}.arx-manifest small{margin-top:2px;color:#8eb7c3;font-size:7px}.arx-equipment-list{display:grid;gap:5px;margin:0;padding:0;list-style:none}.arx-equipment-list li{display:flex;justify-content:space-between;gap:8px;padding:8px;border-radius:7px;background:rgba(30,79,96,.35)}.arx-equipment-list b{font-size:9px}.arx-equipment-list span{color:#8eb7c3;font-size:7px;text-align:right}.arx-journal{margin-top:18px;padding:13px;border:1px solid rgba(166,230,244,.16);border-radius:9px;background:rgba(15,54,70,.4)}.arx-journal p{margin:5px 0;padding-left:10px;border-left:2px solid rgba(246,211,101,.4);color:#aacbd3;font-size:9px}.arx-image-note{color:#6f9eab!important;font-size:7px!important;text-align:center}
      @media(max-width:760px){#arx-mobile-toggle{display:block}.arx-sidebar{display:none;left:auto;right:10px;top:76px;width:min(286px,calc(100vw - 20px));max-height:calc(100vh - 150px)}.arx-sidebar.open{display:block}.arx-side-head button{display:block}.arx-modal{padding:10px}.arx-modal-card{max-height:calc(100vh - 20px);padding:20px 15px}.arx-port-summary,.arx-grid,.arx-vessel-columns{grid-template-columns:1fr}.arx-resupply,.arx-target-facts,.arx-vessel-facts,.arx-store-warning{grid-template-columns:1fr 1fr}.arx-wildlife-card{grid-template-columns:1fr}.arx-photo,.arx-photo img{min-height:230px}.arx-modal-card h2{font-size:25px}.arx-media.hero,.arx-media.result{margin:-20px -15px 16px}.arx-vessel-figure{height:220px}.arx-deck-module{min-width:45px;padding:5px 3px;font-size:6px}.arx-manifest{grid-template-columns:1fr}.arx-operation li{grid-template-columns:24px 1fr}.arx-operation li>span{grid-column:2}}
    `;
    document.head.appendChild(style);
    style.textContent+=`
      .arx-store-list{grid-template-columns:1fr!important}.arx-store-details{padding:0;overflow:hidden}.arx-store-details>summary{display:flex;justify-content:space-between;gap:14px;align-items:center;padding:14px;list-style:none;cursor:pointer}.arx-store-details>summary::-webkit-details-marker{display:none}.arx-store-details>summary:after{content:'＋';flex:0 0 auto;color:#7dd3fc;font-size:17px}.arx-store-details[open]>summary:after{content:'−'}.arx-store-details>summary span{min-width:0}.arx-store-details>summary b,.arx-store-details>summary small{display:block}.arx-store-details>summary b{color:#eff9fb;font-size:12px}.arx-store-details>summary small{margin-top:4px;color:#82afbc;font-size:7px;line-height:1.35;letter-spacing:.07em}.arx-store-details>summary em{margin-left:auto;color:#f6d365;font-size:9px;font-style:normal;white-space:nowrap}.arx-detail-split{display:grid;grid-template-columns:minmax(220px,.9fr) 1.35fr;gap:16px;padding:0 14px 14px;border-top:1px solid rgba(166,230,244,.13)}.arx-detail-split>.arx-media{height:210px;margin:14px 0 0}.arx-detail-split>div{padding-top:7px}.arx-detail-split p{min-height:0}.arx-spec-list{padding-left:18px;color:#b5d0d6;font-size:9px;line-height:1.6}.arx-card button.danger{border:1px solid rgba(249,115,103,.38);background:rgba(111,45,52,.6);color:#ffd0c9}.arx-card button.danger:hover{background:rgba(145,54,61,.72)}.arx-complete{text-align:left}.arx-complete>small,.arx-complete>h2,.arx-complete>p{text-align:center}.arx-complete>button{margin-top:16px}.arx-vessel-overview>header>small{color:#7dd3fc;font-size:8px;font-weight:900;letter-spacing:.16em}.arx-vessel-overview>header h2{margin:7px 0 8px;color:#f4fbfc;font:800 30px/1.05 Georgia,serif}.arx-vessel-overview>header p{margin:0;color:#a9cbd4;font-size:11px;line-height:1.5}.ship-fishing>img,.ship-trawler>img,.ship-coastal>img,.ship-global>img,.ship-icebreaker>img,.ship-nuclear>img{transform:none}.ship-global>img,.ship-icebreaker>img,.ship-nuclear>img{width:96%;height:94%;left:2%;right:2%;bottom:4px}
      @media(max-width:760px){.arx-detail-split{grid-template-columns:1fr}.arx-detail-split>.arx-media{height:180px}.arx-store-details>summary{padding:12px}.arx-store-details>summary em{font-size:8px}.arx-vessel-overview>header h2{font-size:25px}}
    `;
    style.textContent+=`
      .arx-target-facts.compact{grid-template-columns:repeat(3,1fr);margin:13px 0}.arx-check-title{margin:12px 0 7px;font:800 13px Georgia,serif}.arx-readiness{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin:0 0 12px}.arx-readiness>div{display:flex;gap:8px;align-items:center;min-height:42px;padding:7px 9px;border:1px solid rgba(249,115,103,.25);border-radius:7px;background:rgba(92,45,49,.18)}.arx-readiness>div.ready{border-color:rgba(142,240,207,.24);background:rgba(35,91,77,.17)}.arx-readiness i{display:grid;place-items:center;flex:0 0 23px;height:23px;border-radius:50%;background:#8c3b44;color:#fff;font-style:normal;font-weight:900}.arx-readiness .ready i{background:#3e9e7e}.arx-readiness b,.arx-readiness small{display:block}.arx-readiness b{font-size:8px}.arx-readiness small{margin-top:2px;color:#9fc3cd;font-size:7px;line-height:1.25}.arx-operation{width:min(720px,100%);max-height:calc(100vh - 24px);overflow:hidden}.arx-operation h2{font-size:24px}.arx-operation-progress{margin:11px 0 9px;padding:9px}.arx-operation ol{grid-template-columns:1fr;gap:4px}.arx-operation li{min-height:39px;padding:5px}.arx-operation li>i{width:21px;height:21px}.arx-operation li>b{font-size:8px}.arx-operation li>span{font-size:6px}.arx-operation .arx-chance{margin:8px 0}.arx-complete>button{margin-top:8px}.arx-observation-note{padding:8px;border-radius:7px;background:rgba(246,211,101,.1);color:#dbeef1!important;font-size:9px!important}.arx-character-card{width:min(700px,100%)}.arx-avatar-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:16px 0}.arx-avatar-grid button{padding:5px;border:2px solid transparent;border-radius:10px;background:rgba(30,79,96,.48);color:#b8d7df;cursor:pointer}.arx-avatar-grid button.selected{border-color:#f6d365;background:rgba(104,88,37,.38)}.arx-avatar-grid img{display:block;width:100%;aspect-ratio:1;object-fit:cover;border-radius:7px}.arx-avatar-grid span{display:block;margin-top:4px;font-size:6px}.arx-specialty-select{display:block;padding:11px;border-radius:9px;background:rgba(30,79,96,.48)}.arx-specialty-select>span,.arx-specialty-select>small{display:block;color:#8fb7c2;font-size:7px;font-weight:800;letter-spacing:.08em}.arx-specialty-select select{width:100%;margin:7px 0;padding:9px;border:1px solid rgba(166,230,244,.25);border-radius:7px;background:#123d51;color:#eff9fb}.arx-character-summary{display:flex;justify-content:space-between;gap:12px;margin:11px 0;padding:9px;border-left:3px solid #f6d365;background:rgba(246,211,101,.08)}.arx-character-summary b{color:#f6d365}.arx-character-summary span{color:#a8cbd4;font-size:8px}.arx-npc-card{display:grid;grid-template-columns:minmax(220px,.85fr) 1.2fr;gap:20px;width:min(780px,100%)}.arx-npc-card>.arx-media{height:100%;min-height:270px}.arx-npc-person{display:flex;gap:9px;align-items:center;margin:12px 0;padding:8px;border-radius:8px;background:rgba(30,79,96,.42)}.arx-npc-person img{width:48px;height:48px;border-radius:11px;object-fit:cover}.arx-npc-person b,.arx-npc-person small{display:block}.arx-npc-person small{margin-top:3px;color:#8fb7c2;font-size:7px}.arx-aid-note{padding:9px;border:1px solid rgba(246,211,101,.3);border-radius:7px;background:rgba(246,211,101,.08);color:#d9edf0!important;font-style:italic}
      @media(max-width:760px){.arx-readiness{grid-template-columns:1fr}.arx-avatar-grid{grid-template-columns:repeat(3,1fr)}.arx-npc-card{grid-template-columns:1fr}.arx-npc-card>.arx-media{min-height:150px;height:180px}.arx-operation{padding:15px 12px}.arx-operation h2{font-size:19px}.arx-operation ol{grid-template-columns:1fr}.arx-operation li{grid-template-columns:20px 1fr!important}.arx-operation li>span{display:none}.arx-operation-progress b{font-size:18px}}
    `;
    style.textContent+=`.arx-store-details .arx-detail-split>.arx-media img{object-fit:contain!important;background:#123d51}.arx-character-summary img{flex:0 0 auto;width:96px;height:96px;object-fit:cover;border-radius:10px}.arx-character-summary>div{min-width:0}.arx-character-summary b,.arx-character-summary span,.arx-character-summary small{display:block}.arx-heli-resupply{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;margin:12px 0;padding:11px;border:1px solid rgba(246,211,101,.32);border-radius:9px;background:rgba(246,211,101,.08)}.arx-heli-resupply b,.arx-heli-resupply small{display:block}.arx-heli-resupply b{color:#f6d365;font-size:9px}.arx-heli-resupply small{margin-top:3px;color:#9fc3cd;font-size:7px}.arx-heli-resupply button{width:auto!important;min-width:210px}@media(max-width:760px) and (orientation:portrait){.arx-character-summary{display:grid!important;grid-template-columns:1fr!important;justify-items:center!important;text-align:center!important}.arx-character-summary>div{width:100%}.arx-heli-resupply{grid-template-columns:1fr}.arx-heli-resupply button{width:100%!important;min-width:0}}@media(max-width:900px) and (orientation:landscape){.arx-store-details .arx-detail-split>.arx-media{height:min(230px,48vh)!important}.arx-store-details .arx-detail-split>.arx-media img{object-fit:contain!important}}`;
    style.textContent+=`
      .arx-operation-subhead{margin:10px 0 6px;color:#8fb7c2;font-size:8px;letter-spacing:.12em}.arx-operation-scientists{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:6px;margin-bottom:8px}.arx-operation-scientists>div{display:flex;gap:7px;align-items:center;padding:6px;border-radius:7px;background:rgba(30,79,96,.38)}.arx-operation-scientists img{width:34px;height:34px;border-radius:8px;object-fit:cover}.arx-operation-scientists b,.arx-operation-scientists small{display:block}.arx-operation-scientists b{font-size:8px}.arx-operation-scientists small{margin-top:2px;color:#8fb7c2;font-size:6px}
    `;
    style.textContent+=`
      #arx-dev-toggle{position:fixed;z-index:8;right:12px;bottom:12px;padding:6px 9px;border:1px solid rgba(247,167,102,.55);border-radius:7px;background:rgba(59,35,29,.82);color:#ffd2a3;font-size:7px;font-weight:900;letter-spacing:.12em;cursor:pointer;backdrop-filter:blur(8px)}
      .arx-relocation-list{display:grid;gap:7px}.arx-relocation-row{display:grid;grid-template-columns:minmax(170px,1.2fr) minmax(130px,.7fr) minmax(150px,.8fr);gap:10px;align-items:center;padding:10px;border:1px solid rgba(166,230,244,.15);border-radius:8px;background:rgba(30,79,96,.33)}.arx-relocation-row b,.arx-relocation-row small{display:block}.arx-relocation-row small{margin-top:3px;color:#8fb7c2;font-size:7px}.arx-relocation-row>span{color:#8ef0cf;font-size:8px;font-weight:800}.arx-relocation-row.frozen{opacity:.46;filter:saturate(.35)}.arx-relocation-row.frozen>span{color:#b7c0c4}.arx-relocation-row button{padding:8px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:7px;font-weight:900}.arx-relocation-row button:disabled{background:#315766;color:#7896a0}.arx-dev-card{width:min(520px,100%)}.arx-dev-card label{display:block;margin:12px 0;padding:10px;border-radius:8px;background:rgba(30,79,96,.42)}.arx-dev-card label span{display:block;margin-bottom:6px;color:#8fb7c2;font-size:7px;font-weight:900;letter-spacing:.1em}.arx-dev-card select{width:100%;padding:9px;border:1px solid rgba(166,230,244,.25);border-radius:7px;background:#123d51;color:#eff9fb}.arx-dev-warning{margin:12px 0;padding:9px;border:1px solid rgba(247,167,102,.3);border-radius:7px;background:rgba(97,55,35,.22);color:#ffd2a3;font-size:8px;line-height:1.45}
      @media(max-width:760px){#arx-dev-toggle{right:8px;bottom:8px}.arx-relocation-row{grid-template-columns:1fr}.arx-relocation-row button{width:100%}.arx-port-navrow{display:block}.arx-port-cash{justify-content:space-between!important;padding:8px 0!important;border-left:0;border-bottom:1px solid rgba(166,230,244,.14)}.arx-funding-grid{grid-template-columns:1fr}}
    `;
    style.textContent+=`
      .arx-character-name{display:block;margin:16px 0 12px}.arx-character-name span,.arx-specialty-select>span{display:block;margin-bottom:6px;color:#8fb7c2;font-size:7px;font-weight:900;letter-spacing:.11em}.arx-character-name input{width:100%;padding:11px 12px;border:1px solid rgba(166,230,244,.24);border-radius:8px;background:#123d51;color:#eff9fb;font:700 14px system-ui}.arx-avatar-grid button{overflow:hidden}.arx-avatar-grid button img{display:block}.arx-tabs-viewport{position:relative;display:flex;flex:1 1 auto;min-width:0}.arx-tabs-viewport .arx-tabs{flex:1 1 auto;min-width:0}.arx-tab-hint{display:none;pointer-events:none;transition:opacity .12s ease}.arx-tab-hint.hidden{opacity:0!important;visibility:hidden!important}.arx-tabs button.attention{outline:1px solid rgba(142,240,207,.9)!important;outline-offset:-2px!important;box-shadow:inset 0 0 0 1px rgba(142,240,207,.2),inset 0 0 15px rgba(142,240,207,.12)!important;border-radius:5px}#arx-mobile-toggle.attention{border-color:#8ef0cf!important;background:rgba(28,105,85,.96)!important;color:#ecfff8!important;box-shadow:0 0 0 2px rgba(142,240,207,.14),0 0 22px rgba(142,240,207,.48)!important}#arx-mobile-toggle.article-ready{border-color:#f6d365!important;background:rgba(112,78,10,.96)!important;color:#fff4bd!important;box-shadow:0 0 0 2px rgba(246,211,101,.2),0 0 24px rgba(246,211,101,.58)!important}.arx-vessel-purchase-breakdown{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:10px 0}.arx-vessel-purchase-breakdown span{padding:8px;border-radius:7px;background:rgba(30,79,96,.45)}.arx-vessel-purchase-breakdown small,.arx-vessel-purchase-breakdown b{display:block}.arx-vessel-purchase-breakdown small{color:#82adba;font-size:6px;line-height:1.25;letter-spacing:.07em}.arx-vessel-purchase-breakdown b{margin-top:4px;color:#fff1a8;font-size:10px}@media(max-width:760px){.arx-vessel-purchase-breakdown{grid-template-columns:1fr}}
      @media(max-width:760px) and (orientation:portrait){.arx-modal.open{place-items:start center!important}.arx-modal{padding:calc(env(safe-area-inset-top) + 34px) 9px calc(env(safe-area-inset-bottom) + 10px)!important}.arx-modal-card{max-height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 44px)!important}.arx-port-navrow{display:block!important}.arx-tabs-viewport{padding:0 13px}.arx-tab-hint{position:absolute;z-index:5;top:0;bottom:1px;width:16px;display:grid;place-items:center;color:#dffaff;font:900 18px/1 system-ui;background:linear-gradient(90deg,rgba(4,27,40,.98),rgba(4,27,40,.25))}.arx-tab-hint.left{left:0}.arx-tab-hint.right{right:0;transform:none;background:linear-gradient(270deg,rgba(4,27,40,.98),rgba(4,27,40,.25))}.arx-port-cash{justify-content:space-between!important;padding:8px 0!important;border-left:0!important;border-bottom:1px solid rgba(166,230,244,.14)!important}}
      @media(max-width:900px) and (orientation:landscape){.arx-port-navrow{display:flex!important}.arx-tabs-viewport{padding:0!important}.arx-tab-hint{display:none!important}.arx-port-cash{flex:0 0 auto!important;justify-content:flex-end!important;padding:0 10px!important;border-left:1px solid rgba(166,230,244,.18)!important;border-bottom:0!important}}
    `;
    style.textContent+=`
      .arx-research-unified{width:min(780px,100%)!important;max-height:calc(100vh - 24px)!important;overflow:auto!important}.arx-research-unified .arx-media.hero{height:180px;margin:10px 0 14px;border-radius:10px}.arx-research-facts{grid-template-columns:repeat(3,1fr)!important}.arx-research-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:12px}.arx-research-actions.single{grid-template-columns:1fr}.arx-research-actions button,.arx-grant-actions button{width:100%;padding:9px;border:0;border-radius:7px;background:#f6d365;color:#17323b;font-size:7px;font-weight:900;letter-spacing:.06em}.arx-research-actions button:disabled{background:#315766;color:#7896a0}.arx-research-actions .ghost{border:1px solid rgba(166,230,244,.25);background:transparent;color:#a9d2dc}.arx-research-actions .danger,.arx-grant-actions .danger{border:1px solid rgba(249,115,103,.38);background:rgba(111,45,52,.6);color:#ffd0c9}.arx-operation-scientists,.arx-operation-equipment{display:flex;flex-wrap:wrap;gap:7px;margin:7px 0 11px}.arx-operation-scientists>div,.arx-operation-gear{display:flex;align-items:center;gap:7px;min-width:150px;padding:6px;border-radius:7px;background:rgba(30,79,96,.4)}.arx-operation-scientists img,.arx-operation-gear img{width:42px;height:42px;flex:0 0 42px;border-radius:7px;object-fit:cover;background:#123d51}.arx-operation-gear img{object-fit:contain}.arx-operation-scientists b,.arx-operation-scientists small,.arx-operation-gear span{display:block;font-size:7px}.arx-operation-scientists small{margin-top:2px;color:#8fb7c2}.arx-operation-subhead,.arx-mini-label{margin:9px 0 4px;color:#7dd3fc;font:900 8px system-ui;letter-spacing:.1em}.research-offer.locked{filter:saturate(.28);border-color:rgba(148,163,184,.3)!important}.arx-missing-equipment-links{display:grid;gap:6px;margin:8px 0}.arx-missing-equipment-links button{border:1px solid rgba(125,211,252,.4)!important;background:rgba(24,76,98,.78)!important;color:#bcefff!important;text-align:left!important;cursor:pointer!important}.arx-card.grant.locked{filter:saturate(.32);border-color:rgba(148,163,184,.28)!important}.research-offer .arx-operation-scientists>div,.research-offer .arx-operation-gear{min-width:130px;padding:4px}.research-offer .arx-operation-scientists img,.research-offer .arx-operation-gear img{width:34px;height:34px;flex-basis:34px}.arx-grant-advance{display:grid;grid-template-columns:1fr;gap:6px;margin:8px 0}.arx-grant-advance span{padding:7px;border-radius:7px;background:rgba(246,211,101,.08)}.arx-grant-advance small,.arx-grant-advance b{display:block}.arx-grant-advance small{color:#8fb7c2;font-size:6px}.arx-grant-advance b{margin-top:3px;color:#fff1a8;font-size:10px}.arx-grant-actions{display:grid;grid-template-columns:1fr;gap:6px}.arx-publication-tier-guide{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:16px 0;text-align:left}.arx-publication-tier-guide span{padding:11px;border:1px solid rgba(125,211,252,.2);border-radius:8px;background:rgba(30,79,96,.42)}.arx-publication-tier-guide b,.arx-publication-tier-guide small,.arx-publication-tier-guide em{display:block}.arx-publication-tier-guide b{color:#f6d365;font:900 14px system-ui}.arx-publication-tier-guide small{margin-top:3px;color:#7dd3fc;font-size:8px;font-weight:900}.arx-publication-tier-guide em{margin-top:7px;color:#a9cbd4;font-size:8px;font-style:normal;line-height:1.4}.arx-gauge-labels{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px;color:#91bac4;font-size:7px;font-weight:900;letter-spacing:.08em;text-align:center}@media(max-width:760px){.arx-publication-tier-guide{grid-template-columns:1fr}}.arx-result-placeholder{padding:9px;border:1px dashed rgba(166,230,244,.18);border-radius:7px;color:#789eaa;font-size:8px;text-align:center}.arx-research-result{padding:10px;border:1px solid rgba(142,240,207,.24);border-radius:8px;background:rgba(35,91,77,.16)}.arx-research-result>small{color:#8ef0cf;font-size:8px;font-weight:900;letter-spacing:.08em}.arx-research-result>p{color:#b9d7d9;font-size:9px}@media(max-width:760px){.arx-research-facts{grid-template-columns:1fr 1fr!important}.arx-research-actions{grid-template-columns:1fr 1fr}.arx-research-unified .arx-media.hero{height:145px}.arx-grant-advance{grid-template-columns:1fr}}
    `;
    root.addEventListener('click',event=>{
      const mobile=event.target.closest('[data-arx-action="mobile-toggle"]');
      if (mobile) { root.querySelector('#arx-sidebar').classList.toggle('open'); return; }
      handleAction(event); handleTabs(event);
    });
    root.addEventListener('toggle',event=>{
      const detail=event.target.closest?.('[data-arx-store-details]'); if (!detail||!detail.open) return;
      openStoreDetail=detail.dataset.arxStoreDetails;
      detail.closest('.arx-port-card')?.querySelectorAll('[data-arx-store-details][open]').forEach(other=>{if(other!==detail)other.open=false;});
      requestAnimationFrame(()=>detail.scrollIntoView({block:'start',behavior:'smooth'}));
    },true);
  }

  function initialize(config={}) {
    callbacks={...config}; catalog=config.wildlifeCatalog||window.ARCTIC_WILDLIFE_CATALOG||{};
    ensureUI(); renderSidebar(); return api;
  }
  function getVesselModifiers() {
    const ship=vessel();
    let visibilityBonusKm=0;
    if (equipmentOperational('research-radar')) visibilityBonusKm+=12;
    if (equipmentOperational('large-drone')) visibilityBonusKm+=10;
    if (equipmentOperational('manned-helicopter')) visibilityBonusKm+=18;
    if (equipmentOperational('profiling-aerostat')) visibilityBonusKm+=4;
    return {id:ship.id,classId:ship.id,name:ship.shipName||ship.name,modelName:ship.name,className:ship.className,image:ship.image||'assets/vessels/base-vessel.png',cruiseKnots:ship.cruiseKnots,maxKnots:ship.maxKnots,crackedIceFactor:ship.crackedIceFactor||.1,berths:ship.berths,slots:{...ship.slots},helidecks:ship.helidecks,minZoom:ship.minZoom,fuelCapacity:ship.fuelCapacity,foodCapacity:ship.foodCapacity,fuelEnduranceDays:ship.fuelEnduranceDays,foodEnduranceDays:ship.foodEnduranceDays,nuclearFuel:!!ship.nuclearFuel,visibilityBonusKm};
  }
  function getMapTargets() {
    const remove=new Set();
    if(callbacks.researchSitePortClear){
      for(const item of state.targets)if((item.kind==='opportunity'||item.kind==='weather-opportunity')&&!callbacks.researchSitePortClear(item))remove.add(item.id);
    }
    const field=state.targets.filter(item=>(item.kind==='opportunity'||item.kind==='weather-opportunity')&&!remove.has(item.id));
    if(field.length>2){
      const ranked=[...field].sort((a,b)=>Number(!!(b.accepted||b.selected||b.active))-Number(!!(a.accepted||a.selected||a.active))||state.targets.indexOf(b)-state.targets.indexOf(a));
      const keep=new Set(ranked.slice(0,2).map(item=>item.id));
      for(const item of field)if(!keep.has(item.id))remove.add(item.id);
    }
    if(remove.size){
      state.targets=state.targets.filter(item=>!remove.has(item.id));
      if(state.navigation&&remove.has(state.navigation.id))state.navigation=null;
      if(state.lastTargetContext&&remove.has(state.lastTargetContext.id))state.lastTargetContext=null;
    }
    return state.targets.map(item=>({...item,mapEligible:eligible(item,item.weather?{type:item.weather}:null)}));
  }
  function resetWildlifeObservations(ids=[]) { const clear=new Set(ids.map(String)); state.observedIndividuals=(state.observedIndividuals||[]).filter(id=>!clear.has(String(id))); callbacks.onStateChange?.(); }
  function selectTarget(id) { const chosen=state.targets.find(item=>item.id===id),random=chosen&&(chosen.kind==='opportunity'||chosen.kind==='weather-opportunity');state.targets.forEach(item=>{const isRandom=item.kind==='opportunity'||item.kind==='weather-opportunity';if(random){if(isRandom)item.selected=item.id===id;}else item.selected=item.id===id;}); renderSidebar(); }
  function getState() { return clone(state); }
  function createCheckpoint() { return getState(); }
  function restoreCheckpoint(snapshot) {
    if (!snapshot) return;
    if (operationFrame) cancelAnimationFrame(operationFrame);
    operationFrame=0; activeOperation=null; pendingDeparture=null; portOpen=false; promotionQueue=[];
    root?.querySelectorAll('.arx-modal.open').forEach(modal=>modal.classList.remove('open'));
    for (const key of Object.keys(state)) if (Object.prototype.hasOwnProperty.call(snapshot,key)) state[key]=clone(snapshot[key]);
    state.inventory=state.inventory||{}; state.deployments=state.deployments||[]; state.weatherEventsSeen=state.weatherEventsSeen||[]; state.droppedGrantTemplates=state.droppedGrantTemplates||[]; state.scientistRecords=state.scientistRecords||{};
    state.observed=state.observed||[]; state.observedIndividuals=state.observedIndividuals||[]; state.homePortId=state.homePortId||'longyearbyen'; state.recentGrantTemplates=state.recentGrantTemplates||[]; state.recentGrantSites=state.recentGrantSites||[]; state.recentOpportunityTemplates=state.recentOpportunityTemplates||[]; state.lastOpportunitySpawnPosition=state.lastOpportunitySpawnPosition||null; state.grantCooldowns=state.grantCooldowns||{}; state.grantMarketReady=state.grantMarketReady||{}; state.assistedByVessels=state.assistedByVessels||[]; state.bridgeSupportNotice=state.bridgeSupportNotice||null; state.lastPortId=state.lastPortId||null; state.lastProfessorGrantDay=Number(state.lastProfessorGrantDay??-999); state.remoteOffer=state.remoteOffer||null; state.helicopterFoodReminderShown=!!state.helicopterFoodReminderShown; state.elapsedDays=Number(state.elapsedDays)||0; state.playerConfigured=!!state.playerConfigured;
    state.installedEquipment=(state.installedEquipment||[]).filter(id=>EQUIPMENT[id]&&!EQUIPMENT[id].builtIn);
    state.scientists=(state.scientists||[]).map(item=>({...item,missions:item.missions||0,papers:item.papers||0,recruitmentPool:item.recruitmentPool||profileFor(item).recruitmentPool||'international'}));
    for (const scientist of state.scientists) recordScientist(scientist);
    state.offers=(state.offers||[]).filter(Boolean).slice(0,9);
    renderSidebar();
  }
  function ensureMinimumSupplies(fraction=.25) { state.supplies=Math.max(state.supplies,Math.ceil(vessel().supplyCapacity*fraction)); renderSidebar(); }

  const api={
    initialize,enterPort,leavePort,tickDays,getVesselModifiers,getMapTargets,selectTarget,updateNavigation,openTarget,openNavigationPrompt,
    completeTarget,openWildlife,openVessel,openNpcVessel,openCharacterSetup,confirmDeparture,getState,createCheckpoint,restoreCheckpoint,
    restoreSnapshot:restoreCheckpoint,ensureMinimumSupplies,maybeSpawnOpportunity,maybeHelicopterFoodReminder,isWildlifeObserved:id=>(state.observedIndividuals||[]).includes(String(id)),resetWildlifeObservations,
    canAutoOpenTarget:()=>!activeOperation&&!root?.querySelector('.arx-modal.open'),
    isBusy:()=>!!activeOperation||!!root?.querySelector('.arx-modal.open')||!!root?.querySelector('.arx-sidebar.open')
  };
  window.ArcticResearch=api;
})();

