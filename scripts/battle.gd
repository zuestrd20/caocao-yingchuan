class_name YingchuanBattle
extends RefCounted
const W=18
const H=13
const LIMIT=20
var tiles:Array=[]
var units:Array=[]
var round_no=1
var phase="player"
var result=""
var logs:Array[String]=[]
var events:Dictionary={}
var herbs=3
var mp=30
const WIND_COST=8
const WIND_RANGE=3
var move_origin=Vector2i(-1,-1)
var moved=false
var acted=false
var committed=false
func setup():
	tiles.clear();units.clear();logs.clear();events.clear()
	round_no=1;phase="player";result="";herbs=3;mp=30;moved=false;acted=false;committed=false
	for y in H:
		var row:Array=[]
		for x in W:
			var t="grass"
			if x==0 or (x==17 and y<10):t="river"
			if x in [1,16] and y in [0,1,10,11,12]:t="forest"
			if (y==2 or y==10) and x>1 and x<16 and x not in [8,9]:t="wall"
			if x in [2,15] and y>2 and y<10:t="wall"
			if y==6 and x in [7,8,9]:t="wall"
			if x in [4,5] and y in [3,4,5,8,9]:t="village"
			if x in [12,13] and y in [3,4,8,9]:t="village"
			if x in [12,13] and y in [8,9]:t="storehouse"
			if y==7 and x in [8,9]:t="fort"
			row.append(t)
		tiles.append(row)
	add("曹操","caocao","player",Vector2i(9,0),160,46,18,6)
	add("劉備","liubei","ally",Vector2i(7,3),120,31,14,4)
	add("關羽","guanyu","ally",Vector2i(8,3),140,42,18,5)
	add("張飛","zhangfei","ally",Vector2i(10,3),140,43,16,4)
	add("張梁","zhangliang","enemy",Vector2i(8,7),135,31,15,3)
	add("張寶","zhangbao","enemy",Vector2i(9,7),145,32,16,3)
	for p in [Vector2i(3,6),Vector2i(6,6),Vector2i(12,6),Vector2i(3,7),Vector2i(5,7),Vector2i(12,8),Vector2i(8,10),Vector2i(9,10),Vector2i(8,11),Vector2i(9,11),Vector2i(11,11),Vector2i(13,5)]:
		add("黃巾兵","yellow_soldier","enemy",p,72,25,9,3)
	for entry in [["官軍步兵",3,12],["官軍步兵",5,12],["官軍弓兵",6,12],["官軍弓兵",7,12],["官軍策士",10,12],["官軍騎兵",12,12],["官軍騎兵",14,12]]:
		add(entry[0],"yellow_soldier","ally",Vector2i(entry[1],entry[2]),65,24,9,3)
	log_text("漢・中平元年　潁川黃巾討伐戰")
	log_text("烈火映營！黃巾軍混亂，首回合無法行動。")
func add(n:String,key:String,team:String,p:Vector2i,hp:int,power:int,defense:int,mob:int):
	units.append({"id":units.size(),"name":n,"key":key,"team":team,"pos":p,"hp":hp,"max_hp":hp,"power":power,"defense":defense,"move":mob,"done":false})
func log_text(t:String):
	logs.append(t)
func inside(p:Vector2i)->bool:return p.x>=0 and p.y>=0 and p.x<W and p.y<H
func terrain(p:Vector2i)->String:return tiles[p.y][p.x] if inside(p) else "mountain"
func cost(p:Vector2i)->int:
	if terrain(p) in ["mountain","river","wall"]:return 999
	return 2 if terrain(p)=="forest" else 1
func at(p:Vector2i)->int:
	for u in units:
		if u.hp>0 and u.pos==p:return u.id
	return -1
func hostile(a:Dictionary,b:Dictionary)->bool:return (a.team=="enemy")!=(b.team=="enemy")
func adjacent(a:Vector2i,b:Vector2i)->bool:return absi(a.x-b.x)+absi(a.y-b.y)==1
func reachable(id:int)->Dictionary:
	var u=units[id];var dist={u.pos:0};var todo=[u.pos]
	while not todo.is_empty():
		todo.sort_custom(func(a,b):return dist[a]<dist[b])
		var p:Vector2i=todo.pop_front()
		for d in [Vector2i.UP,Vector2i.DOWN,Vector2i.LEFT,Vector2i.RIGHT]:
			var q:Vector2i=p+d
			if not inside(q):continue
			var occup=at(q)
			if occup>=0 and hostile(u,units[occup]):continue
			var c:int=dist[p]+cost(q)
			if c<=u.move and (not dist.has(q) or c<dist[q]):dist[q]=c;todo.append(q)
	return dist
