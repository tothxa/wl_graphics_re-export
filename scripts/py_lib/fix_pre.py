from statistics import mean

from py_lib.parse_init_luas import items, typemap, sizemap

# We can't do this right on creating pre[anim] entry, because we need all
# animations first
def fix_pre_hotspots(name) :
  missing = []
  xs = []
  ys = []
  for anim in items[name].pre.values() :
    if anim.hot_x == None or anim.hot_y == None :
      missing.append(anim)
    else :
      xs.append(anim.hot_x)
      ys.append(anim.hot_y)
  if len(xs) > 0 and len(ys) > 0 :
    mx = round(mean(xs))
    my = round(mean(ys))
    for anim in missing :
      anim.hot_x = mx
      anim.hot_y = my
  else :
    # Let's calculate some rough default.
    # Approximations used:
    #   We treat it as if it were a building
    #   "SW" wall goes to 1/3 of width, rest is "SE"
    #   Door is in the middle of "SE" wall
    #   Southernmost corner is the bottom of the image
    #   Tangent of "SE" wall bottom edge angle from X axis in screen projection
    #     is 0.42
    for anim in missing :
      anim.hot_x = anim.xoff + round(anim.x * 2 / 3)
      anim.hot_y = anim.yoff + anim.y - round(anim.x * 0.42 / 3)

