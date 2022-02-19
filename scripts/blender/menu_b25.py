import bpy
import os.path as ph
import math
import mathutils

base_dirs = [90, 135, 180, 270, 315, 0, 225, 293, 338, 45, 113, 158]

class WidelandsRenderSettings(bpy.types.PropertyGroup):
    prefix = bpy.props.StringProperty(name = "Prefix", description = "Prefix of the image filenames")
    path = bpy.props.StringProperty(name = "Path", description = "Directory to save rendered pics to", subtype='DIR_PATH')
    dir_SW  = bpy.props.BoolProperty(name = "SW" , description = "SouthWest")
    dir_W   = bpy.props.BoolProperty(name = "W"  , description = "West")
    dir_NW  = bpy.props.BoolProperty(name = "NW" , description = "NorthWest")
    dir_NE  = bpy.props.BoolProperty(name = "NE" , description = "NorthEast")
    dir_E   = bpy.props.BoolProperty(name = "E"  , description = "East")
    dir_SE  = bpy.props.BoolProperty(name = "SE" , description = "SouthEast")
    dir_N   = bpy.props.BoolProperty(name = "N"  , description = "North")
    dir_ENE = bpy.props.BoolProperty(name = "ENE", description = "EastNorthEast")
    dir_ESE = bpy.props.BoolProperty(name = "ESE", description = "EastSouthEast")
    dir_S   = bpy.props.BoolProperty(name = "S"  , description = "South")
    dir_WSW = bpy.props.BoolProperty(name = "WSW", description = "WestSouthWest")
    dir_WNW = bpy.props.BoolProperty(name = "WNW", description = "WestNorthWest")
    dir_Orig = bpy.props.BoolProperty(name = "Original pos (buildings)", description = "Make a render with original camera pos as well, can be useful for buildings")

    scale_0_5 = bpy.props.BoolProperty(name = "0.5", description = "Scale to 50%")
    scale_1 = bpy.props.BoolProperty(name = "1", description = "Scale to 100%")
    scale_2 = bpy.props.BoolProperty(name = "2", description = "Scale to 200%")
    scale_4 = bpy.props.BoolProperty(name = "4", description = "Scale to 400%")

    playerColor = bpy.props.BoolProperty(name = "PlayerColors", description = "Render a series with playercolors too. WARNING: Save before, this modifies the file!")
    offset_angle = bpy.props.FloatProperty(name = "Offset Angle", description = "Angle adjustment (degrees)", max=180, min=-180, step=500)
    original_angle = bpy.props.FloatProperty(name = "Original Angle", description = "Original angle before rotation", max=180, min=-180, step=500)
    last_angle = bpy.props.FloatProperty(name = "Last Angle", description = "Last angle we rotated to", max=180, min=-180, step=500)

class WLRenderPanel(bpy.types.Panel):
    bl_label = "Widelands Render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scn = bpy.context.scene
        layout.prop( scn.wl_render_prop, "prefix" )
        layout.prop( scn.wl_render_prop, "path" )
        box = layout.box()
        row = box.row()
        row.label( text="Rendering directions:" )
        row.prop( scn.wl_render_prop, "dir_Orig")
        row = box.row()
        row.prop( scn.wl_render_prop, "dir_SW")
        row.prop( scn.wl_render_prop, "dir_W")
        row.prop( scn.wl_render_prop, "dir_NW")
        row.prop( scn.wl_render_prop, "dir_NE")
        row.prop( scn.wl_render_prop, "dir_E")
        row.prop( scn.wl_render_prop, "dir_SE")
        row = box.row()
        row.prop( scn.wl_render_prop, "dir_N")
        row.prop( scn.wl_render_prop, "dir_ENE")
        row.prop( scn.wl_render_prop, "dir_ESE")
        row.prop( scn.wl_render_prop, "dir_S")
        row.prop( scn.wl_render_prop, "dir_WSW")
        row.prop( scn.wl_render_prop, "dir_WNW")
        box = layout.box()
        row = box.row()
        row.label( text="Scales:" )
        row.prop( scn.wl_render_prop, "scale_0_5")
        row.prop( scn.wl_render_prop, "scale_1")
        row.prop( scn.wl_render_prop, "scale_2")
        row.prop( scn.wl_render_prop, "scale_4")
        row = layout.row()
        row.prop( scn.wl_render_prop, "playerColor")
        row.prop( scn.wl_render_prop, "offset_angle")
        row = layout.row()
        row.operator( "wl.rend", icon='RENDER_ANIMATION' )
        row.operator_menu_enum("wl.rot", 'direction', text="Rotate now!")

