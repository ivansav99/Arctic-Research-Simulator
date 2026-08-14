from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new)


game_path = Path("game.js")
game = game_path.read_text()

# Remove the tile-by-tile winter snow paint. It creates hard rectangular/polygonal
# boundaries over the continuous terrain imagery. Broad seasonal lighting and the
# glacier layer remain.
game = replace_once(
    game,
    "    if(realTerrain){drawRasterSeasonalOverlay();}else{",
    "    if(realTerrain){/* Continuous terrain only; tile snow overlay intentionally disabled. */}else{",
    "disable tile winter snow overlay",
)

# Give the glacier renderer an exact, in-engine draw point below rivers/labels.
game = replace_once(
    game,
    "    drawRivers(minX,maxX,minY,maxY);\n    chartLabels.forEach(drawChartLabel);",
    "    try{window.AR_DRAW_MAIN_GLACIERS?.({ctx,width,height,state,scale,zoomLevel,worldToScreen});}catch(error){console.error('GLACIER DRAW FAILED',error);}\n    drawRivers(minX,maxX,minY,maxY);\n    chartLabels.forEach(drawChartLabel);",
    "main glacier draw hook",
)

# Make minimap geographic scale track main-map zoom. Expanded mode is physically
# larger, but uses the same zoom factor rather than a fixed unrelated scale.
game = replace_once(
    game,
    "  function miniMapGeometry(){return{worldRadius:minimapExpanded?1100:520,centerX:state.x,centerY:state.y};}",
    "  function miniMapGeometry(){const zoom=Math.max(.7,zoomLevel||1),base=minimapExpanded?1100:520;return{worldRadius:base/zoom,centerX:state.x,centerY:state.y};}",
    "zoom-aware minimap geometry",
)

# Draw glaciers inside the minimap's own exact clip/geometry, before symbols.
game = replace_once(
    game,
    "    mini.font='900 9px Georgia,serif';mini.textAlign='center';mini.textBaseline='middle';",
    "    try{window.AR_DRAW_MINI_GLACIERS?.({ctx:mini,project,c,radius,geometry,size,worldRadius});}catch(error){console.error('MINIMAP GLACIER DRAW FAILED',error);}\n    mini.font='900 9px Georgia,serif';mini.textAlign='center';mini.textBaseline='middle';",
    "minimap glacier draw hook",
)

# Pause continuous vessel/ice sound whenever the simulation is paused.
game = replace_once(
    game,
    "    const update=()=>{if(!ac)return;const now=performance.now();if(waveGain)waveGain.gain.setTargetAtTime(state.moving&&!state.ramming?.05:0,ac.currentTime,.35);if(state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};",
    "    const update=paused=>{if(!ac)return;const now=performance.now();if(waveGain)waveGain.gain.setTargetAtTime((!paused&&state.moving&&!state.ramming)?0.05:0,ac.currentTime,.22);if(!paused&&state.ramming&&now-lastCrack>850){lastCrack=now;play('ice');}};",
    "pause ambient ship sound",
)

game = replace_once(
    game,
    "  function frame(now){const dt=Math.min(.04,(now-last)/1000);last=now;sound.update();const paused=state.gameOver||menuOpen||minimapExpanded||!!research?.isBusy?.();let weather;",
    "  function frame(now){const dt=Math.min(.04,(now-last)/1000);last=now;const paused=state.gameOver||menuOpen||minimapExpanded||!!research?.isBusy?.();sound.update(paused);let weather;",
    "compute pause before sound update",
)

# Clean procedural silhouettes for the three large research-vessel classes.
# Their bow is always local -Y; that matches the game's heading transforms.
ship_helper = r"""  function drawResearchShipIcon(cls,size){
    const w=size.w,h=size.h,half=h/2,isNuclear=cls==='nuclear',isIcebreaker=cls==='icebreaker';
    const hull=isNuclear?'#b74b40':isIcebreaker?'#b79a6a':'#35667a';
    const lower=isNuclear?'#762f2a':isIcebreaker?'#76644b':'#173f51';
    const deck=isNuclear?'#f1eadf':isIcebreaker?'#eee8d9':'#eff7f5';
    const accent=isNuclear?'#f3cf62':isIcebreaker?'#76c8cb':'#75c4db';
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.shadowColor='rgba(0,20,30,.28)';ctx.shadowBlur=5;ctx.shadowOffsetY=2;
    ctx.fillStyle=hull;ctx.strokeStyle='rgba(239,251,252,.96)';ctx.lineWidth=1.3;ctx.beginPath();
    ctx.moveTo(0,-half);ctx.bezierCurveTo(w*.34,-half*.74,w*.47,-half*.20,w*.43,half*.47);ctx.quadraticCurveTo(w*.32,half*.89,0,half);ctx.quadraticCurveTo(-w*.32,half*.89,-w*.43,half*.47);ctx.bezierCurveTo(-w*.47,-half*.20,-w*.34,-half*.74,0,-half);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.shadowBlur=0;ctx.fillStyle=lower;ctx.beginPath();ctx.moveTo(-w*.38,half*.42);ctx.quadraticCurveTo(0,half*.58,w*.38,half*.42);ctx.lineTo(w*.30,half*.78);ctx.quadraticCurveTo(0,half*.92,-w*.30,half*.78);ctx.closePath();ctx.fill();
    ctx.fillStyle=deck;ctx.beginPath();ctx.moveTo(-w*.25,-half*.38);ctx.lineTo(w*.25,-half*.38);ctx.lineTo(w*.31,half*.27);ctx.lineTo(-w*.31,half*.27);ctx.closePath();ctx.fill();
    ctx.fillStyle='#31596a';ctx.fillRect(-w*.19,-half*.25,w*.38,Math.max(3,h*.075));
    ctx.fillStyle=accent;ctx.fillRect(-w*.025,-half*.60,w*.05,h*.18);
    ctx.strokeStyle=accent;ctx.lineWidth=1.3;ctx.beginPath();ctx.moveTo(-w*.22,-half*.02);ctx.lineTo(w*.22,-half*.02);ctx.stroke();
    if(isIcebreaker||isNuclear){ctx.strokeStyle=isNuclear?'#f4d66f':'#72c4c7';ctx.lineWidth=1.35;ctx.beginPath();ctx.arc(0,half*.48,isNuclear?w*.22:w*.19,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(-w*.14,half*.48);ctx.lineTo(w*.14,half*.48);ctx.moveTo(0,half*.34);ctx.lineTo(0,half*.62);ctx.stroke();}
    if(cls==='global'){ctx.fillStyle='#f8fbf8';ctx.beginPath();ctx.arc(-w*.14,-half*.45,Math.max(2,w*.075),0,Math.PI*2);ctx.fill();ctx.strokeStyle='#8bd2e2';ctx.beginPath();ctx.moveTo(w*.12,-half*.47);ctx.lineTo(w*.32,-half*.24);ctx.stroke();}
    ctx.restore();
  }
"""

