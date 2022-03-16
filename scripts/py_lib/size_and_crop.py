# Dependencies:
# - lupa (lua python module)
# - pgmagick (graphicsmagick python module)

import os
import sys

import pgmagick

from py_lib.lua_init import lua

def size_and_crop_full(imgf, cols, rows) :
  try :
    img = pgmagick.Image(imgf)
  except Exception as ex :
    print("Couldn't open ", imgf, file = sys.stderr)
    print(ex, file = sys.stderr)
    return None
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
  for ext in ("_1.png", "_00.png", ".png") :
    imgf = basename + ext
    if os.access(imgf, os.F_OK) :
      return size_and_crop_full(imgf, cols, rows)
  print("No image file found for basename: ", basename, file = sys.stderr)
  return None

