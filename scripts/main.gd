extends Control
const Battle=preload("res://scripts/battle.gd")
const ORIGIN=Vector2(28,136)
const CELL=44
const GOLD=Color("d4b477")
const INK=Color("ecdfbf")
const MUTED=Color("abaf9c")
var b=Battle.new()
var font:Font
var textures={}
var selected=0
var hover=Vector2i(-1,-1)
var busy=false
var paused=false
var help_open=false
var intro=true
var restarting=false
var sound_on=true
var fast=false
var elapsed=0.0
var banner="我軍回合"
var floats:Array=[]
var anim_positions={}
var buttons={}
var audio:AudioStreamPlayer
var qa_path=""
var generation=0
var casting=false
func _ready():
	font=load("res://assets/font.otf")
	texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	var asset_groups={"terrain":["grass","road","forest","mountain","river","bridge","village","fort","wall","wall_vertical","storehouse"],"units":["caocao","liubei","guanyu","zhangfei","yellow_soldier","zhangbao","zhangliang","blue_soldier"],"portraits":["caocao","liubei","guanyu","zhangfei","yellow_soldier","zhangbao","zhangliang","blue_soldier"]}
	for group in asset_groups:
		for key in asset_groups[group]:textures[group+"/"+key]=load("res://assets/"+group+"/"+key+".png")
	audio=AudioStreamPlayer.new();add_child(audio);audio.volume_db=-14
	make_button("wait","待命 / 結束行動",Rect2(854,492,188,44),end_turn)
	make_button("undo","撤回移動",Rect2(1052,492,196,44),undo_move)
	make_button("heal","豆・恢復兵力",Rect2(854,546,188,44),heal)
	make_button("wind","旋風・8 MP",Rect2(1052,546,196,44),toggle_wind)
	make_button("help","操作與戰術",Rect2(854,600,188,38),func():help_open=not help_open)
	make_button("pause","暫停",Rect2(1052,600,92,38),func():paused=not paused)
	make_button("sound","音效：開",Rect2(1154,600,94,38),func():sound_on=not sound_on)
	make_button("restart","重新出陣",Rect2(1122,648,126,38),func():restarting=true)
	make_button("start","出陣　→",Rect2(500,581,280,50),func():intro=false;tone(330))
	make_button("close","返回戰場",Rect2(500,628,280,46),func():help_open=false;paused=false)
	make_button("confirm","確定重新出陣",Rect2(420,476,220,48),reset_battle)
	make_button("cancel","取消",Rect2(662,476,198,48),func():restarting=false)
	b.setup()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--qa-screenshot="):qa_path=arg.trim_prefix("--qa-screenshot=");intro=false
	if "--qa-title" in OS.get_cmdline_user_args():intro=true
	if qa_path!="":
		await get_tree().process_frame;await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png(qa_path)
		get_tree().quit()
func make_button(id:String,label:String,r:Rect2,callback:Callable):
	var bt=Button.new();bt.text=label;bt.position=r.position;bt.size=r.size
	bt.add_theme_font_override("font",font);bt.add_theme_font_size_override("font_size",17)
	for state in ["normal","hover","pressed","disabled"]:
		var style=StyleBoxFlat.new();style.bg_color=Color("263a36") if state!="hover" else Color("435b4d")
		style.border_color=Color("796c49");style.set_border_width_all(1);style.set_corner_radius_all(4)
		if state=="disabled":style.bg_color=Color("202a29");style.border_color=Color("39433a")
		bt.add_theme_stylebox_override(state,style)
	bt.add_theme_color_override("font_color",INK);bt.pressed.connect(callback);add_child(bt);buttons[id]=bt
func _process(delta):
	if not paused:elapsed+=delta
	for f in floats:f.life-=delta
	floats=floats.filter(func(f):return f.life>0)
	var modal=intro or help_open or paused or restarting or b.result!=""
	for id in ["wait","undo","heal","wind","help","pause","sound","restart"]:buttons[id].visible=not modal
	buttons.start.visible=intro and not restarting
	buttons.close.visible=(help_open or paused) and not restarting
	buttons.confirm.visible=restarting
	buttons.cancel.visible=restarting
	buttons.wait.disabled=busy or b.phase!="player"
	buttons.undo.disabled=busy or not b.moved or b.acted
	buttons.heal.disabled=busy or b.acted or b.herbs==0 or b.units[0].hp>=b.units[0].max_hp
	buttons.wind.disabled=busy or b.acted or b.mp<b.WIND_COST
	buttons.wind.text="選取敵軍…" if casting else "旋風・8 MP"
	buttons.sound.text="音效："+("開" if sound_on else "關")
	if b.result!="" and not restarting:buttons.restart.visible=true;buttons.restart.position=Vector2(550,570);buttons.restart.size=Vector2(180,48)
	else:buttons.restart.position=Vector2(1122,648);buttons.restart.size=Vector2(126,38)
	queue_redraw()
