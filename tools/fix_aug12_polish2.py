from pathlib import Path
p=Path('tools/ars_aug12_polish2.py')
s=p.read_text()
s=s.replace("const player=playerScientist();if(target?.anyScientist)return player?[player.id]:[];\n    const specialistIds=specialistAssignment(target).ids||[],ids=[...specialistIds];\n    const candidates=state.scientists.filter(item=>(target.specialties||[]).includes(item.specialty)).sort((a,b)=>careerLevel(b.career)-careerLevel(a.career));", "const player=playerScientist(),requiredLevel=templateCareerLevel(target);if(target?.anyScientist)return player?[player.id]:[];\n    const specialistIds=specialistAssignment(target).ids||[],ids=[...specialistIds];\n    const candidates=state.scientists.filter(item=>(target.specialties||[]).includes(item.specialty)&&careerLevel(item.career)>=requiredLevel).sort((a,b)=>careerLevel(b.career)-careerLevel(a.career));")
s=s.replace("e=replace_block(e,'  function participantIdsFor(target) {','  function workRate',participant_block,'participant selection')", "e=replace_block(e,'  function participantIdsFor(target) {','  function creditSpecialtyMission',participant_block,'participant selection')")
p.write_text(s)
