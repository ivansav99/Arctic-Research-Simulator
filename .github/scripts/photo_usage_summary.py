from pathlib import Path
import re
names=['box-corer.webp','coastal-a-frame.webp','deep-adcp.webp','ek80-scientific-echosounder.webp','mini-rov.webp','shallow-adcp.webp','shelf-adcp.webp','coastal-service-toolkit.webp','handheld-water-lab.webp','ice-corer-auger.webp','hull-echosounder-sensor.webp','aerostat-face-free.webp','large-drone-face-free.webp','hydrophone-array-face-free.webp','sonobuoy-pack.webp','polar-float.webp','xbt-kit.webp','medium-science-winch.webp','starlink-terminal.webp','surface-drifter-pair.webp','cloud-radar.webp','swift-buoy.webp','large-drone.webp','aerostat.webp','radiosonde.webp','work-rov.webp','ctd-rosette.webp','sonobuoy.webp','hydrophone-array.webp','argo-float.webp','xbt.webp','argo-float.jpg','sea-ice-station.webp','storm-sea.webp','aerial-survey.webp','arctic-small-boat.webp','river-plume.webp','fishing-trawler.webp','fishing-vessel.webp','noaa-rv-brown.webp','base-vessel.png','base-vessel-source.png']
files=[Path(x) for x in ['expedition.js','game.js','index.html','style.css','visual-assets-data.js','wildlife-data.js','sprite-atlas-data.js'] if Path(x).exists()]
out=[]
for i,name in enumerate(names,1):
 hits=[]
 for p in files:
  text=p.read_text(errors='ignore')
  for line in text.splitlines():
   if name in line:
    hits.append(f'{p.name}: {line.strip()[:520]}')
 out.append(f'{i:03d} | {name} | '+(' || '.join(hits) if hits else 'NOT REFERENCED BY CURRENT RUNTIME'))

out.append('\nREMOTE IMAGE SOURCES IN CURRENT EXPEDITION MEDIA:')
text=Path('expedition.js').read_text(errors='ignore')
# Limit to MEDIA block before SPECIALTIES
block=text[text.find('const MEDIA = {'):text.find('const SPECIALTIES')]
for line in block.splitlines():
 if 'src:' in line and 'http' in line:
  out.append(line.strip())
Path('photo-usage-summary.txt').write_text('\n'.join(out))
