import bpy
import math
import os

rot = bpy.data.objects['MainLightControl'].rotation_euler.z
print("Original direction: {:6.1f}".format(180 * rot / math.pi))

# Rotation should actually be an int multiple of 60 degrees. Widelands "SE",
# "NE", "SW" and "NW" are just approximate shorthand names. Unfortunately all
# current animations were rendered with real-world (multiple of 45 degrees)
# SE, NE, SW and NW, so you should stick to that.
# SW seems to be the base direction in the old menu.py -- this was changed
# to SE in menu_b25.py to match the orientation of buildings in Widelands.
# Most models were made with the old conventions, so 0 is often SW.
#
# We're rotating the lights and the camera around the model, so angles are
# backwards.

angle_s = os.getenv("ANGLE")
if angle_s :
  angle = float(angle_s)
  bpy.data.objects['MainLightControl'].rotation_euler.z = angle * math.pi / 180
  rot = bpy.data.objects['MainLightControl'].rotation_euler.z
  print("New direction: {:6.1f}".format(180 * rot / math.pi))
else :
  print("ANGLE was not given, not rotating.")

