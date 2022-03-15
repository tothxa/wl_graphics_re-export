#!/usr/bin/env python3

# Dependencies:
# - lupa (lua python module)
# - pgmagick (graphicsmagick python module)
# - PySDL2 (SDL2 python module)
# - yad (yet another dialog command line tool)

import io
import os
import re
import subprocess
import sys
from statistics import mean

import lupa
import pgmagick

##### Dialogs #####

def listselect(list, header, text, title = "Please select") :
  opts = []
  if text :
    opts += ["--text", text]
  result = subprocess.run(["yad", "--list", "--title", title,
    "--height", str(min(len(list) * 20, 600)), "--column", header,
    "--separator="] + opts + list, capture_output = True, text = True)
  if result.returncode != 0 or result.stdout == "" :
    return None
  return result.stdout.splitlines()[0]

def warning(text) :
  subprocess.run(["yad", "--image=dialog-warning", "--title=Warning",
    "--button=Close!window-close", "--buttons-layout=center", "--text", text],
    capture_output = False)

def error(text) :
  subprocess.run(["yad", "--image=dialog-error", "--title=Error",
    "--button=Close!window-close", "--buttons-layout=center", "--text", text],
    capture_output = False)


###################

#
# TODO: use argparse, use dialogs for specifying directories when no command
# line arguments are given
#

argc = len(sys.argv) - 1
if argc < 2 or argc > 3 :
  print("Usage: " + sys.argv[0] + " <widelands_datadir> <new_images_dir> [<tribename_prefix>_]")
  sys.exit(1)

pref = ""
if argc == 3 :
  pref = sys.argv[3]


###################

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


#################### lua code for reading old definitions ####################

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
  items = {}

  function descriptions:new_static(def)
    sz = def.size
    if sz == "medium" or sz == "mine" or sz == "none" then
      sz = "small"
    end
    if sz == "port" then
      sz = "big"
    end
    items[def.name] = { old = parse_anims(def) }
    sizemap[def.name] = sz
    typemap[def.name] = "static"
  end

  moving_items = {}
  function descriptions:new_moving(def)
    items[def.name] = { old = parse_anims(def) }
    typemap[def.name] = "moving"
  end
  
  ships = {}
  function descriptions:new_ship_type(def)
    items[def.name] = { old = parse_anims(def) }
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
### end of lua definitions ###


###################### read all spritesheet definitions ######################

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
  if not name in items :
    return None
  if not which in items[name] :
    return None
  if which == "new" :
    return get_new(name, anim)
  if not anim in items[name][which] :
    return None
  return items[name][which][anim]

def get_new(name, anim) :
  # we need this because we don't want to use different hotspots for the
  # animations of the new spritesheets, but the cropping may be different
  a = get_anim(name, "pre", anim)
  if a == None :
    return None
  rv = lua.table_from(a)
  # this is safe, because .new is always created with .pre
  # hot_x and hot_y are always set together
  if items[name].new.hot_x :
    rv.hot_x = items[name].new.hot_x
    rv.hot_y = items[name].new.hot_y
    rv.status = "stored"
  else :
    rv.hot_x = round(mean([anim.hot_x for anim in items[name].pre.values() if anim.hot_x]))
    rv.hot_y = round(mean([anim.hot_y for anim in items[name].pre.values() if anim.hot_y]))
    rv.status = "preliminary"
  return rv

def has_key_new(name) :
  if not name in items :
    return False
  return "new" in items[name]

def store_new(name, anim, imgprops_pre, hotspot_new) :
  if not name in typemap :
    typemap[name] = "unknown"
  if not name in items :
    items[name] = lua.table()
  if not "pre" in items[name] :
    items[name].pre = lua.table()
  # must create pre[anim]
  items[name].pre[anim] = imgprops_pre
  if not "new" in items[name] :
    # new ones shouldn't have different hotspots, first call stores it,
    # others give the same numbers, so we just ignore it
    items[name].new = hotspot_new

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
  pre = size_and_crop_full(os.path.join(dir, fn), cols, rows)
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
  if not has_key_new(item) :
    hotspotfile = os.path.join(dir, fnmatch.group(1) + ".hotspot")
    # file_ok means we can safely create it or replace first line with hotspot value
    new = lua.table(hsfile = hotspotfile, hot_x = None, hot_y = None, file_ok = True)
    hss = ""
    if os.access(hotspotfile, os.F_OK | os.R_OK) :
      if not os.access(hotspotfile, os.W_OK) :
        new.file_ok = False
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


# We can't do this right on creating pre[anim] entry, because we need all
# animations first
def fix_pre_hotspots(name) :
  missing = []
  xs = []
  ys = []
  for anim in items[name].pre.values() :
    if anim.hot_x == None or anim.hot_y == None :
      missing.append(anim)
    else :
      xs.append(anim.hot_x)
      ys.append(anim.hot_y)
  if len(xs) > 0 and len(ys) > 0 :
    mx = round(mean(xs))
    my = round(mean(ys))
    for anim in missing :
      anim.hot_x = mx
      anim.hot_y = my
  else :
    # Let's calculate some rough default.
    # Approximations used:
    #   We treat it as if it were a building
    #   "SW" wall goes to 1/3 of width, rest is "SE"
    #   Door is in the middle of "SE" wall
    #   Southernmost corner is the bottom of the image
    #   Tangent of "SE" wall bottom edge angle from X axis in screen projection
    #     is 0.42
    for anim in missing :
      anim.hot_x = anim.xoff + round(anim.x * 2 / 3)
      anim.hot_y = anim.yoff + anim.y - round(anim.x * 0.42 / 3)


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

scriptdir = os.path.dirname(sys.argv[0])

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
    # TODO: annotate with name, anim name, hotspot coords and status (set/new/changed/can't save)


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


new_buildings = sorted([name for name in items if typemap[name] == "static" and "pre" in items[name]])

def select_building() :
  building = listselect(new_buildings, "Building", "Select building",
    "Please select which building's hotspot you would like to edit")
  anims = sorted(list(items[building].pre))
  if len(anims) > 1 :
    anim = listselect(anims, "Animation", "Select animation",
      "Please select which animation of " + building +
      " you would like to see for editing the hotspot")
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
        current_item = select_building()
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

