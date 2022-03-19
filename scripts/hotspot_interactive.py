#!/usr/bin/env python3

# Dependencies:
# - lupa (lua python module)
# - pgmagick (graphicsmagick python module)
# - PySDL2 (SDL2 python module)
# - yad (yet another dialog command line tool)

import os
import subprocess
import sys

from py_lib.dialogs import listselect, warning, error
from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.query_items import get_anim, get_new, has_key_new
from py_lib.fix_pre import fix_pre_hotspots

# read old definitions and new images
import py_lib.read_spritesheets
from py_lib.read_spritesheets import new_buildings


############################# prepare for display #############################

import sdl2

import py_lib.sdl_init
from py_lib.sdl_init import sdl_shutdown
from py_lib.overlays import overlays, walk_hotspots
from py_lib.background import background
from py_lib.sdl_text import render_text

from py_lib.screen_size import canvas_w, canvas_h, zoom

from py_lib.canvas import canvas, zoomrect

# For buildings and immovables
def place_static(base_overlay, images) :
  sdl2.SDL_BlitSurface(background, None, canvas, None)
  for i in range(min(len(images), len(base_overlay.poslist))) :
    dst = sdl2.SDL_Rect(
            x = base_overlay.poslist[i][0] - base_overlay.hotspot.x,
            y = base_overlay.poslist[i][1] - base_overlay.hotspot.y,
            w = base_overlay.imgsurf.contents.w,
            h = base_overlay.imgsurf.contents.h)
    if i == 0 :
      zoomrect.w = dst.x + dst.w
      zoomrect.h = dst.y + dst.h
    sdl2.SDL_BlitSurface(base_overlay.imgsurf, None, canvas, dst)
    src = sdl2.SDL_Rect(
            x = 0,
            y = 0,
            w = images[i].xoff + images[i].x,
            h = images[i].yoff + images[i].y)
    dst = sdl2.SDL_Rect(
            x = base_overlay.poslist[i][0] - images[i].hot_x,
            y = base_overlay.poslist[i][1] - images[i].hot_y,
            w = 0,
            h = 0)
    sdl2.SDL_BlitSurface(images[i].imgsurf, src, canvas, dst)


def fetch_image(item) :
  if not item.imgsurf:
    imgsurf = sdl2.sdlimage.IMG_Load(item.file.encode())
    if imgsurf :
      sdl2.SDL_SetSurfaceBlendMode(imgsurf, sdl2.SDL_BLENDMODE_BLEND)
      item.imgsurf = imgsurf
    else :
      print("Couldn't load " + imgname)
      return False
  return True


# TODO: show status in list, filter by status
def select_building() :
  building = listselect(new_buildings, "Building", title = "Select building",
    text = "Please select which building's hotspot you would like to edit")
  if not building :
    return None
  anims = sorted(list(items[building].pre))
  if len(anims) > 1 :
    anim = listselect(anims, "Animation", title = "Select animation",
      text = "Please select which animation of " + building +
        " you would like to see for editing the hotspot")
    if not anim :
      return None
  else :
    anim = anims[0]
  pre = get_anim(building, "pre", anim)
  if pre.hot_x == None or pre.hot_y == None :
    fix_pre_hotspots(building)
  fetch_image(pre)
  new = get_new(building, anim)
  current_item = items[building]
  old = None
  if "old" in items[building] :
    it_old = items[building].old
    if anim in it_old :
      old = it_old[anim]
    elif anim != "idle" and "idle" in it_old :
      old = it_old.idle
    else :
      old = it_old[list(it_old)[0]]
  f = None
  if old :
    fetch_image(old)
    f = lambda : place_static(overlays[sizemap[building]], [new, old, pre])
  else :
    f = lambda : place_static(overlays[sizemap[building]], [new, pre])
  return lua.table(name = building, anim = anim, new = new, draw = f)

# let's select one before initialising main window
current_item = select_building()
if current_item == None :
  print("Selection cancelled, exiting.", file = sys.stderr)
  sys.exit(0)

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

# Initialise main window
from py_lib.display import main_window, redraw, destroy_main_window

redraw(current_item)

import ctypes

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
        new_item = select_building()
        if new_item :
          current_item = new_item
          redraw(current_item)
      #if ev.key.keysym.sym == sdl2.SDLK_c :
      #  TODO: current_item = select_anim(current_item.name)
      #  redraw(current_item)
      #if ev.key.keysym.sym == sdl2.SDLK_h or ev.key.keysym.sym == sdl2.SDLK_QUESTION :
      #  TODO: show help window
      if ev.key.keysym.sym == sdl2.SDLK_UP :
        current_item.new.status = "changed"
        current_item.new.hot_y += 1
        redraw(current_item)
      if ev.key.keysym.sym == sdl2.SDLK_DOWN :
        current_item.new.status = "changed"
        current_item.new.hot_y -= 1
        redraw(current_item)
      if ev.key.keysym.sym == sdl2.SDLK_LEFT :
        current_item.new.status = "changed"
        current_item.new.hot_x += 1
        redraw(current_item)
      if ev.key.keysym.sym == sdl2.SDLK_RIGHT :
        current_item.new.status = "changed"
        current_item.new.hot_x -= 1
        redraw(current_item)
      if ev.key.keysym.sym == sdl2.SDLK_BACKSPACE or ev.key.keysym.sym == sdl2.SDLK_BACKSPACE :
        # 1. It may still be None
        # 2. current_item.new = get_new() would invalidate the draw() function
        n = get_new(current_item.name, current_item.anim)
        current_item.new.hot_x = n.hot_x
        current_item.new.hot_y = n.hot_y
        current_item.new.status = n.status
        redraw(current_item)
      if ev.key.keysym.sym == sdl2.SDLK_s and (ev.key.keysym.mod & sdl2.KMOD_CTRL) != 0 :
        save_hotspot()
        # to update status text
        redraw(current_item)
  sdl2.SDL_UpdateWindowSurface(main_window)

sdl_shutdown()
destroy_main_window()

