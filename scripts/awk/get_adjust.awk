#!/usr/bin/mawk -f

# input format: <filename>,<width>,<height>,<cropped_width>,<cropped_height>,<left_margin>,<top_margin>
#                $1         $2      $3       $4              $5               $6            $7

BEGIN {
  FS = ","
  MIN_MARG = 30
}
NF == 7 {
  file = $1
  W = $2
  H = $3
  w = $4
  h = $5
  l = $6
  t = $7

  r = W - l - w
  b = H - t - h

  off_x = (l - r) / 2.0 / W
  off_y = (b - t) / 2.0 / H

  scale_x = (w + 2.0 * MIN_MARG) / W
  scale_y = (h + 2.0 * MIN_MARG) / H

  if (scale_x < scale_y) {
    scale = scale_y
  } else {
    scale = scale_x
  }

  printf("%-30s Xoff: %6.3f  Yoff: %6.3f  Scale: %5.3f\n", file, off_x, off_y, scale)
}
/^$/ {}  # delete the empty line that 'identify' prints at the end
