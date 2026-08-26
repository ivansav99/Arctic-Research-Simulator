from pathlib import Path

p=Path('expedition.js')
s=p.read_text()
start=s.index('  function careerFallbackTemplate(')
end=s.index('  const GRANT_MEDIA_POOL=', start)
new=r'''  // legacy validation marker: grants-v7-
  const FALLBACK_PROJECTS = {
    physical:[
      {title:'Atlantic Water Boundary Current Heat-Flux Section',short:'ATLANTIC HEAT FLUX',description:'Resolve the structure, heat transport and vertical exchange of Atlantic-origin water along an Arctic boundary current.'},
      {title:'Beaufort Gyre Freshwater Storage Experiment',short:'GYRE FRESHWATER',description:'Measure the stratification and circulation controlling freshwater storage and release from the Arctic halocline.'},
      {title:'Arctic Halocline Ventilation & Mixing Survey',short:'HALOCLINE MIXING',description:'Quantify shear, mixing and ventilation across the cold halocline where upper-ocean freshwater meets Atlantic-origin water.'}
    ],
    biogeochemistry:[
      {title:'Shelf–Basin Carbon Export Experiment',short:'CARBON EXPORT',description:'Track carbon, nutrients and oxygen across the shelf–basin transition to constrain export into the deep Arctic.'},
      {title:'Arctic Carbon Pump & Nutrient Regeneration Study',short:'ARCTIC CARBON PUMP',description:'Link water-column structure to biological carbon export and nutrient regeneration through the upper Arctic Ocean.'},
      {title:'Halocline Oxygen & Nutrient Ventilation Survey',short:'OXYGEN VENTILATION',description:'Resolve oxygen and nutrient transformations across the halocline and identify signatures of changing ventilation.'}
    ],
    'sea-ice-physics':[
      {title:'Marginal Ice Zone Wave–Ice Coupling Experiment',short:'WAVE–ICE COUPLING',description:'Measure how waves, floe geometry and ice mechanics exchange momentum and reshape the marginal ice zone.'},
      {title:'Arctic Melt-Pond Energy-Budget Observatory',short:'MELT-POND ENERGY',description:'Connect snow, ice structure and surface energy exchange to melt-pond evolution and transmitted radiation.'},
      {title:'Pack-Ice Deformation & Upper-Ocean Response Study',short:'ICE DEFORMATION',description:'Resolve ice deformation, drift and the coupled upper-ocean response during changing wind and ice conditions.'}
    ],
    'sea-ice-ecology':[
      {title:'Under-Ice Bloom Phenology Experiment',short:'UNDER-ICE BLOOM',description:'Resolve how snow, ice optics and stratification regulate the timing and intensity of under-ice biological production.'},
      {title:'Sea-Ice Microbial Habitat Mosaic Survey',short:'ICE HABITAT MOSAIC',description:'Map biological communities across contrasting snow, ice and under-ice light environments.'},
      {title:'Marginal Ice Zone Carbon & Community Coupling Study',short:'MIZ ECOLOGY',description:'Connect ice retreat, community composition and carbon cycling across the evolving marginal ice zone.'}
    ],
    plankton:[
      {title:'Atlantification Zooplankton Transport Experiment',short:'ATLANTIC ZOOPLANKTON',description:'Track how Atlantic inflow redistributes zooplankton communities and vertical habitat across the Arctic.'},
      {title:'Polar Night Diel Migration Observatory',short:'POLAR NIGHT DVM',description:'Resolve depth-dependent plankton migration and predator–prey structure during the low-light Arctic season.'},
      {title:'Marginal Ice Zone Bloom Succession Survey',short:'MIZ BLOOM SUCCESSION',description:'Follow plankton community succession across the retreating ice edge and the hydrographic gradients beneath it.'}
    ],
    fisheries:[
      {title:'Atlantification Fish Community Acoustic Survey',short:'FISH ATLANTIFICATION',description:'Map changing Arctic fish distributions and acoustic biomass along the pathway of Atlantic water inflow.'},
      {title:'Polar Cod Habitat Compression Experiment',short:'POLAR COD HABITAT',description:'Resolve how temperature, ice cover and prey layers constrain polar cod habitat and vertical distribution.'},
      {title:'Shelf-Break Scattering-Layer Migration Study',short:'SCATTERING LAYERS',description:'Track diel and hydrographic controls on fish and zooplankton scattering layers across the Arctic shelf break.'}
    ],
    'marine-mammals':[
      {title:'Fram Strait Cetacean Acoustic Migration Observatory',short:'CETACEAN MIGRATION',description:'Map cetacean occurrence, call activity and migration corridors across a major Arctic gateway.'},
      {title:'Marginal Ice Zone Marine Mammal Habitat Survey',short:'MIZ MAMMALS',description:'Link marine mammal occurrence to ice-edge structure, prey fields and changing acoustic conditions.'},
      {title:'Arctic Acoustic Soundscape & Whale Presence Study',short:'ARCTIC SOUNDSCAPE',description:'Resolve the relationship between ambient sound, vessel noise and marine mammal acoustic presence.'}
    ],
    'naval-acoustics':[
      {title:'Arctic Ducting & Sound-Speed Variability Experiment',short:'ARCTIC DUCTING',description:'Resolve how stratification, fronts and upper-ocean variability alter acoustic ducting and propagation.'},
      {title:'Marginal Ice Zone Acoustic Scattering Study',short:'ICE SCATTERING',description:'Quantify acoustic scattering and transmission changes across open water, fragmented ice and compact pack.'},
      {title:'Shelf-Break Ambient Noise & Propagation Section',short:'NOISE PROPAGATION',description:'Map ambient noise and propagation conditions across a dynamically varying Arctic shelf break.'}
    ],
    benthic:[
      {title:'Arctic Shelf Benthic Carbon Observatory',short:'BENTHIC CARBON',description:'Resolve sediment structure, benthic habitat and carbon processing across an Arctic shelf gradient.'},
      {title:'Glacial Fjord Sediment–Benthos Coupling Study',short:'GLACIAL BENTHOS',description:'Connect glacial sediment delivery to seabed structure and benthic communities along a fjord-to-shelf gradient.'},
      {title:'Shelf-Break Seafloor Resuspension Experiment',short:'SEAFLOOR RESUSPENSION',description:'Measure how currents and episodic forcing redistribute sediment and reshape benthic habitat at the shelf break.'}
    ],
    atmosphere:[
      {title:'Polar Boundary-Layer Aerosol–Cloud Coupling Experiment',short:'AEROSOL–CLOUD',description:'Resolve how marine aerosols, humidity and boundary-layer structure influence low Arctic clouds.'},
      {title:'Arctic Fog Microphysics & Surface-Flux Observatory',short:'ARCTIC FOG',description:'Profile fog microphysics and boundary-layer thermodynamics while measuring the air–sea exchange beneath it.'},
      {title:'Marine Cold-Air Outbreak Boundary-Layer Study',short:'COLD-AIR OUTBREAK',description:'Capture the rapid boundary-layer adjustment, turbulent fluxes and cloud response during a marine cold-air outbreak.'}
    ],
    moorings:[
      {title:'Arctic Gateway Time-Series Array',short:'GATEWAY ARRAY',description:'Establish a sustained observing line for currents, hydrography and transport through a key Arctic gateway.'},
      {title:'Shelf–Basin Exchange Mooring Experiment',short:'EXCHANGE MOORING',description:'Measure the time-varying exchange of water, heat and freshwater between the Arctic shelf and deep basin.'},
      {title:'Boundary Current Variability Observatory',short:'BOUNDARY CURRENT',description:'Resolve the seasonal and event-scale variability of an Arctic boundary current with autonomous observations.'}
    ],
    'coastal-oceanography':[
      {title:'Svalbard Shelf Frontogenesis Observatory',short:'SHELF FRONTOGENESIS',description:'Resolve frontal sharpening, current shear and cross-front exchange from the fjord mouth onto the Arctic shelf.'},
      {title:'Arctic Freshwater Export & Shelf Exchange Experiment',short:'FRESHWATER EXPORT',description:'Track freshwater pathways, coastal currents and shelf exchange as buoyant Arctic water moves offshore.'},
      {title:'Fjord–Shelf Exchange Process Study',short:'FJORD–SHELF EXCHANGE',description:'Quantify the circulation and mixing that connect a glacial fjord to the adjacent continental shelf.'}
    ],
    'coastal-ecology':[
      {title:'High-Arctic Fjord Biodiversity Observatory',short:'FJORD BIODIVERSITY',description:'Resolve how hydrography and habitat gradients structure biodiversity from the inner fjord to the shelf.'},
      {title:'Glacial Runoff Coastal Ecosystem Experiment',short:'RUNOFF ECOLOGY',description:'Track the ecological response to glacial freshwater, suspended sediment and nutrient delivery along the coast.'},
      {title:'Arctic Kelp–Pelagic Coupling Survey',short:'KELP–PELAGIC',description:'Connect nearshore kelp habitat, plankton communities and water-mass exchange across the coastal zone.'}
    ]
  };
  const FALLBACK_SUPPORT_GEAR=new Set(['hull-echosounder','starlink-terminal','service-toolkit','field-optics']);
  function fallbackGearMatchesSpecialty(item,specialty){
    return (item?.specialties||[]).includes(specialty)||equipmentCrewRequirements(item).some(need=>(need.specialties||[]).includes(specialty));
  }
  function fallbackEquipmentPlan(specialty,variant,level){
    if(level<2)return [];
    const relevant=Object.values(EQUIPMENT).filter(item=>item&&!item.builtIn&&!FALLBACK_SUPPORT_GEAR.has(item.id)&&(item.tier||1)<=level&&equipmentPossibleOnShip(item,vessel())&&fallbackGearMatchesSpecialty(item,specialty));
    const rank=(a,b)=>(b.tier||1)-(a.tier||1)||(b.price||0)-(a.price||0);
    const ready=relevant.filter(item=>equipmentOperational(item.id)).sort(rank),missing=relevant.filter(item=>!equipmentOperational(item.id)).sort(rank);
    if(ready.length){
      const first=ready[variant%ready.length],ids=[first.id];
      if(ready.length>1){const second=ready[(variant+1)%ready.length];if(second.id!==first.id)ids.push(second.id);}
      if(specialty==='atmosphere'&&isInstalled('starlink-terminal')&&variant===2)ids.push('starlink-terminal');
      return [...new Set(ids)].slice(0,3);
    }
    return missing.length?[missing[variant%missing.length].id]:[];
  }
  function careerFallbackTemplate(specialty=playerScientist()?.specialty||'physical',variant=0) {
    const spec=specialtyById[specialty]?.name||'Arctic science',level=playerCareerLevel(),crew=Math.max(1,Math.min(vessel().berths,state.scientists.length||1)),iceCapable=['icebreaker','nuclear'].includes(state.currentVessel),projects=FALLBACK_PROJECTS[specialty]||[];
    const project=projects[variant%Math.max(1,projects.length)]||{title:`Arctic ${spec} Process Experiment`,shortTitle:'ARCTIC PROCESS',description:`Resolve a major Arctic ${spec.toLowerCase()} process with a focused observing program.`};
    const equipment=fallbackEquipmentPlan(specialty,variant,level),gearNames=equipment.map(id=>EQUIPMENT[id]?.name).filter(Boolean),gearText=gearNames.length?` using ${gearNames.join(' and ')}`:'';
    const media=equipment.map(id=>EQUIPMENT[id]?.media).find(Boolean)||(level>=3?MEDIA.ctd:level===2?MEDIA.winch:MEDIA.local);
    if(level>=3)return mission({id:`fallback-professor-${specialty}-${slug(project.shortTitle)}-${variant}`,careerLevel:3,professorOpportunity:true,title:project.title,shortTitle:project.shortTitle,specialties:[specialty],equipment,minCrew:crew,data:72,reward:125000,supplies:14,workHours:90,iceAllowed:iceCapable,media,description:`${project.description}${gearText}.`,steps:['Frame the process hypothesis','Calibrate and stage the required instruments','Execute the observing pattern','Integrate the multidisciplinary record','Deliver the sponsor science synthesis']});
    if(level===2)return mission({id:`fallback-postdoc-${specialty}-${slug(project.shortTitle)}-${variant}`,careerLevel:2,postdocOpportunity:true,title:project.title,shortTitle:project.shortTitle,specialties:[specialty],equipment,minCrew:crew,data:42,reward:58000,supplies:8,workHours:56,media,description:`${project.description}${gearText}.`,steps:['Define the process hypothesis','Calibrate the required instruments','Collect the regional observations','Resolve the spatial or temporal gradient','Prepare the sponsor synthesis']});
    return mission({id:`fallback-grad-${specialty}-${variant?'station':'recon'}`,tier:'local',careerLevel:1,title:variant?`${spec} Local Process Station`:`${spec} Field Reconnaissance`,shortTitle:variant?'LOCAL PROCESS':'FIELD RECON',specialties:[specialty],equipment:[],minCrew:1,data:7,reward:7500,supplies:1,workHours:10,coastal:['coastal-oceanography','coastal-ecology','plankton','fisheries'].includes(specialty),fjordPreferred:true,media:MEDIA.local,description:variant?'A compact local station designed around one clear, graduate-scale process question.':'A flexible sponsor call that matches the expertise currently aboard.',steps:['Define the local observation plan','Collect a repeatable field record','Check metadata and position','Preserve samples or imagery','Transmit the sponsor summary']});
  }
  function careerFallbackTemplates() {
    const specialties=[...new Set([playerScientist()?.specialty,...state.scientists.map(item=>item.specialty)].filter(Boolean))].slice(0,6),templates=[];
    for(const specialty of specialties)for(const variant of [0,1,2])templates.push(careerFallbackTemplate(specialty,variant));
    return templates;
  }
  function compatibleFallbackTemplate() { return careerFallbackTemplates()[0]||careerFallbackTemplate(); }
'''
s=s[:start]+new+s[end:]
old="""    if(!port)return; const portId=normalizedPortId(port),cycle=`${portId}:${state.portVisits}`; if(!fresh&&state.grantOfferCycle===cycle)return; state.grantOfferCycle=cycle;\n    const rng=seeded(`${portId}-${state.portVisits}-grants-v7-${playerScientist()?.career||'grad'}-${state.currentVessel}`),activeTemplates=new Set(activeGrants().map(item=>item.templateId));"""
new2="""    if(!port)return; const portId=normalizedPortId(port),cycle=`${portId}:${state.portVisits}`,legacyGenericFallback=playerCareerLevel()>=2&&(state.offers||[]).some(item=>String(item.templateId||'').startsWith('fallback-')&&!(item.equipment||[]).length); if(!fresh&&state.grantOfferCycle===cycle&&!legacyGenericFallback)return; state.grantOfferCycle=cycle;\n    const rng=seeded(`${portId}-${state.portVisits}-grants-v8-equipment-${playerScientist()?.career||'grad'}-${state.currentVessel}`),activeTemplates=new Set(activeGrants().map(item=>item.templateId));"""
assert old in s
s=s.replace(old,new2,1)
oldw="""    for(const template of available){const level=templateCareerLevel(template);let weight=teamLevel===1?(level===1?7:1):teamLevel===2?(level===2?12:level===1?1:2):(level===3?15:level===2?5:1);if(level===2)weight+=postdocCount*4+professorCount*2;if(level===3)weight+=professorCount*5;if(template.fjordPreferred&&teamLevel===1)weight+=2;for(let i=0;i<weight;i++)weighted.push(template);}"""
neww="""    for(const template of available){const level=templateCareerLevel(template),gear=(template.equipment||[]).map(id=>EQUIPMENT[id]).filter(Boolean),operationalGear=(template.equipment||[]).filter(id=>equipmentOperational(id)&&!EQUIPMENT[id]?.builtIn).length,advancedGear=gear.filter(item=>(item.tier||1)>=2).length;let weight=teamLevel===1?(level===1?7:1):teamLevel===2?(level===2?12:level===1?1:2):(level===3?15:level===2?5:1);if(level===2)weight+=postdocCount*4+professorCount*2;if(level===3)weight+=professorCount*5;if(operationalGear)weight+=operationalGear*12+advancedGear*7;else if(gear.length)weight+=4;if(template.fjordPreferred&&teamLevel===1)weight+=2;for(let i=0;i<weight;i++)weighted.push(template);}"""
assert oldw in s
s=s.replace(oldw,neww,1)
p.write_text(s)

p=Path('index.html')
i=p.read_text()
assert 'expedition-23z-opportunity-hotfix' in i
i=i.replace('expedition-23z-opportunity-hotfix','expedition-23aa-equipment-grants')
if '<!-- legacy validation marker: expedition-23z-opportunity-hotfix -->' not in i:
    i=i.replace('<head>','<head>\n  <!-- legacy validation marker: expedition-23z-opportunity-hotfix -->',1)
p.write_text(i)
