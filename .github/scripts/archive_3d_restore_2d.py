from pathlib import Path
import re


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new)


def sub_once(text, pattern, replacement, label):
    new, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 regex match, found {count}")
    return new

# -----------------------------------------------------------------------------
# Archive the 3D experiment before disconnecting it from the active game.
# -----------------------------------------------------------------------------
archive = Path('archive/3d-relief-2026-08-15')
archive.mkdir(parents=True, exist_ok=True)
for name in ('relief-3d.js', 'relief-3d.css'):
    source = Path(name)
    if source.exists():
        (archive / name).write_bytes(source.read_bytes())

# Save the small engine bridge separately because it is removed below.
game_path = Path('game.js')
game = game_path.read_text()
hook_lines = [line for line in game.splitlines() if 'AR_3D' in line or 'AR_SHOW_TOAST' in line]
(archive / 'engine-hooks.txt').write_text('\n'.join(hook_lines) + '\n')
(archive / 'README.md').write_text('''# Archived 3D relief prototype\n\nFrozen on 2026-08-15 after deciding to continue development in the 2D chart view.\n\nThis folder preserves the last experimental WebGL2 renderer and stylesheet. The active game no longer loads them. The engine bridge that was removed from `game.js` is preserved in `engine-hooks.txt`.\n\nUseful Git history:\n- `910ab696fb935988baad3dfa1faa7da3671cd0a6` enabled the reversible 2D/3D switch.\n- `302dd897120a5f06fb7183d25dc438aae7cbc0b7` improved camera anchoring and terrain fidelity.\n- `933502559714b5badae1db996f183f0d3b4c159f` is the final active 3D range/position iteration.\n\nTo revive the experiment later, restore the renderer files plus the engine bridge from this folder/history rather than rebuilding it from scratch.\n''')

# -----------------------------------------------------------------------------
# Restore the richer atlas vessel art, with only a small bow-corner trim.
# -----------------------------------------------------------------------------
helper = """  function drawSpriteCentered(sprite,widthPx,heightPx){ctx.drawImage(sprite.image,sprite.sx,sprite.sy,sprite.sw,sprite.sh,-widthPx/2,-heightPx/2,widthPx,heightPx);}\n  function drawVesselSpriteCentered(sprite,widthPx,heightPx,cls=''){\n    const top=-heightPx/2,bottom=heightPx/2,left=-widthPx/2,right=widthPx/2,shouldTrim=['global','icebreaker','nuclear'].includes(cls);\n    ctx.save();\n    if(shouldTrim){\n      const shoulder=widthPx*.29,cut=heightPx*.13;\n      ctx.beginPath();\n      ctx.moveTo(-shoulder,top);ctx.lineTo(shoulder,top);ctx.lineTo(right,top+cut);ctx.lineTo(right,bottom);ctx.lineTo(left,bottom);ctx.lineTo(left,top+cut);ctx.closePath();ctx.clip();\n    }\n    if(cls==='icebreaker')ctx.filter='grayscale(.62) sepia(.42) saturate(.72) brightness(1.08)';\n    drawSpriteCentered(sprite,widthPx,heightPx);\n    ctx.restore();\n  }"""
game = once(
    game,
    "  function drawSpriteCentered(sprite,widthPx,heightPx){ctx.drawImage(sprite.image,sprite.sx,sprite.sy,sprite.sw,sprite.sh,-widthPx/2,-heightPx/2,widthPx,heightPx);}",
    helper,
    'vessel sprite trim helper',
)

# Remove the emergency procedural large-vessel silhouettes.
game = sub_once(
    game,
    r"  function drawResearchShipIcon\(cls,size\)\{.*?\n  \}\n  function drawNpcHull",
    "  function drawNpcHull",
    'remove procedural research vessel silhouettes',
)

