#!/bin/sh

if [ $# != 3 ]; then
  echo "Usage: $0 <animation_name> <cols>x<rows> <basename>"
  echo
  echo "  Basename is the name of the animation steps without the sequence numbers,"
  echo "  the scale and the extension."
  echo "  Images must be named <basename><seq_num>_<scale>.png"
  echo "  Output files will be <animation_name>_<cols>x<rows>_<scale>.png"
  exit 1
fi

TMP=$(mktemp -d)

if [ ! -d $TMP ]; then
  echo "Couldn't create tmp dir."
  exit 1
fi

for SCALE in 0.5 1 2 4 ; do
  EXT=_${SCALE}.png
  IN_GLOB="${3}*$EXT"
  OUT="${1}_${2}$EXT"
  TMPOUTB="${TMP}/$(basename $1)"
  TMPOUT1="${TMPOUTB}_first$EXT"
  TMPOUTQ="${TMPOUTB}_quant$EXT"
  GEOM=$(identify -format '%wx%h\n' $IN_GLOB | uniq)
  if [ -n "$GEOM" -a $(echo "$GEOM" | wc -l) -eq 1 ]; then
    montage -background transparent -tile $2 -geometry $GEOM $IN_GLOB -depth 8 "$TMPOUT1"
    pngquant "$TMPOUT1" -o "$TMPOUTQ"
    advpng -z2 -q "$TMPOUTQ"
    mv "$TMPOUTQ" "$OUT"
  else
    echo
    echo "WARNING: Skipping scale ${SCALE}: images have different sizes or no images found"
    ls $IN_GLOB
    echo
  fi
done

