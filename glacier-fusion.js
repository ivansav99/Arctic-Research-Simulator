(() => {
  'use strict';

  const data = window.AR_GLACIER_DATA;
  if (!data || !Array.isArray(data.regions)) return;

  const extentKm = Number(data.extentKm) || 2910;
  const regions = data.regions;
  const overlaySize = 512;
  const nativeDrawImage = CanvasRenderingContext2D.prototype.drawImage;
  const nativeStroke = CanvasRenderingContext2D.prototype.stroke;
  const frameTiles = new WeakMap();
  const tileOverlayCache = new WeakMap();
  let surfacePixels = null;
  let surfaceW = 0;
  let surfaceH = 0;
  let surfaceGeneration = 0;
  let internalDraw = false;

  const surfaceImage = new Image();
  surfaceImage.decoding = 'async';
  surfaceImage.addEventListener('load', () => {
    try {
      const c = document.createElement('canvas');
      c.width = surfaceImage.naturalWidth;
      c.height = surfaceImage.naturalHeight;
      const cc = c.getContext('2d', { willReadFrequently: true });
      nativeDrawImage.call(cc, surfaceImage, 0, 0);
      surfacePixels = cc.getImageData(0, 0, c.width, c.height).data;
      surfaceW = c.width;
      surfaceH = c.height;
      surfaceGeneration++;
    } catch (error) {
      surfacePixels = null;
    }
  });
  surfaceImage.src = data.surfaceImage || '';

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

  function parseWmsBounds(image) {
    const src = String(image?.currentSrc || image?.src || '');
    if (!src.includes('wms.gebco.net')) return null;
    try {
      const url = new URL(src, document.baseURI);
      const format = (url.searchParams.get('format') || '').toLowerCase();
      const bbox = (url.searchParams.get('BBOX') || url.searchParams.get('bbox') || '')
        .split(',').map(Number);
      if (bbox.length !== 4 || bbox.some(v => !Number.isFinite(v))) return null;
      const [minE, minN, maxE, maxN] = bbox;
      const span = Math.max(maxE - minE, maxN - minN);
      return {
        isTile: format.includes('png') && span < 300000,
        isOverview: format.includes('jpeg') && span > 1000000,
        minX: minE / 1000,
        maxX: maxE / 1000,
        minY: -maxN / 1000,
        maxY: -minN / 1000
      };
    } catch (error) {
      return null;
    }
  }

  function intersects(b, bounds) {
    return !(b[2] < bounds.minX || b[0] > bounds.maxX ||
      b[3] < bounds.minY || b[1] > bounds.maxY);
  }

  function buildMask(bounds) {
    const c = document.createElement('canvas');
    c.width = c.height = overlaySize;
    const cc = c.getContext('2d', { willReadFrequently: true });
    const sx = overlaySize / (bounds.maxX - bounds.minX);
    const sy = overlaySize / (bounds.maxY - bounds.minY);
    cc.fillStyle = '#fff';

    for (const region of regions) {
      if (!region?.b || !intersects(region.b, bounds)) continue;
      cc.beginPath();
      for (const ring of region.r || []) {
        for (let i = 0; i < ring.length; i++) {
          const p = ring[i];
          const px = (p[0] - bounds.minX) * sx;
          const py = (p[1] - bounds.minY) * sy;
          if (i) cc.lineTo(px, py); else cc.moveTo(px, py);
        }
        cc.closePath();
      }
      try { cc.fill('evenodd'); } catch (error) { cc.fill(); }
    }
    return cc.getImageData(0, 0, overlaySize, overlaySize).data;
  }

  function buildTileOverlay(image, bounds) {
    const cached = tileOverlayCache.get(image);
    if (cached && cached.surfaceGeneration === surfaceGeneration) return cached.canvas;

    const mask = buildMask(bounds);
    let hasGlacier = false;
    for (let i = 3; i < mask.length; i += 4) {
      if (mask[i]) { hasGlacier = true; break; }
    }
    if (!hasGlacier) {
      tileOverlayCache.set(image, { surfaceGeneration, canvas: null });
      return null;
    }

    const c = document.createElement('canvas');
    c.width = c.height = overlaySize;
    const cc = c.getContext('2d', { willReadFrequently: true });
    const outImage = cc.createImageData(overlaySize, overlaySize);
    const out = outImage.data;
    let terrainPixels = null;
    let luminance = null;
    let integral = null;

    try {
      const terrainCanvas = document.createElement('canvas');
      terrainCanvas.width = terrainCanvas.height = overlaySize;
      const tc = terrainCanvas.getContext('2d', { willReadFrequently: true });
      internalDraw = true;
      nativeDrawImage.call(tc, image, 0, 0, overlaySize, overlaySize);
      internalDraw = false;
      terrainPixels = tc.getImageData(0, 0, overlaySize, overlaySize).data;

      luminance = new Float32Array(overlaySize * overlaySize);
      integral = new Float64Array((overlaySize + 1) * (overlaySize + 1));
      const stride = overlaySize + 1;
      for (let y = 0; y < overlaySize; y++) {
        let rowSum = 0;
        for (let x = 0; x < overlaySize; x++) {
          const j = y * overlaySize + x;
          const i = j * 4;
          const l = terrainPixels[i] * 0.2126 + terrainPixels[i + 1] * 0.7152 + terrainPixels[i + 2] * 0.0722;
          luminance[j] = l;
          rowSum += l;
          integral[(y + 1) * stride + (x + 1)] = integral[y * stride + (x + 1)] + rowSum;
        }
      }
    } catch (error) {
      internalDraw = false;
      terrainPixels = null;
      luminance = null;
      integral = null;
    }

    const spanX = bounds.maxX - bounds.minX;
    const spanY = bounds.maxY - bounds.minY;
    const detailRadius = 11;
    const stride = overlaySize + 1;
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

    for (let y = 0; y < overlaySize; y++) {
      const worldY = bounds.minY + (y + 0.5) / overlaySize * spanY;
      for (let x = 0; x < overlaySize; x++) {
        const j = y * overlaySize + x;
        const mi = j * 4;
        const maskAlpha = mask[mi + 3] / 255;
        if (maskAlpha <= 0) continue;

        const worldX = bounds.minX + (x + 0.5) / overlaySize * spanX;
        const coarse = surfaceHeightAt(worldX, worldY);
        const h = coarse == null ? 0.42 : coarse;
        let detail = 0;

        if (luminance && integral) {
          const x0 = Math.max(0, x - detailRadius);
          const y0 = Math.max(0, y - detailRadius);
          const x1 = Math.min(overlaySize - 1, x + detailRadius);
          const y1 = Math.min(overlaySize - 1, y + detailRadius);
          const xa = x0, ya = y0, xb = x1 + 1, yb = y1 + 1;
          const sum = integral[yb * stride + xb] - integral[ya * stride + xb] -
            integral[yb * stride + xa] + integral[ya * stride + xa];
          const mean = sum / ((x1 - x0 + 1) * (y1 - y0 + 1));
          detail = clamp(luminance[j] - mean, -42, 42);
        }

        // ArcticDEM supplies the broad surface-height trend. Only the local
        // high-frequency relief from the detailed terrain tile is added back.
        const baseGrey = 198 + 48 * Math.sqrt(clamp(h, 0, 1));
        const shade = clamp(baseGrey + detail * 0.72, 168, 252);
        out[mi] = clamp(Math.round(shade - 10), 0, 255);
        out[mi + 1] = clamp(Math.round(shade), 0, 255);
        out[mi + 2] = clamp(Math.round(shade + 4), 0, 255);
        out[mi + 3] = Math.round((0.64 + 0.12 * Math.sqrt(clamp(h, 0, 1))) * maskAlpha * 255);
      }
    }

    cc.putImageData(outImage, 0, 0);
    tileOverlayCache.set(image, { surfaceGeneration, canvas: c });
    return c;
  }

  function rememberTile(ctx, image, bounds, args) {
    if (!bounds?.isTile) return;
    let records = frameTiles.get(ctx);
    if (!records) {
      records = new Map();
      frameTiles.set(ctx, records);
    }

    let dx, dy, dw, dh;
    if (args.length === 4) {
      [dx, dy, dw, dh] = args;
    } else if (args.length === 8) {
      [, , , , dx, dy, dw, dh] = args;
    } else {
      return;
    }
    records.set(String(image.currentSrc || image.src || ''), { image, bounds, dx, dy, dw, dh });
  }

  function drawFusedGlaciers(ctx) {
    const records = frameTiles.get(ctx);
    if (!records?.size) return;
    ctx.save();
    ctx.imageSmoothingEnabled = true;
    try { ctx.imageSmoothingQuality = 'high'; } catch (error) {}
    for (const record of records.values()) {
      const overlay = buildTileOverlay(record.image, record.bounds);
      if (!overlay) continue;
      nativeDrawImage.call(ctx, overlay, record.dx, record.dy, record.dw, record.dh);
    }
    ctx.restore();
  }

  CanvasRenderingContext2D.prototype.drawImage = function(image, ...args) {
    if (internalDraw) return nativeDrawImage.call(this, image, ...args);

    const src = String(image?.currentSrc || image?.src || '');
    const canvasId = this.canvas?.id || '';

    // The old Arctic-wide glacier raster is intentionally not stretched over
    // the detailed main chart. At exactly the point where the engine used to
    // draw it, substitute the fused per-tile glacier surface instead. Keep the
    // low-resolution raster on the minimap where its native scale is adequate.
    if (src.includes('arctic-glacier-relief.png') && canvasId === 'map') {
      drawFusedGlaciers(this);
      return;
    }

    const wms = parseWmsBounds(image);
    if (wms?.isOverview && canvasId === 'map') {
      let records = frameTiles.get(this);
      if (!records) {
        records = new Map();
        frameTiles.set(this, records);
      } else {
        records.clear();
      }
    }

    const result = nativeDrawImage.call(this, image, ...args);
    if (wms?.isTile && canvasId === 'map') rememberTile(this, image, wms, args);
    return result;
  };

  // Glacier polygons remain available to the game for spatial logic and
  // research-site eligibility, but their cartographic outlines are not drawn.
  CanvasRenderingContext2D.prototype.stroke = function(...args) {
    if (this.canvas?.id === 'map') {
      const style = String(this.strokeStyle || '').replace(/\s+/g, '');
      if (style === 'rgba(116,166,183,0.82)' || style === 'rgba(116,166,183,.82)') return;
    }
    return nativeStroke.apply(this, args);
  };
})();