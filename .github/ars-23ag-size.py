from pathlib import Path
import gzip
import math
import re
import statistics
import urllib.request


def mib(n):
    return n / (1024 * 1024)

core_files = [
    'index.html','style.css','coast-data.js','river-data.js','wildlife-data.js',
    'visual-assets-data.js','photo-pass-version.js','expedition.js','sprite-atlas-data.js',
    'glacier-data.js','frame-guard.js','game.js','glacier-overlay-v2.js','manifest.webmanifest'
]
core = [Path(p) for p in core_files if Path(p).exists()]
core_bytes = sum(p.stat().st_size for p in core)
core_gzip = sum(len(gzip.compress(p.read_bytes(), compresslevel=9)) for p in core)

text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in core)
refs = sorted(set(re.findall(r"assets/[A-Za-z0-9_./-]+\.(?:webp|png|jpg|jpeg|svg)", text, flags=re.I)))
local_refs = [Path(p) for p in refs if Path(p).is_file()]
local_asset_bytes = sum(p.stat().st_size for p in local_refs)
production_local = core_bytes + local_asset_bytes

all_assets = [p for p in Path('assets').rglob('*') if p.is_file()]
all_asset_bytes = sum(p.stat().st_size for p in all_assets)
repo_files = [p for p in Path('.').rglob('*') if p.is_file() and '.git' not in p.parts]
repo_bytes = sum(p.stat().st_size for p in repo_files)

print('ARS_SIZE core_raw_bytes=', core_bytes)
print('ARS_SIZE core_raw_mib=', f'{mib(core_bytes):.3f}')
print('ARS_SIZE core_gzip_est_mib=', f'{mib(core_gzip):.3f}')
print('ARS_SIZE referenced_local_asset_count=', len(local_refs))
print('ARS_SIZE referenced_local_assets_mib=', f'{mib(local_asset_bytes):.3f}')
print('ARS_SIZE production_local_raw_mib=', f'{mib(production_local):.3f}')
print('ARS_SIZE all_assets_repo_mib=', f'{mib(all_asset_bytes):.3f}')
print('ARS_SIZE full_checkout_no_git_mib=', f'{mib(repo_bytes):.3f}')

headers={'User-Agent':'ArcticResearchSimulator-size-estimate/1.0'}
def fetch_size(url):
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as response:
        return len(response.read())

overview='https://wms.gebco.net/2024/north-polar/mapserv?BBOX=-2910000%2C-2910000%2C2910000%2C2910000&crs=EPSG%3A3996&format=image%2Fjpeg&height=2048&layers=GEBCO_NORTH_POLAR_VIEW_bed_2024&request=getmap&service=wms&version=1.3.0&width=2048'
try:
    overview_bytes=fetch_size(overview)
    print('ARS_SIZE current_overview_wms_mib=',f'{mib(overview_bytes):.3f}')
    print('ARS_SIZE first_load_core_plus_overview_raw_mib=',f'{mib(core_bytes+overview_bytes):.3f}')
except Exception as e:
    print('ARS_SIZE overview_sample_error=',repr(e))

extent=2910
tile_km=128
halfdiag=tile_km*math.sqrt(2)/2
indices=range(math.floor(-extent/tile_km)-1, math.ceil(extent/tile_km)+1)
tiles=[]
for ix in indices:
    for iy in indices:
        cx=(ix+.5)*tile_km; cy=(iy+.5)*tile_km
        if math.hypot(cx,cy) <= extent+halfdiag:
            tiles.append((ix,iy))
print('ARS_SIZE full_arctic_tile_count=',len(tiles))

samples=[(0,0),(5,0),(10,0),(15,0),(20,0),(-5,7),(-10,12),(12,-14),(-18,-5),(3,18),(-14,-14),(8,20)]
sizes=[]
for ix,iy in samples:
    minx=ix*tile_km*1000; maxx=(ix+1)*tile_km*1000
    minn=-(iy+1)*tile_km*1000; maxn=-iy*tile_km*1000
    url=(f'https://wms.gebco.net/2024/north-polar/mapserv?BBOX={minx}%2C{minn}%2C{maxx}%2C{maxn}'
         '&crs=EPSG%3A3996&format=image%2Fpng&height=1024&layers=GEBCO_NORTH_POLAR_VIEW_bed_2024'
         '&request=getmap&service=wms&version=1.3.0&width=1024')
    try:
        n=fetch_size(url); sizes.append(n); print(f'ARS_SIZE tile_{ix}_{iy}_bytes=',n)
    except Exception as e:
        print(f'ARS_SIZE tile_{ix}_{iy}_error=',repr(e))

if sizes:
    avg=statistics.mean(sizes); med=statistics.median(sizes); count=len(tiles)
    print('ARS_SIZE sampled_tile_count=',len(sizes))
    print('ARS_SIZE tile_average_mib=',f'{mib(avg):.3f}')
    print('ARS_SIZE tile_median_mib=',f'{mib(med):.3f}')
    print('ARS_SIZE full_map_est_average_gib=',f'{avg*count/(1024**3):.3f}')
    print('ARS_SIZE full_map_est_median_gib=',f'{med*count/(1024**3):.3f}')
    print('ARS_SIZE offline_total_average_gib=',f'{(avg*count+production_local)/(1024**3):.3f}')
