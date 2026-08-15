from pathlib import Path
import re


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    return text.replace(old, new)


rp = Path('relief-3d.js')
r = rp.read_text()
r = once(r,
"  const terrainRequestPixels = matchMedia('(pointer:coarse)').matches ? 1536 : 2048;\n  const PIVOT_NDC_SHIFT = 0.50;",
"  const terrainRequestPixels = matchMedia('(pointer:coarse)').matches ? 2048 : 3072;\n  const PIVOT_NDC_SHIFT = 0.28;\n  const TERRAIN_MESH_SCALE = 2.6;\n  const TERRAIN_TEXTURE_SCALE = 3.4;",
'view constants')

r = once(r,
"    const cols = 96;\n    const rows = 72;",
"    const cols = 128;\n    const rows = 96;",
'mesh resolution')

r = once(r,
"    const desiredSpan = Math.max(180, Math.min(1900, Math.hypot(spanX, spanY) * 1.50));",
"    const baseSpan = Math.max(spanX, spanY);\n    const desiredSpan = Math.max(260, Math.min(3600, baseSpan * TERRAIN_TEXTURE_SCALE));",
'terrain request footprint')

r = once(r,
"    const spanX = view.width / view.scale;\n    const spanY = view.height / view.scale;\n    gl.uniform2f(gl.getUniformLocation(program, 'uCenter'), view.x, view.y);\n    gl.uniform2f(gl.getUniformLocation(program, 'uSpan'), spanX, spanY);",
"    const baseSpanX = view.width / view.scale;\n    const baseSpanY = view.height / view.scale;\n    const renderSpan = Math.max(baseSpanX, baseSpanY) * TERRAIN_MESH_SCALE;\n    gl.uniform2f(gl.getUniformLocation(program, 'uCenter'), view.x, view.y);\n    gl.uniform2f(gl.getUniformLocation(program, 'uSpan'), renderSpan, renderSpan);",
'expanded render footprint')

new_inverse = r'''  function inverseProject(clientX, clientY) {
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
'''
r, n = re.subn(r"  function inverseProject\(clientX, clientY\) \{.*?\n  \}\n\n  reliefCanvas\.addEventListener", new_inverse + "\n  reliefCanvas.addEventListener", r, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'inverse projection: expected 1 match, found {n}')
rp.write_text(r)

cp = Path('relief-3d.css')
c = cp.read_text()
c = once(c,
"  bottom: max(-14px, calc(env(safe-area-inset-bottom) - 14px));",
"  bottom: max(19vh, calc(env(safe-area-inset-bottom) + 34px));",
'desktop vessel position')
c = once(c,
"  #relief-3d-ship { width: clamp(110px, 28vw, 152px); bottom: -8px; }",
"  #relief-3d-ship { width: clamp(110px, 28vw, 152px); bottom: max(19vh, calc(env(safe-area-inset-bottom) + 22px)); }",
'mobile vessel position')
c = once(c,
"  #relief-3d-ship { width: clamp(104px, 15vw, 145px); bottom: -20px; }",
"  #relief-3d-ship { width: clamp(104px, 15vw, 145px); bottom: max(18vh, calc(env(safe-area-inset-bottom) + 16px)); }",
'landscape vessel position')
cp.write_text(c)

ip = Path('index.html')
i = ip.read_text()
i = once(i, 'relief-3d.css?v=expedition-23a-relief3d', 'relief-3d.css?v=expedition-23c-viewrange', '3D css cache tag')
i = once(i, 'relief-3d.js?v=expedition-23b-relief3d', 'relief-3d.js?v=expedition-23c-viewrange', '3D js cache tag')
ip.write_text(i)

print('3D vessel position and terrain range updated')
