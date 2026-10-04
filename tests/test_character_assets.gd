extends SceneTree
# Resource/phase smoke checks supplement pixel-level packaging tests.
func _initialize():call_deferred("run")
func run():
 var scene=load("res://main.tscn").instantiate();root.add_child(scene);current_scene=scene
 scene.intro=false;scene.sound_on=false
 var checks=0
 for key in ["caocao","blue_soldier","liubei","guanyu","zhangfei","yellow_soldier","zhangbao","zhangliang"]:
  for group in ["units","portraits"]:
   var texture=scene.textures[group+"/"+key]
   assert(texture!=null and texture.get_width()>0 and texture.get_height()>0,"missing character texture "+key)
   checks+=1
  var sheet=load("res://assets/units/"+key+"_sheet.png")
  assert(sheet!=null and sheet.get_width()==144 and sheet.get_height()==48)
  checks+=1
 for phase in ["player","ally","enemy"]:
  scene.b.phase=phase;scene.queue_redraw();await process_frame
  for unit in scene.b.units:
   assert(scene.textures.has("units/"+unit.key) and scene.textures.has("portraits/"+unit.key))
   checks+=1
 scene.b.phase="player";scene.b.units[0].hp=40;scene.casting=true
 scene.queue_redraw();await process_frame
 assert(scene.casting and scene.b.units[0].hp==40)
 scene.reset_battle();await process_frame
 assert(not scene.casting and scene.b.units[0].hp==scene.b.units[0].max_hp)
 print("CHARACTER RESOURCE PASS ",checks," checks; all phases, wounded/casting and restart")
 quit()
