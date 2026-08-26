from pathlib import Path
p=Path('expedition.js'); s=p.read_text();
old='?v=23ac'; count=s.count(old)
if count != 4: raise SystemExit(f'expected four vessel cache refs, found {count}')
p.write_text(s.replace(old,'?v=23ae'))
ip=Path('index.html'); h=ip.read_text(); oldv='expedition-23ac-grant-clarity-images'; count=h.count(oldv)
if count < 3: raise SystemExit(f'expected cache version in index, found {count}')
ip.write_text(h.replace(oldv,'expedition-23ae-grant-clarity-images'))
print('23ae cache bump applied')
