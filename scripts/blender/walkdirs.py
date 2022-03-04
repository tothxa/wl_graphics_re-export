import bpy
import math
import os

rot = bpy.data.objects['MainLightControl'].rotation_euler.z
print("Original direction: {:6.1f}".format(180 * rot / math.pi))

render_anim = os.getenv("SINGLEFRAME") == None

base_angle_s = os.getenv("ANG_SW")
if base_angle_s :
  base_angle = float(base_angle_s)
else :
  base_angle = 0

print("South-West direction: {:6.1f}".format(base_angle))

out = bpy.context.scene.render.filepath

# These should actually be int multiples of 60 degrees. Widelands "SE", "NE",
# "SW" and "NW" are just approximate shorthand names. Unfortunately all current
# animations were rendered with real-world (multiple of 45 degrees) SE, NE,
# SW and NW, so we keep to that.
# SW seems to be the base direction in the old menu.py -- this was changed
# to SE in menu_b25.py to match the orientation of buildings in Widelands.
# Most models were made with the old conventions, so we go with SW.
#
# We're rotating the lights and the camera around the model, so angles are
# backwards.
for (n, a) in [("_sw_", 0), ("_w_", 45), ("_nw_", 90), ("_ne_", 180), ("_e_", -135), ("_se_", -90)] :
  bpy.data.objects['MainLightControl'].rotation_euler.z = (base_angle + a) * math.pi / 180
  bpy.context.scene.render.filepath = out + n
  rot = bpy.data.objects['MainLightControl'].rotation_euler.z
  fp = bpy.context.scene.render.filepath
  print("Angle: {:4s} = {:6.1f}  -- Rendering to {:40s}".format(n, rot, fp))
  bpy.ops.render.render(animation=render_anim, write_still = not render_anim)