old_npc = """    if(['global','icebreaker','nuclear'].includes(cls)){const dims=cls==='nuclear'?[30,51]:cls==='icebreaker'?[29,49]:[28,47];drawResearchShipIcon(cls,{w:dims[0],h:dims[1]});ctx.restore();return;}\n    if(spriteReady(sprite)){\n      const dims=cls==='coastal'?[25,44]:[23,42];ctx.save();ctx.rotate(Math.PI);drawSpriteCentered(sprite,dims[0],dims[1]);ctx.restore();ctx.globalCompositeOperation='source-atop';ctx.globalAlpha=.3;ctx.fillStyle=npcTint(npc);ctx.fillRect(-dims[0]/2,-dims[1]/2,dims[0],dims[1]);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.restore();return;\n    }"""
new_npc = """    if(spriteReady(sprite)){\n      const dims=cls==='nuclear'?[30,51]:cls==='icebreaker'?[29,49]:cls==='global'?[28,47]:cls==='coastal'?[25,44]:[23,42];\n      ctx.save();ctx.rotate(Math.PI);drawVesselSpriteCentered(sprite,dims[0],dims[1],cls);ctx.restore();\n      if(!['global','icebreaker','nuclear'].includes(cls)){ctx.globalCompositeOperation='source-atop';ctx.globalAlpha=.3;ctx.fillStyle=npcTint(npc);ctx.fillRect(-dims[0]/2,-dims[1]/2,dims[0],dims[1]);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;}\n      ctx.restore();return;\n    }"""
game = once(game, old_npc, new_npc, 'restore NPC atlas vessel art')

old_player = """    const largeClass=vesselIceId(item);\n    if(['global','icebreaker','nuclear'].includes(largeClass)){\n      drawResearchShipIcon(largeClass,size);\n    }else if(spriteReady(sprite)){\n      ctx.save();ctx.rotate(Math.PI);drawSpriteCentered(sprite,size.w,size.h);drawVesselClassDetails(item,size);ctx.restore();\n    }else{"""
new_player = """    const largeClass=vesselIceId(item);\n    if(spriteReady(sprite)){\n      ctx.save();ctx.rotate(Math.PI);drawVesselSpriteCentered(sprite,size.w,size.h,largeClass);drawVesselClassDetails(item,size);ctx.restore();\n    }else{"""
game = once(game, old_player, new_player, 'restore player atlas vessel art')

# Remove the active 3D bridge and make the 2D draw path unconditional again.
game = sub_once(
    game,
    r"  window\.AR_3D_VIEW=\(\)=>\{.*?\};\n  window\.AR_SHOW_TOAST=showToast;\n",
    "",
    'remove active 3D bridge',
)
game = once(
    game,
    "if(!window.AR_3D_ACTIVE){drawMap();drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);/* wildlife labels intentionally hidden; species is revealed on interaction */drawResearchGuidance();}try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}if(!window.AR_3D_ACTIVE)drawVessel();requestAnimationFrame(frame);",
    "drawMap();drawResearchTargets();drawNpcVessels();drawSeasonalLighting();drawWeather(weather);drawPortMarkers();drawWildlifeObservationRings();drawFog(weather);drawResearchTargets(true);/* wildlife labels intentionally hidden; species is revealed on interaction */drawResearchGuidance();try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}drawVessel();requestAnimationFrame(frame);",
    'restore unconditional 2D frame',
)
game_path.write_text(game)

