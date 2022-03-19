### Unused -- just to keep around the testing code.
# imports are also missing

def get_positions_all(hot_x, hot_y, step_x, step_y) :
  def first_pos(hotspot_coord) :
    # '- 1' before '//' so that we don't have to special case '% trianglew == 0';
    # '+ 1' at the end is to compensate for off-by-one difference with Widelands
    return margin + ((hotspot_coord - margin - 1) // trianglew + 1) * trianglew + 1

  x1 = first_pos(hot_x)
  y1 = first_pos(hot_y)
  if x1 % trianglew >= triangleh and y1 % trianglew >= triangleh :
    x1 -= triangleh
    y1 -= triangleh

  # use this to fill the whole canvas with items (no zoomed area)
  return [[x, y] for y in range(y1, (canvas_h + hot_y - step_y), step_y)
                 for x in range(x1, (canvas_w + hot_x - step_x), step_x)]

for o in overlays.values() :
  o.poslist = get_positions(o.hotspot.x, o.hotspot.y, o.step.x, o.step.y)

### for testing
build_big = [
  items[name][which].idle
  for name in sizemap if sizemap[name] == "big"
  for which in items[name] if which != "new"
  if fetch_image(items[name][which].idle)
  ]

build_small = [
  items[name][which].idle
  for name in sizemap if sizemap[name] == "small"
  for which in items[name] if which != "new"
  if fetch_image(items[name][which].idle)
  ]

#place_static(overlays.big, build_big)
#place_static(overlays.small, build_small)
# empty background:
#place_static(overlays.big, [])

# Debug
# print(overlays.small.poslist)
# print(overlays.big.poslist)