def playercolor_mask():
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

class RenderWidelands(bpy.types.Operator):
    bl_idname = "wl.rend"
    bl_label = "Render Animations"

    def do_render_animation(self, mainRot, scn, scale_factor, needed_dirs, dirs, dir_names, filename_suffix):
        original_scale = bpy.context.scene.render.resolution_percentage
        bpy.context.scene.render.resolution_percentage = original_scale * scale_factor
        self.report({'INFO'}, "Scale: %d%%" % bpy.context.scene.render.resolution_percentage)

        numbers_placeholder = '_##'
        if scn.frame_end >= 100:
            numbers_placeholder = numbers_placeholder + '#'

        for i in range(13):
            if needed_dirs[i]:
                mainRot.z = dirs[i]
                scn.render.filepath = ph.join(scn.wl_render_prop.path,scn.wl_render_prop.prefix + dir_names[i] + '_' + str(scale_factor) + numbers_placeholder + filename_suffix)
                bpy.ops.render.render(animation=True)
        bpy.context.scene.render.resolution_percentage = original_scale


    def execute(self, context):
        mainRot = bpy.data.objects['MainLightControl'].rotation_euler
        scn = bpy.context.scene
        wlp = scn.wl_render_prop
        wlp.original_angle = mainRot.z
        needed_dirs = [wlp.dir_SW, wlp.dir_W, wlp.dir_NW, wlp.dir_NE, wlp.dir_E, wlp.dir_SE,
                       wlp.dir_N, wlp.dir_ENE, wlp.dir_ESE, wlp.dir_S, wlp.dir_WSW, wlp.dir_WNW,
                       wlp.dir_Orig]
        dir_names   = ["_sw", "_w", "_nw", "_ne", "_e", "_se",
                       "_n", "_ene", "_ese", "_s", "_wsw", "_wnw",
                       ""]
        dirs = [(dir + wlp.offset_angle)*(2*math.pi/360) for dir in base_dirs]
        dirs.append(wlp.original_angle)

        needed_scales = [wlp.scale_0_5, wlp.scale_1, wlp.scale_2, wlp.scale_4]
        scale_factors = [0.5, 1, 2, 4]

        scn.render.image_settings.color_mode = 'RGBA'

        self.report({'INFO'}, "Rendering animations...")

        for index, scale in enumerate(needed_scales):
            if scale:
                self.do_render_animation(mainRot, scn, scale_factors[index], needed_dirs, dirs, dir_names, '')

        if wlp.playerColor:
            self.report({'INFO'}, "Rendering player colors...")
            playercolor_mask()
            scn.render.image_settings.color_mode = 'RGB'

            for index, scale in enumerate(needed_scales):
                if scale:
                    self.do_render_animation(mainRot, scn, scale_factors[index], needed_dirs, dirs, dir_names, '_pc')

        mainRot.z = wlp.original_angle
        self.report({'INFO'}, "Rendered animations")
        return {'FINISHED'}

