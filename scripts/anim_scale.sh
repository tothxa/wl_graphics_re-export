#!/bin/sh

if [ $# -lt 2 ]; then
  echo "Usage: $0 <new_size_at_scale_1> <images>"
  echo "   Width and height must be equal."
  echo "   The images should be in the same directory, because scaled files will be"
  echo "   written to the directory of the first file."
  exit 1
fi

echo "Size at scale 1: $1"
SIZEHALF=$(($1 / 2))
shift

DIR=$(dirname "$1")
TMP=$(mktemp -d)

if [ ! -d $TMP ]; then
  echo "Couldn't create tmp dir."
  exit 1
fi

for F in "$@"; do
  FN=${F%.png}
  TMPF=${TMP}/$(basename "$FN")

  if [ ! -f "${FN}.png" ]; then
    echo "${FN}.png not found"
    exit 1
  fi

  SIZE=$SIZEHALF
  for SC in 0.5 1 2 4 ; do
    TF=${TMPF}_${SC}.png
    convert ${FN}.png -filter catrom -resize ${SIZE}x${SIZE} $TF

    SIZE=$(($SIZE * 2))
  done
done

CROP="$($(dirname $0)/get_crop.sh ${TMP}/*_0.5.png | tail -1)"

if [ $# -gt 1 -a "${CROP%% *}" != "Common:" ]; then
  echo "Images have different sizes:"
  identify -format "%f: %wx%h\n" "$@"
  exit 1
fi

read IGN_NAME IGN_TOT_W IGN_TOT_H MARG_LEFT WIDTH MARG_RIGHT MARG_TOP HEIGHT MARG_BOTTOM <<EOF
$CROP
EOF

for MARG in $MARG_LEFT $MARG_RIGHT $MARG_TOP $MARG_BOTTOM ; do
  if [ $MARG = 0 ]; then
    echo "Too small margin found:"
    echo "   $CROP"
    exit 1
  fi
done

CR_W=$(($WIDTH + 2))
CR_H=$(($HEIGHT + 2))
OFF_X=$(($MARG_LEFT - 1))
OFF_Y=$(($MARG_TOP - 1))

for SC in 0.5 1 2 4 ; do
  CROP_GEOM=${CR_W}x${CR_H}+${OFF_X}+${OFF_Y}
  echo "Scale: $SC     Crop geometry: $CROP_GEOM"
  for TF in ${TMP}/*_${SC}.png ; do
    SCF=${DIR}/$(basename "$TF")
    convert $TF -crop $CROP_GEOM $SCF
  done

  CR_W=$(($CR_W * 2))
  CR_H=$(($CR_H * 2))
  OFF_X=$(($OFF_X * 2))
  OFF_Y=$(($OFF_Y * 2))
done

