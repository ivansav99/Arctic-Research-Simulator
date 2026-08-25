from pathlib import Path


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text()
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    p.write_text(text.replace(old,new,1))

# Restore the four generated vessel illustrations. Add a version query so a
# browser that cached a missing/old image response is forced to request them.
replace_once(
    'expedition.js',
    "  const VESSEL_IMAGES = {\n    coastal:'assets/vessels/coastal-rv.webp',\n    global:'assets/vessels/noaa-rv-brown.webp',\n    icebreaker:'https://commons.wikimedia.org/wiki/Special:FilePath/Polarforskningssekretariatet%20IMG%202551%20Oden%20Hjorthfjellet.jpg',\n    nuclear:'assets/vessels/nuclear-icebreaker.webp'\n  };",
    "  const VESSEL_IMAGES = {\n    coastal:'assets/vessels/coastal-rv.webp?v=23w',\n    global:'assets/vessels/global-rv.webp?v=23w',\n    icebreaker:'assets/vessels/icebreaker.webp?v=23w',\n    nuclear:'assets/vessels/nuclear-icebreaker.webp?v=23w'\n  };",
    'restore generated vessel art'
)

# Add the helper that buildTarget already calls. Its absence currently throws
# ReferenceError: Can't find variable: pointIsSpaced and interrupts gameplay.
needle="  function targetSpacingKm() {\n    return {fishing:18,trawler:45,coastal:110,global:180,icebreaker:240,nuclear:300}[state.currentVessel]||18;\n  }\n"
insert=needle+"  function pointIsSpaced(point,items=[],minimumKm=0) {\n    if(!Number.isFinite(point?.lat)||!Number.isFinite(point?.lon)||minimumKm<=0)return true;\n    return !(items||[]).some(item=>Number.isFinite(item?.lat)&&Number.isFinite(item?.lon)&&geoDistance(point,item)<minimumKm);\n  }\n"
replace_once('expedition.js',needle,insert,'restore pointIsSpaced')

# Promotion message: show the actual publication count without discussing the
# absence of a paper-count requirement.
replace_once(
    'expedition.js',
    "message:'Reaching 2,000 citations has earned professor status. There is no minimum publication-count requirement. Global research vessels, icebreakers and heavy equipment are unlocked. Professors lead the highest-complexity programs and can originate new grants while at sea.'",
    "message:`Reaching 2,000 citations has earned professor status with ${state.papers.length} published paper${state.papers.length===1?'':'s'}. Global research vessels, icebreakers and heavy equipment are unlocked. Professors lead the highest-complexity programs and can originate new grants while at sea.`",
    'professor promotion wording'
)

# Cache-bust the repaired JS on GitHub Pages.
p=Path('index.html')
text=p.read_text()
old='expedition-23v-grants-wildlife-no-fast-ice'
if old not in text:
    raise SystemExit('index cache version not found')
p.write_text(text.replace(old,'expedition-23w-vessel-art-runtime-hotfix'))

print('ARS 23w hotfix applied')
