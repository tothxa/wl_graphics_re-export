#!/bin/sh

NAME=$(basename $(realpath .))

PC="${NAME}_*_pc_*x*_*.png"
SHEET="${NAME}_*_*x*_*.png"

if [ "$(echo $PC)" != "$PC" ] ; then
  mmv "$PC" "#1_#4_pc.png"
fi

if [ "$(echo $SHEET)" != "$SHEET" ] ; then
  mmv "$SHEET" "#1_#4.png"
fi

