### TODO: carrier and flag overlays

import os
import sys

import sdl2
import sdl2.sdlimage

from py_lib.screen_size import margin, trianglew, triangleh, canvas_w, canvas_h
from py_lib.dialogs import error
from py_lib.lua_init import lua
import py_lib.sdl_init

scriptdir = os.path.dirname(__file__)

def load_overlay_image(imgname) :
  imgname_b = os.path.join(scriptdir, "imgs", imgname).encode()
  imgsurf = sdl2.sdlimage.IMG_Load(imgname_b)
  if imgsurf :
    sdl2.SDL_SetSurfaceBlendMode(imgsurf, sdl2.SDL_BLENDMODE_BLEND)
  else :
    error("Couldn't load " + imgname)
    sys.exit(1)
  return imgsurf

# Sorry, lua tables are so much easier than python dicts. :)
# OOP is not my thing either.
#
# The road overlays were created with graphicsmagick, because SDL doesn't
# support drawing thick lines. As there's no direct interface between pgmagick
# and PySDL2, it's easier to use pre-created files than to recreate them on
# each run.
overlays = lua.eval('''
  { small =
    { hotspot = {x = 75, y = 100},
      step = {x = 128, y = 128},
      imgsurf = python.eval('load_overlay_image("road_small.png")')
    },
    big =
    { hotspot = {x = 141, y = 141},
      step = {x = 256, y = 192},
      imgsurf = python.eval('load_overlay_image("road_big.png")')
    },
    walk =
    { hotspot = {x = 45, y = 45},
      step = {x = 192, y = 192},
      imgsurf = python.eval('load_overlay_image("road_walk.png")')
    },
  }
''')

walk_hotspots = lua.eval('''
  {
    ne = { x =  0, y =  0 },
    se = { x = 64, y =  0 },
    e  = { x = 32, y = 32 },
    sw = { x = 32, y = 96 },
    nw = { x = 96, y = 96 },
    w  = { x = 64, y =128 },
  }
''')

def get_positions(hot_x, hot_y, step_x, step_y) :
  def first_pos(hotspot_coord) :
    # '- 1' before '//' so that we don't have to special case '% trianglew == 0';
    # '+ 1' at the end is to compensate for off-by-one difference with Widelands
    return margin + ((hotspot_coord - margin - 1) // trianglew + 1) * trianglew + 1

  x1 = first_pos(hot_x)
  y1 = first_pos(hot_y)
  if x1 % trianglew >= triangleh and y1 % trianglew >= triangleh :
    x1 -= triangleh
    y1 -= triangleh

  # only 3 places (new, old, pre) on the left side, leaving room for
  # one zoomed image (of new) on the right
  return [[x1, y1 + i * step_y] for i in range(3)]

for o in overlays.values() :
  o.poslist = get_positions(o.hotspot.x, o.hotspot.y, o.step.x, o.step.y)

