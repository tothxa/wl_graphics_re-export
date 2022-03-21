import os
import sys

# parse arguments:
from py_lib.cmdline import luapaths, newpaths

from py_lib.dialogs import warning
from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.new_hotspot import new_hotspot_init

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

