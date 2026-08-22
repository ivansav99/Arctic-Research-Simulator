from pathlib import Path
import re

src=Path('expedition.js').read_text()
game=Path('game.js').read_text()
parts=[]
for name,pattern,text in [
 ('renderResearchWindow',r'function renderResearchWindow\(target,options=\{\}\) \{.*?\n  \}\n  function openTarget',src),
 ('action-handler',r"else if \(action==='accept'.*?else if \(action==='publish'\) publishPaper\(\);",src),
 ('root-style',r"root\.innerHTML=.*?style\.textContent\+=`[\s\S]*?`;",src),
 ('resource-warning',r'function updateResourceWarning\(\)\{.*?\}',game),
 ('resource-update-near',r'ui\.fuelLevel\.style\.width=.*?updateResourceWarning\(\);',game),
]:
 m=re.search(pattern,text,re.S)
 parts.append(f'===== {name} =====\n'+(m.group(0) if m else 'NOT FOUND')+'\n')
Path('p23o-inspect.txt').write_text('\n'.join(parts))
