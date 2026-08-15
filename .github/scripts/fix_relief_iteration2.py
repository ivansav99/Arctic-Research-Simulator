from pathlib import Path
import re


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    return text.replace(old, new)


def sub_once(text, pattern, replacement, label):
    new, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 regex match, found {n}')
    return new

# --- 2D glacier: restore topographic texture while remaining fully opaque ---
gp = Path('glacier-overlay-v2.js')
g = gp.read_text()
new_build_field = r'''  function buildField(centerX, centerY, scale, width, height) {
    if (!fieldCtx) return;
    const heights = new Float32Array(FIELD * FIELD);
    const spanX = width / scale;
    const spanY = height / scale;
    for (let py = 0; py < FIELD; py++) {
      const wy = centerY + ((py + 0.5) / FIELD - 0.5) * spanY;
      for (let px = 0; px < FIELD; px++) {
        const wx = centerX + ((px + 0.5) / FIELD - 0.5) * spanX;
        const h = surfaceHeightAt(wx, wy);
        heights[py * FIELD + px] = h == null ? 0.30 : Math.max(0, Math.min(1, h));
      }
    }

    const image = fieldCtx.createImageData(FIELD, FIELD);
    const out = image.data;
    const sample = (x, y) => heights[Math.max(0, Math.min(FIELD - 1, y)) * FIELD + Math.max(0, Math.min(FIELD - 1, x))];
    const sun = [-0.42, -0.58, 0.70];
    for (let py = 0; py < FIELD; py++) {
      for (let px = 0; px < FIELD; px++) {
        const h = heights[py * FIELD + px];
        const dx = (sample(px + 1, py) - sample(px - 1, py)) * 20;
        const dy = (sample(px, py + 1) - sample(px, py - 1)) * 20;
        const nx = -dx, ny = -dy, nz = 1;
        const inv = 1 / Math.max(0.001, Math.hypot(nx, ny, nz));
        const illumination = Math.max(0.54, Math.min(1.20, 0.76 + (nx * sun[0] + ny * sun[1] + nz * sun[2]) * inv * 0.38));
        const lift = Math.sqrt(h);
        const base = 207 + 47 * lift;
        const tone = Math.max(174, Math.min(255, Math.round(base * illumination)));
        const j = (py * FIELD + px) * 4;
        out[j] = Math.max(0, tone - 5);
        out[j + 1] = tone;
        out[j + 2] = Math.min(255, tone + 4);
        out[j + 3] = 255;
      }
    }
    fieldCtx.putImageData(image, 0, 0);
  }
'''
g = sub_once(g, r"  function buildField\(centerX, centerY, scale, width, height\) \{.*?\n  \}\n\n  window\.AR_DRAW_MAIN_GLACIERS", new_build_field + "\n  window.AR_DRAW_MAIN_GLACIERS", 'glacier hillshade field')
gp.write_text(g)

# --- 3D relief: local sharp texture + boat-centered screen pivot ---
rp = Path('relief-3d.js')
r = rp.read_text()
r = replace_once(r,
"  const sourceUrl = 'https://wms.gebco.net/2024/north-polar/mapserv?BBOX=-2910000%2C-2910000%2C2910000%2C2910000&crs=EPSG%3A3996&format=image%2Fjpeg&height=2048&layers=GEBCO_NORTH_POLAR_VIEW_bed_2024&request=getmap&service=wms&version=1.3.0&width=2048';",
"  const terrainRequestPixels = matchMedia('(pointer:coarse)').matches ? 1536 : 2048;\n  const PIVOT_NDC_SHIFT = 0.50;",
'global terrain source constant')

r = replace_once(r,
"  let terrainReady = false;\n  let mode = '2d';",
"  let terrainReady = false;\n  let terrainTexCenterX = 0;\n  let terrainTexCenterY = 0;\n  let terrainTexSpan = 0;\n  let terrainRequestSerial = 0;\n  let terrainLoading = false;\n  let mode = '2d';",
'local terrain state')

r = replace_once(r,
"      uniform vec2 uCenter;\n      uniform vec2 uSpan;\n      uniform float uExtent;",
"      uniform vec2 uCenter;\n      uniform vec2 uSpan;\n      uniform vec2 uTexCenter;\n      uniform float uTexSpan;\n      uniform float uExtent;\n      uniform float uPivotShift;",
'local texture uniforms')

r = replace_once(r,
"      out vec2 vTerrainUv;\n      out float vRelief;",
"      out vec2 vTerrainUv;\n      out vec2 vGlacierUv;\n      out float vRelief;",
'glacier uv varying vertex')

