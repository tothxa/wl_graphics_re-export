#!/bin/sh

NAME=$(basename $(realpath .))

PC_DIR="${NAME}_*_pc_*_*x*_*.png"
PC="${NAME}_*_pc_*x*_*.png"
SHEET="${NAME}_*_*x*_*.png"

# this needs to be done separately, as there's ambiguity of which '*' picks
# up the direction part of the filename with $SHEET above
SHEET_DIR="${NAME}_*_*_*x*_*.png"

if [ "$(echo $PC_DIR)" != "$PC_DIR" ] ; then
  mmv "$PC_DIR" "#1_#2_#5_pc.png"
fi

if [ "$(echo $SHEET_DIR)" != "$SHEET_DIR" ] ; then
  mmv "$SHEET_DIR" "#1_#2_#5.png"
fi

if [ "$(echo $PC)" != "$PC" ] ; then
  mmv "$PC" "#1_#4_pc.png"
fi

if [ "$(echo $SHEET)" != "$SHEET" ] ; then
  mmv "$SHEET" "#1_#4.png"
fi

