from pathlib import Path
p=Path('tools/build_glacier_surface.py')
s=p.read_text()
s=s.replace("let surfaceElevationPixels=null,surfaceElevationW=0,surfaceElevationH=0;", "let surfaceElevationPixels=null,surfaceElevationW=0,surfaceElevationH=0,surfaceElevationGeneration=0;")
s=s.replace("surfaceElevationPixels=surfaceElevationCtx.getImageData(0,0,surfaceElevationW,surfaceElevationH).data;for(const tile of terrainTileCache.values()){tile.seasonCanvas=null;tile.seasonBucket=-1;}", "surfaceElevationPixels=surfaceElevationCtx.getImageData(0,0,surfaceElevationW,surfaceElevationH).data;surfaceElevationGeneration++;")
needle='''    old_high = "const x=tile.minX+(px+.5)/m*TERRAIN_TILE_KM,y=tile.minY+(py+.5)/m*TERRAIN_TILE_KM,lat=unpolar(x,y).lat,high=tile.heightProxy[j]/255;"'''
insert='''    cache_old = "if(!tile.maskReady)return null;const winter=iceGrowth(),bucket=Math.round(winter*16);if(tile.seasonCanvas&&tile.seasonBucket===bucket)return tile.seasonCanvas;"
    cache_new = "if(!tile.maskReady)return null;const winter=iceGrowth(),bucket=Math.round(winter*16);if(tile.seasonCanvas&&tile.seasonBucket===bucket&&tile.seasonSurfaceGeneration===surfaceElevationGeneration)return tile.seasonCanvas;"
    g = replace_once(g, cache_old, cache_new, "season surface generation")
    finish_old = "tile.seasonCanvas=c;tile.seasonBucket=bucket;return c;"
    finish_new = "tile.seasonCanvas=c;tile.seasonBucket=bucket;tile.seasonSurfaceGeneration=surfaceElevationGeneration;return c;"
    g = replace_once(g, finish_old, finish_new, "season surface cache stamp")

'''+needle
if needle not in s: raise SystemExit('builder cache insertion anchor missing')
s=s.replace(needle,insert,1)
p.write_text(s)
print('glacier builder startup ordering fixed')
