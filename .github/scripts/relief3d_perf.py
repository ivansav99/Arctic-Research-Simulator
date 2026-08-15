from pathlib import Path


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    return text.replace(old, new)

p = Path('game.js')
s = p.read_text()
old = "updateResourceWarning();drawMap();drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);/* wildlife labels intentionally hidden; species is revealed on interaction */drawResearchGuidance();try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}if(!window.AR_3D_ACTIVE)drawVessel();requestAnimationFrame(frame);"
new = "updateResourceWarning();if(!window.AR_3D_ACTIVE){drawMap();drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);/* wildlife labels intentionally hidden; species is revealed on interaction */drawResearchGuidance();}try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}if(!window.AR_3D_ACTIVE)drawVessel();requestAnimationFrame(frame);"
s = once(s, old, new, 'skip hidden 2D main renderer')
p.write_text(s)

p = Path('relief-3d.js')
s = p.read_text()
s = once(s,
"  let lastLabelDraw = 0;\n  let webglFailed = false;",
"  let lastLabelDraw = 0;\n  let last3DDraw = 0;\n  const target3DFrameMs = matchMedia('(pointer:coarse)').matches ? 33 : 22;\n  let webglFailed = false;",
'3D frame pacing state')
s = once(s,
"    if (mode !== '3d' || !gl || !terrainReady) return;\n    resize();",
"    if (mode !== '3d' || !gl || !terrainReady) return;\n    if (now - last3DDraw < target3DFrameMs) return;\n    last3DDraw = now;\n    resize();",
'3D frame cap')
p.write_text(s)
print('3D performance patch applied')