class RotateWidelands(bpy.types.Operator):
    bl_idname = "wl.rot"
    bl_label = "Rotate to position"

    direction = bpy.props.EnumProperty(items=(
        ('SW' , 'SW' , "SouthWest"),
        ('W'  , 'W'  , "West"),
        ('NW' , 'NW' , "NorthWest"),
        ('NE' , 'NE' , "NorthEast"),
        ('E'  , 'E'  , "East"),
        ('SE' , 'SE' , "SouthEast"),
        ('N'  , 'N'  , "North"),
        ('ENE', 'ENE', "EastNorthEast"),
        ('ESE', 'ESE', "EastSouthEast"),
        ('S'  , 'S'  , "South"),
        ('WSW', 'WSW', "WestSouthWest"),
        ('WNW', 'WNW', "WestNorthWest"),
        ('ORIG', 'Back', "Rotate back")))

    def execute(self, context):
        mainRot = bpy.data.objects['MainLightControl'].rotation_euler
        scn = bpy.context.scene
        wlp = scn.wl_render_prop
        if(self.direction == 'ORIG'):
            mainRot.z = wlp.original_angle
        else:
            if(mainRot.z != wlp.last_angle):
                wlp.original_angle = mainRot.z
            dir_enum = ['SW', 'W', 'NW', 'NE', 'E', 'SE', 'N', 'ENE', 'ESE', 'S', 'WSW', 'WNW']
            dirs = [(dir + wlp.offset_angle)*(2*math.pi/360) for dir in base_dirs]
            enum_to_dir = dict(zip(dir_enum, dirs))

            mainRot.z = enum_to_dir[self.direction]
            wlp.last_angle = mainRot.z

        self.report({'INFO'}, "Rotated")
        return {'FINISHED'}


def register():
    unregister()
    bpy.utils.register_class( WidelandsRenderSettings )
    bpy.types.Scene.wl_render_prop = bpy.props.PointerProperty(type=WidelandsRenderSettings)
    bpy.utils.register_class( RenderWidelands )
    bpy.utils.register_class( RotateWidelands )
    bpy.utils.register_class( WLRenderPanel )

def unregister():
    try:
        bpy.utils.unregister_class( RenderWidelands )
        bpy.utils.unregister_class( RotateWidelands )
        bpy.utils.unregister_class( WLRenderPanel )
        bpy.utils.unregister_class( WidelandsRenderSettings )
    except RuntimeError:
        pass

def register_standard_menu():
    register()
    if not bpy.context.scene.wl_render_prop.values():
        wlp=bpy.context.scene.wl_render_prop
        wlp.path = "//"
        wlp.prefix = ph.splitext(ph.basename(bpy.data.filepath))[0]
        (wlp.dir_SW, wlp.dir_W, wlp.dir_NW, wlp.dir_NE, wlp.dir_E, wlp.dir_SE,
           wlp.dir_N, wlp.dir_ENE, wlp.dir_ESE, wlp.dir_S, wlp.dir_WSW, wlp.dir_WNW,
           wlp.dir_Orig, wlp.scale_0_5, wlp.scale_1, wlp.scale_2, wlp.scale_4)=(True, True, True, True, True, True,
           False, False, False, False, False, False, False, False, True, False, False)
        wlp.playerColor=False
        wlp.offset_angle=0

def register_building_menu():
    register()
    if not bpy.context.scene.wl_render_prop.values():
        wlp=bpy.context.scene.wl_render_prop
        wlp.path = "//"
        wlp.prefix = ph.splitext(ph.basename(bpy.data.filepath))[0]
        (wlp.dir_SW, wlp.dir_W, wlp.dir_NW, wlp.dir_NE, wlp.dir_E, wlp.dir_SE,
           wlp.dir_N, wlp.dir_ENE, wlp.dir_ESE, wlp.dir_S, wlp.dir_WSW, wlp.dir_WNW,
           wlp.dir_Orig, wlp.scale_0_5, wlp.scale_1, wlp.scale_2, wlp.scale_4)=(False, False, False, False, False, False,
           False, False, False, False, False, False, True, False, True, False, False)
        wlp.playerColor=False
        wlp.offset_angle=0
