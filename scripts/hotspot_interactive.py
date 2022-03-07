#!/usr/bin/env python3

import io
import os
import re
import sys

import lupa
import pgmagick

argc = len(sys.argv) - 1
if argc < 2 or argc > 3 :
  print("Usage: " + sys.argv[0] + " <widelands_datadir> <new_images_dir> [<tribename_prefix>_]")
  sys.exit(1)

pref = ""
if argc == 3 :
  pref = sys.argv[3]

lua = lupa.LuaRuntime(unpack_returned_tuples=False)

def size_and_crop_full(imgf, cols, rows) :
  img = pgmagick.Image(imgf)
  if cols * rows > 1 :
    w = img.columns()
    h = img.rows()
    if w % cols != 0 or h % rows != 0 :
      raise AssertionError
    cropgeom = pgmagick.Geometry(w // cols, h // rows, 0, 0)
    img.crop(cropgeom)
  bb = img.boundingBox()
  return lua.table(file = imgf, x = bb.width(), y = bb.height(), xoff = bb.xOff(), yoff = bb.yOff())

def size_and_crop_base(basename, cols, rows) :
  imgf = basename + "_1.png"
  if not os.access(imgf, os.F_OK) :
    imgf = basename + "_00.png"
  return size_and_crop_full(imgf, cols, rows)

lua.execute('''
  function ignore() end
  pop_textdomain = ignore
  push_textdomain = ignore
  pgettext = ignore
  _ = ignore
  include = ignore  -- used by Amazon and Frisian immovables only (rare trees and berry bushes)

  path = {}
  function path.dirname()
    return python.eval("dir")
  end
  path.list_files = ignore  -- used by soldiers to get level icons

  size_and_crop_base=python.eval("size_and_crop_base")

  function parse_anims(def)
    imgs = {}
    if def.animations then
      for name, anim in pairs(def.animations) do
        if anim.basename then
          bn = anim.basename
        else
          bn = name
        end
        if name == "idle" or bn ~= "idle" then  -- there are some where idle is used as placeholder for working
          box = size_and_crop_base(dirname .. "/" .. bn, 1, 1)
          box.hot_x = anim.hotspot[1]
          box.hot_y = anim.hotspot[2]
          imgs[name] = box
        end
      end
    end
    if def.spritesheets then
      for name, sprsh in pairs(def.spritesheets) do
        dirs = { "" }
        if sprsh.directional then
          dirs = { "_se", "_e", "_ne", "_nw", "_w", "_sw" }
        end
        for i, d in ipairs(dirs) do
          n_d = name .. d
          box = size_and_crop_base(dirname .. "/" .. n_d, sprsh.columns, sprsh.rows)
          box.hot_x = sprsh.hotspot[1]
          box.hot_y = sprsh.hotspot[2]
          imgs[n_d] = box
        end
      end
    end
    return imgs
  end

  typemap = {}
  sizemap = {}

  descriptions = {}
  items = { static = {}, moving = {}, ships = {}, unknown = {} }

  function descriptions:new_static(def)
    sz = def.size
    if sz == "medium" or sz == "mine" or sz == "none" then
      sz = "small"
    end
    if sz == "port" then
      sz = "big"
    end
    items.static[def.name] = { old = parse_anims(def) }
    sizemap[def.name] = sz
    typemap[def.name] = "static"
  end

  moving_items = {}
  function descriptions:new_moving(def)
    items.moving[def.name] = { old = parse_anims(def) }
    typemap[def.name] = "moving"
  end
  
  ships = {}
  function descriptions:new_ship_type(def)
    items.ships[def.name] = { old = parse_anims(def) }
    typemap[def.name] = "ship"
  end

  for i, type in ipairs { "constructionsite", "dismantlesite", "militarysite",
      "productionsite", "trainingsite", "warehouse", "immovable" } do
    descriptions["new_"..type.."_type"] = descriptions.new_static
  end

  for i, type in ipairs { "carrier", "ferry", "soldier", "ware", "worker" } do
    descriptions["new_"..type.."_type"] = descriptions.new_moving
  end

  wl = {}
  function wl.Descriptions()
    return descriptions
  end
''')

def parse_inits(dir) :
  for entry in os.scandir(dir) :
    if entry.is_dir() :
      parse_inits(entry.path)
    elif entry.name == "init.lua" :
      lua.eval("dofile('" + entry.path + "')")

parse_inits(sys.argv[1])

items = lua.eval("items")
typemap = lua.eval("typemap")
sizemap = lua.eval("sizemap")

def get_anim(name, which, anim) :
  t = typemap[name]
  if t == None :
    return None
  if not t in items :
    return None
  if not name in items[t] :
    return None
  if not which in items[t][name] :
    return None
  if not anim in items[t][name][which] :
    return None
  return items[t][name][which][anim]

def get_new(name, anim) :
  # we need this because we don't want to use different hotspots for the
  # animations of the new spritesheets, but the cropping may be different
  a = get_anim(name, "pre", anim)
  if a == None :
    return None

  rv = a.copy()
  # this is safe, because .new is always created with .pre
  rv.hot_x = items[typemap[name]].new.hot_x
  rv.hot_y = items[typemap[name]].new.hot_y
  return rv

def has_new(name) :
  t = typemap[name]
  if t == None :
    return False
  if not name in items[t] :
    return False
  return "new" in items[t][name]

def set_new_hotspot(name, hotspot) :
  # this should only be called when we already have an entry for the new
  # spritesheet
  items[typemap[name]][name].new = hotspot

def store_new(name, anim, imgprops_pre, hotspot_new) :
  t = typemap[name]
  if t == None :
    t = "unknown"
  if not name in items[t] :
    items[t][name] = lua.table()

  if not "pre" in items[t][name] :
    items[t][name].pre = lua.table()
  # must create pre[anim]
  items[t][name].pre[anim] = imgprops_pre

  if not "new" in items[t][name] :
    # new ones shouldn't have different hotspots, first call stores it,
    # others give the same numbers, so we just ignore it
    items[t][name].new = hotspot_new

def pre_hot_1(old_size, old_off, old_hot, new_size, new_off) :
  return new_off + (old_hot - old_off) * new_size / old_size

fnparse = re.compile("([a-z_]+)_(idle|working|build|unoccupied|empty)_([0-9]+)x([0-9]+)_1\.png")
hsparse = re.compile("^([0-9]*),([0-9]*)$")

def new_hotspot_init(dir, fn) :
  fnmatch = fnparse.match(fn)
  if fnmatch == None :
    return None

  item = pref + fnmatch.group(1)
  anim = fnmatch.group(2)
  cols = int(fnmatch.group(3))
  rows = int(fnmatch.group(4))

  pre = size_and_crop_full(dir + "/" + fn, cols, rows)

  # old = lua.eval('get_anim("{}", "{}")'.format(item, anim))
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
  if not has_new(item) :
    hotspotfile = dir + "/" + fnmatch.group(1) + ".hotspot"
    # file_ok means we can safely create it or replace first line with hotspot value
    new = lua.table(hsfile = hotspotfile, hot_x = None, hot_y = None, file_ok = True)
    hss = ""
    if os.access(hotspotfile, os.F_OK) :
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

def do_new(dir) :
  for entry in os.scandir(dir) :
    if entry.is_dir() :
      do_new(entry.path)
    else :
      new_hotspot_init(dir, entry.name)

do_new(sys.argv[2])

import ctypes

import sdl2
import sdl2.sdlimage
import sdl2.sdlttf