r = replace_once(r,
"        vec2 tuv = (world + vec2(uExtent)) / (2.0 * uExtent);\n        vTerrainUv = tuv;\n        vec3 terrain = texture(uTerrain, clamp(tuv, 0.001, 0.999)).rgb;\n        float glacierMask = texture(uGlacierMask, clamp(tuv, 0.001, 0.999)).r;\n        float glacierElev = texture(uGlacierElev, clamp(tuv, 0.001, 0.999)).r;",
"        vec2 tuv = (world - uTexCenter) / uTexSpan + vec2(0.5);\n        vec2 guv = (world + vec2(uExtent)) / (2.0 * uExtent);\n        vTerrainUv = tuv;\n        vGlacierUv = guv;\n        vec3 terrain = texture(uTerrain, clamp(tuv, 0.001, 0.999)).rgb;\n        float glacierMask = texture(uGlacierMask, clamp(guv, 0.001, 0.999)).r;\n        float glacierElev = texture(uGlacierElev, clamp(guv, 0.001, 0.999)).r;",
'local terrain/global glacier uv')

r = replace_once(r,
"        gl_Position = uVP * vec4(local, 1.0);\n        vRelief = z;",
"        gl_Position = uVP * vec4(local, 1.0);\n        gl_Position.y -= uPivotShift * gl_Position.w;\n        vRelief = z;",
'boat screen pivot shader')

r = replace_once(r,
"      in vec2 vTerrainUv;\n      in float vRelief;",
"      in vec2 vTerrainUv;\n      in vec2 vGlacierUv;\n      in float vRelief;",
'glacier uv varying fragment')

r = replace_once(r,
"        vec2 uv = clamp(vTerrainUv, 0.001, 0.999);\n        vec3 color = texture(uTerrain, uv).rgb;\n        float glacier = texture(uGlacierMask, uv).r;\n        if (glacier > 0.35) {\n          float elev = texture(uGlacierElev, uv).r;",
"        vec2 uv = clamp(vTerrainUv, 0.001, 0.999);\n        vec2 guv = clamp(vGlacierUv, 0.001, 0.999);\n        vec3 color = texture(uTerrain, uv).rgb;\n        float luminance = dot(color, vec3(0.24, 0.60, 0.16));\n        color = mix(vec3(luminance), color, 1.10);\n        color = clamp((color - 0.5) * 1.06 + 0.5, 0.0, 1.0);\n        float glacier = texture(uGlacierMask, guv).r;\n        if (glacier > 0.35) {\n          float elev = texture(uGlacierElev, guv).r;",
'preserve terrain color and glacier uv')

r = replace_once(r,
"        float light = clamp(0.68 + dot(normal, sun) * 0.34, 0.50, 1.18);\n        color *= light;\n        float distanceFog = smoothstep(0.55, 2.2, vForward);\n        color = mix(color, vec3(0.66, 0.80, 0.84), distanceFog * 0.24);",
"        float light = clamp(0.80 + dot(normal, sun) * 0.24, 0.66, 1.14);\n        color *= light;",
'remove washed out fog')

r = replace_once(r,
"    loadTerrainTexture();\n    buildGlacierTextures();",
"    buildGlacierTextures();",
'defer terrain request')

