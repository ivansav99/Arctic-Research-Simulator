from pathlib import Path
p=Path('expedition.js')
s=p.read_text()
old="    const science=names.length?`${names.join(names.length>2?', ':names.length===2?' & ':'')}${names.length>2?` & ${names.pop()}`:''} made this opportunity possible with ${fields.join(' / ')||'the science team'} expertise.`:`Your science team made this opportunity possible.`;"
new="    const scientistNames=names.length>2?`${names.slice(0,-1).join(', ')} & ${names.at(-1)}`:names.join(' & ');\n    const science=scientistNames?`${scientistNames} made this opportunity possible with ${fields.join(' / ')||'the science team'} expertise.`:`Your science team made this opportunity possible.`;"
if s.count(old)!=1: raise SystemExit(f'expected exactly one scientist sentence, found {s.count(old)}')
p.write_text(s.replace(old,new,1))
print('23ad opportunity copy fix applied')