game = replace_once(
    game,
    "  function drawNpcHull(length,width,fill,accent='#eaf8fa'){",
    ship_helper + "  function drawNpcHull(length,width,fill,accent='#eaf8fa'){",
    "large vessel icon helper",
)

# Large NPC research vessels use the clean silhouettes. Remaining atlas-backed
# ship art is rotated 180 degrees because that atlas was authored bow-down.
game = replace_once(
    game,
    "    if(spriteReady(sprite)){\n      const dims=cls==='nuclear'?[30,51]:cls==='icebreaker'?[29,49]:cls==='global'?[28,47]:cls==='coastal'?[25,44]:[23,42];drawSpriteCentered(sprite,dims[0],dims[1]);ctx.globalCompositeOperation='source-atop';ctx.globalAlpha=.3;ctx.fillStyle=npcTint(npc);ctx.fillRect(-dims[0]/2,-dims[1]/2,dims[0],dims[1]);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.restore();return;\n    }",
    "    if(['global','icebreaker','nuclear'].includes(cls)){const dims=cls==='nuclear'?[30,51]:cls==='icebreaker'?[29,49]:[28,47];drawResearchShipIcon(cls,{w:dims[0],h:dims[1]});ctx.restore();return;}\n    if(spriteReady(sprite)){\n      const dims=cls==='coastal'?[25,44]:[23,42];ctx.save();ctx.rotate(Math.PI);drawSpriteCentered(sprite,dims[0],dims[1]);ctx.restore();ctx.globalCompositeOperation='source-atop';ctx.globalAlpha=.3;ctx.fillStyle=npcTint(npc);ctx.fillRect(-dims[0]/2,-dims[1]/2,dims[0],dims[1]);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.restore();return;\n    }",
    "npc vessel silhouettes and heading",
)

# Player's large-vessel marker uses the same clean class-specific silhouettes.
game = replace_once(
    game,
    "    if(spriteReady(sprite)){\n      ctx.save();ctx.rotate(Math.PI);drawSpriteCentered(sprite,size.w,size.h);drawVesselClassDetails(item,size);ctx.restore();\n    }else{",
    "    const largeClass=vesselIceId(item);\n    if(['global','icebreaker','nuclear'].includes(largeClass)){\n      drawResearchShipIcon(largeClass,size);\n    }else if(spriteReady(sprite)){\n      ctx.save();ctx.rotate(Math.PI);drawSpriteCentered(sprite,size.w,size.h);drawVesselClassDetails(item,size);ctx.restore();\n    }else{",
    "player large vessel silhouettes",
)

game_path.write_text(game)

exp_path = Path("expedition.js")
exp = exp_path.read_text()
exp = replace_once(
    exp,
    "    isBusy:()=>!!activeOperation||!!root?.querySelector('.arx-modal.open')",
    "    isBusy:()=>!!activeOperation||!!root?.querySelector('.arx-modal.open')||!!root?.querySelector('.arx-sidebar.open')",
    "research sidebar pause",
)
exp_path.write_text(exp)

css_path = Path("style.css")
css = css_path.read_text()
css += r"""

/* 2026-08-14 navigation chart cleanup */
.nav-chart-open #arx-mobile-toggle{display:none!important}
.minimap.expanded #minimap{width:min(76vw,64vh,620px)!important;height:min(76vw,64vh,620px)!important;max-height:none!important;aspect-ratio:1/1!important;border-radius:50%!important}
@media(max-width:620px){.minimap.expanded #minimap{width:min(90vw,55vh,430px)!important;height:min(90vw,55vh,430px)!important;max-height:none!important;aspect-ratio:1/1!important;border-radius:50%!important}}
"""
css_path.write_text(css)

print("Cleanup patch applied successfully")