new_loader = r'''  function terrainTextureUrl(cx, cy, span) {
    const half = span / 2;
    const minE = Math.round((cx - half) * 1000);
    const maxE = Math.round((cx + half) * 1000);
    const minN = Math.round(-(cy + half) * 1000);
    const maxN = Math.round(-(cy - half) * 1000);
    return `https://wms.gebco.net/2024/north-polar/mapserv?BBOX=${minE}%2C${minN}%2C${maxE}%2C${maxN}&crs=EPSG%3A3996&format=image%2Fpng&height=${terrainRequestPixels}&layers=GEBCO_NORTH_POLAR_VIEW_bed_2024&request=getmap&service=wms&version=1.3.0&width=${terrainRequestPixels}`;
  }

  function ensureTerrainTexture(view) {
    if (!gl || !terrainTexture || !view || terrainLoading) return;
    const spanX = view.width / view.scale;
    const spanY = view.height / view.scale;
    const desiredSpan = Math.max(180, Math.min(1900, Math.hypot(spanX, spanY) * 1.50));
    const moved = terrainTexSpan > 0 ? Math.hypot(view.x - terrainTexCenterX, view.y - terrainTexCenterY) : Infinity;
    const scaleChanged = terrainTexSpan <= 0 || desiredSpan < terrainTexSpan * 0.78 || desiredSpan > terrainTexSpan * 1.28;
    if (terrainReady && moved < terrainTexSpan * 0.11 && !scaleChanged) return;

    const serial = ++terrainRequestSerial;
    const image = new Image();
    const requestX = view.x;
    const requestY = view.y;
    const requestSpan = desiredSpan;
    terrainLoading = true;
    image.crossOrigin = 'anonymous';
    image.decoding = 'async';
    image.onload = () => {
      if (serial !== terrainRequestSerial || !gl) return;
      try {
        gl.bindTexture(gl.TEXTURE_2D, terrainTexture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        terrainTexCenterX = requestX;
        terrainTexCenterY = requestY;
        terrainTexSpan = requestSpan;
        terrainReady = true;
      } catch (error) {
        console.error('3D local terrain texture upload failed', error);
      } finally {
        terrainLoading = false;
      }
    };
    image.onerror = () => {
      if (serial !== terrainRequestSerial) return;
      terrainLoading = false;
      console.warn('3D local terrain texture unavailable.');
      if (!terrainReady && mode === '3d') {
        setMode('2d', false);
        try { window.AR_SHOW_TOAST?.('3D TERRAIN SOURCE UNAVAILABLE · RETURNED TO 2D'); } catch (error) {}
      }
    };
    image.src = terrainTextureUrl(requestX, requestY, requestSpan);
  }

'''
r = sub_once(r, r"  function loadTerrainTexture\(\) \{.*?\n  \}\n\n  function chaikin", new_loader + "  function chaikin", 'replace global terrain loader')

r = replace_once(r,
"    return {\n      x: (cx / cw * .5 + .5) * innerWidth,\n      y: (1 - (cy / cw * .5 + .5)) * innerHeight,\n      w: cw\n    };",
"    const ndcY = cy / cw - PIVOT_NDC_SHIFT;\n    return {\n      x: (cx / cw * .5 + .5) * innerWidth,\n      y: (1 - (ndcY * .5 + .5)) * innerHeight,\n      w: cw\n    };",
'projected screen pivot')

r = replace_once(r,
"    shipCtx.translate(cx, 0);\n    shipCtx.rotate(turn * .42);\n    shipCtx.translate(-cx, 0);",
"    const turnPivotY = stern - 10;\n    shipCtx.translate(cx, turnPivotY);\n    shipCtx.rotate(turn * .42);\n    shipCtx.translate(-cx, -turnPivotY);",
'stern turn pivot')

r = replace_once(r,
"    if (mode !== '3d' || !gl || !terrainReady) return;\n    if (now - last3DDraw < target3DFrameMs) return;\n    last3DDraw = now;\n    resize();\n    const view = getView();\n    if (!view || !Number.isFinite(view.scale) || view.scale <= 0) return;",
"    if (mode !== '3d' || !gl) return;\n    const view = getView();\n    if (!view || !Number.isFinite(view.scale) || view.scale <= 0) return;\n    ensureTerrainTexture(view);\n    if (!terrainReady) return;\n    if (now - last3DDraw < target3DFrameMs) return;\n    last3DDraw = now;\n    resize();",
'render local terrain request')

r = replace_once(r,
"    gl.uniform2f(gl.getUniformLocation(program, 'uCenter'), view.x, view.y);\n    gl.uniform2f(gl.getUniformLocation(program, 'uSpan'), spanX, spanY);\n    gl.uniform1f(gl.getUniformLocation(program, 'uExtent'), extentKm);",
"    gl.uniform2f(gl.getUniformLocation(program, 'uCenter'), view.x, view.y);\n    gl.uniform2f(gl.getUniformLocation(program, 'uSpan'), spanX, spanY);\n    gl.uniform2f(gl.getUniformLocation(program, 'uTexCenter'), terrainTexCenterX, terrainTexCenterY);\n    gl.uniform1f(gl.getUniformLocation(program, 'uTexSpan'), terrainTexSpan);\n    gl.uniform1f(gl.getUniformLocation(program, 'uExtent'), extentKm);\n    gl.uniform1f(gl.getUniformLocation(program, 'uPivotShift'), PIVOT_NDC_SHIFT);",
'local texture and pivot uniforms')

rp.write_text(r)

# Cache-bust only changed runtime scripts.
ip = Path('index.html')
i = ip.read_text()
i = i.replace('glacier-overlay-v2.js?v=expedition-22z-glacierfix', 'glacier-overlay-v2.js?v=expedition-23b-glacierrelief')
i = i.replace('relief-3d.js?v=expedition-23a-relief3d', 'relief-3d.js?v=expedition-23b-relief3d')
ip.write_text(i)

print('Iteration 2 relief corrections applied')
