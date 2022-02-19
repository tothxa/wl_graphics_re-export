import bpy

for scene in bpy.data.scenes:
   print("Scene: ", scene.name)
   print("Resolution: ", scene.render.resolution_x, scene.render.resolution_y)
   print("Percentage: ", scene.render.resolution_percentage)
   print("Border: ", scene.render.use_border)
   print("Anitaliasing: ", scene.render.use_antialiasing, scene.render.antialiasing_samples, scene.render.pixel_filter_type)

   camera = scene.camera
   print("Camera scale: ", camera.data.ortho_scale)