# -----------------------------------------------------------------------------
# Glacier renderer: use the already-rendered high-resolution terrain as texture.
# Canvas blend mode `color` removes all green/brown hue while preserving the
# detailed terrain luminance. A light screen pass lifts it into ice-white/gray.
# -----------------------------------------------------------------------------
glacier = r"""(() => {
  'use strict';

  const data = window.AR_GLACIER_DATA;
  if (!data || !Array.isArray(data.regions)) return;

  function chaikin(ring, iterations) {
    let pts = Array.isArray(ring) ? ring : [];
    for (let pass = 0; pass < iterations && pts.length >= 4; pass++) {
      const next = [];
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i], b = pts[(i + 1) % pts.length];
        next.push([a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25]);
        next.push([a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75]);
      }
      pts = next;
    }
    return pts;
  }

  const regions = data.regions.map(region => ({
    ...region,
    r: (region.r || []).map(ring => {
      const n = ring.length;
      const iterations = n < 90 ? 2 : n < 260 ? 1 : 0;
      return iterations ? chaikin(ring, iterations) : ring;
    })
  }));

  function intersects(b, bounds) {
    return b && !(b[2] < bounds.minX || b[0] > bounds.maxX || b[3] < bounds.minY || b[1] > bounds.maxY);
  }

  function visibleFor(centerX, centerY, radiusX, radiusY, margin = 16) {
    const bounds = {
      minX: centerX - radiusX - margin,
      maxX: centerX + radiusX + margin,
      minY: centerY - radiusY - margin,
      maxY: centerY + radiusY + margin
    };
    return regions.filter(region => intersects(region.b, bounds));
  }

  function appendRegionsPath(ctx, visible, project) {
    ctx.beginPath();
    for (const region of visible) {
      for (const ring of region.r || []) {
        for (let i = 0; i < ring.length; i++) {
          const s = project(ring[i]);
          if (i) ctx.lineTo(s.x, s.y); else ctx.moveTo(s.x, s.y);
        }
        ctx.closePath();
      }
    }
  }

  function recolorExistingTerrain(ctx, width, height, compact = false) {
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'color';
    const supportsColorBlend = ctx.globalCompositeOperation === 'color';
    if (supportsColorBlend) {
      // Preserve every high-resolution ridge/valley luminance value while
      // eliminating the green/tan bedrock hue completely.
      ctx.fillStyle = compact ? 'rgb(222,228,231)' : 'rgb(220,227,230)';
      ctx.fillRect(0, 0, width, height);
      // Lift the neutralized terrain into the white/gray glacier range without
      // flattening its fine shading.
      ctx.globalCompositeOperation = 'screen';
      ctx.globalAlpha = compact ? .28 : .32;
      ctx.fillStyle = 'rgb(226,233,236)';
      ctx.fillRect(0, 0, width, height);
    } else {
      // Conservative fallback for an old browser lacking canvas blend modes.
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = .94;
      ctx.fillStyle = 'rgb(226,234,237)';
      ctx.fillRect(0, 0, width, height);
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
  }

  window.AR_DRAW_MAIN_GLACIERS = ({ctx, width, height, state, scale, worldToScreen}) => {
    if (!ctx || !state || !Number.isFinite(scale) || scale <= 0 || !worldToScreen) return;
    const radiusX = width / scale / 2, radiusY = height / scale / 2;
    const visible = visibleFor(state.x, state.y, radiusX, radiusY);
    if (!visible.length) return;

    ctx.save();
    appendRegionsPath(ctx, visible, p => worldToScreen(p[0], p[1]));
    try { ctx.clip('evenodd'); } catch (error) { ctx.clip(); }
    recolorExistingTerrain(ctx, width, height, false);
    ctx.restore();
  };

  window.AR_DRAW_MINI_GLACIERS = ({ctx, project, c, radius, geometry, size, worldRadius}) => {
    if (!ctx || !project || !geometry || !Number.isFinite(radius) || radius <= 0) return;
    const visible = visibleFor(geometry.centerX, geometry.centerY, worldRadius, worldRadius, 0);
    if (!visible.length) return;

    ctx.save();
    ctx.beginPath();ctx.arc(c, c, radius, 0, Math.PI * 2);ctx.clip();
    appendRegionsPath(ctx, visible, p => project(p[0], p[1]));
    try { ctx.clip('evenodd'); } catch (error) { ctx.clip(); }
    const side = Number(size) || Math.max(ctx.canvas.width, ctx.canvas.height);
    recolorExistingTerrain(ctx, side, side, true);
    ctx.restore();
  };
})();
"""
Path('glacier-overlay-v2.js').write_text(glacier)

# -----------------------------------------------------------------------------
# Active HTML: 2D only. 3D files remain preserved under archive/.
# -----------------------------------------------------------------------------
index_path = Path('index.html')
index = index_path.read_text()
index = sub_once(index, r"\n  <link rel=\"stylesheet\" href=\"relief-3d\.css\?v=[^\"]+\">", "", 'remove active 3D stylesheet')
index = sub_once(index, r"\n  <script src=\"relief-3d\.js\?v=[^\"]+\"></script>", "", 'remove active 3D script')
index = re.sub(r'game\.js\?v=[^\"]+', 'game.js?v=expedition-23d-2drestore', index, count=1)
index = re.sub(r'glacier-overlay-v2\.js\?v=[^\"]+', 'glacier-overlay-v2.js?v=expedition-23d-terrainice', index, count=1)
index_path.write_text(index)

# Root renderer files are no longer active; the archived copies above are the
# canonical frozen experiment.
Path('relief-3d.js').unlink(missing_ok=True)
Path('relief-3d.css').unlink(missing_ok=True)

print('Archived 3D experiment, restored 2D vessel art, and recolored glacier terrain texture.')
