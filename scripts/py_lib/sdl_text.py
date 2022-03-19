# Dependencies:
# - PySDL2
# - fontconfig
import subprocess

import sdl2.sdlttf

from py_lib.dialogs import warning
import py_lib.sdl_init

font = None
getfont_result = subprocess.run(["fc-match", ":fontformat=truetype:family=sans",
  "--format", "%{file}"], capture_output = True, text = True)
if getfont_result.returncode != 0 or getfont_result.stdout == "" :
  warning("Can't find system truetype fonts. No texts will be shown in graphics window.")
else :
  if sdl2.sdlttf.TTF_Init() < 0 :
    warning("Couldn't initialise SDL TTF module. No texts will be shown in graphics window.")
  else :
    font = sdl2.sdlttf.TTF_OpenFont(getfont_result.stdout.encode(), 20)
    if font == None :
      warning("Couldn't initialise font. No texts will be shown in graphics window.")
    else :
      txtcolour = sdl2.SDL_Color(r = 255, g = 255, b = 0, a = 255)

def render_text(text) :
  if font == None :
    return None
  return sdl2.sdlttf.TTF_RenderText_Blended(font, text.encode(), txtcolour)

