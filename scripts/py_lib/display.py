import sys

import sdl2

from py_lib.dialogs import error
from py_lib.screen_size import canvas_w, canvas_h, zoom
import py_lib.sdl_init
from py_lib.sdl_text import render_text
from py_lib.canvas import canvas, zoomrect

main_window = sdl2.SDL_CreateWindow(b"Test Hotspots",
  sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
  canvas_w, canvas_h, sdl2.SDL_WINDOW_SHOWN)
if not main_window :
  error("Couldn't create main window.")
  sys.exit(1)
mainw_surf = sdl2.SDL_GetWindowSurface(main_window)

def redraw(current_item) :
  current_item.draw()
  zoomdst = sdl2.SDL_Rect(x = zoomrect.w, y = 0,
                          w = zoomrect.w * zoom, h = zoomrect.h * zoom)
  sdl2.SDL_BlitScaled(canvas, zoomrect, canvas, zoomdst)
  sdl2.SDL_BlitSurface(canvas, None, mainw_surf, None)
  # TODO: can't save, old and pre txts, txt position, help hint
  txtsurf = render_text("{:s}: {:s}  {:d},{:d}  {:s}".format(
    current_item.name, current_item.anim,
    current_item.new.hot_x, current_item.new.hot_y,
    current_item.new.status))
  if txtsurf != None :
    sdl2.SDL_BlitSurface(txtsurf, None, mainw_surf, None)
  sdl2.SDL_UpdateWindowSurface(main_window)

def destroy_main_window() :
  sdl2.SDL_FreeSurface(mainw_surf)
  sdl2.SDL_DestroyWindow(main_window)

