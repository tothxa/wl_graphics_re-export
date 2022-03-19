import sdl2
import sdl2.sdlimage
import sdl2.sdlttf

if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0 :
  error("SDL initialisation failed.")
  sys.exit(1)

if sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG) < 0 :
  error("SDL Image initialisation failed.")
  sys.exit(1)

def sdl_shutdown() :
  sdl2.sdlimage.IMG_Quit()
  sdl2.sdlttf.TTF_Quit()

