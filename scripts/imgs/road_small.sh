convert -size 150x150 xc:transparent \
  -stroke gray -strokewidth 10 \
    -draw 'path M42,67,L106,67' \
    -draw 'path M42,131,L106,131' \
  -fill none -strokewidth 8.4 \
    -draw 'path M74,99,L106,131' \
    -draw 'path M42,67,L10,99' \
    -draw 'path M10,99,L42,131' \
    -draw 'path M106,67,L138,99' \
    -draw 'path M138,99,L106,131' \
  -fill '#FF000080' \
    -draw 'point 74,99' \
  -fill transparent \
    -draw 'point 42,67' \
    -draw 'point 106,67' \
    -draw 'point 10,99' \
    -draw 'point 138,99' \
    -draw 'point 42,131' \
    -draw 'point 106,131' \
  /tmp/road_small.png
