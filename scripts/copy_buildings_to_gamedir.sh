#!/bin/sh

if [ $# -ne 2 ]; then
  echo "Usage: $0 <tribe> <game_datadir>"
  exit 1
fi

case "$1" in
  amazons|atlanteans|barbarians|empire|frisians)
    TRIBE=$1
  ;;
  am|amz)
    TRIBE=amazons
  ;;
  at|atl)
    TRIBE=atlanteans
  ;;
  b|ba|bar)
    TRIBE=barbarians
  ;;
  e|em|emp)
    TRIBE=empire
  ;;
  f|fr|fri)
    TRIBE=frisians
  ;;
  *)
    echo "Invalid tribe name: '$1'"
    exit 1
  ;;
esac

TYPES="productionsites militarysites trainingsites warehouses"

is_buildings_dir () {
  for T in $TYPES ; do
    if ! [ -d "$1/$T" ]; then
      return 1
    fi
  done
  return 0
}

GAMEDIR=""
for SUBDIR in "" "/data/tribes/buildings" "/tribes/buildings" "/buildings"
do
  TRY="$2$SUBDIR"
  if [ -d "$TRY" ]; then 
    if is_buildings_dir "$TRY" ; then
      GAMEDIR="$TRY"
      break
    fi
  fi
done

if [ -z "$GAMEDIR" ]; then
  echo "Invalid directory: '$2'"
  exit 1
fi

FINAL_NAME="$(dirname $0)/final_name.sh"
if ! [ -x "$FINAL_NAME" ]; then
  FINAL_NAME=""
fi

find_target () {
  for T in $TYPES ; do
    D="${GAMEDIR}/${T}/${TRIBE}/$1"
    if [ -d "$D" ]; then
      echo "$D"
      return 0
    fi
  done
  return 1
}

SUFFIX="_idle_1x1_1.png"
GLOB='_*[0-9]x[0-9]*_[0-4].*png'
for i in $(find . -name "*$SUFFIX" ) ; do
  BUILDING="$(basename $i $SUFFIX)"
  SRCDIR="$(dirname $i)"
  TGTDIR="$(find_target $BUILDING)"
  if [ -z "$TGTDIR" ]; then
    echo "No target for '$BUILDING' ($i)"
    continue
  fi

  # this is needed for e.g. coalmine vs. coalmine_deep
  for PRG in idle build working unoccupied empty ; do
    BASE="${SRCDIR}/${BUILDING}_${PRG}"
    if [ "$(echo -n "${BASE}"${GLOB})" != "${BASE}${GLOB}" ]; then
      echo "Copying files for $BASE"
      cp -pi "${BASE}"$GLOB "$TGTDIR"
    fi
  done

  if [ -n "$FINAL_NAME" ]; then
    cd "$TGTDIR"
    "$FINAL_NAME"
    cd -
  fi
done

