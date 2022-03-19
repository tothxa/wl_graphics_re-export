import sys

import sdl2

from py_lib.dialogs import error
from py_lib.screen_size import margin, trianglew, triangleh, canvas_w, canvas_h
import py_lib.sdl_init

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

