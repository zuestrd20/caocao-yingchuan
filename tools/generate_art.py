#!/usr/bin/env python3
"""Original, hand-constructed pixel artwork for Cao Cao: First Battle.
All source geometry and palettes are original. No external artwork is used.
Run with Python 3 + Pillow. Nearest-neighbour rendering is intentional.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random, json, math, argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, help='Generate the legacy pixel pack into a separate directory for reference.')
args=parser.parse_args()
A=args.output_dir.resolve() if args.output_dir else ROOT/'assets'
if (A/'sources'/'chibi'/'layout.json').exists():
 raise SystemExit('Protected Q-version character artwork: run tools/import_chibi_art.py to rebuild it. To inspect the legacy pixel pack, use --output-dir /tmp/yingchuan-legacy (not assets).')
for sub in ('terrain','units','portraits','previews'):(A/sub).mkdir(exist_ok=True,parents=True)
P={
 'ink':'#20282c','deep':'#263f36','grass':'#788653','g1':'#89955d','g2':'#647347','g3':'#9ba369','g4':'#bac080',
 'forest':'#344f37','leaf':'#466343','leaf2':'#607b46','leaf3':'#829450','bark':'#665644','barklight':'#92754a',
 'dirt':'#b7a06c','dirtlight':'#c9b37d','dirtshade':'#9c885d','stone':'#8d9084','stone2':'#b3b2a0','stoneshadow':'#646e65',
 'water':'#477883','waterdark':'#3d6678','waterlight':'#659598','foam':'#a5b9a8',
 'gold':'#d9b96b','goldshade':'#a47b43','cream':'#e5d5a4','red':'#9a4f44','redlight':'#bc6652','blue':'#496578','bluelight':'#728c94',
 'skin':'#d5ab7d','skinlight':'#ebc291','skinshadow':'#a67c5c','black':'#293038','white':'#efdfb6'}
def canvas(size=(32,32),color=None):
 im=Image.new('RGBA',size,color or (0,0,0,0));return im,ImageDraw.Draw(im)
def grass(seed=0):
 im,d=canvas(color=P['grass']);r=random.Random(111+seed)
 for _ in range(68):
  x,y=r.randrange(32),r.randrange(32);c=r.choice([P['g1'],P['g2'],P['g3']]);d.line((x,y,x+r.randrange(1,3),y),fill=c)
 for x,y in [(4,6),(25,3),(20,23),(7,28)]:
  d.point((x,y-1),fill=P['g3']);d.line((x-1,y,x+1,y),fill=P['g2'])
 return im

def tree(d,x,y,s=1):
 # Unmistakable tiered Chinese mountain pine, compact top-down silhouette.
 d.ellipse((x-6*s,y+4*s,x+7*s,y+8*s),fill=P['g2'])
 d.rectangle((x-1*s,y-1*s,x+1*s,y+7*s),fill=P['bark'])
 d.line((x,y+2*s,x,y+6*s),fill=P['barklight'])
 for yy,ww in [(y,7*s),(y-4*s,6*s),(y-8*s,4*s)]:
  d.polygon([(x,yy-5*s),(x-ww,yy+3*s),(x-ww+2*s,yy+5*s),(x+ww,yy+4*s)],fill=P['forest'])
  d.polygon([(x,yy-4*s),(x-ww+1*s,yy+2*s),(x-1*s,yy+2*s),(x+3*s,yy)],fill=P['leaf'])
  d.line((x-ww+3*s,yy+1*s,x-2*s,yy+1*s),fill=P['leaf2'])
  d.point((x-1*s,yy-2*s),fill=P['leaf3'])

def roof(d,box):
 x,y,w,h=box
 d.polygon([(x+2,y+h),(x+5,y+3),(x+w-5,y+3),(x+w-2,y+h),(x+w,y+h-1),(x+w-1,y+h+2),(x,y+h+2),(x-1,y+h-1)],fill=P['ink'])
 d.polygon([(x+5,y+3),(x+w-5,y+3),(x+w-1,y+h),(x+1,y+h)],fill=P['blue'])
 d.line((x+4,y+3,x+w-4,y+3),fill=P['bluelight'])
 d.line((x+2,y+h-1,x+w-2,y+h-1),fill=P['bluelight'])
 for xx in range(x+4,x+w-3,3):d.line((xx,y+4,xx-1,y+h-2),fill='#3a505d')
 d.line((x+3,y+1,x+w-3,y+1),fill=P['cream']);d.point((x+2,y),fill=P['cream']);d.point((x+w-2,y),fill=P['cream'])

def terrain(name):
 im=grass();d=ImageDraw.Draw(im)
 if name=='road':
  d.polygon([(7,0),(27,0),(26,7),(32,11),(32,26),(24,25),(24,32),(6,32),(7,25),(0,24),(0,8),(8,8)],fill=P['dirtshade'])
  d.polygon([(10,0),(24,0),(23,11),(32,13),(32,22),(21,22),(21,32),(9,32),(10,22),(0,21),(0,11),(11,11)],fill=P['dirt'])
  for x,y in [(12,4),(17,8),(4,15),(14,15),(25,16),(13,25),(19,30)]:d.line((x,y,x+2,y),fill=P['dirtlight'])
  for x,y in [(8,3),(29,23),(5,20),(23,28)]:d.point((x,y),fill=P['barklight'])
 elif name=='forest':
  tree(d,9,17);tree(d,23,16);tree(d,16,25)
 elif name=='mountain':
  d.ellipse((1,25,30,31),fill=P['g2'])
  d.polygon([(1,27),(8,8),(11,13),(17,1),(23,13),(25,10),(31,27),(25,30),(8,30)],fill=P['stoneshadow'])
  d.polygon([(3,26),(8,9),(10,15),(17,3),(18,14),(14,24),(16,28),(8,29)],fill=P['stone'])
  d.polygon([(17,3),(18,14),(21,19),(20,24),(25,29),(30,26),(24,14),(22,17)],fill='#737d70')
  d.polygon([(8,9),(6,18),(9,16),(11,18),(17,3),(14,15),(17,13),(18,8)],fill=P['stone2'])
  d.line((18,14,15,23),fill='#505f59');d.line((24,16,27,24),fill=P['stone'])
  d.line((6,25,10,23),fill=P['g1']);d.line((21,28,25,27),fill=P['g2'])
 elif name in ('river','bridge'):
  d.rectangle((0,0,31,31),fill=P['water'])
  for y in range(2,32,7):
   for x in range(-4+(y%3)*2,33,13):
    d.line((x,y,x+7,y),fill=P['waterdark']);d.line((x+2,y+1,x+9,y+1),fill=P['waterlight'])
    d.line((x+4,y+2,x+7,y+2),fill=P['waterlight'])
  for x,y in [(4,5),(23,12),(12,25)]:d.line((x,y,x+3,y),fill=P['foam'])
  if name=='bridge':
   d.rectangle((0,8,31,25),fill='#344953');d.rectangle((0,8,31,22),fill='#815f40')
   for x in range(0,32,4):
    d.rectangle((x,9,x+2,21),fill='#b39461');d.line((x,10,x,20),fill='#ccac71');d.point((x+1,13),fill='#8f6f47')
   for yy in (7,22):
    d.rectangle((0,yy,31,yy+1),fill=P['bark']);d.line((0,yy,31,yy),fill=P['cream'])
    for xx in (2,12,22,30):d.rectangle((xx-1,yy-2,xx,yy+2),fill=P['barklight']);d.point((xx-1,yy-2),fill=P['cream'])
 elif name=='village_house':
  d.ellipse((1,20,30,31),fill=P['g2']);d.rectangle((6,14,26,26),fill='#62594a')
  d.rectangle((7,14,25,24),fill=P['cream']);d.rectangle((15,19,19,26),fill='#574c41')
  d.rectangle((9,18,12,21),fill=P['blue']);d.line((10,18,10,21),fill=P['barklight'])
  d.rectangle((22,17,24,21),fill='#bea57b');d.line((7,24,25,24),fill=P['barklight'])
  roof(d,(3,4,25,10));d.line((7,15,7,25),fill=P['red']);d.line((25,15,25,25),fill=P['red'])
  d.rectangle((13,26,21,28),fill=P['dirt']);d.line((14,27,20,27),fill=P['dirtlight'])
  d.rectangle((1,22,4,25),fill=P['bark']);d.rectangle((2,19,3,22),fill=P['leaf2'])
  d.ellipse((27,22,30,26),fill=P['leaf']);d.point((28,22),fill=P['leaf3'])
 elif name in ('village','tent','storehouse'):
  large=name=='storehouse'
  # Canvas campaign tent, guy ropes and central dark entrance.
  d.ellipse((1,23,30,31),fill=P['g2'])
  x1,x2=(3,28) if large else (6,26)
  apex=7 if large else 9
  d.polygon([(x1,26),(x1+2,14),(16,apex),(x2-2,14),(x2,26)],fill='#4b4936')
  d.polygon([(x1+2,24),(x1+4,15),(16,apex+1),(16,25)],fill='#bc9d61')
  d.polygon([(16,apex+1),(x2-4,15),(x2-2,24),(16,25)],fill='#967b4d')
  d.polygon([(16,apex+2),(12,24),(20,24)],fill='#544b36')
  d.polygon([(16,apex+2),(15,23),(19,24)],fill='#76613f')
  d.line((x1+4,15,16,apex+1,x2-4,15),fill='#d8bb78')
  d.line((x1+2,24,11,24),fill='#d8bb78');d.line((21,24,x2-2,24),fill='#b3955e')
  d.line((x1+3,16,1,27),fill='#d5c18a');d.line((x2-3,16,30,27),fill='#d5c18a')
  d.rectangle((0,26,2,28),fill=P['bark']);d.rectangle((29,26,31,28),fill=P['bark'])
  d.line((16,6,16,apex),fill=P['barklight'])
  if large:
   d.rectangle((4,24,9,28),fill='#806441');d.rectangle((4,24,9,25),fill='#b99b62');d.line((6,25,6,28),fill='#d1b375')
   d.rectangle((23,23,27,28),fill='#765b3d');d.line((23,25,27,25),fill='#b89962');d.point((25,23),fill='#c5a668')
  else:
   d.polygon([(17,6),(23,7),(21,10),(17,9)],fill='#b7a358')
 elif name in ('wall','wall_vertical'):
  # Wooden palisades tile seamlessly horizontally; vertical variant included.
  d.rectangle((0,24,31,28),fill=P['g2'])
  for x in range(0,32,4):
   d.polygon([(x,9),(x+1,6),(x+2,9),(x+2,26),(x,26)],fill='#4e4a35')
   d.rectangle((x,10,x+1,24),fill='#987849');d.line((x,9,x,23),fill='#c0a16a')
   d.point((x+1,14),fill='#735b3c')
  for y in (14,22):
   d.line((0,y,31,y),fill='#65553b');d.line((0,y+1,31,y+1),fill='#ae905a')
   for x in range(1,32,4):d.point((x,y),fill='#d5ba80')
  if name=='wall_vertical': im=im.transpose(Image.Transpose.ROTATE_90)
 elif name=='fort':
  d.ellipse((0,24,31,31),fill=P['g2']);d.rectangle((2,15,29,28),fill=P['stoneshadow']);d.rectangle((3,16,28,25),fill=P['stone'])
  for y in (18,22,26):
   d.line((3,y,28,y),fill=P['stoneshadow'])
   for x in range(4+(y%8),29,7):d.line((x,y-3,x,y),fill=P['stoneshadow'])
  for x in (2,6,10,21,25,29):d.rectangle((x-1,13,x+1,17),fill=P['stone2'])
  d.rectangle((12,18,20,28),fill=P['ink']);d.rectangle((13,20,19,27),fill=P['bark']);d.line((16,20,16,27),fill=P['goldshade'])
  d.rectangle((9,7,23,16),fill=P['red']);roof(d,(7,1,18,8))
  d.rectangle((11,12,13,14),fill=P['ink']);d.rectangle((19,12,21,14),fill=P['ink'])
  d.line((27,2,27,13),fill=P['bark']);d.polygon([(28,2),(32,3),(31,7),(28,6)],fill=P['redlight'])
 return im

TERRAINS=['grass','road','forest','mountain','river','bridge','village','fort','wall','tent','storehouse']
for i,n in enumerate(TERRAINS):terrain(n).save(A/'terrain'/f'{n}.png')
for n in ('village_house','wall_vertical'):terrain(n).save(A/'terrain'/f'{n}.png')
# Gentle alternate grass tiles break repetition without changing readability.
for i in range(1,4):grass(i).save(A/'terrain'/f'grass_{i}.png')

CHARS={
'caocao':dict(name='曹操',main='#416377',light='#72939d',dark='#293f50',cape='#934d49',skin='#d7ad80',beard='#34323a',hat='crown',weapon='sword',mounted=True,horse='#805d45',accent='#e1bc6a'),
'blue_soldier':dict(name='官军',main='#466b81',light='#86a1a7',dark='#2e465b',cape='#516c81',skin='#cda57a',beard='#483a31',hat='helmet',weapon='spear',mounted=False,accent='#d4b775'),
'liubei':dict(name='刘备',main='#55775c',light='#91a171',dark='#344d40',cape='#dbd3aa',skin='#dcb38a',beard='#493b32',hat='cap',weapon='swords',mounted=False,accent='#dfc77f'),
'guanyu':dict(name='关羽',main='#3f745c',light='#75a178',dark='#234c42',cape='#274e47',skin='#bf785d',beard='#282e2e',hat='green',weapon='glaive',mounted=True,horse='#a46b49',accent='#d6b765'),
'zhangfei':dict(name='张飞',main='#516a77',light='#87959a',dark='#2b424e',cape='#744a43',skin='#bb8c68',beard='#282c30',hat='band',weapon='serpent',mounted=False,accent='#d2ae61'),
'yellow_soldier':dict(name='黄巾兵',main='#a18c46',light='#d8bd62',dark='#6f633e',cape='#9b8447',skin='#c79d71',beard='#4e4133',hat='yellow',weapon='spear',mounted=False,accent='#e7ca69'),
'zhangbao':dict(name='张宝',main='#796782',light='#ab90a1',dark='#493f60',cape='#beb065',skin='#cab088',beard='#4b3834',hat='priest',weapon='staff',mounted=False,accent='#e0bf5f'),
'zhangliang':dict(name='张梁',main='#a47846',light='#d4a666',dark='#71503b',cape='#8a453d',skin='#bf956d',beard='#3d302c',hat='yellow',weapon='sword',mounted=False,accent='#dec064'),
}

def weapon(d,c,mounted=False):
 w=c['weapon'];x=38
 if w in ('spear','glaive','serpent','staff'):
  d.line((x,6,x-4,39),fill=P['ink'],width=3);d.line((x,6,x-4,39),fill='#b79d66',width=1)
  if w=='glaive':
   d.polygon([(39,2),(44,5),(43,11),(39,15),(37,13),(39,9),(37,6)],fill=P['ink']);d.polygon([(39,3),(43,5),(42,10),(39,12),(40,8)],fill='#c5d1be');d.line((39,4,41,7),fill='#edecd0')
   d.line((37,14,42,16),fill='#a55447',width=2)
  elif w=='serpent':
   d.line([(39,1),(36,4),(40,7),(37,10)],fill='#d5d4b3',width=2);d.point((39,1),fill=P['white'])
  elif w=='spear':
   d.polygon([(39,1),(36,7),(37,11),(39,9),(41,7)],fill=P['ink']);d.polygon([(39,2),(37,7),(39,8)],fill='#c1c9b1');d.line((37,11,41,13),fill='#ab6148',width=2)
  else:
   d.ellipse((35,1,41,7),fill=P['goldshade']);d.ellipse((36,2,40,6),fill=P['gold']);d.rectangle((37,7,39,10),fill='#a95647');d.line((38,0,38,2),fill=P['cream'])
 else:
  d.polygon([(34,25),(41,12),(43,11),(42,15),(36,28)],fill=P['ink']);d.polygon([(35,24),(41,13),(41,16),(36,26)],fill='#c8d1bb');d.line((33,25,38,28),fill=P['goldshade'],width=2);d.line((34,28,32,32),fill=P['barklight'],width=2)
  if w=='swords':
   d.polygon([(13,26),(7,15),(5,14),(7,20),(12,29)],fill=P['ink']);d.line((7,17,12,26),fill='#c8d1bb',width=2);d.line((10,28,15,26),fill=P['goldshade'],width=2)

def draw_horse(d,c):
 # The horse's head, forelegs and tack remain visible around the rider.
 h=c['horse'];hs='#4c4138';hl='#b08a60'
 d.polygon([(7,29),(4,32),(3,38),(5,38),(8,33)],fill=P['ink'])
 d.polygon([(8,29),(6,32),(6,35),(8,31)],fill=hs)
 for points in [[(11,33),(14,34),(13,42),(10,42)],[(19,34),(22,35),(23,42),(20,42)],[(31,33),(34,32),(35,41),(32,41)],[(36,31),(39,29),(41,40),(38,41)]]:
  d.polygon(points,fill=P['ink']);d.line((points[0][0]+1,points[0][1]+2,points[-1][0]+1,points[-1][1]-1),fill=h)
 d.polygon([(8,26),(14,23),(30,24),(34,17),(38,16),(42,19),(44,24),(41,26),(36,24),(35,31),(30,36),(14,36),(8,33)],fill=P['ink'])
 d.polygon([(9,27),(14,25),(30,26),(35,18),(38,18),(41,20),(42,24),(39,24),(36,22),(34,30),(29,34),(15,34),(10,32)],fill=h)
 d.line((12,26,27,26),fill=hl,width=2);d.line((33,23,36,19),fill=hl,width=2)
 d.polygon([(34,17),(34,13),(37,17),(40,17),(41,14),(42,19)],fill=P['ink'])
 d.point((39,20),fill=P['cream']);d.point((40,21),fill=P['ink']);d.line((38,23,42,24),fill=P['goldshade'])
 d.polygon([(16,26),(28,26),(29,33),(17,32)],fill=c['cape']);d.line((18,32,28,33),fill=c['accent']);d.line((24,25,23,35),fill=P['goldshade'])
 d.line((37,22,31,27,27,24),fill=P['cream'])

def head(d,c,cx,cy):
 # 11 x 13 head, three-quarter view.
 skin=c['skin'];hat=c['hat']
 d.polygon([(cx-5,cy-4),(cx+4,cy-4),(cx+5,cy+2),(cx+3,cy+6),(cx-2,cy+6),(cx-5,cy+2)],fill=P['ink'])
 d.polygon([(cx-4,cy-2),(cx+3,cy-2),(cx+4,cy+2),(cx+2,cy+5),(cx-2,cy+4),(cx-4,cy+1)],fill=skin)
 d.line((cx-2,cy-1,cx+1,cy-1),fill=P['skinlight']);d.point((cx+4,cy+1),fill=P['skinshadow'])
 d.line((cx-3,cy+1,cx-1,cy+1),fill=P['ink']);d.point((cx+2,cy+1),fill=P['ink']);d.point((cx,cy+2),fill=P['skinshadow'])
 if c['weapon'] in ('glaive','serpent'):
  d.polygon([(cx-3,cy+3),(cx+3,cy+3),(cx+3,cy+7),(cx,cy+12 if c['weapon']=='glaive' else cy+8),(cx-3,cy+7)],fill=c['beard'])
  d.line((cx,cy+5,cx,cy+8),fill='#45433a')
 else:
  d.line((cx-2,cy+4,cx+2,cy+4),fill=c['beard']);d.rectangle((cx-1,cy+5,cx+1,cy+6),fill=c['beard'])
 if hat=='crown':
  d.polygon([(cx-5,cy-3),(cx-4,cy-6),(cx+4,cy-6),(cx+5,cy-3)],fill=c['dark']);d.rectangle((cx-3,cy-9,cx+2,cy-5),fill=P['ink']);d.rectangle((cx-2,cy-8,cx+1,cy-6),fill=c['main']);d.line((cx-4,cy-3,cx+4,cy-3),fill=c['accent']);d.point((cx,cy-4),fill=P['cream'])
 elif hat=='helmet':
  d.polygon([(cx-5,cy-2),(cx-5,cy-6),(cx-2,cy-8),(cx+2,cy-8),(cx+5,cy-5),(cx+5,cy+2)],fill=c['dark']);d.polygon([(cx-4,cy-3),(cx-3,cy-6),(cx+2,cy-6),(cx+4,cy-3)],fill=c['main']);d.line((cx-3,cy-5,cx+2,cy-5),fill=c['light']);d.line((cx-5,cy-3,cx+5,cy-3),fill=c['accent']);d.line((cx,cy-7,cx,cy-4),fill=c['light'])
 elif hat=='green':
  d.polygon([(cx-5,cy-3),(cx-4,cy-7),(cx+1,cy-9),(cx+4,cy-6),(cx+4,cy-3)],fill=c['dark']);d.line((cx-4,cy-5,cx+3,cy-5),fill=c['light']);d.line((cx-4,cy-3,cx+3,cy-3),fill=c['accent'])
 elif hat=='priest':
  d.polygon([(cx-6,cy-3),(cx-3,cy-11),(cx+2,cy-11),(cx+5,cy-3)],fill=c['dark']);d.polygon([(cx-4,cy-4),(cx-2,cy-9),(cx+1,cy-9),(cx+3,cy-4)],fill=c['accent']);d.rectangle((cx-1,cy-8,cx,cy-4),fill='#885b45');d.line((cx-5,cy-3,cx+4,cy-3),fill=P['gold'])
 elif hat=='yellow':
  d.polygon([(cx-5,cy-3),(cx-4,cy-6),(cx,cy-8),(cx+4,cy-6),(cx+5,cy-2)],fill=c['dark']);d.polygon([(cx-5,cy-3),(cx-3,cy-6),(cx+3,cy-6),(cx+4,cy-3)],fill=c['accent']);d.line((cx-4,cy-4,cx+3,cy-4),fill='#f0d57d');d.polygon([(cx-5,cy-3),(cx-9,cy+1),(cx-7,cy+3),(cx-3,cy-2)],fill=c['accent'])
 elif hat=='band':
  d.polygon([(cx-6,cy-1),(cx-6,cy-5),(cx-3,cy-7),(cx+3,cy-6),(cx+5,cy-4),(cx+5,cy+1)],fill=P['black']);d.line((cx-5,cy-3,cx+4,cy-3),fill=c['accent'],width=2);d.rectangle((cx-1,cy-8,cx+1,cy-6),fill=P['black'])
 else:
  d.polygon([(cx-5,cy-3),(cx-3,cy-7),(cx+3,cy-6),(cx+4,cy-3)],fill=c['dark']);d.line((cx-4,cy-3,cx+4,cy-3),fill=c['accent']);d.rectangle((cx-1,cy-10,cx+1,cy-7),fill=P['black']);d.point((cx,cy-8),fill=c['accent'])

def unit(key,frame=0):
 c=CHARS[key];im,d=canvas((48,48));d.ellipse((7,39,40,45),fill=(24,34,28,85))
 mounted=c['mounted'];cx=22;cy=13 if mounted else 16
 if mounted:draw_horse(d,c)
 # Cape outlines give the figure a strong military silhouette.
 y=cy+6
 d.polygon([(cx-5,y-4),(cx-10,y+3),(cx-11,y+14),(cx-4,y+11),(cx+6,y+12),(cx+9,y+6),(cx+5,y-3)],fill=P['ink'])
 d.polygon([(cx-5,y-3),(cx-9,y+4),(cx-9,y+11),(cx-3,y+9),(cx+5,y+10),(cx+7,y+6),(cx+4,y-2)],fill=c['cape'])
 d.line((cx-7,y+1,cx-7,y+8),fill=c['light'])
 if not mounted:
  d.polygon([(cx-7,y+9),(cx+6,y+9),(cx+7,y+15),(cx-8,y+15)],fill=P['ink'])
  d.rectangle((cx-6,y+13,cx-2,y+18),fill=c['dark']);d.rectangle((cx+2,y+13,cx+6,y+18),fill=c['dark'])
  d.rectangle((cx-8,y+17,cx-2,y+19),fill=P['ink']);d.rectangle((cx+1,y+17,cx+7,y+19),fill=P['ink'])
 d.polygon([(cx-6,y-3),(cx+5,y-3),(cx+7,y+7),(cx+5,y+11),(cx-6,y+11),(cx-8,y+7)],fill=P['ink'])
 d.polygon([(cx-5,y-2),(cx+4,y-2),(cx+5,y+8),(cx-6,y+8)],fill=c['main'])
 # Lamellar plates at actual pixel level.
 for yy in range(y+1,y+8,3):
  d.line((cx-5,yy,cx+4,yy),fill=c['dark'])
  for xx in range(cx-4,cx+5,3):d.point((xx,yy+1),fill=c['light'])
 d.line((cx-5,y,cx+4,y),fill=c['light']);d.line((cx-6,y+8,cx+5,y+8),fill=c['accent'],width=2)
 d.rectangle((cx-1,y+7,cx+1,y+9),fill=P['gold']);d.point((cx,y+8),fill=P['cream'])
 # Angular shoulders and bracers.
 d.polygon([(cx-8,y-2),(cx-4,y-3),(cx-3,y+1),(cx-8,y+3),(cx-10,y+1)],fill=c['dark']);d.line((cx-8,y-1,cx-4,y-2),fill=c['accent'])
 d.polygon([(cx+4,y-3),(cx+8,y-1),(cx+10,y+3),(cx+6,y+4),(cx+4,y+1)],fill=c['main']);d.line((cx+5,y-2,cx+8,y),fill=c['light'])
 d.rectangle((cx+7,y+3,cx+10,y+7),fill=c['dark']);d.rectangle((cx+8,y+7,cx+10,y+9),fill=c['skin'])
 if mounted:
  d.polygon([(cx+2,y+7),(cx+7,y+10),(cx+6,y+16),(cx+2,y+16),(cx+3,y+11),(cx-1,y+10)],fill=c['dark']);d.line((cx+4,y+11,cx+4,y+14),fill=c['light']);d.rectangle((cx+2,y+15,cx+7,y+17),fill=P['ink'])
 weapon(d,c,mounted);head(d,c,cx,cy)
 if frame==1:
  # Separate idle frame: plume/tassel and shoulder glint shift subtly.
  d.point((cx+7,y),fill=P['cream']);d.point((cx+8,y),fill=c['light'])
 if frame==2:
  # Clean hit flash, preserving sprite alpha.
  overlay=Image.new('RGBA',im.size,(233,206,161,0));overlay.putalpha(im.getchannel('A').point(lambda x:80 if x else 0));im=Image.alpha_composite(im,overlay)
 return im

for k in CHARS:
 unit(k).save(A/'units'/f'{k}.png')
 strip=Image.new('RGBA',(144,48))
 for f in range(3):strip.alpha_composite(unit(k,f),(48*f,0))
 strip.save(A/'units'/f'{k}_sheet.png')

# Portraits are 64px original drawings displayed at clean integer 2x scale.
def portrait(key):
 c=CHARS[key];im,d=canvas((64,64),P['ink']);main=c['main'];light=c['light'];dark=c['dark'];skin=c['skin'];hat=c['hat'];beard=c['beard']
 # Restrained tapestry ground, silhouette, and double brass frame.
 d.rectangle((2,2,61,61),fill='#233b3a');d.rectangle((3,3,60,60),outline='#596d58')
 for y in range(5,60,7):
  for x in range(5,60,7):
   d.line([(x,y+2),(x+2,y),(x+4,y+2)],fill='#2b4441')
 d.polygon([(5,59),(9,43),(21,36),(41,36),(55,44),(61,59)],fill=P['ink'])
 d.polygon([(6,59),(11,44),(23,39),(39,39),(53,45),(59,60)],fill=c['cape'])
 d.polygon([(16,43),(22,38),(40,38),(49,45),(51,60),(12,60)],fill=dark)
 d.polygon([(21,42),(29,45),(38,41),(45,46),(45,60),(18,60)],fill=main)
 # Raised lamellar chest plates.
 for yy in range(47,61,4):
  d.line((18,yy,45,yy),fill=dark)
  for xx in range(19,45,5):
   d.line((xx,yy+1,xx,yy+3),fill=light);d.point((xx+2,yy+1),fill=c['accent'])
 d.polygon([(9,43),(17,40),(23,45),(20,49),(10,49)],fill=main);d.line((10,43,17,41,22,45),fill=c['accent'],width=2)
 d.polygon([(41,43),(49,41),(55,46),(54,50),(44,49)],fill=main);d.line((42,43,49,42,54,46),fill=c['accent'],width=2)
 d.line((17,50,12,59),fill=light);d.line((49,50,54,59),fill=dark)
 # Neck and collar.
 d.polygon([(26,33),(38,32),(39,40),(32,46),(24,41)],fill='#987153');d.polygon([(27,35),(36,34),(36,41),(31,43),(27,40)],fill=skin)
 d.polygon([(22,37),(30,43),(26,48),(20,42)],fill=P['cream']);d.polygon([(39,37),(32,43),(35,47),(43,42)],fill=c['accent'])
 # Individual head silhouette, asymmetry and firm face planes.
 broad=key=='zhangfei';left=20 if broad else 22;right=43 if broad else 41
 d.polygon([(left+2,15),(left+6,11),(right-6,11),(right-2,15),(right,26),(right-2,34),(35,40),(28,39),(left+1,33),(left-1,24)],fill=P['ink'])
 d.polygon([(left+2,17),(left+6,14),(right-6,14),(right-2,18),(right-1,27),(right-4,35),(34,38),(28,36),(left+2,31)],fill=skin)
 d.polygon([(left+3,18),(left+7,15),(32,15),(31,22),(28,26),(29,31),(26,32),(left+3,28)],fill=P['skinlight'] if key!='guanyu' else '#d89370')
 d.polygon([(36,16),(right-2,19),(right-1,28),(right-4,34),(34,36),(33,32),(37,27)],fill='#aa7758' if key!='guanyu' else '#914d42')
 d.rectangle((left-1,23,left+1,28),fill=P['skinshadow']);d.rectangle((right-1,23,right+1,28),fill=P['skinshadow']);d.point((right,24),fill=skin)
 # Heavy expressive brows, narrow eyes, angular nose.
 brow_y=23 if broad else 22
 d.line((left+3,brow_y+1,left+8,brow_y),fill=beard,width=2);d.line((34,brow_y,right-3,brow_y+1),fill=beard,width=2)
 if broad:
  d.rectangle((left+4,25,left+8,26),fill='#f4dfb1');d.point((left+7,25),fill=P['ink']);d.rectangle((35,25,39,26),fill='#f4dfb1');d.point((36,25),fill=P['ink'])
 else:
  d.line((left+4,25,left+8,25),fill=P['cream']);d.point((left+7,25),fill=P['ink']);d.line((35,25,right-4,25),fill=P['cream']);d.point((35,25),fill=P['ink'])
 d.line((32,25,31,29),fill=P['skinshadow']);d.line((31,29,34,29),fill='#8e604b');d.point((31,28),fill=P['skinlight'])
 # Facial hair makes each portrait identifiable even without its label.
 if key=='guanyu':
  d.polygon([(24,31),(28,32),(31,31),(35,32),(40,30),(39,40),(36,49),(32,56),(27,48),(24,40)],fill=beard)
  d.line((29,35,29,47,32,52),fill='#45453b');d.line((35,35,34,46),fill='#434039');d.line((28,33,35,33),fill='#9d6650')
 elif key=='zhangfei':
  d.polygon([(22,28),(25,30),(28,31),(31,30),(35,31),(39,29),(42,27),(43,35),(39,41),(34,46),(28,44),(24,39),(21,34)],fill=beard)
  d.line((27,33,31,32,36,33),fill='#594238',width=2);d.line((29,35,34,35),fill=skin);d.point((26,37),fill='#51493b');d.line((32,38,32,42),fill='#51493b')
 elif key=='liubei':
  d.line((27,32,30,31,33,31,36,32),fill=beard);d.line((29,35,34,35),fill='#915f50');d.polygon([(29,36),(34,36),(33,42),(31,44),(29,41)],fill=beard);d.point((31,38),fill='#736047')
 elif key=='yellow_soldier':
  d.line((27,33,34,33),fill='#855f49');d.point((28,36),fill=beard);d.point((33,36),fill=beard);d.point((31,37),fill=beard)
 else:
  d.line((25,32,29,31,31,32,34,31,37,32),fill=beard,width=2)
  d.polygon([(26,34),(29,36),(34,36),(37,33),(36,39),(32,44),(28,41)],fill=beard);d.line((30,37,31,41),fill='#64503d');d.line((30,34,34,34),fill=skin)
 # Crowns and wraps.
 if hat=='crown':
  d.polygon([(20,18),(21,12),(25,10),(39,10),(43,14),(42,19)],fill=dark);d.polygon([(25,12),(25,5),(36,5),(37,12)],fill=P['ink']);d.rectangle((27,6,34,12),fill=main)
  d.line((27,7,34,7),fill=light);d.line((21,17,41,17),fill=c['accent'],width=2);d.rectangle((29,15,33,19),fill=P['gold']);d.point((31,16),fill=P['cream']);d.line((22,14,27,13),fill=light)
 elif hat=='helmet':
  d.polygon([(19,23),(20,14),(25,9),(36,9),(42,15),(44,26),(40,30),(40,20),(23,20),(23,28),(20,29)],fill=dark);d.polygon([(21,18),(24,12),(29,10),(35,11),(40,17),(39,19)],fill=main);d.line((24,14,29,11,35,12),fill=light);d.line((31,10,31,19),fill=light,width=2);d.line((21,20,40,20),fill=c['accent'],width=2);d.line((20,24,22,25),fill=light);d.line((41,23,42,25),fill=light)
 elif hat=='green':
  d.polygon([(20,20),(22,11),(26,5),(35,5),(41,12),(42,19)],fill=dark);d.polygon([(22,16),(26,7),(34,7),(39,12),(39,16)],fill=main);d.line((25,11,34,9,39,13),fill=light);d.line((22,18,40,18),fill=c['accent']);d.polygon([(22,17),(18,26),(18,38),(21,35),(24,19)],fill=main)
 elif hat=='band':
  d.polygon([(19,23),(18,16),(21,11),(26,8),(35,8),(42,12),(44,17),(43,23),(40,18),(24,18)],fill=beard);d.polygon([(27,10),(28,5),(32,3),(36,6),(35,11)],fill=beard);d.line((20,18,42,18),fill=c['accent'],width=3);d.rectangle((29,16,33,20),fill=P['goldshade']);d.point((31,17),fill=P['cream']);d.polygon([(20,19),(14,22),(17,25),(21,21)],fill=c['accent'])
 elif hat=='priest':
  d.polygon([(20,20),(24,9),(25,3),(36,3),(39,10),(43,20)],fill=dark);d.polygon([(23,17),(27,5),(34,5),(39,17)],fill=c['accent']);d.rectangle((29,6,33,16),fill='#785047');d.line((30,8,32,8),fill=P['cream']);d.line((30,11,32,11),fill=P['cream']);d.line((31,8,31,14),fill=P['cream']);d.line((21,18,41,18),fill=P['gold'],width=2)
 elif hat=='yellow':
  d.polygon([(20,21),(20,14),(23,9),(29,7),(37,9),(42,13),(43,20)],fill=dark);d.polygon([(21,18),(24,11),(30,9),(36,11),(40,15),(41,19)],fill=c['accent']);d.line((22,16,37,14,40,16),fill='#f0d47b',width=2);d.line((21,20,40,20),fill=P['goldshade']);d.polygon([(22,18),(16,22),(14,30),(18,28),(24,20)],fill=c['accent']);d.line((18,23,17,26),fill=P['cream'])
 else:
  d.polygon([(21,18),(23,11),(28,8),(36,9),(41,15),(41,19)],fill=dark);d.polygon([(25,13),(28,9),(36,10),(38,14)],fill=main);d.rectangle((29,4,34,10),fill=P['ink']);d.line((30,6,33,6),fill=c['accent']);d.line((21,18,40,18),fill=c['accent'],width=2);d.rectangle((29,16,32,19),fill=P['gold'])
 # Engraved frame corners. No generated text baked into portraits.
 d.rectangle((1,1,62,62),outline=P['goldshade']);d.rectangle((0,0,63,63),outline=P['ink'])
 for xx,yy,sx,sy in [(3,3,1,1),(60,3,-1,1),(3,60,1,-1),(60,60,-1,-1)]:
  d.line((xx,yy,xx+5*sx,yy),fill=P['gold']);d.line((xx,yy,xx,yy+5*sy),fill=P['gold']);d.point((xx+2*sx,yy+2*sy),fill=P['goldshade'])
 return im.resize((128,128),Image.Resampling.NEAREST)
for k in CHARS:portrait(k).save(A/'portraits'/f'{k}.png')
# Compact atlases are convenience files; individual PNGs are authoritative.
tatlas=Image.new('RGBA',(32*len(TERRAINS),32))
for i,n in enumerate(TERRAINS):tatlas.alpha_composite(terrain(n),(32*i,0))
tatlas.save(A/'terrain_atlas.png')
uatlas=Image.new('RGBA',(48*len(CHARS),48))
patlas=Image.new('RGBA',(128*len(CHARS),128))
for i,k in enumerate(CHARS):
 uatlas.alpha_composite(unit(k),(i*48,0));patlas.alpha_composite(portrait(k),(i*128,0))
uatlas.save(A/'unit_atlas.png');patlas.save(A/'portrait_atlas.png')
# Human-readable art inspection sheet, with Chinese labels from installed font.
font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font=ImageFont.truetype(font_path,18,index=2);small=ImageFont.truetype(font_path,14,index=2);title=ImageFont.truetype(font_path,27,index=2)
sheet=Image.new('RGB',(1280,660),'#1b2c2e');d=ImageDraw.Draw(sheet)
d.text((24,15),'曹操传 · 颍川初战',font=title,fill=P['cream']);d.text((26,52),'ORIGINAL PIXEL ART  /  TERRAIN · UNITS · PORTRAITS',font=small,fill='#9bad9a')
names=['平原','道路','树林','山地','河流','木桥','帐篷','营寨','木栅','军帐','粮仓']
for i,n in enumerate(TERRAINS):
 x=24+i*112;sheet.paste(terrain(n).resize((96,96),Image.Resampling.NEAREST),(x,92));d.text((x,199),names[i],font=small,fill=P['cream'])
for i,(k,c) in enumerate(CHARS.items()):
 x=24+i*155
 d.rectangle((x,254,x+135,389),fill='#344f43',outline='#516957')
 # Unit screenshots display on actual ground; portraits retain authored frames.
 tile=grass(i).resize((136,136),Image.Resampling.NEAREST);sheet.paste(tile,(x,254))
 spr=unit(k).resize((144,144),Image.Resampling.NEAREST);sheet.paste(spr,(x-4,246),spr)
 p=portrait(k);sheet.paste(p,(x+4,417),p)
 d.text((x+3,553),c['name'],font=font,fill=P['cream']);d.text((x+3,581),'CAVALRY' if c['mounted'] else 'INFANTRY',font=small,fill='#9bad9a')
d.text((24,628),'32px terrain  ·  48px transparent units  ·  128px portraits  ·  nearest-neighbour rendering',font=small,fill='#9bad9a')
sheet.save(A/'previews'/'contact_sheet.png')
manifest={'license':'Original artwork; created for this project. No third-party artwork used.','terrain_size':[32,32],'unit_size':[48,48],'portrait_size':[128,128],'filter':'nearest','terrain_order':TERRAINS,'unit_order':list(CHARS),'unit_sheet_frames':['idle','idle_glint','hit'],'units':{k:{'display_name':c['name'],'mounted':c['mounted'],'weapon':c['weapon']}for k,c in CHARS.items()}}
(A/'art_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'Generated {len(TERRAINS)} terrain types, {len(CHARS)} units, and {len(CHARS)} portraits in {A}')
