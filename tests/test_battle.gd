extends SceneTree
const B=preload("res://scripts/battle.gd")
var checks=0
func check(value:bool,label:String):
	checks+=1
	if not value:push_error("FAIL: "+label);quit(1)
func _initialize():
	var b=B.new();b.setup()
	check(b.units.size()==25,"original troop roster counts")
	check(b.reachable(0).has(Vector2i(9,2)),"north gate reachable")
	check(not b.reachable(0).has(Vector2i(7,2)),"wall impassable")
	check(not b.reachable(0).has(Vector2i(0,0)),"water impassable")
	var start=b.units[0].pos
	check(b.move_unit(0,Vector2i(9,2)),"legal movement")
	check(not b.move_unit(0,Vector2i(9,1)),"no second movement")
	check(b.undo() and b.units[0].pos==start,"undo exact restoration")
	b.units[0].hp=80
	check(b.heal() and b.units[0].hp==145 and b.herbs==2,"herb resource and heal")
	check(not b.undo() and not b.heal(),"no undo or second heal after commit")
	b.setup();b.units[0].pos=Vector2i(7,7)
	var hp=b.units[4].hp;var result=b.strike(0,4)
	check(not result.is_empty() and b.units[4].hp<hp and b.acted,"attack commits")
	check(not b.undo(),"attack forbids undo")
	b.setup();b.units[0].hp=0
	check(b.check_result()=="defeat","Cao defeat")
	b.setup();b.round_no=20;b.next_round()
	check(b.result=="defeat","turn limit")
	b.setup();b.units[4].hp=0
	check(b.check_result()=="","one leader insufficient")
	b.units[5].hp=0
	check(b.check_result()=="victory","both leaders victory")
	b.setup();b.units[0].pos=Vector2i(7,7)
	check(b.can_cast(4),"wind range valid")
	var own_hp=b.units[0].hp;var old_mp=b.mp
	check(b.cast_wind(4)>0 and b.mp==old_mp-8 and b.units[0].hp==own_hp,"wind spends MP no counter")
	check(b.acted and not b.undo() and b.cast_wind(4)==0,"wind consumes action once")
	b.setup();b.mp=7
	check(not b.can_cast(4) and b.cast_wind(4)==0,"insufficient MP")
	b.setup();check(not b.can_cast(4),"wind out of range")
	b.units[0].hp=0;b.check_result()
	check(not b.heal() and b.cast_wind(4)==0 and b.strike(0,4).is_empty(),"terminal actions blocked")
	for strategy in ["aggressive","wait","low_hp_defeat_fixture"]:
		b.setup();var attacks=0
		if strategy=="low_hp_defeat_fixture":b.units[0].hp=1
		while b.result=="" and b.round_no<=20:
			if strategy!="wait":
				if strategy=="aggressive" and b.units[0].hp<90 and b.herbs>0:b.heal()
				else:
					var p=b.ai_plan(0)
					if p.pos!=b.units[0].pos:b.move_unit(0,p.pos)
					if p.target>=0 and b.can_attack(0,p.target):b.strike(0,p.target);attacks+=1
			b.wait_player()
			for team in ["ally","enemy"]:
				b.phase=team
				if team=="enemy" and b.round_no==1:continue
				for u in b.units:
					if b.result!="":break
					if u.team!=team or u.hp<=0:continue
					var p=b.ai_plan(u.id)
					if p.pos!=u.pos:b.move_unit(u.id,p.pos)
					if p.target>=0 and b.can_attack(u.id,p.target):b.strike(u.id,p.target)
			if b.result=="":b.next_round()
		print("SIM ",strategy,": ",b.result," round=",b.round_no," CaoHP=",b.units[0].hp," attacks=",attacks," alive allies=",b.units.filter(func(u):return u.team=="ally" and u.hp>0).size())
		if strategy=="aggressive":check(b.result=="victory" and attacks>0,"complete action-driven win")
		if strategy=="low_hp_defeat_fixture":check(b.result=="defeat" and attacks>0,"action-driven counterattack defeat from labeled low HP fixture")
	print("PASS ",checks," deterministic assertions")
	quit()
