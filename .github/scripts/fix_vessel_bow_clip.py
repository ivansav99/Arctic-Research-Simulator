from pathlib import Path

p=Path('game.js')
s=p.read_text()
old="""      ctx.beginPath();
      ctx.moveTo(-shoulder,top);ctx.lineTo(shoulder,top);ctx.lineTo(right,top+cut);ctx.lineTo(right,bottom);ctx.lineTo(left,bottom);ctx.lineTo(left,top+cut);ctx.closePath();ctx.clip();"""
new="""      ctx.beginPath();
      // Atlas vessel art is authored bow-down and rotated PI by the caller.
      // Trim the source-image bottom corners so the displayed bow is chamfered.
      ctx.moveTo(left,top);ctx.lineTo(right,top);ctx.lineTo(right,bottom-cut);ctx.lineTo(shoulder,bottom);ctx.lineTo(-shoulder,bottom);ctx.lineTo(left,bottom-cut);ctx.closePath();ctx.clip();"""
if s.count(old)!=1:
    raise SystemExit(f'expected one bow clip block, found {s.count(old)}')
p.write_text(s.replace(old,new))
print('Corrected bow-side clipping mask')
