import Blender
from Blender import Scene, Object, Camera
from Blender.Scene import Render

import math
import os

maincontrol = Blender.Object.Get("MainLightControl")

rot = maincontrol.RotZ
print "Original direction: %6.1f" % (rot * 180 / math.pi)

render_anim = os.getenv("SINGLEFRAME") == None

base_angle_s = os.getenv("ANG_SW")
if base_angle_s :
  base_angle = float(base_angle_s)
else :
  base_angle = 0

print "South-West direction: %6.1f" % base_angle

scene = Blender.Scene.GetCurrent()
context = scene.getRenderingContext()

# old blender is terrible...
outdir = os.getcwd() + os.sep + Blender.sys.makename(Blender.Get("filename"), strip=1)
if not render_anim :
  context.startFrame(1)
  context.endFrame(1)

# These should actually be int multiples of 60 degrees. Widelands SE, NE,
# SW and NW are just approximate shorthand names. Unfortunately all current
# animations were rendered with real-world (multiple of 45 degrees) SE, NE,
# SW and NW, so we keep to that.
# SW seems to be the base direction in the old menu.py -- this was changed
# to SE in menu_b25.py to match the orientation of buildings in Widelands.
#
# We're rotating the lights and the camera around the model, so angles are
# backwards.
for (n, a) in [("_sw_", 0), ("_w_", 45), ("_nw_", 90), ("_ne_", 180), ("_e_", -135), ("_se_", -90)] :
  maincontrol.RotZ = (base_angle + a) * math.pi / 180
  context.renderPath = outdir + n + os.sep
  rot = maincontrol.RotZ * 180 / math.pi
  fp = context.renderPath
  print "Angle: %4s = %6.1f  -- Rendering to %40s" % (n, rot, fp)
  context.renderAnim()

