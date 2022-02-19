import bpy
import math
import mathutils

print("Changing to playercolor mask")
bpy.context.scene.world.use_sky_blend = False
bpy.context.scene.world.horizon_color = mathutils.Color((0, 0, 0))
for mat in bpy.data.materials:
   if mat.name.startswith('PlayerColor'):
      mat.diffuse_color=mathutils.Color((1, 1, 1))
   else:
      mat.diffuse_color=mathutils.Color((0, 0, 0))
   mat.use_textures=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
   mat.use_vertex_color_light=False
   mat.use_vertex_color_paint=False
   mat.use_object_color=False
   mat.use_face_texture=False
   mat.use_face_texture_alpha=False
   mat.raytrace_mirror.use=False
   mat.use_transparency=False
   mat.use_shadeless=True
   mat.alpha=1
   bpy.context.scene.render.image_settings.color_mode = 'RGB'

print("Playercolor mask done.")

