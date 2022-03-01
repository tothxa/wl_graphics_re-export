#!/bin/sh

if [ $# != 2 ]; then
  echo "Usage: $0 <animation_name> <basename>"
  echo
  echo "  Basename is the name of the scaled images without the scale and the"
  echo "  extension."
  echo "  Images must be named <basename>_<scale>.png"
  echo "  Output files will be <animation_name>_1x1_<scale>.png"
  exit 1
fi

TMP=$(mktemp -d)

if [ ! -d $TMP ]; then
  echo "Couldn't create tmp dir."
  exit 1
fi

for SCALE in 0.5 1 2 4 ; do
  EXT=_${SCALE}.png
  IN="${2}$EXT"
  OUT="${1}_1x1$EXT"
  TMPOUT="${TMP}/$(basename $1)$EXT"
  if [ -f "$IN" ]; then
    pngquant "$IN" -o "$TMPOUT"
    advpng -z2 -q "$TMPOUT"
    mv "$TMPOUT" "$OUT"
  else
    echo
    echo "WARNING: File not found for scale ${SCALE}: $IN"
    echo
  fi
done

