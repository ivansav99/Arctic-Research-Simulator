from pathlib import Path
src=Path('expedition.js').read_text(); game=Path('game.js').read_text()
def cut(text,needle,before,after):
 i=text.find(needle)
 return f'INDEX {i}\n'+(text[max(0,i-before):min(len(text),i+after)] if i>=0 else 'NOT FOUND')
out='===== RENDER =====\n'+cut(src,'renderResearchWindow',1000,18000)+'\n===== RESOURCE =====\n'+cut(game,'updateResourceWarning',2500,8000)+'\n===== EK80 =====\n'+cut(src,'ek80:',500,1500)
Path('p23o-inspect2.txt').write_text(out)
