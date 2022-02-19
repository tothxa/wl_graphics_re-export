#!/usr/bin/mawk -f

# input format: <filename>,<width>,<height>,<cropped_width>,<cropped_height>,<left_margin>,<top_margin>
#                $1         $2      $3       $4              $5               $6            $7
# needs 2 lines of input: first is data for the new high resolution file, second is data for old scale 1 file

BEGIN { FS = "," }
NF == 7 {
  print $1, $2, $3, $4, $5
  if (NR == 1) {
    new = $1
    new_W = $2
    new_H = $3
    new_w = $4
    new_h = $5
  } else {
    old = $1
    old_w = $4
    old_h = $5
  }
}
/^$/ { --NR }  # ignore the empty line that 'identify' prints at the end
END {
  if (NR != 2) {
    print "2 lines of input are needed!"
    exit 1
  }
  scale_w = old_w / new_w
  scale_h = old_h / new_h
  size_w = new_W * scale_w
  size_h = new_H * scale_h
  print "Scale:", scale_w, scale_h, "     Size:", size_w, size_h, "\n"
}

