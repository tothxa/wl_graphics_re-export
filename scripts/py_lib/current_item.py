import os
import sys

from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.query_items import get_anim, get_new, has_key_new
from py_lib.fix_pre import fix_pre_hotspots
from py_lib.drawlist import set_static_drawitems, set_compare_drawitems, \
  set_over_drawitems, set_labels, update_label_0, fetch_image
from py_lib.select_item import select_new_item

current_item = lua.table(name = "", anim = "", new = None, labels = [])

def format_new_label() :
  # TODO: show if can't save
  current_item.labels[0] = "{:s}: {:s}  {:d},{:d}  {:s}".format(
    current_item.name, current_item.anim,
    current_item.new.hot_x, current_item.new.hot_y,
    current_item.new.status)

def update_new_label() :
  format_new_label()
  update_label_0(current_item.labels[0])

def set_current(name, anim) :
  pre = get_anim(name, "pre", anim)
  if pre.hot_x == None or pre.hot_y == None :
    fix_pre_hotspots(name)
  fetch_image(pre)
  new = get_new(name, anim)
  old = None
  if "old" in items[name] :
    it_old = items[name].old
    if anim in it_old :
      old = it_old[anim]
    elif anim != "idle" and "idle" in it_old :
      old = it_old.idle
    else :
      old = it_old[list(it_old)[0]]
  # TODO: labels: old and pre hotspots, old anim name if different
  if old :
    set_static_drawitems(sizemap[name], [new, old, pre])
    labels = ["new", "current", "preliminary"]
  else :
    set_static_drawitems(sizemap[name], [new, pre])
    labels = ["new", "preliminary"]
  current_item.name = name
  current_item.anim = anim
  current_item.new = new
  current_item.labels = labels
  format_new_label()
  set_labels(current_item.labels)

# let's select one before initialising main window
building_selected = False
while not building_selected :
  (name, anim) = select_new_item()
  if not name :
    print("Selection cancelled, exiting.", file = sys.stderr)
    sys.exit(0)
  if typemap[name] == "static" :
    building_selected = True
  else :
    warning("Only buildings are implemented.")
set_current(name, anim)

def switch_anim() :
  # TODO: select and switch anim
  #       should preserve changed hotspot?
  pass

def change_hotspot(dir, val) :
  current_item.new.status = "changed"
  current_item.new["hot_" + dir] += val
  update_new_label()

def reset_hotspot() :
  # 1. It may still be None
  # 2. current_item.new = get_new() would invalidate the drawlist entry
  n = get_new(current_item.name, current_item.anim)
  current_item.new.hot_x = n.hot_x
  current_item.new.hot_y = n.hot_y
  current_item.new.status = n.status
  update_new_label()

def save_hotspot() :
  if current_item.new.status == "stored" :
    return
  item = items[current_item.name].new
  hssl = [""]
  if not item.file_ok :
    warning("Hotspot can't be saved!")
    return
  if os.access(item.hsfile, os.F_OK) :
    if os.access(item.hsfile, os.R_OK | os.W_OK) :
      hsf = open(item.hsfile)
      hssl = hsf.readlines()
      hsf.close()
    else :
      item.file_ok = False
      current_item.file_ok = False
      warning("Hotspot can't be saved!")
      return
  elif not os.access(os.path.dirname(item.hsfile), os.W_OK | os.X_OK) :
    item.file_ok = False
    current_item.file_ok = False
    warning("Hotspot can't be saved!")
    return
  hssl[0] = "{:d},{:d}\n".format(current_item.new.hot_x, current_item.new.hot_y)
  hsf = open(item.hsfile, "w")
  for l in hssl :
    hsf.write(l)
  hsf.close()
  item.hot_x = current_item.new.hot_x
  item.hot_y = current_item.new.hot_y
  item.status = "stored"
  current_item.new.status = "stored"
  update_new_label()

