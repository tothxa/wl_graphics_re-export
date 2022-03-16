from statistics import mean

from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap

def get_anim(name, which, anim) :
  if not name in items :
    return None
  if not which in items[name] :
    return None
  if which == "new" :
    return get_new(name, anim)
  if not anim in items[name][which] :
    return None
  return items[name][which][anim]

def get_new(name, anim) :
  # we need this because we don't want to use different hotspots for the
  # animations of the new spritesheets, but the cropping may be different
  a = get_anim(name, "pre", anim)
  if a == None :
    return None
  rv = lua.table_from(a)
  # this is safe, because .new is always created with .pre
  # hot_x and hot_y are always set together
  if items[name].new.hot_x :
    rv.hot_x = items[name].new.hot_x
    rv.hot_y = items[name].new.hot_y
    rv.status = "stored"
  else :
    rv.hot_x = round(mean([anim.hot_x for anim in items[name].pre.values() if anim.hot_x]))
    rv.hot_y = round(mean([anim.hot_y for anim in items[name].pre.values() if anim.hot_y]))
    rv.status = "preliminary"
  return rv

def has_key_new(name) :
  if not name in items :
    return False
  return "new" in items[name]

