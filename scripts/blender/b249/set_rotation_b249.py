import Blender
from Blender import Scene, Object, Camera
from Blender.Scene import Render

import math
import os

maincontrol = Blender.Object.Get("MainLightControl")
scene = Blender.Scene.GetCurrent()
context = scene.getRenderingContext()

rot = maincontrol.RotZ
print "Original direction: %6.1f" % (rot * 180 / math.pi)

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
  maincontrol.RotZ = angle * math.pi / 180
  rot = maincontrol.RotZ * 180 / math.pi
  print "New direction: %6.1f" % (rot * 180 / math.pi)
else :
  print "ANGLE was not given, not rotating."