func text(t:String,p:Vector2,size:int=18,c:Color=INK):draw_string(font,p,t,HORIZONTAL_ALIGNMENT_LEFT,-1,size,c)
func panel(r:Rect2,c:Color=Color("192925")):
	draw_style_box(panel_style(c),r)
func panel_style(c:Color)->StyleBoxFlat:
	var s=StyleBoxFlat.new();s.bg_color=c;s.border_color=Color("776a47");s.set_border_width_all(1);s.set_corner_radius_all(6);return s
func tex(key:String,r:Rect2,color:Color=Color.WHITE):
	if textures.has(key):draw_texture_rect(textures[key],r,false,color)
func _draw():
	draw_rect(Rect2(0,0,1280,800),Color("101b1b"))
	for x in range(0,1280,16):draw_line(Vector2(x,0),Vector2(x-150,800),Color(0.3,0.35,0.3,0.025))
	text("曹 操 傳",Vector2(28,49),31,GOLD);text("潁川初陣",Vector2(210,49),29)
	text("黃巾之亂　/　中平元年（184）",Vector2(30,82),16,MUTED)
	text("第 %02d / 20 回合"%mini(b.round_no,20),Vector2(863,44),25,GOLD)
	text(banner,Vector2(1070,44),22,Color("99c5b0"))
	panel(Rect2(28,96,792,30),Color("24372e"));text("勝利：擊退張梁、張寶　　敗北：曹操敗退或超過 20 回合",Vector2(42,117),16)
	text("原創素材・首關玩法重製",Vector2(866,80),16,MUTED)
	for y in b.H:
		for x in b.W:
			var p=Vector2i(x,y);var r=Rect2(ORIGIN+Vector2(p)*CELL,Vector2(CELL,CELL));var tile=b.terrain(p)
			tex("terrain/grass",r)
			tex("terrain/"+("wall_vertical" if tile=="wall" and x in [2,15] and y>2 and y<10 else tile),r)
			if tile=="wall" and not textures.has("terrain/wall"):
				for i in 6:draw_rect(Rect2(r.position+Vector2(i*7,8),Vector2(4,27)),Color("876242"))
			draw_rect(r,Color(0.1,0.2,0.13,0.16),false,1)
	if selected==0 and b.phase=="player" and not b.moved and not busy:
		for p in b.reachable(0):
			if b.at(p)<0:draw_rect(Rect2(ORIGIN+Vector2(p)*CELL+Vector2(1,1),Vector2(CELL-2,CELL-2)),Color(0.24,0.66,0.8,0.22))
	if selected==0:
		for u in b.units:
			if (b.can_cast(u.id) if casting else b.can_attack(0,u.id)):draw_rect(Rect2(ORIGIN+Vector2(u.pos)*CELL+Vector2(1,1),Vector2(CELL-2,CELL-2)),Color(0.95,0.3,0.25,0.5),false,3)
	if b.inside(hover):
		draw_rect(Rect2(ORIGIN+Vector2(hover)*CELL,Vector2(CELL,CELL)),GOLD,false,2)
		if selected==0 and not b.moved:
			var path=b.path_to(0,hover)
			for i in range(1,path.size()):draw_line(ORIGIN+Vector2(path[i-1])*CELL+Vector2(22,22),ORIGIN+Vector2(path[i])*CELL+Vector2(22,22),Color(0.8,0.9,0.8,0.5),2)
	if b.round_no==1:
		for x in [5,6,11,12]:
			var fp=ORIGIN+Vector2(x*CELL,2*CELL)
			draw_circle(fp+Vector2(22,20),8+sin(elapsed*8+x)*3,Color("de692d"));draw_circle(fp+Vector2(22,24),5,Color("efbe61"))
	for u in b.units:
		if u.hp<=0:continue
		var pos:Vector2=anim_positions.get(u.id,Vector2(u.pos));var center=ORIGIN+pos*CELL
		var color=Color("73bfe8") if u.team=="player" else (Color("75aa7b") if u.team=="ally" else Color("df6653"))
		draw_shadow(center+Vector2(5,27),Vector2(34,14),Color(0,0,0,0.3))
		draw_arc(center+Vector2(22,30),16,0,TAU,24,color,2)
		var key=u.key
		if u.team=="ally" and key=="yellow_soldier" and textures.has("units/blue_soldier"):key="blue_soldier"
		tex("units/"+key,Rect2(center+Vector2(-2,-8),Vector2(48,48)),Color(0.8,0.9,1) if u.team=="ally" and key=="yellow_soldier" else Color.WHITE)
		draw_rect(Rect2(center+Vector2(4,39),Vector2(36,4)),Color("252b28"));draw_rect(Rect2(center+Vector2(4,39),Vector2(36*float(u.hp)/u.max_hp,4)),color)
		if selected==u.id:draw_rect(Rect2(center+Vector2(1,0),Vector2(42,43)),GOLD,false,2)
		if u.id<6:
			text(u.name,center+Vector2(4,-8),13,INK)
		if u.done:draw_circle(center+Vector2(37,5),3,GOLD)
	for f in floats:text(f.label,f.pos+Vector2(0,-(1.2-f.life)*35),24,f.color)
	draw_side()
	panel(Rect2(28,722,1220,62),Color("182521"))
	var start=maxi(0,b.logs.size()-3)
	for i in range(start,b.logs.size()):text(b.logs[i],Vector2(42,740+(i-start)*18),14,MUTED if i<b.logs.size()-1 else INK)
	if intro:draw_intro()
	elif help_open:draw_help()
	elif paused:draw_modal("戰場暫停","按 Esc 或「返回戰場」繼續。")
	elif b.result!="":draw_result()
	if restarting:
		draw_rect(Rect2(0,0,1280,800),Color(0.02,0.06,0.05,0.85));panel(Rect2(350,280,580,290));text("重新出陣？",Vector2(520,340),30,GOLD);text("本次戰鬥進度將會清除。",Vector2(468,403),22)
