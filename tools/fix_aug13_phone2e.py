from pathlib import Path
p=Path('tools/ars_aug13_phone2.py')
s=p.read_text()
old='g=replace_once(g,"function setDestination(screenX,screenY){pendingResearchTargetId=null;","function setDestination(screenX,screenY){pendingResearchTargetId=null;pendingResearchArrival=null;",\'manual destination clear\')'
new='''g=replace_once(g,"function setDestination(clientX,clientY){pendingResearchTargetId=null;","function setDestination(clientX,clientY){pendingResearchTargetId=null;pendingResearchArrival=null;",'manual destination clear')\ng=replace_once(g,"const geometry=miniMapGeometry();pendingResearchTargetId=null;setWorldDestination","const geometry=miniMapGeometry();pendingResearchTargetId=null;pendingResearchArrival=null;setWorldDestination",'minimap destination clear')\ng=replace_once(g,"departWithCheck(()=>{pendingResearchTargetId=null;state.portDestination=portItem.city;","departWithCheck(()=>{pendingResearchTargetId=null;pendingResearchArrival=null;state.portDestination=portItem.city;",'port destination clear')'''
if old not in s: raise SystemExit('manual destination patch line missing')
s=s.replace(old,new,1)
p.write_text(s)
print('fixed manual navigation clear patch')
