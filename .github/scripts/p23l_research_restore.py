from pathlib import Path

EXP=Path('expedition.js'); INDEX=Path('index.html')
exp=EXP.read_text(); index=INDEX.read_text()

def once(text, old, new, label):
    n=text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, got {n}')
    return text.replace(old,new,1)

# A previous gameplay edit accidentally removed the shared mission-capability
# helper block while leaving its callers throughout grant + opportunity logic.
# Restore the helpers from the last known-good implementation.
for missing in ['templateCareerLevel','missionMinCrew','templateRelativeReward','missionSpecialistRequirements','expandedSpecialistNeeds','specialistAssignment','specialistRequirementsMet','missionFitsCurrentVessel']:
    if f'function {missing}' in exp:
        raise SystemExit(f'{missing} already exists; refusing duplicate restore')

anchor="  function payroll() { return state.scientists.reduce((sum,item) => sum + (CAREERS[item.career]?.salary || 0), 0); }"
helpers=r'''  function templateCareerLevel(template) {
    let level=1; for (const id of [...(template.equipment||[]),...(template.consumables||[])]) level=Math.max(level,EQUIPMENT[id]?.tier||1); return Math.min(3,level);
  }
  function missionMinCrew(template) {
    const title=String(template?.title||'').toLowerCase();
    if ((template?.berthReserve||0)>0 && (template?.stationDelivery||template?.anyScientist||/deliver|transport|supply|field team|team deployment/.test(title))) return 1;
    const explicit=Number(template?.minCrew); if(Number.isFinite(explicit)&&explicit>0)return Math.max(1,Math.round(explicit));
    const level=templateCareerLevel(template),bounds={1:[1,3],2:[3,10],3:[10,20]}[level]||[1,3];
    const rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level).map(item=>Number(item.reward)||0).filter(value=>value>0);
    const low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low,reward=Math.max(low,Number(template?.reward)||low),t=high>low?clamp((reward-low)/(high-low),0,1):0;
    return Math.round(bounds[0]+(bounds[1]-bounds[0])*t);
  }
  function templateRelativeReward(template) {
    const level=templateCareerLevel(template),rewards=TEMPLATES.filter(item=>templateCareerLevel(item)===level&&!item.weather).map(item=>Number(item.reward)||0).filter(Boolean),low=rewards.length?Math.min(...rewards):0,high=rewards.length?Math.max(...rewards):low;
    return high>low?clamp(((Number(template?.reward)||low)-low)/(high-low),0,1):0;
  }
  function missionSpecialistRequirements(template) {
    if(Array.isArray(template?.specialistRequirements))return clone(template.specialistRequirements);
    if(template?.anyScientist)return [];
    const level=templateCareerLevel(template),specialties=[...new Set(template?.specialties||[])];
    if(level<2||specialties.length<2)return [];
    const relative=templateRelativeReward(template),seed=[...String(template?.id||template?.title||'')].reduce((sum,ch)=>(sum*31+ch.charCodeAt(0))>>>0,17),interdisciplinary=relative>=.42&&(seed%100)<(level>=3?62:42);
    if(!interdisciplinary)return [];
    const count=level>=3&&specialties.length>=3&&relative>=.7&&(seed%3!==1)?3:2,minCareer=level>=3?'professor':'postdoc';
    return specialties.slice(0,count).map(specialty=>({specialties:[specialty],minCareer,count:1}));
  }
  function expandedSpecialistNeeds(template) {
    const needs=[];for(const requirement of missionSpecialistRequirements(template))for(let i=0;i<(requirement.count||1);i++)needs.push(requirement);return needs;
  }
  function specialistAssignment(template) {
    const needs=expandedSpecialistNeeds(template);if(!needs.length)return {missing:0,ids:[]};let best=[];
    const walk=(index,used,ids)=>{if(index>=needs.length){if(ids.length>best.length)best=[...ids];return;}walk(index+1,used,ids);const need=needs[index];for(const scientist of state.scientists){if(used.has(scientist.id)||careerLevel(scientist.career)<careerLevel(need.minCareer)||!(need.specialties||[]).includes(scientist.specialty))continue;used.add(scientist.id);ids.push(scientist.id);walk(index+1,used,ids);ids.pop();used.delete(scientist.id);}};walk(0,new Set(),[]);return {missing:Math.max(0,needs.length-best.length),ids:best};
  }
  function specialistRequirementsMet(template) { return specialistAssignment(template).missing===0; }
  function missionFitsCurrentVessel(template,ship=vessel()) { return missionMinCrew(template)+Math.max(0,Number(template?.berthReserve)||0)<=ship.berths; }
  function vesselRewardScale(ship=vessel()) {
    const starter=VESSELS.fishing,baseCapital=Math.max(1,vesselPurchasePrice(starter)||120000),capital=Math.max(baseCapital,vesselPurchasePrice(ship)||ship.marketPrice||baseCapital);
    const operatingCost=s=>Math.max(1,(s.nuclearFuel?0:s.fuelCapacity*s.fuelUnitCost)+s.foodCapacity*s.foodUnitCost+s.supplyCapacity*250),baseOperating=operatingCost(starter),operating=operatingCost(ship);
    const capitalIndex=1+Math.max(0,Math.log10(capital/baseCapital))*1.35,operatingIndex=1+Math.max(0,Math.log10(operating/baseOperating))*.9;
    return clamp(capitalIndex*.7+operatingIndex*.3,1,12);
  }
'''
exp=once(exp,anchor,helpers+anchor,'restore research helper block')

# Put the intended vessel economics multiplier back now that the helper exists.
exp=once(exp,
"    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03);",
"    const scale=.88+rng()*.26, vesselScale=DATA_SCALE_BY_VESSEL[state.currentVessel]||3, crewScale=1+Math.min(.5,Math.max(0,state.scientists.length-1)*.03), rewardScale=vesselRewardScale();",
'restore reward scale local')
exp=once(exp,
"reward:Math.round(template.reward*scale*(kind === 'opportunity'||kind==='weather-opportunity' ? 1.6 : 2)*iceValueMultiplier)",
"reward:Math.round(template.reward*scale*(kind === 'opportunity'||kind==='weather-opportunity' ? 1.6 : 2)*iceValueMultiplier*rewardScale)",
'restore reward scale use')

index=once(index,'expedition.js?v=expedition-23k-port-grants','expedition.js?v=expedition-23l-research','research cache bust')

EXP.write_text(exp); INDEX.write_text(index)
