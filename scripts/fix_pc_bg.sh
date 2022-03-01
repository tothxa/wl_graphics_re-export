#!/bin/sh

TMP=$(mktemp -d)

if [ ! -d $TMP ]; then
  echo "Couldn't create tmp dir."
  exit 1
fi

for IMG in "$@" ; do
  TMPIMG="${TMP}/$(basename $IMG)"
  if GEOM=$(identify -format '%wx%h' $IMG) ; then
    montage -background black -geometry $GEOM $IMG -depth 8 "$TMPIMG"
    mv "$TMPIMG" "$IMG"
  else
    echo
    echo "WARNING: Skipping file ${IMG}"
    echo "$GEOM"
    echo
  fi
done

