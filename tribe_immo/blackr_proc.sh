#!/bin/sh

X=55
Y=862
DX=296
DXR=0
DY=-127

FRAMES=1

for GROWSTEP in tiny small medium ripe harvested; do
  for FR in $(seq $FRAMES); do
    W=296
    H=288

    OUTPREFIX=blackroot_field_${GROWSTEP}_0${FR}
    SIZE4F=${OUTPREFIX}_4.png
    convert blackroot_field000${FR}.png -crop ${W}x${H}+${X}+${Y} $SIZE4F

    for SC in 2 1 0.5; do
      W=$(($W / 2))
      H=$(($H / 2))
      convert $SIZE4F -filter catrom -resize ${W}x${H} ${OUTPREFIX}_${SC}.png
    done
  done

  X=$(($X + $DX + $DXR))
  Y=$(($Y + $DY))
  DXR=$((($DXR + 1) % 2))
done
