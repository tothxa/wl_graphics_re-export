import Blender
from Blender import Scene, Object, Camera
from Blender.Scene import Render

def dump(obj, name):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "%s.%s = %s" % (name, attr, getattr(obj, attr)))

scene = Scene.GetCurrent()
render = scene.getRenderingContext()
render.imageSizeX(1000)
render.imageSizeY(1000)
render.enableOversampling(True)
render.crop = False

dump(render, "Render")
dump(scene.objects.camera, "Camera")
# camera = Camera.get(scene.objects.camera.name)
# if camera.getScale() == 6.25 :
#    camera.setScale(6.5)
# print "Scale: %6.3f" % camera.getScale()

