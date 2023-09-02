#!/bin/sh

X=74
Y=582
DX=208
DY=-89

FRAMES=5

for GROWSTEP in tiny small medium ripe; do
  for FR in $(seq $FRAMES); do
    W=208
    H=184

    OUTPREFIX=reedfield_${GROWSTEP}_0${FR}
    SIZE4F=${OUTPREFIX}_4.png
    convert reedfield000${FR}.png -crop ${W}x${H}+${X}+${Y} $SIZE4F

    for SC in 2 1 0.5; do
      W=$(($W / 2))
      H=$(($H / 2))
      convert $SIZE4F -filter catrom -resize ${W}x${H} ${OUTPREFIX}_${SC}.png
    done
  done

  X=$(($X + $DX))
  Y=$(($Y + $DY))
done
