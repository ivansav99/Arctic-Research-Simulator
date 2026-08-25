from pathlib import Path
import re

source = Path('.github/ars-23t-patch.py').read_text()
source, count = re.subn(
    r"# Active grants also visibly grey out when equipment/crew capability is lost\..*?# Hard acceptance guard:",
    "# Active grant cards already report CAPABILITY CURRENTLY MISSING; map and arrow greying is handled in game.js.\n\n# Hard acceptance guard:",
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f'patch2 source adjustment: expected 1 block, found {count}')
exec(compile(source, '.github/ars-23t-patch2-expanded.py', 'exec'), {'__name__': '__main__'})
