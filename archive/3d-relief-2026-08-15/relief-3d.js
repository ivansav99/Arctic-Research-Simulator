(() => {
  'use strict';

  const map = document.getElementById('map');
  const game = document.getElementById('game');
  if (!map || !game) return;

  const STORAGE_KEY = 'arctic-research-render-mode-v1';
  const extentKm = 2910;
  const dprCap = 1.5;
  const terrainRequestPixels = matchMedia('(pointer:coarse)').matches ? 2048 : 3072;
  const PIVOT_NDC_SHIFT = 0.28;
  const TERRAIN_MESH_SCALE = 2.6;
  const TERRAIN_TEXTURE_SCALE = 3.4;

  const reliefCanvas = document.createElement('canvas');
  reliefCanvas.id = 'relief-3d-canvas';
  reliefCanvas.setAttribute('aria-hidden', 'true');
  game.insertBefore(reliefCanvas, map.nextSibling);

  const labelCanvas = document.createElement('canvas');
  labelCanvas.id = 'relief-3d-labels';
  labelCanvas.setAttribute('aria-hidden', 'true');
  game.insertBefore(labelCanvas, reliefCanvas.nextSibling);
  const labelCtx = labelCanvas.getContext('2d');

  const shipCanvas = document.createElement('canvas');
  shipCanvas.id = 'relief-3d-ship';
  shipCanvas.width = 260;
  shipCanvas.height = 310;
  shipCanvas.setAttribute('aria-hidden', 'true');
  game.appendChild(shipCanvas);
  const shipCtx = shipCanvas.getContext('2d');

  const toggle = document.createElement('div');
  toggle.className = 'relief-mode-toggle hud';
  toggle.setAttribute('role', 'group');
  toggle.setAttribute('aria-label', 'Map view');
  toggle.innerHTML = '<button type="button" data-relief-mode="2d">2D</button><button type="button" data-relief-mode="3d">3D</button>';
  game.appendChild(toggle);

  const badge = document.createElement('div');
  badge.className = 'relief-3d-badge';
  badge.textContent = '3D RELIEF · EXPERIMENTAL';
  game.appendChild(badge);

  let gl = null;
  let program = null;
  let vao = null;
  let indexCount = 0;
  let terrainTexture = null;
  let glacierMaskTexture = null;
  let glacierElevTexture = null;
  let terrainReady = false;
  let terrainTexCenterX = 0;
  let terrainTexCenterY = 0;
  let terrainTexSpan = 0;
  let terrainRequestSerial = 0;
  let terrainLoading = false;
  let mode = '2d';
  let currentYaw = 0;
  let lastNow = performance.now();
  let lastLabelDraw = 0;
  let last3DDraw = 0;
  const target3DFrameMs = matchMedia('(pointer:coarse)').matches ? 33 : 22;
  let webglFailed = false;
  let vpMatrix = new Float32Array(16);
  let lastView = null;

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const wrapPi = a => {
    while (a > Math.PI) a -= Math.PI * 2;
    while (a < -Math.PI) a += Math.PI * 2;
    return a;
  };

  function readStoredMode() {
    try {
      const query = new URLSearchParams(location.search).get('view');
      if (query === '3d' || query === '2d') return query;
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored === '3d' ? '3d' : '2d';
    } catch (error) {
      return '2d';
    }
  }

  function storeMode(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (error) {}
  }

  function getView() {
    try {
      const view = window.AR_3D_VIEW?.();
      if (view && Number.isFinite(view.x) && Number.isFinite(view.y)) return view;
    } catch (error) {}
    const text = document.getElementById('position')?.textContent || '';
    const match = text.match(/([0-9.]+)\s*°?N\s+([0-9.]+)\s*°?([EW])/i);
    if (!match) return null;
    const lat = Number(match[1]);
    const lon = Number(match[2]) * (match[3].toUpperCase() === 'W' ? -1 : 1);
    const center = polar(lat, lon);
    const zoom = Math.max(.7, (parseFloat(document.getElementById('zoom-level')?.textContent || '100') || 100) / 100);
    return {
      x: center.x,
      y: center.y,
      angle: currentYaw,
      zoomLevel: zoom,
      scale: Math.max(3.4, Math.min(5.2, Math.min(innerWidth, innerHeight) / 145)) * zoom,
      width: innerWidth,
      height: innerHeight,
      vesselId: 'global',
      vesselName: 'Research Vessel',
      moving: false,
      ramming: false,
      labels: []
    };
  }

  const PS_A = 6378137;
  const PS_F = 1 / 298.257223563;
  const PS_E = Math.sqrt(PS_F * (2 - PS_F));
  const PS_LAT_TS = 75 * Math.PI / 180;
  const psT = phi => Math.tan(Math.PI / 4 - phi / 2) /
    Math.pow((1 - PS_E * Math.sin(phi)) / (1 + PS_E * Math.sin(phi)), PS_E / 2);
  const PS_MC = Math.cos(PS_LAT_TS) /
    Math.sqrt(1 - PS_E * PS_E * Math.sin(PS_LAT_TS) ** 2);
  const PS_TC = psT(PS_LAT_TS);
  function polar(lat, lon) {
    if (lat >= 89.999999) return { x: 0, y: 0 };
    const phi = lat * Math.PI / 180;
    const a = lon * Math.PI / 180;
    const r = PS_A * PS_MC * psT(phi) / PS_TC / 1000;
    return { x: r * Math.sin(a), y: r * Math.cos(a) };
  }

  function createShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const message = gl.getShaderInfoLog(shader) || 'shader compilation failed';
      gl.deleteShader(shader);
      throw new Error(message);
    }
    return shader;
  }

  function initWebGL() {
    if (gl || webglFailed) return !!gl;
    gl = reliefCanvas.getContext('webgl2', {
      antialias: true,
      alpha: false,
      depth: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: false
    });
    if (!gl) {
      webglFailed = true;
      return false;
    }

    const vertexSource = `#version 300 es
      precision highp float;
      layout(location=0) in vec2 a_uv;
      uniform sampler2D uTerrain;
      uniform sampler2D uGlacierMask;
      uniform sampler2D uGlacierElev;
      uniform vec2 uCenter;
      uniform vec2 uSpan;
      uniform vec2 uTexCenter;
      uniform float uTexSpan;
      uniform float uExtent;
      uniform float uPivotShift;
      uniform float uYaw;
      uniform float uVerticalLand;
      uniform float uVerticalSea;
      uniform mat4 uVP;
      out vec2 vTerrainUv;
      out vec2 vGlacierUv;
      out float vRelief;
      out float vForward;

      float landHeight(vec3 c) {
        float warm = max(0.0, (c.r - c.b) / 0.49);
        float bright = max(0.0, ((c.r + c.g + c.b) / 3.0 - 0.65) / 0.35);
        return clamp(warm * 0.72 + bright * 0.48, 0.0, 1.0);
      }
      float depthProxy(vec3 c) {
        float lum = dot(c, vec3(0.24, 0.56, 0.20));
        float blueBias = max(0.0, c.b - c.r * 0.55);
        return clamp((0.61 - lum) * 1.55 + blueBias * 0.55, 0.0, 1.0);
      }
      bool looksLand(vec3 c) {
        bool green = c.g > c.b + 0.047 && c.g > c.r + 0.055;
        bool tan = c.r > c.b + 0.071 && c.g > c.b + 0.027;
        bool pale = c.r > 0.83 && c.g > 0.80 && c.b > 0.74;
        return green || tan || pale;
      }

      void main() {
        vec2 world = uCenter + vec2((a_uv.x - 0.5) * uSpan.x, (a_uv.y - 0.5) * uSpan.y);
        vec2 tuv = (world - uTexCenter) / uTexSpan + vec2(0.5);
        vec2 guv = (world + vec2(uExtent)) / (2.0 * uExtent);
        vTerrainUv = tuv;
        vGlacierUv = guv;
        vec3 terrain = texture(uTerrain, clamp(tuv, 0.001, 0.999)).rgb;
        float glacierMask = texture(uGlacierMask, clamp(guv, 0.001, 0.999)).r;
        float glacierElev = texture(uGlacierElev, clamp(guv, 0.001, 0.999)).r;
        bool land = looksLand(terrain) || glacierMask > 0.4;
        float reliefKm;
        if (glacierMask > 0.4) {
          reliefKm = 0.10 + glacierElev * 4.0;
        } else if (land) {
          reliefKm = 0.06 + pow(landHeight(terrain), 1.30) * 3.6;
        } else {
          reliefKm = -pow(depthProxy(terrain), 1.10) * 4.8;
        }
        float normalizer = max(uSpan.x, uSpan.y);
        float z = reliefKm * (land ? uVerticalLand : uVerticalSea) / max(45.0, normalizer) * 2.0;
        vec2 delta = world - uCenter;
        float c = cos(-uYaw), s = sin(-uYaw);
        vec2 rotated = vec2(c * delta.x - s * delta.y, s * delta.x + c * delta.y);
        vec2 p = rotated / max(45.0, normalizer) * 2.0;
        vec3 local = vec3(p.x, -p.y, z);
        gl_Position = uVP * vec4(local, 1.0);
        gl_Position.y -= uPivotShift * gl_Position.w;
        vRelief = z;
        vForward = local.y;
      }
    `;

    const fragmentSource = `#version 300 es
      precision highp float;
      uniform sampler2D uTerrain;
      uniform sampler2D uGlacierMask;
      uniform sampler2D uGlacierElev;
      in vec2 vTerrainUv;
      in vec2 vGlacierUv;
      in float vRelief;
      in float vForward;
      out vec4 outColor;

      void main() {
        vec2 uv = clamp(vTerrainUv, 0.001, 0.999);
        vec2 guv = clamp(vGlacierUv, 0.001, 0.999);
        vec3 color = texture(uTerrain, uv).rgb;
        float luminance = dot(color, vec3(0.24, 0.60, 0.16));
        color = mix(vec3(luminance), color, 1.10);
        color = clamp((color - 0.5) * 1.06 + 0.5, 0.0, 1.0);
        float glacier = texture(uGlacierMask, guv).r;
        if (glacier > 0.35) {
          float elev = texture(uGlacierElev, guv).r;
          float lift = sqrt(clamp(elev, 0.0, 1.0));
          float grey = mix(0.80, 0.985, lift);
          color = vec3(grey * 0.985, grey, min(1.0, grey * 1.01));
        }
        float dx = dFdx(vRelief);
        float dy = dFdy(vRelief);
        vec3 normal = normalize(vec3(-dx * 9.0, -dy * 9.0, 1.0));
        vec3 sun = normalize(vec3(-0.38, -0.52, 0.76));
        float light = clamp(0.80 + dot(normal, sun) * 0.24, 0.66, 1.14);
        color *= light;
        outColor = vec4(color, 1.0);
      }
    `;

    const vs = createShader(gl.VERTEX_SHADER, vertexSource);
    const fs = createShader(gl.FRAGMENT_SHADER, fragmentSource);
    program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error(gl.getProgramInfoLog(program) || 'program link failed');
    }

    const cols = 128;
    const rows = 96;
    const vertices = new Float32Array((cols + 1) * (rows + 1) * 2);
    let k = 0;
    for (let y = 0; y <= rows; y++) {
      for (let x = 0; x <= cols; x++) {
        vertices[k++] = x / cols;
        vertices[k++] = y / rows;
      }
    }
    const indices = new Uint32Array(cols * rows * 6);
    k = 0;
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const a = y * (cols + 1) + x;
        const b = a + 1;
        const c = a + cols + 1;
        const d = c + 1;
        indices[k++] = a; indices[k++] = c; indices[k++] = b;
        indices[k++] = b; indices[k++] = c; indices[k++] = d;
      }
    }
    indexCount = indices.length;

    vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    const vbo = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    const ibo = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibo);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
    gl.bindVertexArray(null);

    terrainTexture = gl.createTexture();
    glacierMaskTexture = gl.createTexture();
    glacierElevTexture = gl.createTexture();
    for (const texture of [terrainTexture, glacierMaskTexture, glacierElevTexture]) {
      gl.bindTexture(gl.TEXTURE_2D, texture);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([50, 112, 140, 255]));
    }

    buildGlacierTextures();
    return true;
  }

  function terrainTextureUrl(cx, cy, span) {
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
    const baseSpan = Math.max(spanX, spanY);
    const desiredSpan = Math.max(260, Math.min(3600, baseSpan * TERRAIN_TEXTURE_SCALE));
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

  function chaikin(ring, passes) {
    let pts = Array.isArray(ring) ? ring : [];
    for (let pass = 0; pass < passes && pts.length >= 4; pass++) {
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

  function buildGlacierTextures() {
    const data = window.AR_GLACIER_DATA;
    if (!data || !Array.isArray(data.regions)) {
      uploadNeutralGlacierTextures();
      return;
    }
    const size = 1024;
    const mask = document.createElement('canvas');
    mask.width = mask.height = size;
    const mc = mask.getContext('2d');
    mc.fillStyle = '#000';
    mc.fillRect(0, 0, size, size);
    mc.fillStyle = '#fff';
    mc.beginPath();
    const project = p => ({
      x: (p[0] + extentKm) / (2 * extentKm) * size,
      y: (p[1] + extentKm) / (2 * extentKm) * size
    });
    for (const region of data.regions) {
      for (const sourceRing of region.r || []) {
        const passes = sourceRing.length < 90 ? 2 : sourceRing.length < 260 ? 1 : 0;
        const ring = passes ? chaikin(sourceRing, passes) : sourceRing;
        for (let i = 0; i < ring.length; i++) {
          const p = project(ring[i]);
          if (i) mc.lineTo(p.x, p.y); else mc.moveTo(p.x, p.y);
        }
        mc.closePath();
      }
    }
    try { mc.fill('evenodd'); } catch (error) { mc.fill(); }

    gl.bindTexture(gl.TEXTURE_2D, glacierMaskTexture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, mask);

    const elev = new Image();
    elev.decoding = 'async';
    elev.onload = () => {
      gl.bindTexture(gl.TEXTURE_2D, glacierElevTexture);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, elev);
    };
    elev.onerror = uploadNeutralGlacierTextures;
    elev.src = data.surfaceImage || 'assets/data/arctic-surface-elevation.png';
  }

  function uploadNeutralGlacierTextures() {
    if (!gl) return;
    gl.bindTexture(gl.TEXTURE_2D, glacierMaskTexture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 255]));
    gl.bindTexture(gl.TEXTURE_2D, glacierElevTexture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([76, 76, 76, 255]));
  }

  function normalize(v) {
    const l = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / l, v[1] / l, v[2] / l];
  }
  function cross(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  }
  function subtract(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

  function perspective(out, fovy, aspect, near, far) {
    const f = 1 / Math.tan(fovy / 2);
    out.set([
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (far + near) / (near - far), -1,
      0, 0, (2 * far * near) / (near - far), 0
    ]);
    return out;
  }

  function lookAt(out, eye, center, up) {
    const z = normalize(subtract(eye, center));
    const x = normalize(cross(up, z));
    const y = cross(z, x);
    out.set([
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -dot(x, eye), -dot(y, eye), -dot(z, eye), 1
    ]);
    return out;
  }

  function multiply(out, a, b) {
    const r = new Float32Array(16);
    for (let col = 0; col < 4; col++) {
      for (let row = 0; row < 4; row++) {
        r[col * 4 + row] =
          a[0 * 4 + row] * b[col * 4 + 0] +
          a[1 * 4 + row] * b[col * 4 + 1] +
          a[2 * 4 + row] * b[col * 4 + 2] +
          a[3 * 4 + row] * b[col * 4 + 3];
      }
    }
    out.set(r);
    return out;
  }

  function buildVP(aspect) {
    const projection = new Float32Array(16);
    const view = new Float32Array(16);
    perspective(projection, 50 * Math.PI / 180, aspect, .08, 12);
    lookAt(view, [0, -1.65, 1.90], [0, .55, -.05], [0, 0, 1]);
    multiply(vpMatrix, projection, view);
  }

  function resize() {
    const dpr = Math.min(devicePixelRatio || 1, dprCap);
    const w = Math.max(1, Math.round(innerWidth * dpr));
    const h = Math.max(1, Math.round(innerHeight * dpr));
    if (reliefCanvas.width !== w || reliefCanvas.height !== h) {
      reliefCanvas.width = w;
      reliefCanvas.height = h;
    }
    if (labelCanvas.width !== w || labelCanvas.height !== h) {
      labelCanvas.width = w;
      labelCanvas.height = h;
      labelCtx?.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    buildVP(innerWidth / Math.max(1, innerHeight));
  }
  addEventListener('resize', resize, { passive: true });
  resize();

  function projectLocal(local) {
    const x = local[0], y = local[1], z = local[2];
    const m = vpMatrix;
    const cx = m[0] * x + m[4] * y + m[8] * z + m[12];
    const cy = m[1] * x + m[5] * y + m[9] * z + m[13];
    const cw = m[3] * x + m[7] * y + m[11] * z + m[15];
    if (cw <= .03) return null;
    const ndcY = cy / cw - PIVOT_NDC_SHIFT;
    return {
      x: (cx / cw * .5 + .5) * innerWidth,
      y: (1 - (ndcY * .5 + .5)) * innerHeight,
      w: cw
    };
  }

  function projectWorld(worldX, worldY, view, z = 0) {
    const dx = worldX - view.x;
    const dy = worldY - view.y;
    const c = Math.cos(-currentYaw), s = Math.sin(-currentYaw);
    const rx = c * dx - s * dy;
    const ry = s * dx + c * dy;
    const normalizer = Math.max(view.width / view.scale, view.height / view.scale, 45);
    return projectLocal([rx / normalizer * 2, -ry / normalizer * 2, z]);
  }

  function drawLabels(view, now) {
    if (!labelCtx || now - lastLabelDraw < 90) return;
    lastLabelDraw = now;
    labelCtx.clearRect(0, 0, innerWidth, innerHeight);
    const labels = Array.isArray(view.labels) ? view.labels : [];
    for (const label of labels) {
      const defaultMin = label.kind === 'country' ? .3 : label.kind === 'water' ? .3 : label.kind === 'strait' ? .45 : label.kind === 'city' ? .55 : .4;
      if (view.zoomLevel < (label.minZoom ?? defaultMin)) continue;
      const w = polar(label.lat, label.lon);
      const p = projectWorld(w.x, w.y, view, .018);
      if (!p || p.x < -90 || p.x > innerWidth + 90 || p.y < 78 || p.y > innerHeight + 20) continue;
      let fs = label.kind === 'country' ? 14 : label.kind === 'city' ? 9 : label.kind === 'water' ? 11 : 10;
      fs *= clamp(Math.pow(view.zoomLevel, .2), .85, 1.25);
      labelCtx.save();
      labelCtx.textAlign = 'center';
      labelCtx.textBaseline = 'middle';
      labelCtx.lineWidth = label.kind === 'city' ? 3 : 4;
      labelCtx.strokeStyle = 'rgba(5,34,48,.72)';
      labelCtx.fillStyle = label.kind === 'city' ? '#f36c5d' : label.kind === 'water' || label.kind === 'strait' ? '#e7fbff' : '#eff7e8';
      labelCtx.font = label.kind === 'water' || label.kind === 'strait'
        ? `italic 700 ${fs}px Georgia,serif`
        : `${label.kind === 'country' ? 900 : 750} ${fs}px system-ui,sans-serif`;
      labelCtx.strokeText(label.name, p.x, p.y);
      labelCtx.fillText(label.name, p.x, p.y);
      if (label.kind === 'city') {
        labelCtx.fillStyle = '#f36c5d';
        labelCtx.strokeStyle = '#fff1df';
        labelCtx.lineWidth = 1.5;
        labelCtx.beginPath();
        labelCtx.arc(p.x, p.y + 11, 3.8, 0, Math.PI * 2);
        labelCtx.fill();
        labelCtx.stroke();
      }
      labelCtx.restore();
    }
  }

  function shipPalette(id) {
    if (id === 'nuclear') return { hull: '#b53f37', dark: '#672825', deck: '#f1eadf', accent: '#f4cd57', window: '#2b5368' };
    if (id === 'icebreaker') return { hull: '#b79b6e', dark: '#62533e', deck: '#eee7d6', accent: '#6ec7ca', window: '#31596a' };
    if (id === 'global') return { hull: '#35677b', dark: '#163e52', deck: '#edf6f3', accent: '#70c6dc', window: '#274f64' };
    if (id === 'coastal') return { hull: '#e3e7df', dark: '#48636e', deck: '#f8f5e9', accent: '#e1ad4d', window: '#355c70' };
    if (id === 'trawler') return { hull: '#b94d43', dark: '#63332e', deck: '#f2eadb', accent: '#efc85e', window: '#35586a' };
    return { hull: '#2f6277', dark: '#153c50', deck: '#f2f5eb', accent: '#e8bd52', window: '#31596a' };
  }

  function drawShip(view) {
    if (!shipCtx) return;
    const id = view.vesselId || 'fishing';
    const p = shipPalette(id);
    shipCtx.clearRect(0, 0, shipCanvas.width, shipCanvas.height);
    const cx = 130;
    const bow = 36;
    const stern = 274;
    const halfStern = id === 'nuclear' ? 67 : id === 'icebreaker' ? 62 : id === 'global' ? 56 : 50;
    const halfMid = halfStern * .82;
    const turn = clamp(wrapPi((view.angle || 0) - currentYaw), -.30, .30);
    shipCtx.save();
    const turnPivotY = stern - 10;
    shipCtx.translate(cx, turnPivotY);
    shipCtx.rotate(turn * .42);
    shipCtx.translate(-cx, -turnPivotY);

    const shadow = shipCtx.createRadialGradient(cx, stern - 12, 5, cx, stern - 12, 82);
    shadow.addColorStop(0, 'rgba(0,20,29,.40)');
    shadow.addColorStop(1, 'rgba(0,20,29,0)');
    shipCtx.fillStyle = shadow;
    shipCtx.beginPath();
    shipCtx.ellipse(cx, stern - 8, 86, 28, 0, 0, Math.PI * 2);
    shipCtx.fill();

    const hull = shipCtx.createLinearGradient(cx - halfStern, 0, cx + halfStern, 0);
    hull.addColorStop(0, p.dark);
    hull.addColorStop(.28, p.hull);
    hull.addColorStop(.65, p.hull);
    hull.addColorStop(1, p.dark);
    shipCtx.fillStyle = hull;
    shipCtx.strokeStyle = 'rgba(244,253,253,.88)';
    shipCtx.lineWidth = 2;
    shipCtx.beginPath();
    shipCtx.moveTo(cx, bow);
    shipCtx.bezierCurveTo(cx + halfMid * .62, bow + 22, cx + halfMid, 94, cx + halfStern, stern - 50);
    shipCtx.quadraticCurveTo(cx + halfStern * .86, stern - 8, cx, stern);
    shipCtx.quadraticCurveTo(cx - halfStern * .86, stern - 8, cx - halfStern, stern - 50);
    shipCtx.bezierCurveTo(cx - halfMid, 94, cx - halfMid * .62, bow + 22, cx, bow);
    shipCtx.closePath();
    shipCtx.fill();
    shipCtx.stroke();

    shipCtx.fillStyle = p.deck;
    shipCtx.beginPath();
    shipCtx.moveTo(cx, bow + 18);
    shipCtx.lineTo(cx + halfMid * .52, 99);
    shipCtx.lineTo(cx + halfMid * .67, 190);
    shipCtx.lineTo(cx - halfMid * .67, 190);
    shipCtx.lineTo(cx - halfMid * .52, 99);
    shipCtx.closePath();
    shipCtx.fill();

    const house = shipCtx.createLinearGradient(cx - 40, 0, cx + 40, 0);
    house.addColorStop(0, '#c9d9d8');
    house.addColorStop(.5, '#fbfcf7');
    house.addColorStop(1, '#b9cdcf');
    shipCtx.fillStyle = house;
    shipCtx.strokeStyle = 'rgba(32,72,84,.72)';
    shipCtx.lineWidth = 1.5;
    shipCtx.beginPath();
    shipCtx.moveTo(cx - 37, 103);
    shipCtx.lineTo(cx + 37, 103);
    shipCtx.lineTo(cx + 43, 166);
    shipCtx.lineTo(cx - 43, 166);
    shipCtx.closePath();
    shipCtx.fill();
    shipCtx.stroke();

    shipCtx.fillStyle = p.window;
    for (let i = -3; i <= 3; i++) shipCtx.fillRect(cx + i * 10 - 3.4, 111, 7, 7);
    shipCtx.fillStyle = p.accent;
    shipCtx.fillRect(cx - 4, 70, 8, 41);
    shipCtx.strokeStyle = p.accent;
    shipCtx.lineWidth = 3;
    shipCtx.beginPath();
    shipCtx.moveTo(cx, 74);
    shipCtx.lineTo(cx + 34, 92);
    shipCtx.stroke();

    if (['global', 'icebreaker', 'nuclear'].includes(id)) {
      shipCtx.fillStyle = id === 'nuclear' ? '#ddc25d' : '#65bfc4';
      shipCtx.strokeStyle = 'rgba(238,251,250,.9)';
      shipCtx.lineWidth = 2;
      shipCtx.beginPath();
      shipCtx.ellipse(cx, 222, id === 'nuclear' ? 31 : 27, 18, 0, 0, Math.PI * 2);
      shipCtx.fill();
      shipCtx.stroke();
      shipCtx.strokeStyle = '#f7fbf5';
      shipCtx.lineWidth = 2;
      shipCtx.beginPath();
      shipCtx.moveTo(cx - 15, 222); shipCtx.lineTo(cx + 15, 222);
      shipCtx.moveTo(cx, 212); shipCtx.lineTo(cx, 232);
      shipCtx.stroke();
    } else {
      shipCtx.strokeStyle = p.accent;
      shipCtx.lineWidth = 2;
      shipCtx.beginPath();
      shipCtx.moveTo(cx - 35, 214);
      shipCtx.lineTo(cx + 35, 214);
      shipCtx.stroke();
    }

    if (view.moving) {
      shipCtx.globalCompositeOperation = 'destination-over';
      const wake = shipCtx.createLinearGradient(cx, stern - 5, cx, shipCanvas.height);
      wake.addColorStop(0, 'rgba(234,251,255,.48)');
      wake.addColorStop(1, 'rgba(234,251,255,0)');
      shipCtx.fillStyle = wake;
      shipCtx.beginPath();
      shipCtx.moveTo(cx - 20, stern - 4);
      shipCtx.quadraticCurveTo(cx - 50, 296, cx - 60, 310);
      shipCtx.lineTo(cx + 60, 310);
      shipCtx.quadraticCurveTo(cx + 50, 296, cx + 20, stern - 4);
      shipCtx.closePath();
      shipCtx.fill();
      shipCtx.globalCompositeOperation = 'source-over';
    }
    shipCtx.restore();
  }

  function setMode(next, announce = true) {
    next = next === '3d' ? '3d' : '2d';
    if (next === '3d') {
      try {
        if (!initWebGL()) throw new Error('WebGL2 unavailable');
      } catch (error) {
        console.error('3D relief initialization failed', error);
        webglFailed = true;
        next = '2d';
        if (announce) window.AR_SHOW_TOAST?.('3D RELIEF UNAVAILABLE ON THIS DEVICE');
      }
    }
    mode = next;
    window.AR_3D_ACTIVE = mode === '3d';
    document.body.classList.toggle('relief-3d-active', mode === '3d');
    toggle.querySelectorAll('button').forEach(button => button.classList.toggle('active', button.dataset.reliefMode === mode));
    storeMode(mode);
    if (announce) {
      const message = mode === '3d' ? '3D RELIEF VIEW · EXPERIMENTAL' : '2D CHART VIEW';
      try { window.AR_SHOW_TOAST?.(message); } catch (error) {}
    }
  }

  toggle.addEventListener('click', event => {
    const button = event.target.closest('button[data-relief-mode]');
    if (!button) return;
    setMode(button.dataset.reliefMode);
  });

  function render(now) {
    requestAnimationFrame(render);
    const dt = Math.min(.05, Math.max(0, (now - lastNow) / 1000));
    lastNow = now;
    if (mode !== '3d' || !gl) return;
    const view = getView();
    if (!view || !Number.isFinite(view.scale) || view.scale <= 0) return;
    ensureTerrainTexture(view);
    if (!terrainReady) return;
    if (now - last3DDraw < target3DFrameMs) return;
    last3DDraw = now;
    resize();
    lastView = view;
    if (!Number.isFinite(currentYaw)) currentYaw = view.angle || 0;
    const delta = wrapPi((view.angle || 0) - currentYaw);
    const follow = 1 - Math.exp(-dt * 1.65);
    currentYaw = wrapPi(currentYaw + delta * follow);

    gl.viewport(0, 0, reliefCanvas.width, reliefCanvas.height);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.disable(gl.CULL_FACE);
    gl.clearColor(.36, .58, .66, 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(program);
    gl.bindVertexArray(vao);

    const baseSpanX = view.width / view.scale;
    const baseSpanY = view.height / view.scale;
    const renderSpan = Math.max(baseSpanX, baseSpanY) * TERRAIN_MESH_SCALE;
    gl.uniform2f(gl.getUniformLocation(program, 'uCenter'), view.x, view.y);
    gl.uniform2f(gl.getUniformLocation(program, 'uSpan'), renderSpan, renderSpan);
    gl.uniform2f(gl.getUniformLocation(program, 'uTexCenter'), terrainTexCenterX, terrainTexCenterY);
    gl.uniform1f(gl.getUniformLocation(program, 'uTexSpan'), terrainTexSpan);
    gl.uniform1f(gl.getUniformLocation(program, 'uExtent'), extentKm);
    gl.uniform1f(gl.getUniformLocation(program, 'uPivotShift'), PIVOT_NDC_SHIFT);
    gl.uniform1f(gl.getUniformLocation(program, 'uYaw'), currentYaw);
    gl.uniform1f(gl.getUniformLocation(program, 'uVerticalLand'), 8.0);
    gl.uniform1f(gl.getUniformLocation(program, 'uVerticalSea'), 2.7);
    gl.uniformMatrix4fv(gl.getUniformLocation(program, 'uVP'), false, vpMatrix);

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, terrainTexture);
    gl.uniform1i(gl.getUniformLocation(program, 'uTerrain'), 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, glacierMaskTexture);
    gl.uniform1i(gl.getUniformLocation(program, 'uGlacierMask'), 1);
    gl.activeTexture(gl.TEXTURE2);
    gl.bindTexture(gl.TEXTURE_2D, glacierElevTexture);
    gl.uniform1i(gl.getUniformLocation(program, 'uGlacierElev'), 2);

    gl.drawElements(gl.TRIANGLES, indexCount, gl.UNSIGNED_INT, 0);
    gl.bindVertexArray(null);
    drawLabels(view, now);
    drawShip(view);
  }

  function inverseProject(clientX, clientY) {
    const view = lastView || getView();
    if (!view) return null;
    const baseSpanX = view.width / view.scale;
    const baseSpanY = view.height / view.scale;
    const searchSpan = Math.max(baseSpanX, baseSpanY) * TERRAIN_MESH_SCALE;
    let worldX = view.x + (clientX / innerWidth - .5) * searchSpan;
    let worldY = view.y + (clientY / innerHeight - .5) * searchSpan;
    const eps = Math.max(0.08, Math.max(baseSpanX, baseSpanY) / 1200);

    for (let iteration = 0; iteration < 10; iteration++) {
      const p = projectWorld(worldX, worldY, view, 0);
      if (!p) return null;
      const ex = p.x - clientX;
      const ey = p.y - clientY;
      if (Math.hypot(ex, ey) < .45) break;
      const px = projectWorld(worldX + eps, worldY, view, 0);
      const py = projectWorld(worldX, worldY + eps, view, 0);
      if (!px || !py) break;
      const j00 = (px.x - p.x) / eps, j10 = (px.y - p.y) / eps;
      const j01 = (py.x - p.x) / eps, j11 = (py.y - p.y) / eps;
      const det = j00 * j11 - j01 * j10;
      if (Math.abs(det) < 1e-7) break;
      const stepX = (j11 * ex - j01 * ey) / det;
      const stepY = (-j10 * ex + j00 * ey) / det;
      worldX -= stepX;
      worldY -= stepY;
      const dx = worldX - view.x, dy = worldY - view.y;
      const limit = searchSpan * .58;
      worldX = view.x + clamp(dx, -limit, limit);
      worldY = view.y + clamp(dy, -limit, limit);
    }

    return {
      x: (worldX - view.x) * view.scale + view.width / 2,
      y: (worldY - view.y) * view.scale + view.height / 2
    };
  }

  reliefCanvas.addEventListener('pointerdown', event => {
    if (mode !== '3d') return;
    const mapped = inverseProject(event.clientX, event.clientY);
    if (!mapped) return;
    event.preventDefault();
    try {
      map.dispatchEvent(new PointerEvent('pointerdown', {
        bubbles: true,
        cancelable: true,
        pointerId: 1,
        pointerType: 'mouse',
        isPrimary: true,
        clientX: mapped.x,
        clientY: mapped.y,
        button: 0,
        buttons: 1
      }));
    } catch (error) {
      map.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, clientX: mapped.x, clientY: mapped.y, button: 0 }));
    }
  }, { passive: false });

  window.AR_RELIEF_3D = {
    setMode,
    getMode: () => mode,
    isReady: () => !!(gl && terrainReady),
    resetCamera: () => { const view = getView(); if (view) currentYaw = view.angle || 0; }
  };

  setMode(readStoredMode(), false);
  requestAnimationFrame(render);
})();
