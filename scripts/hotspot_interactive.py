#!/usr/bin/env python3

# Dependencies:
# - lupa (lua python module)
# - pgmagick (graphicsmagick python module)
# - PySDL2 (SDL2 python module)
# - yad (yet another dialog command line tool)

# initialise parser
import py_lib.lua_init
import py_lib.parse_init_luas

# read old definitions and new images
import py_lib.read_spritesheets

# initialise SDL
import ctypes
import sdl2
import py_lib.sdl_init
from py_lib.sdl_init import sdl_shutdown

# initialise and select current item
from py_lib.select_item import select_new_item
import py_lib.current_item
from py_lib.current_item import set_current, switch_anim, save_hotspot, \
  change_hotspot, reset_hotspot

# initialise main window
from py_lib.display import refresh, redraw, destroy_main_window

redraw()

# main event loop
ev = sdl2.SDL_Event()
stop = False
while not stop :
  while sdl2.SDL_PollEvent(ctypes.byref(ev)) != 0:
    if ev.type == sdl2.SDL_QUIT :
      stop = True
    elif ev.type == sdl2.SDL_KEYDOWN :
      if ev.key.keysym.sym == sdl2.SDLK_q :
        stop = True
      if ev.key.keysym.sym == sdl2.SDLK_n :
        (new_name, new_anim) = select_new_item()
        if new_name :
          set_current(new_name, new_anim)
          redraw()
      if ev.key.keysym.sym == sdl2.SDLK_c :
        switch_anim()
        redraw()
      #if ev.key.keysym.sym == sdl2.SDLK_h or ev.key.keysym.sym == sdl2.SDLK_QUESTION :
      #  TODO: show help window
      if ev.key.keysym.sym == sdl2.SDLK_UP :
        change_hotspot("y", 1)
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_DOWN :
        change_hotspot("y", -1)
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_LEFT :
        change_hotspot("x", 1)
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_RIGHT :
        change_hotspot("x", -1)
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_BACKSPACE or ev.key.keysym.sym == sdl2.SDLK_BACKSPACE :
        reset_hotspot()
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_s and (ev.key.keysym.mod & sdl2.KMOD_CTRL) != 0 :
        save_hotspot()
        # to update status text
        redraw()
  refresh()

# clean up, just to be nice :)
sdl_shutdown()
destroy_main_window()

