from pathlib import Path

source=Path('.github/ars-23v-patch.py').read_text()
marker='# Cache bust the modified scripts for the live Pages build.'
if marker not in source:
    raise SystemExit('23v patch marker missing')
source=source.split(marker,1)[0]
source += """
# Cache bust all modified script references for the live Pages build.
p=Path('index.html')
text=p.read_text()
old='expedition-23u-field-opportunity-audio'
if old not in text:
    raise SystemExit('23u cache version missing')
p.write_text(text.replace(old,'expedition-23v-grants-wildlife-no-fast-ice'))
print('ARS 23v corrected patch applied')
"""
exec(compile(source,'.github/ars-23v-patch2-generated.py','exec'))
