from pathlib import Path
p=Path('tools/ars_aug13_phone2.py')
s=p.read_text()
old="e=replace_once(e,\"name:'You'\",\"name:'Chief Scientist'\",'initial player name')"
new="e=replace_once(e,\"const initialScientist = {id:'player', profileId:null, name:'You',\",\"const initialScientist = {id:'player', profileId:null, name:'Chief Scientist',\",'initial player name')"
if old not in s: raise SystemExit('initial player name patch line missing')
s=s.replace(old,new,1)
p.write_text(s)
print('fixed initial player name patch target')
