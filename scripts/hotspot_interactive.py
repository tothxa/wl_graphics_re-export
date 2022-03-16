#!/usr/bin/env python3

# Dependencies:
# - lupa (lua python module)
# - pgmagick (graphicsmagick python module)
# - PySDL2 (SDL2 python module)
# - yad (yet another dialog command line tool)

import os
import subprocess
import sys

# parse arguments:
from py_lib.cmdline import luapaths, newpaths

from py_lib.dialogs import listselect, warning, error
from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.query_items import get_anim, get_new, has_key_new
from py_lib.new_hotspot import new_hotspot_init
from py_lib.fix_pre import fix_pre_hotspots


###################### read all spritesheet definitions ######################

def parse_inits(dir) :
  for entry in os.scandir(dir) :
    if entry.is_dir() :
      parse_inits(entry.path)
    elif entry.name == "init.lua" :
      lua.eval("dofile('" + entry.path + "')")

if luapaths :
  for luadir in luapaths :
    parse_inits(luadir)
else :
  warning("No Lua directories were given. Item types cannot be determined, "
    "hotspots cannot be precalculated.")
# TODO: dialogs allowing selection of luapaths (while ask : select)

def do_new(dir, prefix) :
  for entry in os.scandir(dir) :
    if entry.is_dir() :
      do_new(entry.path, prefix)
    else :
      new_hotspot_init(dir, prefix, entry.name)

have_new = False

for k in newpaths :
  prefix = k
  dirs = newpaths[k]
  if dirs :
    for dir in dirs :
      have_new = True
      do_new(dir, prefix)

if not have_new:
  warning("No directories of new images. Nothing to do!")
  sys.exit(1)
# TODO: dialogs allowing selection of newpaths (while ask : while select tribe : select path)


############################# prepare for display #############################

import ctypes

import sdl2
import sdl2.sdlimage
import sdl2.sdlttf


if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0 :
  error("SDL initialisation failed.")
  sys.exit(1)

if sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG) < 0 :
  error("SDL Image initialisation failed.")
  sys.exit(1)

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

margin = 15
trianglew = 64
triangleh = 32
zoom = 4
zoom_x = max([o.step.x for o in overlays.values()]) + 2 * margin
canvas_w = (zoom + 1) * zoom_x
canvas_h = max(3, zoom) * (max([o.step.y for o in overlays.values()]) + 2 * margin)

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

  # use this to fill the whole canvas with items (no zoomed area)
  #return [[x, y] for y in range(y1, (canvas_h + hot_y - step_y), step_y)
  #               for x in range(x1, (canvas_w + hot_x - step_x), step_x)]

  # only 3 places (new, old, pre) on the left side, leaving room for
  # one zoomed image (of new) on the right
  return [[x1, y1 + i * step_y] for i in range(3)]

for ovl in ["small", "big", "walk"] :
  o = overlays[ovl]
  o.poslist = get_positions(o.hotspot.x, o.hotspot.y, o.step.x, o.step.y)

# Debug
# print(overlays.small.poslist)
# print(overlays.big.poslist)

### TODO: carrier and flag overlays

background = sdl2.SDL_CreateRGBSurface(0, canvas_w, canvas_h, 32, 0, 0, 0, 0)
if not background :
  error("Background surface creation failed.")
  sys.exit(1)

background_renderer = sdl2.SDL_CreateSoftwareRenderer(background)
if not background_renderer :
  error("Background renderer creation failed.")
  sys.exit(1)

sdl2.SDL_SetRenderDrawColor(background_renderer, 0, 120, 0, 255)
sdl2.SDL_RenderClear(background_renderer)

sdl2.SDL_SetRenderDrawColor(background_renderer, 0, 0, 0, 255)
for even in [0, triangleh] :
  for y in range(margin + even, canvas_h - margin, trianglew) :
    for x in range(margin + even, canvas_w - margin, trianglew) :
      sdl2.SDL_RenderDrawPoint(background_renderer, x, y)

sdl2.SDL_DestroyRenderer(background_renderer)

