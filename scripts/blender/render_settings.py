import os
import bpy

imgsize_s = os.getenv("IMGSIZE")
if imgsize_s and imgsize_s.isdigit() :
  imgsize = int(imgsize_s)
else :
  imgsize = 1000

# big:   1000
# medium: 800
# small:  600
# worker: 400

print("Image size: ", imgsize)

camscale_s = os.getenv("SCALE")
if camscale_s :
  camscale = float(camscale_s)

off_x_s = os.getenv("XOFFSET")
if off_x_s :
  off_x = float(off_x_s)

off_y_s = os.getenv("YOFFSET")
if off_y_s :
  off_y = float(off_y_s)

for scene in bpy.data.scenes:
   scene.render.resolution_x = imgsize
   scene.render.resolution_y = imgsize
   scene.render.resolution_percentage = 100
   scene.render.use_border = False
   scene.render.use_antialiasing = True
   scene.render.antialiasing_samples = '16'
   scene.render.pixel_filter_type = 'MITCHELL'
   scene.render.alpha_mode = 'TRANSPARENT'

   camera = scene.camera
   if camscale_s :
      camera.data.ortho_scale = camscale
   elif camera.data.ortho_scale == 6.25 :
      camera.data.ortho_scale = 6.5
   print("Camera: {}   Scale: {:7.3f}".format(camera.name, camera.data.ortho_scale))
   if off_x_s :
      camera.data.shift_x = off_x
      print("      x offset: {:6.3f}".format(camera.data.shift_x))
   if off_y_s :
      camera.data.shift_y = off_y
      print("      y offset: {:6.3f}".format(camera.data.shift_y))

