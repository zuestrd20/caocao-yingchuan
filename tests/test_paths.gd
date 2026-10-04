extends SceneTree
const B=preload("res://scripts/battle.gd")
var n=0
func ck(v:bool,msg:String):
 n+=1
 if not v:push_error(msg);quit(1)
func _initialize():
 var b=B.new();b.setup()
 for u in b.units:
  var r=b.reachable(u.id)
  for dest in r:
   var p=b.path_to(u.id,dest)
   ck(not p.is_empty(),"reachable path exists")
   ck(p[0]==u.pos and p[-1]==dest,"path endpoints")
   var spent=0
   for i in range(1,p.size()):
    ck(b.adjacent(p[i-1],p[i]),"path adjacent")
    ck(b.cost(p[i])<999,"passable")
    var occupant=b.at(p[i])
    ck(occupant<0 or not b.hostile(u,b.units[occupant]),"no hostile transit")
    spent+=b.cost(p[i])
   ck(spent==r[dest] and spent<=u.move,"exact weighted distance")
 b.units[0].pos=Vector2i(1,2)
 ck(b.reachable(0)[Vector2i(1,1)]==2,"forest costs two")
 b.setup();b.units[0].pos=Vector2i(7,4)
 ck(b.reachable(0).has(Vector2i(7,3)),"friendly transit allowed")
 ck(not b.move_unit(0,Vector2i(7,3)),"friendly occupied endpoint blocked")
 b.setup();b.units[0].pos=Vector2i(7,7);b.units[0].hp=1
 b.strike(0,4)
 ck(b.units[0].hp==0 and b.result=="defeat","counterattack kills low HP player")
 b.setup();b.phase="enemy";b.units[0].pos=Vector2i(7,7);b.units[0].hp=1
 b.strike(4,0)
 ck(b.result=="defeat","enemy attack kills low HP player")
 print("REVIEW PASS ",n," assertions")
 quit()
