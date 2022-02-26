#!/bin/sh

if [ $# -lt 2 -o $# -gt 3 ]; then
  echo "Usage: $0 <image> <new_width_at_scale_1> [<new_height_at_scale_1>]"
  exit 1
fi

FN=${1%.png}

if [ ! -f "${FN}.png" ]; then
  echo "${FN}.png not found"
  exit 1
fi

TMP=$(mktemp -d)

if [ ! -d $TMP ]; then
  echo "Couldn't create tmp dir."
  exit 1
fi

TMPF=${TMP}/$(basename "$FN")

W=$(($2 / 2))

if [ $# -eq 3 ]; then
  echo "Size at scale 1: ${2}x$3"
  H=$(($3 / 2))
else
  echo "Size at scale 1: $2"
  H=$W
fi

for SC in 0.5 1 2 4 ; do
  TF=${TMPF}_${SC}.png
  SCF=${FN}_${SC}.png
  convert ${FN}.png -filter catrom -resize ${W}x${H} $TF

  if [ $SC = "0.5" ]; then
    CROP="$($(dirname $0)/get_crop.sh ${TMPF}_${SC}.png)"

    read IGN_NAME IGN_TOT_W IGN_TOT_H MARG_LEFT WIDTH MARG_RIGHT MARG_TOP HEIGHT MARG_BOTTOM <<-EOF
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

  else
    CR_W=$(($CR_W * 2))
    CR_H=$(($CR_H * 2))
    OFF_X=$(($OFF_X * 2))
    OFF_Y=$(($OFF_Y * 2))
  fi

  CROP_GEOM=${CR_W}x${CR_H}+${OFF_X}+${OFF_Y}
  echo "Scale: $SC     Crop geometry: $CROP_GEOM"
  convert $TF -crop $CROP_GEOM $SCF

  W=$(($W * 2))
  H=$(($H * 2))
done

