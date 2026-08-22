from pathlib import Path
import re, json

asset_names = [
'box-corer.webp','coastal-a-frame.webp','deep-adcp.webp','ek80-scientific-echosounder.webp','mini-rov.webp','shallow-adcp.webp','shelf-adcp.webp','coastal-service-toolkit.webp','handheld-water-lab.webp','ice-corer-auger.webp','hull-echosounder-sensor.webp','aerostat-face-free.webp','large-drone-face-free.webp','hydrophone-array-face-free.webp','sonobuoy-pack.webp','polar-float.webp','xbt-kit.webp','medium-science-winch.webp','starlink-terminal.webp','surface-drifter-pair.webp','cloud-radar.webp','swift-buoy.webp','large-drone.webp','aerostat.webp','radiosonde.webp','work-rov.webp','ctd-rosette.webp','sonobuoy.webp','hydrophone-array.webp','argo-float.webp','xbt.webp','argo-float.jpg',
'sea-ice-station.webp','storm-sea.webp','aerial-survey.webp','arctic-small-boat.webp','river-plume.webp',
'fishing-trawler.webp','fishing-vessel.webp','noaa-rv-brown.webp','base-vessel.png','base-vessel-source.png'
]
files=[p for p in Path('.').glob('*') if p.suffix in {'.js','.html','.css','.md'} and p.is_file()]
rows=[]
for name in asset_names:
    hits=[]
    for p in files:
        text=p.read_text(errors='ignore')
        for m in re.finditer(re.escape(name), text):
            start=text.rfind('\n',0,m.start())+1; end=text.find('\n',m.end())
            if end<0:end=len(text)
            line=text[start:end].strip()
            hits.append({'file':str(p),'line':line[:700]})
    rows.append({'asset':name,'hits':hits})

# Current remotely sourced image entries in expedition MEDIA and wildlife source data.
remote=[]
for p in [Path('expedition.js'),Path('wildlife-data.js')]:
    if not p.exists(): continue
    text=p.read_text(errors='ignore')
    for m in re.finditer(r"(?:src|photo|image)\s*:\s*['\"](https?://[^'\"]+)",text):
        start=text.rfind('\n',0,m.start())+1; end=text.find('\n',m.end())
        if end<0:end=len(text)
        remote.append({'file':str(p),'url':m.group(1),'line':text[start:end].strip()[:900]})
Path('photo-usage-audit.json').write_text(json.dumps({'local':rows,'remote':remote},indent=2))
print(len(rows),len(remote))
