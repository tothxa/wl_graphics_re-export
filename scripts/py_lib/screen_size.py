margin = 15
trianglew = 64
triangleh = 32
zoom = 4
# max_ovl_x = max([o.step.x for o in overlays.values()]) + 2 * margin
max_ovl_x = 256 + 2 * margin
# max_ovl_y = max([o.step.y for o in overlays.values()]) + 2 * margin
max_ovl_y = 192 + 2 * margin
canvas_w = (zoom + 1) * max_ovl_x
canvas_h = max(3, zoom) * max_ovl_y

