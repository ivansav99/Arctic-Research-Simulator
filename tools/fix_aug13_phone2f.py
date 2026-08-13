from pathlib import Path
p=Path('tools/ars_aug13_phone2.py')
s=p.read_text()
s=s.replace('shore_anchor="  function shorelineSlide(x,y,vx,vy,dt,targetX,targetY){"','shore_anchor="  function shorelineSlide(x,y,vx,vy,motionDt,targetX,targetY){"')
p.write_text(s)
print('fixed shoreline helper patch target')
