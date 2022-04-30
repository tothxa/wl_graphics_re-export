import os
import Blender
from Blender import Scene, Object, Camera
from Blender.Scene import Render

imgsize_s = os.getenv("IMGSIZE")
if imgsize_s and imgsize_s.isdigit() :
  imgsize = int(imgsize_s)
else :
  imgsize = 1000

print "Image size: ", imgsize

scene = Scene.GetCurrent()
render = scene.getRenderingContext()
render.imageSizeX(imgsize)
render.imageSizeY(imgsize)
render.enableOversampling(True)
render.enableBorderRender(False)
render.crop = False

camscale_s = os.getenv("SCALE")
if camscale_s :
  camscale = float(camscale_s)

off_x_s = os.getenv("XOFFSET")
if off_x_s :
  off_x = float(off_x_s)

off_y_s = os.getenv("YOFFSET")
if off_y_s :
  off_y = float(off_y_s)

# camera = Camera.Get(scene.objects.camera.name)
for camera in Camera.Get():
  if camscale_s :
    camera.setScale(camscale)
  elif camera.getScale() == 6.25 :
    camera.setScale(6.5)
  print "Camera: %s   Scale: %6.3f" % (camera.name, camera.getScale())
  if off_x_s :
    camera.shiftX = off_x
    print "      x offset: %6.3f" % camera.shiftX
  if off_y_s :
    camera.shiftY = off_y
    print "      y offset: %6.3f" % camera.shiftY