func path_to(id:int,dest:Vector2i)->Array:
	var dist=reachable(id)
	if not dist.has(dest):return []
	var p=dest;var path=[p]
	while p!=units[id].pos:
		var found=false
		for d in [Vector2i.UP,Vector2i.DOWN,Vector2i.LEFT,Vector2i.RIGHT]:
			var q:Vector2i=p+d
			if dist.has(q) and dist[q]+cost(p)==dist[p]:p=q;path.push_front(p);found=true;break
		if not found:return []
	return path
func move_unit(id:int,p:Vector2i)->bool:
	if result!="" or units[id].done or units[id].hp<=0 or (at(p)>=0 and at(p)!=id) or not reachable(id).has(p):return false
	if id==0:
		if moved or acted or phase!="player":return false
		move_origin=units[id].pos;moved=true
	units[id].pos=p
	return true
func undo()->bool:
	if not moved or acted or committed or phase!="player":return false
	units[0].pos=move_origin;moved=false
	return true
func defense_bonus(id:int)->int:
	return 6 if terrain(units[id].pos) in ["forest","fort","village","storehouse"] else 0
func damage(a:int,b:int)->int:return maxi(8,units[a].power-units[b].defense-defense_bonus(b))
func can_attack(a:int,b:int)->bool:return units[a].hp>0 and units[b].hp>0 and hostile(units[a],units[b]) and adjacent(units[a].pos,units[b].pos)
func strike(a:int,b:int)->Dictionary:
	if result!="" or units[a].done or (a==0 and (acted or phase!="player")) or not can_attack(a,b):return {}
	var hit=damage(a,b);units[b].hp=maxi(0,units[b].hp-hit)
	log_text("%s → %s　傷害 %d"%[units[a].name,units[b].name,hit])
	var counter=0
	if units[b].hp>0:
		counter=maxi(4,damage(b,a)/2);units[a].hp=maxi(0,units[a].hp-counter)
	else:log_text("%s 敗退！"%units[b].name)
	if a==0:acted=true;committed=true;units[0].done=true
	check_result()
	return {"damage":hit,"counter":counter}
func heal()->bool:
	if result!="" or units[0].hp<=0 or phase!="player" or acted or herbs<=0 or units[0].hp>=units[0].max_hp:return false
	herbs-=1;units[0].hp=mini(units[0].max_hp,units[0].hp+65);acted=true;committed=true;units[0].done=true
	log_text("曹操使用豆，恢復 65 兵力。")
	return true
func wait_player():
	if result!="" or phase!="player":return
	acted=true;committed=true;units[0].done=true
func check_result()->String:
	if units[0].hp<=0:result="defeat"
	elif units[4].hp<=0 and units[5].hp<=0:result="victory"
	elif round_no>LIMIT:result="defeat"
	return result
func next_round():
	if result!="":return
	round_no+=1;phase="player";moved=false;acted=false;committed=false
	for u in units:u.done=false
	check_result()
	log_text("第 %d 回合・我軍"%round_no)
func distances_from(goal:Vector2i)->Dictionary:
	var dist={goal:0};var todo=[goal]
	while not todo.is_empty():
		var p:Vector2i=todo.pop_front()
		for d in [Vector2i.UP,Vector2i.DOWN,Vector2i.LEFT,Vector2i.RIGHT]:
			var q:Vector2i=p+d
			if inside(q) and cost(q)<999 and not dist.has(q):dist[q]=dist[p]+1;todo.append(q)
	return dist
func ai_plan(id:int)->Dictionary:
	var u=units[id];var reach=reachable(id);var best=u.pos;var score=1e9;var target=-1
	for foe in units:
		if foe.hp<=0 or not hostile(u,foe):continue
		var strategic=distances_from(foe.pos)
		for p in reach:
			if at(p)>=0 and at(p)!=id:continue
			var d=int(strategic.get(p,999))
			var s=float(d)*100.0+float(reach[p])*1.2+float(foe.hp)*0.03
			if s<score:score=s;best=p;target=foe.id
	return {"pos":best,"target":target}

func can_cast(target:int)->bool:
	if result!="" or phase!="player" or acted or mp<WIND_COST or units[0].hp<=0:return false
	if target<0 or target>=units.size() or units[target].hp<=0 or units[target].team!="enemy":return false
	var d:Vector2i=units[target].pos-units[0].pos
	return absi(d.x)+absi(d.y)<=WIND_RANGE
func cast_wind(target:int)->int:
	if not can_cast(target):return 0
	mp-=WIND_COST
	var amount=maxi(12,38-units[target].defense/2)
	units[target].hp=maxi(0,units[target].hp-amount)
	acted=true;committed=true;units[0].done=true
	log_text("曹操施展旋風 → %s　傷害 %d（無反擊）"%[units[target].name,amount])
	if units[target].hp==0:log_text(units[target].name+" 敗退！")
	check_result()
	return amount
