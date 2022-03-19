import sys

import sdl2

from py_lib.dialogs import error
from py_lib.screen_size import canvas_w, canvas_h, zoom
import py_lib.sdl_init

canvas = sdl2.SDL_CreateRGBSurface(0, canvas_w, canvas_h, 32, 0, 0, 0, 0)
if not canvas :
  error("Canvas surface creation failed.")
  sys.exit(1)

# Source rectangle of the canvas area to be zoomed
zoomrect = sdl2.SDL_Rect(0, 0, 0, 0)

