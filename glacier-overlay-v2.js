(() => {
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
