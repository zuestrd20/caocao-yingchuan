from pathlib import Path
from fontTools import subset
root=Path(__file__).resolve().parents[1]
texts=''.join(p.read_text() for p in root.rglob('*.gd'))+''.join(chr(i) for i in range(32,127))
opts=subset.Options(font_number=3)
f=subset.load_font('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',opts)
s=subset.Subsetter();s.populate(text=texts);s.subset(f)
subset.save_font(f,str(root/'assets/font.otf'),opts)
