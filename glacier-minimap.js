(() => {
  'use strict';
  const data = window.AR_GLACIER_DATA;
  const mini = document.getElementById('minimap');
  const panel = document.getElementById('minimap-panel');
  const game = document.getElementById('game');
  if (!data || !mini || !game || !Array.isArray(data.regions)) return;

  const layer = document.createElement('canvas');
  layer.id = 'glacier-minimap-overlay';
  layer.setAttribute('aria-hidden', 'true');
  Object.assign(layer.style, {
    position: 'fixed', pointerEvents: 'none', zIndex: '4', display: 'none'
  });
  game.appendChild(layer);
  const ctx = layer.getContext('2d');
  if (!ctx) return;

  const A = 6378137;
  const F = 1 / 298.257223563;
  const E = Math.sqrt(F * (2 - F));
  const LAT_TS = 75 * Math.PI / 180;
  const t = phi => Math.tan(Math.PI / 4 - phi / 2) /
    Math.pow((1 - E * Math.sin(phi)) / (1 + E * Math.sin(phi)), E / 2);
  const MC = Math.cos(LAT_TS) / Math.sqrt(1 - E * E * Math.sin(LAT_TS) ** 2);
  const TC = t(LAT_TS);

  function polar(lat, lon) {
    if (lat >= 89.999999) return { x: 0, y: 0 };
    const phi = lat * Math.PI / 180;
    const a = lon * Math.PI / 180;
    const r = A * MC * t(phi) / TC / 1000;
    return { x: r * Math.sin(a), y: r * Math.cos(a) };
  }

  function center() {
    const text = document.getElementById('position')?.textContent || '';
    const m = text.match(/([0-9.]+)\s*°?N\s+([0-9.]+)\s*°?([EW])/i);
    if (!m) return null;
    const lat = Number(m[1]);
    const lon = Number(m[2]) * (m[3].toUpperCase() === 'W' ? -1 : 1);
    return Number.isFinite(lat) && Number.isFinite(lon) ? polar(lat, lon) : null;
  }

  function intersects(b, bounds) {
    return b && !(b[2] < bounds.minX || b[0] > bounds.maxX ||
      b[3] < bounds.minY || b[1] > bounds.maxY);
  }

  function syncLayer() {
    const rect = mini.getBoundingClientRect();
    if (rect.width < 2 || rect.height < 2) {
      layer.style.display = 'none';
      return null;
    }
    layer.style.display = 'block';
    layer.style.left = `${rect.left}px`;
    layer.style.top = `${rect.top}px`;
    layer.style.width = `${rect.width}px`;
    layer.style.height = `${rect.height}px`;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const pw = Math.max(1, Math.round(rect.width * dpr));
    const ph = Math.max(1, Math.round(rect.height * dpr));
    if (layer.width !== pw || layer.height !== ph) {
      layer.width = pw;
      layer.height = ph;
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { width: rect.width, height: rect.height };
  }

  function draw() {
    requestAnimationFrame(draw);
    try {
      const box = syncLayer();
      const c = center();
      if (!box || !c) return;
      const w = box.width;
      const h = box.height;
      ctx.clearRect(0, 0, w, h);
      const expanded = panel?.classList.contains('expanded') || false;
      const worldRadius = expanded ? 1100 : 520;
      const canonicalSize = Number(mini.width) || 300;
      const canonicalRadius = canonicalSize / 2 - (expanded ? 30 : 20);
      const radius = canonicalRadius * (w / canonicalSize);
      const k = radius / worldRadius;
      const bounds = {
        minX: c.x - worldRadius, maxX: c.x + worldRadius,
        minY: c.y - worldRadius, maxY: c.y + worldRadius
      };
      const visible = data.regions.filter(region => intersects(region.b, bounds));
      if (!visible.length) return;
      const project = p => ({
        x: w / 2 + (p[0] - c.x) * k,
        y: h / 2 + (p[1] - c.y) * k
      });
      ctx.save();
      ctx.beginPath();
      ctx.arc(w / 2, h / 2, radius, 0, Math.PI * 2);
      ctx.clip();
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
      ctx.fillStyle = 'rgba(228,241,245,.78)';
      try { ctx.fill('evenodd'); } catch (error) { ctx.fill(); }
      ctx.restore();
    } catch (error) {
      console.error('Glacier minimap overlay error', error);
    }
  }

  requestAnimationFrame(draw);
})();
