import sys

import sdl2

from py_lib.dialogs import error
from py_lib.screen_size import canvas_w, canvas_h, zoom
import py_lib.sdl_init
from py_lib.sdl_text import render_text
from py_lib.background import background
from py_lib.drawlist import drawlist

main_window = sdl2.SDL_CreateWindow(b"Test Hotspots",
  sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
  canvas_w, canvas_h, sdl2.SDL_WINDOW_SHOWN)
if not main_window :
  error("Couldn't create main window.")
  sys.exit(1)
mainw_surf = sdl2.SDL_GetWindowSurface(main_window)

def draw_items(poslist, itemlist) :
  for i in range(min(len(poslist), len(itemlist))) :
    if itemlist[i] and itemlist[i].imgsurf :
      src = sdl2.SDL_Rect(
              x = 0,
              y = 0,
              w = itemlist[i].xoff + itemlist[i].x,
              h = itemlist[i].yoff + itemlist[i].y)
      dst = sdl2.SDL_Rect(
              x = poslist[i][0] - itemlist[i].hot_x,
              y = poslist[i][1] - itemlist[i].hot_y,
              w = 0,
              h = 0)
      sdl2.SDL_BlitSurface(itemlist[i].imgsurf, src, mainw_surf, dst)

def redraw() :
  sdl2.SDL_BlitSurface(background, None, mainw_surf, None)

  # draw base overlays
  first = True
  for bpos in drawlist.base_positions :
    dst = sdl2.SDL_Rect(
            x = bpos[0] - drawlist.base_overlay.hotspot.x,
            y = bpos[1] - drawlist.base_overlay.hotspot.y,
            w = drawlist.base_overlay.imgsurf.contents.w,
            h = drawlist.base_overlay.imgsurf.contents.h)
    if first :
      zoomrect = sdl2.SDL_Rect(
                   x = 0,
                   y = 0,
                   w = dst.x + dst.w,
                   h = dst.y + dst.h)
      first = False
    sdl2.SDL_BlitSurface(drawlist.base_overlay.imgsurf, None, mainw_surf, dst)

  for i in ["items", "items_compare", "items_over"] :
    draw_items(drawlist.item_positions, drawlist[i])

  # draw zoomed image
  zoomdst = sdl2.SDL_Rect(x = zoomrect.w, y = 0,
                          w = zoomrect.w * zoom, h = zoomrect.h * zoom)
  sdl2.SDL_BlitScaled(mainw_surf, zoomrect, mainw_surf, zoomdst)

  # draw labels
  for i in range(min(len(drawlist.label_positions), len(drawlist.labels))) :
    if drawlist.labels[i] :
      dst = sdl2.SDL_Rect(
              x = drawlist.label_positions[i][0],
              y = drawlist.label_positions[i][1],
              w = 0,
              h = 0)
      sdl2.SDL_BlitSurface(drawlist.labels[i], None, mainw_surf, dst)

  # TODO: help hint

  sdl2.SDL_UpdateWindowSurface(main_window)

def destroy_main_window() :
  sdl2.SDL_FreeSurface(mainw_surf)
  sdl2.SDL_DestroyWindow(main_window)

