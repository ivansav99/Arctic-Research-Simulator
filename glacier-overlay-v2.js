(() => {
  'use strict';

  const data = window.AR_GLACIER_DATA;
  if (!data || !Array.isArray(data.regions)) return;

  const extentKm = Number(data.extentKm) || 2910;
  let surfacePixels = null;
  let surfaceW = 0;
  let surfaceH = 0;

  // Smooth only coarse rings. Detailed Natural Earth rings are already dense;
  // multiplying those points would add CPU cost without improving the edge.
  function chaikin(ring, iterations) {
    let pts = Array.isArray(ring) ? ring : [];
    for (let pass = 0; pass < iterations && pts.length >= 4; pass++) {
      const next = [];
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i];
        const b = pts[(i + 1) % pts.length];
        next.push([
          a[0] * 0.75 + b[0] * 0.25,
          a[1] * 0.75 + b[1] * 0.25
        ]);
        next.push([
          a[0] * 0.25 + b[0] * 0.75,
          a[1] * 0.25 + b[1] * 0.75
        ]);
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

  // A modest field resolution is enough because the ArcticDEM source is broad
  // relief. Fine terrain texture continues to come from the underlying chart.
  const FIELD = 112;
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

  function intersects(b, bounds) {
    return b && !(b[2] < bounds.minX || b[0] > bounds.maxX ||
      b[3] < bounds.minY || b[1] > bounds.maxY);
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

  function buildField(centerX, centerY, scale, width, height) {
    if (!fieldCtx) return;
    const image = fieldCtx.createImageData(FIELD, FIELD);
    const out = image.data;
    const spanX = width / scale;
    const spanY = height / scale;
    for (let py = 0; py < FIELD; py++) {
      const wy = centerY + ((py + 0.5) / FIELD - 0.5) * spanY;
      for (let px = 0; px < FIELD; px++) {
        const wx = centerX + ((px + 0.5) / FIELD - 0.5) * spanX;
        const h = surfaceHeightAt(wx, wy);
        const hh = h == null ? 0.30 : Math.max(0, Math.min(1, h));
        const lift = Math.sqrt(hh);
        // Low ice is cool light gray; high ice approaches clean white.
        const grey = Math.round(214 + 39 * lift);
        const j = (py * FIELD + px) * 4;
        out[j] = Math.max(0, grey - 4);
        out[j + 1] = grey;
        out[j + 2] = Math.min(255, grey + 3);
        out[j + 3] = 255;
      }
    }
    fieldCtx.putImageData(image, 0, 0);
  }

  window.AR_DRAW_MAIN_GLACIERS = ({ctx, width, height, state, scale, worldToScreen}) => {
    if (!ctx || !state || !Number.isFinite(scale) || scale <= 0 || !worldToScreen) return;
    const radiusX = width / scale / 2;
    const radiusY = height / scale / 2;
    const visible = visibleFor(state.x, state.y, radiusX, radiusY);
    if (!visible.length) return;

    ctx.save();
    appendRegionsPath(ctx, visible, p => worldToScreen(p[0], p[1]));
    try { ctx.clip('evenodd'); } catch (error) { ctx.clip(); }

    buildField(state.x, state.y, scale, width, height);
    ctx.globalAlpha = 1;
    ctx.imageSmoothingEnabled = true;
    try { ctx.imageSmoothingQuality = 'high'; } catch (error) {}
    if (fieldCtx) {
      ctx.drawImage(fieldCanvas, 0, 0, width, height);
    } else {
      ctx.fillStyle = 'rgb(226,235,238)';
      ctx.fillRect(0, 0, width, height);
    }
    ctx.restore();
  };

  window.AR_DRAW_MINI_GLACIERS = ({ctx, project, c, radius, geometry, worldRadius}) => {
    if (!ctx || !project || !geometry || !Number.isFinite(radius) || radius <= 0) return;
    const visible = visibleFor(geometry.centerX, geometry.centerY, worldRadius, worldRadius, 0);
    if (!visible.length) return;

    ctx.save();
    ctx.beginPath();
    ctx.arc(c, c, radius, 0, Math.PI * 2);
    ctx.clip();
    appendRegionsPath(ctx, visible, p => project(p[0], p[1]));
    ctx.fillStyle = 'rgb(230,238,241)';
    try { ctx.fill('evenodd'); } catch (error) { ctx.fill(); }
    ctx.restore();
  };
})();
