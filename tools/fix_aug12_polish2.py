from pathlib import Path
p=Path('tools/ars_aug12_polish2.py')
s=p.read_text()
s=s.replace("const player=playerScientist();if(target?.anyScientist)return player?[player.id]:[];\n    const specialistIds=specialistAssignment(target).ids||[],ids=[...specialistIds];\n    const candidates=state.scientists.filter(item=>(target.specialties||[]).includes(item.specialty)).sort((a,b)=>careerLevel(b.career)-careerLevel(a.career));", "const player=playerScientist(),requiredLevel=templateCareerLevel(target);if(target?.anyScientist)return player?[player.id]:[];\n    const specialistIds=specialistAssignment(target).ids||[],ids=[...specialistIds];\n    const candidates=state.scientists.filter(item=>(target.specialties||[]).includes(item.specialty)&&careerLevel(item.career)>=requiredLevel).sort((a,b)=>careerLevel(b.career)-careerLevel(a.career));")
s=s.replace("e=replace_block(e,'  function participantIdsFor(target) {','  function workRate',participant_block,'participant selection')", "e=replace_block(e,'  function participantIdsFor(target) {','  function creditSpecialtyMission',participant_block,'participant selection')")
lines=[]
for line in s.splitlines():
    if "'wildlife data reward')" in line:
        lines.append("e=replace_once(e,\"if (firstIndividual) { state.observedIndividuals.push(individualId); addData(2); addLog(`${item.displayName} observation archived · +2 data.`); }\",\"if (firstIndividual) { const wildlifeData=wildlifeObservationData(); state.observedIndividuals.push(individualId); addData(wildlifeData); addLog(`${item.displayName} observation archived · +${wildlifeData} data.`); }\",'wildlife data reward')")
    elif "'wildlife modal data text')" in line:
        lines.append("e=replace_once(e,\"${firstIndividual?'OBSERVATION ARCHIVED · +2 DATA':'THIS INDIVIDUAL ALREADY OBSERVED · +0 DATA'}\",\"${firstIndividual?`OBSERVATION ARCHIVED · +${wildlifeObservationData()} DATA`:'THIS INDIVIDUAL ALREADY OBSERVED · +0 DATA'}\",'wildlife modal data badge')")
        lines.append("e=replace_once(e,\"${firstIndividual?'A new individual observation added exactly 2 data points. Its glowing chart ring is now cleared.':'This is the same animal or school already recorded during this expedition, so no additional data were added.'}\",\"${firstIndividual?`A new individual observation added ${wildlifeObservationData()} data points. Its glowing chart ring is now cleared.`:'This is the same animal or school already recorded during this expedition, so no additional data were added.'}\",'wildlife modal data text')")
    else:
        lines.append(line)
p.write_text('\n'.join(lines)+'\n')