getfont_result = subprocess.run(["fc-match", ":fontformat=truetype:family=sans",
  "--format", "%{file}"], capture_output = True, text = True)
if getfont_result.returncode != 0 or getfont_result.stdout == "" :
  warning("Can't find system truetype fonts. No texts will be shown in graphics window.")
if sdl2.sdlttf.TTF_Init() < 0 :
  warning("Couldn't initialise SDL TTF module. No texts will be shown in graphics window.")
font = sdl2.sdlttf.TTF_OpenFont(getfont_result.stdout.encode(), 20)
if font == None :
  warning("Couldn't initialise font. No texts will be shown in graphics window.")
else :
  txtcolour = sdl2.SDL_Color(r = 255, g = 255, b = 0, a = 255)

def render_text(text) :
  if font == None :
    return None
  return sdl2.sdlttf.TTF_RenderText_Blended(font, text.encode(), txtcolour)


### Intermediate SDL surface where we do all the drawing. Will be blitted to
### main window. (in original size and zoomed)
canvas = sdl2.SDL_CreateRGBSurface(0, canvas_w, canvas_h, 32, 0, 0, 0, 0)
if not canvas :
  error("Canvas surface creation failed.")
  sys.exit(1)

# Source rectangle of the canvas area to be zoomed
zoomrect = sdl2.SDL_Rect(0, 0, 0, 0)

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


### for testing
#build_big = [
#  items[name][which].idle
#  for name in sizemap if sizemap[name] == "big"
#  for which in items[name] if which != "new"
#  if fetch_image(items[name][which].idle)
#  ]

#build_small = [
#  items[name][which].idle
#  for name in sizemap if sizemap[name] == "small"
#  for which in items[name] if which != "new"
#  if fetch_image(items[name][which].idle)
#  ]

#place_static(overlays.big, build_big)
#place_static(overlays.small, build_small)
# empty background:
#place_static(overlays.big, [])


new_buildings = sorted(
  [name for name in items
    if typemap[name] == "static" and "pre" in items[name]])

# TODO: show status, filter by status
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


############################## display window ##############################

main_window = sdl2.SDL_CreateWindow(b"Test Hotspots",
  sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
  canvas_w, canvas_h, sdl2.SDL_WINDOW_SHOWN)
if not main_window :
  error("Couldn't create main window.")
  sys.exit(1)
mainw_surf = sdl2.SDL_GetWindowSurface(main_window)

def redraw() :
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

redraw()

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
          redraw()
      #if ev.key.keysym.sym == sdl2.SDLK_c :
      #  TODO: current_item = select_anim(current_item.name)
      #  redraw()
      #if ev.key.keysym.sym == sdl2.SDLK_h or ev.key.keysym.sym == sdl2.SDLK_QUESTION :
      #  TODO: show help window
      if ev.key.keysym.sym == sdl2.SDLK_UP :
        current_item.new.status = "changed"
        current_item.new.hot_y += 1
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_DOWN :
        current_item.new.status = "changed"
        current_item.new.hot_y -= 1
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_LEFT :
        current_item.new.status = "changed"
        current_item.new.hot_x += 1
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_RIGHT :
        current_item.new.status = "changed"
        current_item.new.hot_x -= 1
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_BACKSPACE or ev.key.keysym.sym == sdl2.SDLK_BACKSPACE :
        # 1. It may still be None
        # 2. current_item.new = get_new() would invalidate the draw() function
        n = get_new(current_item.name, current_item.anim)
        current_item.new.hot_x = n.hot_x
        current_item.new.hot_y = n.hot_y
        current_item.new.status = n.status
        redraw()
      if ev.key.keysym.sym == sdl2.SDLK_s and (ev.key.keysym.mod & sdl2.KMOD_CTRL) != 0 :
        save_hotspot()
        # to update status text
        redraw()
  sdl2.SDL_UpdateWindowSurface(main_window)

sdl2.sdlimage.IMG_Quit()
sdl2.sdlttf.TTF_Quit()
sdl2.SDL_FreeSurface(mainw_surf)
sdl2.SDL_DestroyWindow(main_window)