func draw_shadow(pos:Vector2,s:Vector2,c:Color):
	var points=PackedVector2Array()
	for i in 24:points.append(pos+s/2+Vector2(cos(i*TAU/24),sin(i*TAU/24))*s/2)
	draw_colored_polygon(points,c)
func draw_side():
	panel(Rect2(842,96,406,378))
	var id=selected
	if b.inside(hover) and b.at(hover)>=0:id=b.at(hover)
	if id<0:id=0
	var u=b.units[id]
	tex("portraits/"+u.key,Rect2(862,117,112,112))
	text(u.name,Vector2(994,145),27,GOLD)
	text({"player":"我軍・群雄","ally":"友軍・自動行動","enemy":"敵軍・黃巾"}[u.team],Vector2(994,178),16,MUTED)
	text("兵力　%d / %d"%[u.hp,u.max_hp],Vector2(994,213),17)
	if id==0:text("策略　%d / 30 MP"%b.mp,Vector2(994,239),15,Color("83c9ce"))
	text("攻擊 %d　防禦 %d　移動 %d"%[u.power,u.defense,u.move],Vector2(862,259),19)
	draw_line(Vector2(862,278),Vector2(1226,278),Color("4b5645"))
	text("許子將・軍令",Vector2(862,307),20,GOLD)
	var hints=["點曹操 → 藍格移動 → 紅框敵軍攻擊", "移動後可撤回；攻擊或用豆即結束行動。", "友軍由電腦操作；全部軍令後進入敵軍。"]
	if casting:hints=["旋風：點紅框內敵軍施法。", "射程 3 格，消耗 8 MP，不受反擊。", "右鍵取消施法；施法後無法撤回移動。"]
	elif busy:hints=["戰況演出中…", "友軍及敵軍逐一行動。", "Esc 暫停　/　右鍵查看地形"]
	elif b.acted:hints=["曹操本回合已行動。", "點「待命 / 結束行動」推進回合。", "綠色是友軍，紅色是敵軍。"]
	for i in hints.size():text(hints[i],Vector2(862,338+i*27),15,MUTED)
	var terrain_name={"grass":"平原","forest":"樹林・移動 2 / 防禦 +6","wall":"柵欄・不可通行","river":"河川・不可通行","village":"營帳・防禦 +6","fort":"營寨・防禦 +6","storehouse":"兵糧庫・防禦 +6","road":"道路","bridge":"橋樑","mountain":"山地"}
	text("地形："+str(terrain_name.get(b.terrain(hover),"—")) if b.inside(hover) else "兵糧：豆 × %d（每次恢復 65）"%b.herbs,Vector2(862,447),16,GOLD)
	text("左鍵：選擇 / 移動 / 攻擊",Vector2(854,672),16,MUTED)
	text("右鍵：取消選擇　Esc：暫停",Vector2(854,698),16,MUTED)
