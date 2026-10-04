extends SceneTree
func _initialize():
 call_deferred("run")
func run():
 var packed=load("res://main.tscn")
 var scene=packed.instantiate();root.add_child(scene);current_scene=scene
 scene.intro=false;scene.sound_on=false
 scene.move_animation(0,Vector2i(9,2))
 await process_frame;await process_frame
 scene.reset_battle()
 await process_frame;await process_frame
 var next=current_scene;next.intro=false;next.sound_on=false
 if next.b.units[0].pos!=Vector2i(9,0) or next.busy:
  push_error("Movement restart failed");quit(1);return
 next.end_turn()
 await create_timer(0.5).timeout
 next.reset_battle()
 await process_frame;await process_frame
 next=current_scene;next.intro=false;next.sound_on=false
 await create_timer(0.3).timeout
 if next.b.phase!="player" or next.b.round_no!=1 or next.busy:
  push_error("AI restart failed");quit(1);return
 next.b.units[0].pos=Vector2i(7,7)
 next.attack_animation(0,4)
 await process_frame
 next.reset_battle()
 await process_frame;await process_frame
 next=current_scene;next.sound_on=false
 await create_timer(0.3).timeout
 if next.b.units[4].hp!=135 or next.b.acted:
  push_error("Attack restart failed");quit(1);return
 print("RESTART REVIEW PASS movement, AI and attack coroutine cancellation")
 quit()
