from __future__ import annotations

import argparse
import json
import math
import os
import re
import tarfile
import tempfile
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image
import shapefile
from pyproj import Transformer
from shapely.geometry import shape, Polygon, MultiPolygon, box
from shapely.ops import transform
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
import rasterio

EXTENT_M = 2_910_000
GRID = 1456  # ~4 km cells across the 5820 km chart
MIN_LAT = 63.25
SIMPLIFY_M = 1800
MIN_AREA_M2 = 2_000_000
MAX_ELEV_M = 4000.0


def iter_polygons(geom):
    if geom.is_empty:
        return
    if isinstance(geom, Polygon):
        yield geom
    elif isinstance(geom, MultiPolygon):
        yield from geom.geoms
    else:
        for part in getattr(geom, "geoms", []):
            yield from iter_polygons(part)


def round_ring(coords):
    # EPSG:3996 +northing is opposite the game's +y direction.
    out = []
    for easting, northing in coords:
        x = round(easting / 1000.0, 1)
        y = round(-northing / 1000.0, 1)
        if not out or out[-1] != [x, y]:
            out.append([x, y])
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def load_glaciers(ne_zip: Path):
    work = Path(tempfile.mkdtemp(prefix="ars-ne-"))
    with zipfile.ZipFile(ne_zip) as zf:
        zf.extractall(work)
    shp = next(work.rglob("ne_10m_glaciated_areas.shp"))
    reader = shapefile.Reader(str(shp))
    to_ps = Transformer.from_crs("EPSG:4326", "EPSG:3996", always_xy=True)
    chart = box(-EXTENT_M, -EXTENT_M, EXTENT_M, EXTENT_M)
    projected = []
    vector = []
    for sr in reader.iterShapeRecords():
        src = shape(sr.shape.__geo_interface__)
        if src.is_empty or src.bounds[3] < MIN_LAT:
            continue
        geom = transform(to_ps.transform, src)
        if not geom.is_valid:
            geom = geom.buffer(0)
        geom = geom.intersection(chart)
        if geom.is_empty:
            continue
        # Simplification keeps fronts recognizable while making collision checks cheap.
        geom = geom.simplify(SIMPLIFY_M, preserve_topology=True)
        for poly in iter_polygons(geom):
            if poly.area < MIN_AREA_M2:
                continue
            projected.append(poly)
            rings = [round_ring(poly.exterior.coords)]
            rings += [round_ring(r.coords) for r in poly.interiors]
            rings = [r for r in rings if len(r) >= 3]
            if not rings:
                continue
            minx, miny, maxx, maxy = poly.bounds
            vector.append({
                "b": [round(minx/1000,1), round(-maxy/1000,1), round(maxx/1000,1), round(-miny/1000,1)],
                "r": rings,
            })
    print(f"glacier polygons: {len(vector)}")
    return projected, vector


def find_dem_tifs(arcticdem_tar: Path):
    out = Path(tempfile.mkdtemp(prefix="ars-arcticdem-"))
    with tarfile.open(arcticdem_tar, "r:gz") as tf:
        members = [m for m in tf.getmembers() if m.name.lower().endswith(".tif") and "dem" in Path(m.name).name.lower()]
        if not members:
            raise RuntimeError("No ArcticDEM GeoTIFF found in archive")
        tf.extractall(out, members=members)
    tifs = []
    for p in out.rglob("*.tif"):
        n = p.name.lower()
        if any(skip in n for skip in ("count", "mad", "datamask", "hillshade", "browse")):
            continue
        tifs.append(p)
    if not tifs:
        raise RuntimeError("No usable ArcticDEM DEM GeoTIFF after extraction")
    print("DEM files:", len(tifs), [p.name for p in tifs[:4]])
    return tifs


