import argparse

from py_lib.utils import flatten

pargs = argparse.ArgumentParser(
  description = "Program to test and edit hotspots of new image files for "
    "Widelands items.",
  epilog = "All directories will be searched recursively.",
  formatter_class = argparse.RawDescriptionHelpFormatter)

oldargs = pargs.add_argument_group(
  "Old spritesheet and animation definitions",
  "Specify locations of the init.lua files of the current items.\n"
    "This can be the entire 'tribes' and 'world' subdirectories of the\n"
    "Widelands data directory, but not the rest.")
oldargs.add_argument(
  "-lua", "--luapaths", nargs = "*", metavar = "DIR", action = "append",
  help =
    "Directories of existing item definitions, ie. the tribes, workers or "
    "wares directories in the Widelands data directory or their "
    "subdirectories.")

newargs = pargs.add_argument_group(
  "New spritesheet images",
  "These options specify directories containing the new spritesheet images.\n"
    "Spritesheets should be named\n"
    "     <itemname>_<animation>_<cols>x<rows>_<scale>.png\n"
    "\n"
    "If the filenames in a tribe specific directory tree do not contain the\n"
    "tribename prefix, then it can be automatically added with the following\n"
    "options for all spritesheets in the directory tree:")
newargs.add_argument(
  "-amz", "--amazons", dest = "amzpaths", nargs = "*", metavar = "DIR",
  action = "append",
  help = "Prepend 'amazons_' to spritesheet file names in these directories.")
newargs.add_argument(
  "-atl", "--atlanteans", dest = "atlpaths", nargs = "*", metavar = "DIR",
  action = "append",
  help =
    "Prepend 'atlanteans_' to spritesheet file names in these directories.")
newargs.add_argument(
  "-bar", "--barbarians", dest = "barpaths", nargs = "*", metavar = "DIR",
  action = "append",
  help =
    "Prepend 'barbarians_' to spritesheet file names in these directories.")
newargs.add_argument(
  "-emp", "--empire", dest = "emppaths", nargs = "*", metavar = "DIR",
  action = "append",
  help = "Prepend 'empire_' to spritesheet file names in these directories.")
newargs.add_argument(
  "-fri", "--frisians", dest = "fripaths", nargs = "*", metavar = "DIR",
  action = "append",
  help = "Prepend 'frisians_' to spritesheet file names in these directories.")
newargs.add_argument(
  "-nopref", "--no-prefix", dest = "noppaths", nargs = "*", metavar = "DIR",
  action = "append",
  help = "Use spritesheet file names from these directories for item names "
    "as they are.")
# TODO: newargs.add_argument("-cust", "--custom-prefix",
#       dest="custom", nargs="+", metavar="DIR", action=???)

parsed_args = pargs.parse_args()

# I have python 3.7 -- python 3.8 should have action = "extend" to make
# flattening unnecessary
luapaths = flatten(parsed_args.luapaths)
newpaths = {
  "amazons_": flatten(parsed_args.amzpaths),
  "atlanteans_": flatten(parsed_args.atlpaths),
  "barbarians_": flatten(parsed_args.barpaths),
  "empire_": flatten(parsed_args.emppaths),
  "frisians_": flatten(parsed_args.fripaths),
  "": flatten(parsed_args.noppaths) }

