convert -size 190x190 xc:transparent \
  -stroke gray -strokewidth 10 \
    -draw 'path M12,76,L140,76' \
    -draw 'path M44,172,L172,172' \
  -fill none -strokewidth 8.4 \
    -draw 'path M12,76,L76,12' \
    -draw 'path M76,12,L140,76' \
    -draw 'path M44,172,L108,108' \
    -draw 'path M108,108,L172,172' \
  -fill '#FF000080' \
    -draw 'point 44,44' \
    -draw 'point 108,44' \
    -draw 'point 76,76' \
    -draw 'point 76,140' \
    -draw 'point 140,140' \
    -draw 'point 108,172' \
  -fill transparent \
    -draw 'point 12,76' \
    -draw 'point 76,12' \
    -draw 'point 140,76' \
    -draw 'point 44,172' \
    -draw 'point 108,108' \
    -draw 'point 172,172' \
  /tmp/road_walk.png