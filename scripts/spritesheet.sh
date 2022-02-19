#!/bin/sh

if [ $# != 2 ]; then
  echo "Usage: $0 <cols>x<rows> <basename>"
  echo
  echo "  Basename is the name of the animation steps without the sequence numbers,"
  echo "  the scale and the extension."
  echo "  Images must be named <basename><seq_num>_<scale>.png"
  echo "  Output files will be <basename>_sheet_<scale>.png"
  exit 1
fi

for SCALE in 0.5 1 2 4 ; do
  EXT=_${SCALE}.png
  IN_GLOB="${2}*$EXT"
  OUT="$2_sheet$EXT"
  GEOM=$(identify -format '%wx%h\n' $IN_GLOB | uniq)
  if [ -n "$GEOM" -a $(echo "$GEOM" | wc -l) -eq 1 ]; then
    montage -tile $1 -geometry $GEOM $IN_GLOB -depth 8 $OUT
  else
    echo
    echo "WARNING: Skipping scale ${SCALE}: images have different sizes or no images found"
    ls $IN_GLOB
    echo
  fi
done