func overlay_card():
	draw_rect(Rect2(0,0,1280,800),Color(0.015,0.04,0.035,0.88));panel(Rect2(235,130,810,540),Color("1c302b"))
func draw_intro():
	overlay_card();text("第一戰",Vector2(575,181),20,GOLD);text("潁 川 之 戰",Vector2(467,241),43,INK)
	tex("portraits/caocao",Rect2(281,289,144,144))
	text("曹操",Vector2(327,464),22,GOLD)
	text("「賊營火起，此正破敵之機！」",Vector2(459,313),25)
	for i in 5:
		text(["黃巾之亂席捲天下。曹操率軍抵達潁川，","與劉備、關羽、張飛合力討伐張梁、張寶。","我軍僅操作曹操，友軍將自行進攻。","敵營遭火攻，首回合混亂。把握時機！","勝利：擊退兩名主將　｜　時限：20 回合"][i],Vector2(460,358+i*33),18,MUTED)
	text("以原版首關人物與戰況為本，地圖尺度與數值重新設計。",Vector2(328,558),16,GOLD)
func draw_help():
	overlay_card();text("行軍要訣",Vector2(535,198),33,GOLD)
	var lines=["① 點選曹操：藍色格子是本回合可移動範圍。","② 點藍格移動：路徑不可穿越敌軍、河川或柵欄。","③ 點相鄰紅框敵軍：攻擊一次，敵軍若存活會反擊。","④「撤回移動」只在攻擊或使用豆之前有效。","⑤「待命 / 結束行動」：友軍 → 敵軍 → 下一回合。","豆可恢復 65 兵力，消耗曹操本回合行動，共有 3 個。","旋風：射程 3 格，消耗 8 MP 與行動，不受反擊。","曹操敗退或第 20 回合結束仍未擊敗雙將，即為敗北。","戰鬥數值為重製版設計；原版素材與程式未使用。"]
	for i in lines.size():text(lines[i],Vector2(285,260+i*35),19,INK if i<5 else MUTED)
func draw_modal(title:String,body:String):
	overlay_card();text(title,Vector2(520,305),38,GOLD);text(body,Vector2(435,394),23)
func draw_result():
	overlay_card();var won=b.result=="victory"
	text("戰 役 勝 利" if won else "兵 敗 潁 川",Vector2(470,248),43,GOLD)
	text("張梁、張寶皆已敗退。潁川之圍已解！" if won else ("曹操敗退。勝敗乃兵家常事，再整旗鼓！" if b.units[0].hp<=0 else "二十回合已盡，討伐未成。"),Vector2(340,335),23)
	text("戰鬥回合　%d　　曹操兵力　%d / %d"%[mini(b.round_no,20),b.units[0].hp,b.units[0].max_hp],Vector2(382,397),23,MUTED)
	text("第一戰・潁川之戰　完" if won else "善用友軍牽制，保留豆維持曹操兵力。",Vector2(420,474),22)
func _gui_input(event):
	if event is InputEventMouseMotion:hover=Vector2i(((event.position-ORIGIN)/CELL).floor())
	if not event is InputEventMouseButton or not event.pressed:return
	if intro or help_open or paused or restarting or b.result!="" or busy:return
	if event.button_index==MOUSE_BUTTON_RIGHT:casting=false;selected=-1;return
	if event.button_index!=MOUSE_BUTTON_LEFT:return
	var p=Vector2i(((event.position-ORIGIN)/CELL).floor())
	if not b.inside(p):return
	var id=b.at(p)
	if id>=0:
		if casting:
			if b.can_cast(id):cast_animation(id)
			return
		if selected==0 and not b.acted and b.can_attack(0,id):attack_animation(0,id)
		else:selected=id;tone(280)
	elif selected==0 and not casting and not b.moved and not b.acted:move_animation(0,p)
func _unhandled_key_input(event):
	if event.is_action_pressed("ui_cancel"):
		if restarting:restarting=false
		elif help_open:help_open=false
		elif not intro and b.result=="":paused=not paused
func delay(seconds:float):
	var token=generation
	var t=0.0
	while t<seconds:
		if token!=generation or not is_inside_tree():return
		await get_tree().process_frame
		if token!=generation or not is_inside_tree():return
		if not paused and not help_open and not restarting:t+=get_process_delta_time()
