#automask python script (unstable)
#Needs Blender 2.43 or release candidates
#tested on linux build

#CAUTION: Be sure to have saved/copied your model before
#running this. No undo available.

#HOWTO: Add your player color objects to a group named
#PlayerColor in the 'Object and Links' Panel (F7).
#Also, if you just want to use part of a mesh, add a
#material named PlayerColor to it. Make sure there is
#only one PlayerColor material and this same one is
#added to all surfaces that need it.
#Press Alt-P with mouse cursor over this window.

#Note: This Code is awful.
#Don't know why, but with any other attempt to relink materials
#for more than 300 objects/meshes blender 243 segfaults unevitably.
#Under 200 objects it seems to be no problem to change materials
#with NMesh.setMaterials/Object.setMaterials.
#So if you want to improve this code, use at
#least helmsmith-animation for testing.

#Nevertheless...

import Blender as BL

objects = BL.Object.Get()

def blackout_materials():
    materials = BL.Material.Get()
    for material in materials:
        print material.name

        #delete all material ipos
        mipo = material.getIpo()
        if mipo != None:
            material.clearIpo()

        #clear all material texture channels
        for i in [0,1,2,3,4,5,6,7,8,9]:
            material.clearTexture(i)

        #change all present materials to shadeless black
        material.setRGBCol(0.0,0.0,0.0)
        material.setMode("Shadeless")
        material.setAlpha(1.0)


def blackout_objects():
    #define new shadeless materials (black/white)
    shadelessblack = BL.Material.New()
    shadelessblack.setRGBCol(0.0,0.0,0.0)
    shadelessblack.setMode("Shadeless")

    #apply shadeless materials to objects with no materials
    for object in objects:
        objtype = object.getType()
        if objtype == "Mesh":
            nmesh = object.getData()
            if not nmesh.getMaterials():
                if not object.getMaterials():
                    nmesh.materials.append( shadelessblack )
                    nmesh.update()
                else:
                    nmesh.hasVertexColours(0)
                    nmesh.hasFaceUV(0)
                    nmesh.hasVertexUV(0)
                    #nmesh.update()

    #remove all mesh color/uv layers
    meshes = BL.Mesh.Get()
    for mesh in meshes:
        collayers = mesh.getColorLayerNames()
        for coll in collayers:
            mesh.removeColorLayer(coll)
            mesh.update()
        uvlayers = mesh.getUVLayerNames()
        for uvl in uvlayers:
            mesh.removeUVLayer(uvl)
            mesh.update()

def whiteout_objects_in_playercolor_group():
    shadelesswhite = BL.Material.New()
    shadelesswhite.setRGBCol(1.0,1.0,1.0)
    shadelesswhite.setMode("Shadeless")

    #search for player color objects and make them shadeless white
    groups = BL.Group.Get()

    havepcgrp = 0
    havepcobj = 0
    for pcgroup in groups:
        if pcgroup.name == "PlayerColor":
            havepcgrp = 1
            break

    if havepcgrp == 0:
        print "Please add group 'PlayerColor'"
        print "Use 'Object and Links' Panel (F7)"
    else:
        for obj in list(pcgroup.objects):
            if obj.getType() == "Mesh":
                havepcobj = 1
                nmesh = obj.getData(0,0)
                if obj.getMaterials():
                    obj.setMaterials([shadelesswhite])
                #FIXME: it sometimes happens, that faces
                #must be assigned to lower material indices.
                #Without that faces are rendered invisible
                #Should do this automatically here
                nmesh.setMaterials([shadelesswhite])
                obj.colbits = (1<<0)+(1<<0)#...
                nmesh.update()
            else:
                print "Warning 'PlayerColor' object must be mesh type"
    if havepcobj == 0:
        print "Warning: no 'PlayerColor' object found"

def whiteout_player_color_material():
    """
    This searches for a Material calles PlayerColor and makes it shadeless
    white
    """
    try:
        m = BL.Material.Get("PlayerColor")
        m.setRGBCol(1.,1.,1.)
        m.setMode("Shadeless")
    except NameError:
        pass


def setup_world():
    #world and render settings
    world = BL.World.GetCurrent()
    world.setSkytype(0x04)
    world.setHor([0.0,0.0,0.0])
    scene = BL.Scene.GetCurrent()
    context = scene.getRenderingContext()
    context.enableKey()
    context.enableOversampling(0)
    context.enableRGBColor()
    context.setImageType(BL.Scene.Render.PNG)

def main():
    # leave edit mode
    if BL.Window.EditMode():
        BL.Window.EditMode(0)

    blackout_materials()
    blackout_objects()

    whiteout_objects_in_playercolor_group()
    whiteout_player_color_material()
    setup_world()


if __name__ == '__main__':
    main()

