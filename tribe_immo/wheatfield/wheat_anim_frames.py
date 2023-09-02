import bpy

parts = ["field_particles", "field_particles.001"]
velo = [None, 0, 0.062, 0.1, 0.062, 0]

scene = bpy.data.scenes[0]

for fno in [1, 2, 3, 4, 5]:
    scene.frame_set(fno)
    for p in parts:
        bpy.data.particles[p].object_align_factor[0] = velo[fno]
    bpy.context.scene.render.filepath = "wheatfield%04d" % fno
    bpy.ops.render.render(write_still = True)

