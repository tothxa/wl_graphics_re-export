# Dependencies:
# - lupa (lua python module)
# - pgmagick (graphicsmagick python module)

from os.path import dirname, join

from py_lib.lua_init import lua
from py_lib.size_and_crop import size_and_crop_full, size_and_crop_base

luafile = join(dirname(__file__), "parse_inits.lua")
lua.execute('dofile(python.eval("luafile"))')

items = lua.eval("items")
typemap = lua.eval("typemap")
sizemap = lua.eval("sizemap")
