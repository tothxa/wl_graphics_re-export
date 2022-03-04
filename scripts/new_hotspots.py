#!/usr/bin/env python3

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
  return lua.table(x = bb.width(), y = bb.height(), xoff = bb.xOff(), yoff = bb.yOff())

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

  items = {}
  descriptions = {}
  function descriptions:new(def)
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
        box = size_and_crop_base(dirname .. "/" .. name, sprsh.columns, sprsh.rows)
        box.hot_x = sprsh.hotspot[1]
        box.hot_y = sprsh.hotspot[2]
        imgs[name] = box
      end
    end
    items[def.name] = imgs
  end

  for i, type in ipairs { "constructionsite", "dismantlesite", "militarysite", "productionsite",
      "trainingsite", "warehouse", "carrier", "ferry", "immovable", "ship", "soldier", "ware",
      "worker" } do
    descriptions["new_"..type.."_type"] = descriptions.new
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

def new_hot_1(old_size, old_off, old_hot, new_size, new_off) :
  return new_off + (old_hot - old_off) * new_size / old_size

fnparse = re.compile("([a-z_]+)_(idle|working|build|unoccupied|empty)_([0-9]+)x([0-9]+)_1\.png")

def new_hotspot(dir, fn) :
  fnmatch = fnparse.match(fn)
  if fnmatch == None :
    return None

  item = pref + fnmatch.group(1)
  anim = fnmatch.group(2)
  cols = int(fnmatch.group(3))
  rows = int(fnmatch.group(4))

  item_old = lua.eval("items." + item)
  if not item_old :
    print("No matching old item found: ", item, file = sys.stderr)
    return None
  old = item_old[anim]
  if not old :
    print("Animation not found: ", item, anim, file = sys.stderr)
    return None
  new = size_and_crop_full(dir + "/" + fn, cols, rows)

  hot_x = new_hot_1(old.x, old.xoff, old.hot_x, new.x, new.xoff)
  hot_y = new_hot_1(old.y, old.yoff, old.hot_y, new.y, new.yoff)
  print("{:s} {:s} {:1.0f},{:1.0f}".format(item, anim, hot_x, hot_y))

def do_new(dir) :
  for entry in os.scandir(dir) :
    if entry.is_dir() :
      do_new(entry.path)
    else :
      new_hotspot(dir, entry.name)

do_new(sys.argv[2])