func move_animation(id:int,dest:Vector2i):
	var token=generation
	var path=b.path_to(id,dest)
	if path.is_empty() or (b.at(dest)>=0 and b.at(dest)!=id):return
	busy=true
	for i in range(1,path.size()):
		var t=0.0
		while t<1.0:
			await get_tree().process_frame
			if token!=generation or not is_inside_tree():return
			if paused or help_open or restarting:continue
			t+=get_process_delta_time()*8
			anim_positions[id]=Vector2(path[i-1]).lerp(Vector2(path[i]),minf(1,t))
	b.move_unit(id,dest);anim_positions.erase(id);busy=false;tone(240)
	check_talk(id)
func check_talk(id:int):
	if id!=0:return
	for boss in [4,5]:
		if b.can_attack(0,boss) and not b.events.has(boss):
			b.events[boss]=true;b.log_text("曹操：黃巾逆賊，速速投降！　"+b.units[boss].name+"：休想！")
func attack_animation(a:int,target:int):
	var token=generation
	if not b.can_attack(a,target):return
	busy=true
	check_talk(a)
	var from=Vector2(b.units[a].pos);var dest=Vector2(b.units[target].pos)
	anim_positions[a]=from.lerp(dest,0.28);tone(155)
	await delay(0.16)
	if token!=generation or not is_inside_tree():return
	var hit=b.strike(a,target);anim_positions.erase(a)
	floats.append({"label":"−%d"%hit.damage,"pos":ORIGIN+dest*CELL+Vector2(4,8),"life":1.2,"color":Color("ffc576")})
	if hit.counter>0:floats.append({"label":"−%d"%hit.counter,"pos":ORIGIN+from*CELL+Vector2(4,8),"life":1.2,"color":Color("ff8976")})
	await delay(0.55)
	if token!=generation or not is_inside_tree():return
	busy=false
	if b.result!="":banner="戰役結束"
func end_turn():
	var token=generation
	if busy or paused or help_open or restarting or b.result!="" or b.phase!="player":return
	casting=false
	b.wait_player();busy=true;selected=-1;b.phase="ally";banner="友軍回合"
	await delay(0.35)
	if token!=generation:return
	for team in ["ally","enemy"]:
		b.phase=team;banner="友軍回合" if team=="ally" else "敵軍回合"
		if team=="enemy" and b.round_no==1:
			b.log_text("黃巾軍陷入混亂，無法行動！");await delay(0.7)
			if token!=generation:return
			continue
		for u in b.units:
			if u.team!=team or u.hp<=0:continue
			if b.result!="":break
			var plan=b.ai_plan(u.id)
			if plan.target<0:continue
			if plan.pos!=u.pos:await move_animation(u.id,plan.pos)
			if token!=generation:return
			busy=true
			if b.can_attack(u.id,plan.target):await attack_animation(u.id,plan.target)
			if token!=generation:return
			busy=true;u.done=true;await delay(0.10)
			if token!=generation:return
		if b.result!="":break
	busy=false
	if b.result=="":b.next_round();selected=0;banner="我軍回合" if b.result=="" else "戰役結束"
	else:banner="戰役結束"
func undo_move():
	if busy or paused or help_open or restarting:return
	casting=false
	if b.undo():tone(260)
func heal():
	if busy or paused or help_open or restarting:return
	casting=false
	if b.heal():tone(520);floats.append({"label":"+65","pos":ORIGIN+Vector2(b.units[0].pos)*CELL,"life":1.2,"color":Color("a2e39b")})
func reset_battle():
	generation+=1
	b.setup();anim_positions.clear();floats.clear()
	selected=0;busy=false;paused=false;help_open=false;restarting=false;intro=true;casting=false;banner="我軍回合"
func toggle_wind():
	if busy or b.acted or b.mp<b.WIND_COST:return
	casting=not casting;selected=0
func cast_animation(target:int):
	if busy or not b.can_cast(target):return
	var token=generation
	busy=true;casting=false;tone(620)
	await delay(0.25)
	if token!=generation:return
	var amount=b.cast_wind(target)
	floats.append({"label":"旋風 −%d"%amount,"pos":ORIGIN+Vector2(b.units[target].pos)*CELL,"life":1.2,"color":Color("9fe3d0")})
	await delay(0.55)
	if token!=generation:return
	busy=false
	if b.result!="":banner="戰役結束"
func tone(freq:float):
	if not sound_on:return
	var wav=AudioStreamWAV.new();wav.format=AudioStreamWAV.FORMAT_16_BITS;wav.mix_rate=22050
	var bytes=PackedByteArray();bytes.resize(2205*2)
	for i in 2205:
		var sample=int(sin(TAU*freq*i/22050.0)*12000*(1.0-i/2205.0));bytes.encode_s16(i*2,sample)
	wav.data=bytes;audio.stream=wav;audio.play()
