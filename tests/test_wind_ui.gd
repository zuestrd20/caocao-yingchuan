extends SceneTree
func _initialize():call_deferred("run")
func run():
 var scene=load("res://main.tscn").instantiate();root.add_child(scene);current_scene=scene
 scene.intro=false;scene.sound_on=false
 scene.b.units[0].pos=Vector2i(7,7);scene.b.units[0].hp=80
 var mp=scene.b.mp;var hp=scene.b.units[4].hp
 scene.cast_animation(4);scene.cast_animation(4);scene.heal();scene.undo_move();scene.end_turn()
 await create_timer(0.9).timeout
 assert(scene.b.mp==mp-8,"exactly one MP charge")
 assert(scene.b.units[4].hp<hp and scene.b.units[0].hp==80,"one spell no counterattack or queued heal")
 assert(scene.b.acted and scene.b.phase=="player" and not scene.b.undo(),"spell commits and endturn rejected during busy")
 scene.reset_battle();scene.intro=false;scene.b.units[0].pos=Vector2i(7,7)
 mp=scene.b.mp;hp=scene.b.units[4].hp
 scene.cast_animation(4);await process_frame;scene.reset_battle()
 await create_timer(0.9).timeout
 assert(scene.b.mp==mp and scene.b.units[4].hp==hp and not scene.b.acted and not scene.busy,"restart cancels pending spell")
 print("WIND REVIEW PASS duplicate input, resource, commit, no-counter and restart")
 quit()
