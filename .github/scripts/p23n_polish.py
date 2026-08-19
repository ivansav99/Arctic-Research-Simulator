from pathlib import Path

p=Path('expedition.js')
s=p.read_text()

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected 1, got {n}')
    s=s.replace(old,new,1)

once("  function missionRewardScore(template,distanceKm,kind) {","  function missionRewardScore(template,distanceKm,kind,actualWorkHours=template.workHours) {",'reward score signature')
once("workScore=clamp(((template.workHours||10)-8)/135,0,1);","workScore=clamp(((actualWorkHours||10)-8)/135,0,1);",'actual work score')
once("  function missionRewardAmount(template,kind,distanceKm,rng) {\n    const official=kind==='grant'||kind==='contract',range=official?[40000,60000]:[10000,15000];\n    const score=clamp(missionRewardScore(template,distanceKm,kind)+(rng()-.5)*.05,0,1);","  function missionRewardAmount(template,kind,distanceKm,rng,actualWorkHours=template.workHours) {\n    const official=kind==='grant'||kind==='contract',range=official?[40000,60000]:[10000,15000];\n    const score=clamp(missionRewardScore(template,distanceKm,kind,actualWorkHours)+(rng()-.5)*.05,0,1);",'reward amount work arg')
once("reward:missionRewardAmount(template,kind,distance,rng),","reward:missionRewardAmount(template,kind,distance,rng,template.workHours*scale),",'reward call actual hours')
# Both offer and active-grant cards can display the ice factor, but it affects data value now, not cash.
count=s.count('ICE PREMIUM ×')
if count!=2: raise SystemExit(f'ice premium labels: expected 2, got {count}')
s=s.replace('ICE PREMIUM ×','ICE DATA VALUE ×')
once('Ice-capable expeditions receive strong sponsor premiums for work in thicker pack ice.','Ice-capable expeditions can produce especially valuable data in thicker pack ice.','port grant help')
p.write_text(s)
print('p23n polish applied')
