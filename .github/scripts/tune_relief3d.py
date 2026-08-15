from pathlib import Path
p=Path('relief-3d.js')
s=p.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected 1, found {n}')
    s=s.replace(old,new)

once("    lookAt(view, [0, -1.72, 1.58], [0, .58, -.05], [0, 0, 1]);","    lookAt(view, [0, -1.65, 1.90], [0, .55, -.05], [0, 0, 1]);",'camera angle')
once("    image.onerror = () => {\n      console.warn('3D terrain overview unavailable; 3D mode will remain disabled.');\n      terrainReady = false;\n    };","    image.onerror = () => {\n      console.warn('3D terrain overview unavailable; returning to 2D.');\n      terrainReady = false;\n      if(mode==='3d'){setMode('2d',false);try{window.AR_SHOW_TOAST?.('3D TERRAIN SOURCE UNAVAILABLE · RETURNED TO 2D');}catch(error){}}\n    };",'terrain failure rollback')
p.write_text(s)
print('3D relief failure path tuned')