def build_surface(tifs):
    dst_transform = from_bounds(-EXTENT_M, -EXTENT_M, EXTENT_M, EXTENT_M, GRID, GRID)
    dst = np.full((GRID, GRID), np.nan, dtype=np.float32)
    for p in tifs:
        with rasterio.open(p) as src:
            reproject(
                source=rasterio.band(src, 1),
                destination=dst,
                src_transform=src.transform,
                src_crs=src.crs,
                src_nodata=src.nodata,
                dst_transform=dst_transform,
                dst_crs="EPSG:3996",
                dst_nodata=np.nan,
                resampling=Resampling.bilinear,
                init_dest_nodata=False,
                num_threads=2,
            )
    valid = np.isfinite(dst) & (dst > -500) & (dst < 9000)
    elev = np.where(valid, np.clip(dst, 0, MAX_ELEV_M), 0).astype(np.float32)
    print("surface valid cells:", int(valid.sum()), "elevation max:", float(elev.max()))
    return elev, valid, dst_transform


def relief_rgba(elev, valid, glacier_mask):
    norm = np.clip(elev / MAX_ELEV_M, 0, 1)
    safe = np.where(valid, norm, 0)
    gy, gx = np.gradient(safe)
    mag = np.hypot(gx, gy)
    directional = (-gx - gy) / (mag + 1e-5)
    shade = np.clip(0.94 + directional * 0.10, 0.80, 1.08)
    yy, xx = np.indices(norm.shape)
    # Long, restrained flow/crevasse bands give glacier ice a texture unlike sea ice floes.
    flow = 3.0*np.sin(xx*0.19 + yy*0.055) + 1.8*np.sin(xx*0.047 - yy*0.13)
    base = 174 + 77 * np.sqrt(norm)
    r = np.clip(base * shade + flow, 145, 252)
    g = np.clip((base + 4) * shade + flow, 150, 254)
    b = np.clip((base + 10) * shade + flow, 158, 255)
    rgba = np.zeros((*norm.shape, 4), dtype=np.uint8)
    mask = glacier_mask.astype(bool)
    rgba[...,0] = np.where(mask, r, 0).astype(np.uint8)
    rgba[...,1] = np.where(mask, g, 0).astype(np.uint8)
    rgba[...,2] = np.where(mask, b, 0).astype(np.uint8)
    rgba[...,3] = np.where(mask, 255, 0).astype(np.uint8)
    return rgba


def surface_rgba(elev, valid):
    q = np.zeros(elev.shape, dtype=np.uint8)
    q[valid] = 1 + np.rint(np.clip(elev[valid] / MAX_ELEV_M, 0, 1) * 254).astype(np.uint8)
    rgba = np.zeros((*elev.shape, 4), dtype=np.uint8)
    rgba[...,0] = q
    rgba[...,1] = q
    rgba[...,2] = q
    rgba[...,3] = np.where(valid, 255, 0).astype(np.uint8)
    return rgba


def make_assets(ne_zip: Path, arcticdem_tar: Path, repo: Path):
    projected, vector = load_glaciers(ne_zip)
    tifs = find_dem_tifs(arcticdem_tar)
    elev, valid, dst_transform = build_surface(tifs)
    mask = rasterize(
        [(p, 1) for p in projected],
        out_shape=(GRID, GRID), transform=dst_transform,
        fill=0, dtype="uint8", all_touched=True,
    )
    outdir = repo / "assets" / "data"
    outdir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(surface_rgba(elev, valid), "RGBA").save(outdir / "arctic-surface-elevation.png", optimize=True, compress_level=9)
    Image.fromarray(relief_rgba(elev, valid, mask), "RGBA").save(outdir / "arctic-glacier-relief.png", optimize=True, compress_level=9)
    data = {
        "source": "Natural Earth 1:10m Glaciated Areas + ArcticDEM v4.1 surface elevation",
        "extentKm": EXTENT_M // 1000,
        "grid": GRID,
        "maxElevationM": int(MAX_ELEV_M),
        "surfaceImage": "assets/data/arctic-surface-elevation.png",
        "reliefImage": "assets/data/arctic-glacier-relief.png",
        "regions": vector,
    }
    (repo / "glacier-data.js").write_text("window.AR_GLACIER_DATA=" + json.dumps(data, separators=(",", ":")) + ";\n")
    print("glacier-data.js bytes:", (repo / "glacier-data.js").stat().st_size)
    print("surface png bytes:", (outdir / "arctic-surface-elevation.png").stat().st_size)
    print("relief png bytes:", (outdir / "arctic-glacier-relief.png").stat().st_size)


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)


