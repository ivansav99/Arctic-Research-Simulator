from pathlib import Path

p=Path('game.js')
s=p.read_text()

def replace_once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s=s.replace(old,new)

replace_once(
"  function frame(now){const dt=Math.min(.04,(now-last)/1000);last=now;const paused=state.gameOver||menuOpen||minimapExpanded||!!research?.isBusy?.();sound.update(paused);let weather;",
"  window.AR_3D_VIEW=()=>{const ship=vesselModifiers();return{x:state.x,y:state.y,angle:state.angle,zoomLevel,scale,width,height,moving:state.moving,commandActive:state.commandActive,ramming:state.ramming,paused:state.gameOver||menuOpen||minimapExpanded||!!research?.isBusy?.(),started:state.started,seasonDay:state.seasonDay,year:state.year,vesselId:vesselIceId(ship),vesselName:ship.name||'Research Vessel',labels:chartLabels};};\n  window.AR_SHOW_TOAST=showToast;\n  function frame(now){const dt=Math.min(.04,(now-last)/1000);last=now;const paused=state.gameOver||menuOpen||minimapExpanded||!!research?.isBusy?.();sound.update(paused);let weather;",
'3D view state hook')

replace_once(
"drawResearchGuidance();try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}drawVessel();requestAnimationFrame(frame);",
"drawResearchGuidance();try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}if(!window.AR_3D_ACTIVE)drawVessel();requestAnimationFrame(frame);",
'3D vessel switch')

p.write_text(s)
print('3D engine hooks applied')
