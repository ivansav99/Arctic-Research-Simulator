from pathlib import Path

source=Path('.github/ars-23u-patch.py').read_text()
old="""replace_once(
    'game.js',
    \"if(d<=27&&d<best){best=d;hit={target,distance:item.distance};}\",
    \"if(d<=36&&d<best){best=d;hit={target,distance:item.distance};}\",
    'research marker tap radius'
)"""
new="""replace_once(
    'game.js',
    \"function nearbyResearchTargetAt(clientX,clientY){let match=null,best=27;\",
    \"function nearbyResearchTargetAt(clientX,clientY){let match=null,best=36;\",
    'research marker tap radius'
)"""
if old not in source:
    raise SystemExit('Could not find old research marker matcher in 23u patch script')
source=source.replace(old,new,1)
exec(compile(source,'.github/ars-23u-patch.py','exec'))