def patch_app(repo: Path):
    index = repo / "index.html"
    s = index.read_text()
    s = s.replace("expedition-22n-mapfix", "expedition-22p-glaciers")
    if "glacier-data.js" not in s:
        s = replace_once(s, '  <script src="river-data.js"></script>\n', '  <script src="river-data.js"></script>\n  <script src="glacier-data.js?v=expedition-22p-glaciers"></script>\n', "glacier script")
    index.write_text(s)

    game = repo / "game.js"
    g = game.read_text()
    load_anchor = "  const loadSprite=src=>{const img=new Image();img.decoding='async';img.src=src;return img;};\n"
    glacier_boot = r'''  const GLACIER_DATA=window.AR_GLACIER_DATA||{regions:[]},GLACIER_EXTENT_KM=Number(window.AR_GLACIER_DATA?.extentKm)||2910;
  const glacierReliefImage=loadSprite(GLACIER_DATA.reliefImage||''),surfaceElevationImage=loadSprite(GLACIER_DATA.surfaceImage||'');
  const surfaceElevationCanvas=document.createElement('canvas'),surfaceElevationCtx=surfaceElevationCanvas.getContext('2d',{willReadFrequently:true});let surfaceElevationPixels=null,surfaceElevationW=0,surfaceElevationH=0;
  function prepareSurfaceElevation(){try{if(!surfaceElevationImage.naturalWidth)return;surfaceElevationW=surfaceElevationImage.naturalWidth;surfaceElevationH=surfaceElevationImage.naturalHeight;surfaceElevationCanvas.width=surfaceElevationW;surfaceElevationCanvas.height=surfaceElevationH;surfaceElevationCtx.drawImage(surfaceElevationImage,0,0);surfaceElevationPixels=surfaceElevationCtx.getImageData(0,0,surfaceElevationW,surfaceElevationH).data;for(const tile of terrainTileCache.values()){tile.seasonCanvas=null;tile.seasonBucket=-1;}}catch(error){surfaceElevationPixels=null;}}
  surfaceElevationImage.addEventListener('load',prepareSurfaceElevation);if(surfaceElevationImage.complete)prepareSurfaceElevation();
  function surfaceElevationNormAt(x,y){if(!surfaceElevationPixels||Math.abs(x)>GLACIER_EXTENT_KM||Math.abs(y)>GLACIER_EXTENT_KM)return null;const fx=(x+GLACIER_EXTENT_KM)/(2*GLACIER_EXTENT_KM)*(surfaceElevationW-1),fy=(y+GLACIER_EXTENT_KM)/(2*GLACIER_EXTENT_KM)*(surfaceElevationH-1),x0=Math.max(0,Math.min(surfaceElevationW-1,Math.floor(fx))),y0=Math.max(0,Math.min(surfaceElevationH-1,Math.floor(fy))),x1=Math.min(surfaceElevationW-1,x0+1),y1=Math.min(surfaceElevationH-1,y0+1),tx=fx-x0,ty=fy-y0;const q=(px,py)=>surfaceElevationPixels[(py*surfaceElevationW+px)*4]||0,q00=q(x0,y0),q10=q(x1,y0),q01=q(x0,y1),q11=q(x1,y1);if(!(q00||q10||q01||q11))return null;const cv=v=>v?Math.max(0,(v-1)/254):null,a=cv(q00),b=cv(q10),c=cv(q01),d=cv(q11),vals=[a,b,c,d].filter(v=>v!=null);if(!vals.length)return null;const fallback=vals.reduce((sum,v)=>sum+v,0)/vals.length,v00=a??fallback,v10=b??fallback,v01=c??fallback,v11=d??fallback;return(v00*(1-tx)+v10*tx)*(1-ty)+(v01*(1-tx)+v11*tx)*ty;}
  const glacierRegions=(GLACIER_DATA.regions||[]).map((item,index)=>({id:index,b:item.b,r:item.r})),GLACIER_CELL=128,glacierGrid=new Map(),glacierCellKey=(gx,gy)=>`${gx},${gy}`;
  for(const region of glacierRegions){const [minX,minY,maxX,maxY]=region.b;for(let gx=Math.floor(minX/GLACIER_CELL);gx<=Math.floor(maxX/GLACIER_CELL);gx++)for(let gy=Math.floor(minY/GLACIER_CELL);gy<=Math.floor(maxY/GLACIER_CELL);gy++){const key=glacierCellKey(gx,gy);if(!glacierGrid.has(key))glacierGrid.set(key,[]);glacierGrid.get(key).push(region);}}
  function pointInGlacierRing(x,y,ring){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if(((a[1]>y)!==(b[1]>y))&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;}return inside;}
  function glacierAt(x,y){const regions=glacierGrid.get(glacierCellKey(Math.floor(x/GLACIER_CELL),Math.floor(y/GLACIER_CELL)))||[];for(const region of regions){const b=region.b;if(x<b[0]||x>b[2]||y<b[1]||y>b[3]||!pointInGlacierRing(x,y,region.r[0]))continue;let hole=false;for(let i=1;i<region.r.length;i++)if(pointInGlacierRing(x,y,region.r[i])){hole=true;break;}if(!hole)return true;}return false;}
  function drawGlacierRelief(target=ctx,project=worldToScreen,alpha=.98){if(!glacierReliefImage.complete||!glacierReliefImage.naturalWidth)return false;const a=project(-GLACIER_EXTENT_KM,-GLACIER_EXTENT_KM),b=project(GLACIER_EXTENT_KM,GLACIER_EXTENT_KM),left=Math.min(a.x,b.x),top=Math.min(a.y,b.y),w=Math.abs(b.x-a.x),h=Math.abs(b.y-a.y);target.save();target.globalAlpha*=alpha;target.imageSmoothingEnabled=true;try{target.imageSmoothingQuality='high';}catch(error){}target.drawImage(glacierReliefImage,left,top,w,h);target.restore();return true;}
  function drawPermanentGlaciers(){if(!drawGlacierRelief())return;const bounds=visibleWorldBounds(12);ctx.save();ctx.strokeStyle='rgba(116,166,183,.82)';ctx.lineWidth=Math.max(.75,Math.min(2.2,scale*.22));for(const region of glacierRegions){const b=region.b;if(b[2]<bounds.minX||b[0]>bounds.maxX||b[3]<bounds.minY||b[1]>bounds.maxY)continue;ctx.beginPath();for(const ring of region.r){ring.forEach((p,i)=>{const s=worldToScreen(p[0],p[1]);i?ctx.lineTo(s.x,s.y):ctx.moveTo(s.x,s.y);});ctx.closePath();}ctx.stroke();}ctx.restore();}
'''
    if "const GLACIER_DATA=" not in g:
        g = replace_once(g, load_anchor, load_anchor + glacier_boot, "glacier bootstrap")

    g = replace_once(g, "  const isBlocked=(x,y)=>isLand(x,y)&&!riverAt(x,y);", "  const isBlocked=(x,y)=>glacierAt(x,y)||(isLand(x,y)&&!riverAt(x,y));", "glacier collision")
    g = replace_once(g, "function iceTypeAt(x,y){if(isLand(x,y))return'open';", "function iceTypeAt(x,y){if(glacierAt(x,y))return'glacier';if(isLand(x,y))return'open';", "glacier ice type")
    g = replace_once(g, "function naturalIceTypeAt(x,y){if(isLand(x,y))return'open';", "function naturalIceTypeAt(x,y){if(glacierAt(x,y))return'glacier';if(isLand(x,y))return'open';", "natural glacier type")
    g = replace_once(g, "function iceNavigationRule(type,thickness,vessel=vesselModifiers()){\n    if(type==='open')return{speedFactor:1,breaking:false};", "function iceNavigationRule(type,thickness,vessel=vesselModifiers()){\n    if(type==='glacier')return null;\n    if(type==='open')return{speedFactor:1,breaking:false};", "glacier navigation rule")
    g = replace_once(g, "if(pos.lat<MIN_LAT||isLand(x,y))continue;", "if(pos.lat<MIN_LAT||isBlocked(x,y))continue;", "port glacier blocking")

    old_high = "const x=tile.minX+(px+.5)/m*TERRAIN_TILE_KM,y=tile.minY+(py+.5)/m*TERRAIN_TILE_KM,lat=unpolar(x,y).lat,high=tile.heightProxy[j]/255;"
    new_high = "const x=tile.minX+(px+.5)/m*TERRAIN_TILE_KM,y=tile.minY+(py+.5)/m*TERRAIN_TILE_KM,lat=unpolar(x,y).lat,high=surfaceElevationNormAt(x,y)??tile.heightProxy[j]/255;"
    g = replace_once(g, old_high, new_high, "ArcticDEM seasonal relief")
    old_color = "const mix=white/(white+green+.0001),i=j*4;out[i]=Math.round(66+(248-66)*mix);out[i+1]=Math.round(132+(251-132)*mix);out[i+2]=Math.round(76+(249-76)*mix);out[i+3]=Math.round(Math.min(.9,a)*255);"
    new_color = "const mix=white/(white+green+.0001),i=j*4,snowGrey=Math.round(180+70*Math.sqrt(high));out[i]=Math.round(66+(snowGrey-66)*mix);out[i+1]=Math.round(132+(Math.min(253,snowGrey+4)-132)*mix);out[i+2]=Math.round(76+(Math.min(255,snowGrey+9)-76)*mix);out[i+3]=Math.round(Math.min(.92,a)*255);"
    g = replace_once(g, old_color, new_color, "white grey snow elevation palette")

    map_anchor = "    if(realTerrain){drawRasterSeasonalOverlay();}else{const nearSvalbard=(()=>{const pos=unpolar(state.x,state.y);return pos.lat>74.5&&pos.lat<82.5&&pos.lon>-5&&pos.lon<45;})();land.forEach(shape=>{const visible=!(shape.maxX<minX||shape.minX>maxX||shape.maxY<minY||shape.minY>maxY)||nearSvalbard&&svalbardLand.includes(shape);if(!visible)return;pathPolygon(ctx,shape.pts,worldToScreen);ctx.fillStyle=shape.color;ctx.fill();ctx.strokeStyle='rgba(239,247,221,.9)';ctx.lineWidth=2;ctx.stroke();drawLandTopography(shape);});}\n    drawRivers(minX,maxX,minY,maxY);"
    map_new = map_anchor.replace("\n    drawRivers", "\n    drawPermanentGlaciers();\n    drawRivers")
    g = replace_once(g, map_anchor, map_new, "draw permanent glaciers")

    mini_anchor = "if(!miniTerrain)land.forEach(shape=>{pathPolygon(mini,shape.pts,project);mini.fillStyle=shape.color;mini.fill();mini.strokeStyle='rgba(245,251,231,.72)';mini.lineWidth=.35;mini.stroke();});"
    g = replace_once(g, mini_anchor, mini_anchor + "drawGlacierRelief(mini,project,.96);", "minimap glaciers")
    g = g.replace("TERRAIN: IBCAO / GEBCO · HI-RES TILES", "TERRAIN: IBCAO / GEBCO · ARCTICDEM SURFACE · GLACIERS")
    g = g.replace("const GAME_VERSION='expedition-22c-visuals'", "const GAME_VERSION='expedition-22p-glaciers'")
    game.write_text(g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--natural-earth", required=True, type=Path)
    ap.add_argument("--arcticdem", required=True, type=Path)
    ap.add_argument("--repo", default=".", type=Path)
    args = ap.parse_args()
    repo = args.repo.resolve()
    make_assets(args.natural_earth, args.arcticdem, repo)
    patch_app(repo)
    print("ARS glacier + ArcticDEM patch complete")

if __name__ == "__main__":
    main()
