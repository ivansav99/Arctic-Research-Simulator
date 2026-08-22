from pathlib import Path

src=Path('expedition.js').read_text()
game=Path('game.js').read_text()
parts=[]

def around(text, needle, before=1500, after=9000):
    i=text.find(needle)
    if i<0:return 'NOT FOUND'
    return text[max(0,i-before):min(len(text),i+after)]

parts.append('===== renderResearchWindow =====\n'+around(src,'function renderResearchWindow',500,15000))
parts.append('\n===== openTarget/actions =====\n'+around(src,'function openTarget',500,10000))
parts.append('\n===== root/toggles =====\n'+around(src,'root.innerHTML=',300,5000))
parts.append('\n===== updateResourceWarning =====\n'+around(game,'updateResourceWarning',1500,5000))
parts.append('\n===== fuel width calls =====\n'+around(game,"ui.fuelLevel.style.width",1500,5000))
Path('p23o-inspect.txt').write_text('\n'.join(parts))
