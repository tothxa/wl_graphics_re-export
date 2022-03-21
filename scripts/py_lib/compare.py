import os
import sys

from py_lib.lua_init import lua
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.query_items import get_anim, get_new
from py_lib.fix_pre import fix_pre_hotspots
from py_lib.drawlist import set_compare_drawitems, set_over_drawitems, \
  clear_compare, clear_over, fetch_image, drawlist
from py_lib.select_item import select_other

compare = lua.table(name = None, anim = None)
over = lua.table(name = None, anim = None)

# TODO: make this work for moving/directional as well
def make_list(name, anim) :
  pre = get_anim(name, "pre", anim)
  if not pre :
    # one of them must exist, otherwise select couldn't return it
    old = get_anim(name, "old", anim)
    return [old] * len(drawlist.item_positions)
  if pre.hot_x == None or pre.hot_y == None :
    fix_pre_hotspots(name)
  fetch_image(pre)
  new = get_new(name, anim)
  if len(drawlist.item_positions) == 3 :
    old = None
    if "old" in items[name] :
      it_old = items[name].old
      if anim in it_old :
        old = it_old[anim]
      elif anim != "idle" and "idle" in it_old :
        old = it_old.idle
      else :
        old = it_old[list(it_old)[0]]
    return [new, old, pre]
  return [new, pre]

def get_items(which) :
  (name, anim) = select_other()
  if not name :
    return None
  which.name = name
  which.anim = anim
  return make_list(name, anim)

def set_compare() :
  cmp_list = get_items(compare)
  if cmp_list :
    # TODO: label?
    set_compare_drawitems(cmp_list)

def set_over() :
  over_list = get_items(over)
  if over_list :
    # TODO: label?
    set_over_drawitems(over_list)

def toggle_compare() :
  if len(drawlist.items_compare) > 0 :
    clear_compare()
  elif not compare.name :
    set_compare()
  else :
    # we need to regenerate the list, because current_item may change, so
    # len(drawlist.item_positions) may also change
    cmp_list = make_list(compare.name, compare.anim)
    if cmp_list :
      # TODO: label?
      set_compare_drawitems(cmp_list)

def toggle_over() :
  if len(drawlist.items_over) > 0 :
    clear_over()
  elif not over.name :
    set_over()
  else :
    # we need to regenerate the list, because current_item may change, so
    # len(drawlist.item_positions) may also change
    over_list = make_list(over.name, over.anim)
    if over_list :
      # TODO: label?
      set_over_drawitems(over_list)

