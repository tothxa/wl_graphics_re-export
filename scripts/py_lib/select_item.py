import sys

from py_lib.dialogs import warning, listselect, listselect_cols, filters_dialog
from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap

new_buildings = sorted(
  [name for name in items
    if typemap[name] == "static" and "pre" in items[name]])

# TODO: show status in list, filter by status
def select_new_item() :
  name = listselect(new_buildings, "Building", title = "Select building",
    text = "Please select which building's hotspot you would like to edit")
  if not name :  # selection cancelled
    return [None, None]
  anims = sorted(list(items[name].pre))
  if len(anims) > 1 :
    anim = listselect(anims, "Animation", title = "Select animation",
      text = "Please select which animation of " + name +
        " you would like to see for editing the hotspot")
    if not anim :  # selection cancelled
      return [None, None]
  else :
    anim = anims[0]
  return [name, anim]


