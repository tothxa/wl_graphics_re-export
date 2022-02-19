#!/usr/bin/mawk -f

# input format: <filename>,<width>,<height>,<cropped_width>,<cropped_height>,<left_margin>,<top_margin>
#                $1         $2      $3       $4              $5               $6            $7
#
# output: <filename> <width> <height> <left_margin> <cropped_width> <right_margin> <top_margin> <cropped_height> <bottom_margin>

BEGIN { FS = "," }
NF == 7 {
  right_m = $2 - $4 - $6
  bottom_m = $3 - $5 - $7
  if (NR == 1) {
    min_l = $6
    min_r = right_m
    min_top = $7
    min_btm = bottom_m
    W = $2
    H = $3
  } else {
    if ($6 < min_l) min_l = $6
    if ($7 < min_top) min_top = $7
    if (right_m < min_r) min_r = right_m
    if (bottom_m < min_btm) min_btm = bottom_m
    if ($2 != W) W = 0
    if ($3 != H) H = 0
  }
  print $1, $2, $3, $6, $4, right_m, $7, $5, bottom_m
}
/^$/ { --NR }  # ignore the empty line that 'identify' prints at the end
END {
  if (NR > 1) {
    if (W * H > 0) {
      print "Common:", W, H, min_l, W - min_l - min_r, min_r, min_top, H - min_top - min_btm, min_btm
    } else {
      print "Min. margins:", min_l, min_r, min_top, min_btm
    }
  }
}

