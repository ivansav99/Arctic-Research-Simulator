(() => {
  'use strict';

  const data = window.AR_GLACIER_DATA;
  const map = document.getElementById('map');
  const game = document.getElementById('game');
  if (!data || !map || !game || !Array.isArray(data.regions)) return;

  // Independent visual layer only. This script never replaces or patches any
  // game canvas method, so a glacier rendering problem cannot stop drawMap().
  const overlay = document.createElement('canvas');
  overlay.id = 'glacier-overlay';
  overlay.setAttribute('aria-hidden', 'true');
  Object.assign(overlay.style, {
    position: 'fixed',
    inset: '0',
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: '1'
  });
  game.appendChild(overlay);

  const ctx = overlay.getContext('2d');
  if (!ctx) return;

  const extentKm = Number(data.extentKm) || 2910;
  const regions = data.regions;
  let width = 0;
  let height = 0;
  let dpr = 1;
  let surfacePixels = null;
  let surfaceW = 0;
  let surfaceH = 0;
  let lastDraw = 0;

  // A small viewport-aligned color field gives the broad ArcticDEM elevation
  // signal. The opacity is deliberately moderate so the much finer IBCAO/
  // GEBCO relief already drawn by the game remains visible underneath.
  const FIELD = 96;
  const fieldCanvas = document.createElement('canvas');
  fieldCanvas.width = FIELD;
  fieldCanvas.height = FIELD;
  const fieldCtx = fieldCanvas.getContext('2d', { willReadFrequently: true });

  const surfaceImage = new Image();
  surfaceImage.decoding = 'async';
  surfaceImage.addEventListener('load', () => {
    try {
      const c = document.createElement('canvas');
      c.width = surfaceImage.naturalWidth;
      c.height = surfaceImage.naturalHeight;
      const cc = c.getContext('2d', { willReadFrequently: true });
      cc.drawImage(surfaceImage, 0, 0);
      surfacePixels = cc.getImageData(0, 0, c.width, c.height).data;
      surfaceW = c.width;
      surfaceH = c.height;
    } catch (error) {
      console.warn('Glacier surface image could not be sampled; using neutral ice tint.', error);
      surfacePixels = null;
    }
  });
  surfaceImage.src = data.surfaceImage || 'assets/data/arctic-surface-elevation.png';

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    const pw = Math.max(1, Math.round(width * dpr));
    const ph = Math.max(1, Math.round(height * dpr));
    if (overlay.width !== pw || overlay.height !== ph) {
      overlay.width = pw;
      overlay.height = ph;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
  }
  window.addEventListener('resize', resize, { passive: true });
  resize();

  // Same EPSG:3996 polar stereographic geometry used by the game.
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

  function currentCamera() {
    const text = document.getElementById('position')?.textContent || '';
    const match = text.match(/([0-9.]+)\s*°?N\s+([0-9.]+)\s*°?([EW])/i);
    if (!match) return null;
    const lat = Number(match[1]);
    const lon = Number(match[2]) * (match[3].toUpperCase() === 'W' ? -1 : 1);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    const center = polar(lat, lon);
    const zoomText = document.getElementById('zoom-level')?.textContent || '100%';
    const zoom = Math.max(0.4, (parseFloat(zoomText) || 100) / 100);
    const baseScale = Math.max(3.4, Math.min(5.2, Math.min(width, height) / 145));
    return { x: center.x, y: center.y, scale: baseScale * zoom };
  }

  function surfaceHeightAt(x, y) {
    if (!surfacePixels || Math.abs(x) > extentKm || Math.abs(y) > extentKm) return null;
    const fx = (x + extentKm) / (2 * extentKm) * (surfaceW - 1);
    const fy = (y + extentKm) / (2 * extentKm) * (surfaceH - 1);
    const x0 = Math.max(0, Math.min(surfaceW - 1, Math.floor(fx)));
    const y0 = Math.max(0, Math.min(surfaceH - 1, Math.floor(fy)));
    const x1 = Math.min(surfaceW - 1, x0 + 1);
    const y1 = Math.min(surfaceH - 1, y0 + 1);
    const tx = fx - x0;
    const ty = fy - y0;
    const q = (px, py) => surfacePixels[(py * surfaceW + px) * 4] || 0;
    const cv = v => v ? Math.max(0, (v - 1) / 254) : null;
    const a = cv(q(x0, y0));
    const b = cv(q(x1, y0));
    const c = cv(q(x0, y1));
    const d = cv(q(x1, y1));
    const valid = [a, b, c, d].filter(v => v != null);
    if (!valid.length) return null;
    const fallback = valid.reduce((sum, v) => sum + v, 0) / valid.length;
    const v00 = a ?? fallback;
    const v10 = b ?? fallback;
    const v01 = c ?? fallback;
    const v11 = d ?? fallback;
    return (v00 * (1 - tx) + v10 * tx) * (1 - ty) +
      (v01 * (1 - tx) + v11 * tx) * ty;
  }

  function visibleBounds(camera, margin = 16) {
    return {
      minX: camera.x - width / camera.scale / 2 - margin,
      maxX: camera.x + width / camera.scale / 2 + margin,
      minY: camera.y - height / camera.scale / 2 - margin,
      maxY: camera.y + height / camera.scale / 2 + margin
    };
  }

  function intersects(b, bounds) {
    return b && !(b[2] < bounds.minX || b[0] > bounds.maxX ||
      b[3] < bounds.minY || b[1] > bounds.maxY);
  }

  function buildField(camera) {
    if (!fieldCtx) return;
    const image = fieldCtx.createImageData(FIELD, FIELD);
    const out = image.data;
    const spanX = width / camera.scale;
    const spanY = height / camera.scale;
    for (let py = 0; py < FIELD; py++) {
      const wy = camera.y + ((py + 0.5) / FIELD - 0.5) * spanY;
      for (let px = 0; px < FIELD; px++) {
        const wx = camera.x + ((px + 0.5) / FIELD - 0.5) * spanX;
        const h = surfaceHeightAt(wx, wy);
        const hh = h == null ? 0.32 : Math.max(0, Math.min(1, h));
        const lift = Math.sqrt(hh);
        const grey = Math.round(220 + 28 * lift);
        const j = (py * FIELD + px) * 4;
        out[j] = Math.max(0, grey - 10);
        out[j + 1] = grey;
        out[j + 2] = Math.min(255, grey + 5);
        out[j + 3] = Math.round(102 + 34 * lift);
      }
    }
    fieldCtx.putImageData(image, 0, 0);
  }

  function draw(now) {
    requestAnimationFrame(draw);
    if (now - lastDraw < 55) return;
    lastDraw = now;

    resize();
    ctx.clearRect(0, 0, width, height);
    const camera = currentCamera();
    if (!camera) return;

    const bounds = visibleBounds(camera);
    const visible = regions.filter(region => intersects(region.b, bounds));
    if (!visible.length) return;

    const project = p => ({
      x: width / 2 + (p[0] - camera.x) * camera.scale,
      y: height / 2 + (p[1] - camera.y) * camera.scale
    });

    ctx.save();
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
    try { ctx.clip('evenodd'); } catch (error) { ctx.clip(); }

    buildField(camera);
    ctx.imageSmoothingEnabled = true;
    try { ctx.imageSmoothingQuality = 'high'; } catch (error) {}
    if (fieldCtx) {
      ctx.drawImage(fieldCanvas, 0, 0, width, height);
    } else {
      ctx.fillStyle = 'rgba(218,232,236,.46)';
      ctx.fillRect(0, 0, width, height);
    }
    ctx.restore();
  }

  requestAnimationFrame(draw);
})();
