import sys

import sdl2
import sdl2.sdlimage

from py_lib.lua_init import lua
from py_lib.overlays import overlays, walk_hotspots
from py_lib.sdl_text import render_text
import py_lib.sdl_init

drawlist = lua.table(
  base_overlay = None,
  base_positions = [],
  zoomrect = sdl2.SDL_Rect(0, 0, 0, 0),
  item_positions = [],
  items = [],

  # these will be shown semi-transparent over the main items
  # this is meant to be used to compare with similar items or enhancements
  items_compare = [],

  # these will be shown over the main and compare items
  # this is meant to show how workers enter/leave a building
  # and to pair soldiers for attack/evade/die
  items_over = [],

  label_positions = [],
  labels = []
  )

def clear_compare() :
  drawlist.items_compare = []

def clear_over() :
  drawlist.items_over = []

def fetch_image(item) :
  if not item.imgsurf:
    imgsurf = sdl2.sdlimage.IMG_Load(item.file.encode())
    if imgsurf :
      sdl2.SDL_SetSurfaceBlendMode(imgsurf, sdl2.SDL_BLENDMODE_BLEND)
      item.imgsurf = imgsurf
    else :
      print("Couldn't load " + imgname, file = sys.stderr)
      return False
  return True

def set_base_positions() :
  drawlist.base_positions = drawlist.base_overlay.poslist
  drawlist.zoomrect = sdl2.SDL_Rect(
    x = 0,
    y = 0,
    w = drawlist.base_positions[0][0] - drawlist.base_overlay.hotspot.x +
        drawlist.base_overlay.imgsurf.contents.w,
    h = drawlist.base_positions[0][1] - drawlist.base_overlay.hotspot.y +
        drawlist.base_overlay.imgsurf.contents.h)
  drawlist.label_positions = [[3, 0]] + [
    [3, drawlist.zoomrect.h + i * drawlist.base_overlay.step.y]
      for i in range(len(drawlist.base_positions) - 1)]

def set_static_drawitems(size, itemlist) :
  clear_compare()
  clear_over()
  drawlist.base_overlay = overlays[size]
  for item in itemlist :
    fetch_image(item)
  drawlist.items = itemlist
  set_base_positions()
  drawlist.item_positions = drawlist.base_positions

### TODO: set_moving_drawitems()
# Must add directional animations in the same order as the hotspot offsets.
# Maybe separate directional and non-directional functions are best.
# (soldier attack/evade/die East/West can NOT be handled as directional,
#  because they have different hotspots, which need separate editing)

# We create separate SDL surfaces for these, so that the alpha mod change
# doesn't affect the original items.
def set_compare_drawitems(itemlist) :
  for item in drawlist.items_compare :
    sdl2.SDL_FreeSurface(item.imgsurf)
  drawlist.items_compare = []
  for item in itemlist :
    item_copy = lua.table()
    for f in ("file", "x", "y", "xoff", "yoff", "hot_x", "hot_y") :
      item_copy[f] = item[f]
    if fetch_image(item_copy) :
      sdl2.SDL_SetSurfaceAlphaMod(item_copy.imgsurf, 100)
      drawlist.items_compare.append(item_copy)
    else :
      drawlist.items_compare.append(None)

def set_over_drawitems(itemlist) :
  for item in itemlist :
    fetch_image(item)
  drawlist.items_over = itemlist

def set_labels(label_list) :
  for label in drawlist.labels :
    sdl2.SDL_FreeSurface(label)
  drawlist.labels = []
  for label in label_list :
    drawlist.labels.append(render_text(label))

# Only the first one needs frequent updates
def update_label_0(new_label) :
  sdl2.SDL_FreeSurface(drawlist.labels[0])
  drawlist.labels[0] = render_text(new_label)

