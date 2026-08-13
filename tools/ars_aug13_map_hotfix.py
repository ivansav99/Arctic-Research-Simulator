from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)

# index.html: cache-bust the hotfix and keep an invisible legacy resume element
# so iOS cannot crash if it briefly pairs fresh HTML with an older cached game.js.
p = Path('index.html')
s = p.read_text()
s = s.replace('expedition-22m-phone2', 'expedition-22n-mapfix')
if 'id="resume-button"' not in s:
    s = replace_once(
        s,
        '          <button id="how-button" class="secondary" type="button">HOW TO PLAY</button>\n',
        '          <button id="how-button" class="secondary" type="button">HOW TO PLAY</button>\n          <button id="resume-button" class="hidden" type="button" aria-hidden="true" tabindex="-1"></button>\n',
        'legacy resume compatibility element'
    )
p.write_text(s)

# expedition.js: only show tab overflow hints when there is actually more content
# in that direction.
p = Path('expedition.js')
e = p.read_text()
if 'function updatePortTabHints(' not in e:
    helper = """  function updatePortTabHints(tabs) {
    if (!tabs) return;
    const viewport=tabs.closest('.arx-tabs-viewport'); if(!viewport) return;
    const left=viewport.querySelector('.arx-tab-hint.left'), right=viewport.querySelector('.arx-tab-hint.right');
    const max=Math.max(0,tabs.scrollWidth-tabs.clientWidth), epsilon=2;
    left?.classList.toggle('hidden',max<=epsilon||tabs.scrollLeft<=epsilon);
    right?.classList.toggle('hidden',max<=epsilon||tabs.scrollLeft>=max-epsilon);
  }
"""
    e = replace_once(e, '  function renderPort() {\n', helper + '\n  function renderPort() {\n', 'tab hint helper')
old = "    const card=modal.querySelector('.arx-port-card'), tabs=card.querySelector('.arx-tabs'); card.scrollTop=portScrollTop; tabs.scrollLeft=portTabsScrollLeft;\n"
new = "    const card=modal.querySelector('.arx-port-card'), tabs=card.querySelector('.arx-tabs'); card.scrollTop=portScrollTop; tabs.scrollLeft=portTabsScrollLeft;\n    const syncTabHints=()=>updatePortTabHints(tabs); tabs.addEventListener('scroll',syncTabHints,{passive:true}); requestAnimationFrame(syncTabHints);\n"
e = replace_once(e, old, new, 'tab hint scroll sync')
e = replace_once(e, '.arx-tab-hint{display:none;pointer-events:none}', '.arx-tab-hint{display:none;pointer-events:none;transition:opacity .12s ease}.arx-tab-hint.hidden{opacity:0!important;visibility:hidden!important}', 'tab hint hidden CSS')
p.write_text(e)

# game.js: the minimap is supplemental. A failure there must never terminate the
# primary map animation loop or prevent the player vessel from drawing.
p = Path('game.js')
g = p.read_text()
g = replace_once(
    g,
    'drawResearchGuidance();drawMiniMap();drawVessel();requestAnimationFrame(frame);}',
    "drawResearchGuidance();try{drawMiniMap();}catch(error){console.error('MINIMAP DRAW FAILED',error);}drawVessel();requestAnimationFrame(frame);}",
    'minimap frame isolation'
)
p.write_text(g)

print('ARS map/cache/tab hotfix applied')
