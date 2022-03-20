import os
import re
import sys

from py_lib.lua_init import lua
from py_lib.size_and_crop import size_and_crop_full
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.query_items import get_anim, has_key_new

def store_new(name, anim, imgprops_pre, hotspot_new) :
  if not name in typemap :
    typemap[name] = "unknown"
  if not name in items :
    items[name] = lua.table()
  if not "pre" in items[name] :
    items[name].pre = lua.table()
  # must create pre[anim]
  items[name].pre[anim] = imgprops_pre
  if not "new" in items[name] :
    # new ones shouldn't have different hotspots, first call stores it,
    # others give the same numbers, so we just ignore it
    items[name].new = hotspot_new

def pre_hot_1(old_size, old_off, old_hot, new_size, new_off) :
  return new_off + (old_hot - old_off) * new_size / old_size

fnparse = re.compile("([a-z_]+)_(idle|working|build|unoccupied|empty)_([0-9]+)x([0-9]+)_1\.png")
hsparse = re.compile("^([0-9]*),([0-9]*)$")

def new_hotspot_init(dir, prefix, fn) :
  fnmatch = fnparse.match(fn)
  if fnmatch == None :
    return None
  item = prefix + fnmatch.group(1)
  anim = fnmatch.group(2)
  cols = int(fnmatch.group(3))
  rows = int(fnmatch.group(4))
  pre = size_and_crop_full(os.path.join(dir, fn), cols, rows)
  old = get_anim(item, "old", anim)
  if not old :
    print("Animation not found: ", item, anim, file = sys.stderr)
    pre.hot_x = None
    pre.hot_y = None
  else :
    hot_x = pre_hot_1(old.x, old.xoff, old.hot_x, pre.x, pre.xoff)
    hot_y = pre_hot_1(old.y, old.yoff, old.hot_y, pre.y, pre.yoff)
    pre.hot_x = round(hot_x)
    pre.hot_y = round(hot_y)
    # print("{:s} {:s} {:1.0f},{:1.0f}".format(item, anim, hot_x, hot_y))
  new = None
  if not has_key_new(item) :
    hotspotfile = os.path.join(dir, fnmatch.group(1) + ".hotspot")
    # file_ok means we can safely create it or replace first line with hotspot value
    new = lua.table(hsfile = hotspotfile, hot_x = None, hot_y = None, file_ok = True)
    hss = ""
    if os.access(hotspotfile, os.F_OK | os.R_OK) :
      if not os.access(hotspotfile, os.W_OK) :
        new.file_ok = False
      hsf = open(hotspotfile)
      hss = hsf.readline()
      hsf.close()
    hsmatch = hsparse.match(hss)
    if hsmatch :
      new.hot_x = int(hsmatch.group(1))
      new.hot_y = int(hsmatch.group(2))
    elif hss != "" and hss != "\n" :
      new.file_ok = False
  store_new(item, anim, pre, new)

