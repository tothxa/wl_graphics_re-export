# TODO: store filters by selection type?
#       maybe in a static dict, where key would be passed by caller to select_impl?

import sys

from py_lib.dialogs import warning, listselect, listselect_cols, filters_dialog
from py_lib.lua_init import lua
from py_lib.query_items import get_status
from py_lib.parse_init_luas import items, typemap, sizemap
from py_lib.utils import flatten

new_buildings = sorted(
  [name for name in items
    if typemap[name] == "static" and "pre" in items[name]])

def select_anim(name, which) :
  anims = []
  for w in which :
    al = None
    if items[name][w] :
      al = list(items[name][w])
    if al :
      anims += al
  if not anims :
    return None
  anims = sorted(set(anims))
  if len(anims) < 1 :
    return None
  if len(anims) > 1 :
    anim = listselect(anims, "Animation", title = "Select animation",
      text = "Please select which animation of " + name +
        " you would like to see for editing the hotspot")
    if not anim :  # selection cancelled
      return None
  else :
    anim = anims[0]
  return anim

# I'm afraid that the order may get messed up in the dialog if it's a dict of
# { <name> = { type = ..., values = ...}, ...}
all_filters = [
  dict(name = "type",   type = ":CB",
        values = "clear!static!moving"),
  dict(name = "status", type = ":CB",
        values = "clear!old!new!preliminary!stored"),
  dict(name = "tribe",  type = ":CB",
        values = "clear!world!amazons!atlanteans!barbarians!empire!frisians"),
  dict(name = "name",   type = "", values = "")]

def mark_value(options, selected) :
  if selected == "clear" :
    return options
  opt_part = options.partition(selected)
  if opt_part[1] == "" :  # not found
    return options
  return opt_part[0] + "^" + opt_part[1] + opt_part[2]

def select_filters(filters) :
  selected = []
  for f in all_filters :
    fn = f["name"]
    if fn not in filters :
      continue
    ft = f["type"]
    if ft == "" :
      fv = filters[fn]
    else :
      fv = mark_value(f["values"], filters[fn])
    selected.append(dict(name = fn, type = f["type"], values = fv))
  return selected

def filter_list(l, filters) :
  filtered = l.copy()
  for fn in filters :
    fv = filters[fn]
    if fv == "clear" or fv == "" :
      continue
    elif fn == "type" :
      filtered = [ i for i in filtered if typemap[i] == fv ]
    elif fn == "status" :
      if fv == "old" :
        filtered = [ i for i in filtered if not "pre" in items[i] ]
      else :
        filtered = [ i for i in filtered if "pre" in items[i] ]
        if fv == "preliminary" :
          filtered = [ i for i in filtered if not items[i].new.hot_x ]
        elif fv == "stored" :
          filtered = [ i for i in filtered if items[i].new.hot_x ]
        # else : it's "new", or something's very wrong...
    elif fn == "tribe" :
      if fv == "world" :
        for t in ["amazons", "atlanteans", "barbarians", "empire",
                  "frisians"] :
          filtered = [ i for i in filtered if not t in i ]
      else :
        filtered = [ i for i in filtered if fv in i ]
    elif fn == "name" :
      filtered = [ i for i in filtered if fv in i ]
  return filtered

headers = ["Name", "Type", "Status"]

def select_impl(prefilter, disable_filters, text, title) :
  itemlist = sorted(list(items))
  remaining_filters = all_filters
  if prefilter :
    itemlist = filter_list(itemlist, prefilter)
  if disable_filters :
    remaining_filters = [f for f in all_filters
                           if not f["name"] in disable_filters]
  current_list = itemlist
  current_filters = None
  while True :  # will exit by one of the returns
    l = flatten([(name, typemap[name], get_status(name))
                  for name in current_list])
    selection = listselect_cols(l, headers, text, title)
    if isinstance(selection, str) :
      return selection
    elif selection == 1 :  # cancel
      return None
    elif selection == 3 :  # filter
      if current_filters :
        filterspec = select_filters(current_filters)
      else :
        filterspec = remaining_filters
      filter = filters_dialog(filterspec)
      if filter :
        new_list = filter_list(itemlist, filter)
        if len(new_list) > 0 :
          current_list = new_list
          current_filters = filter
        else :
          warning("No items are matching filter " + str(filter))

filter_new = dict(type = "static", status = "new")

def select_new_item() :
  name = select_impl(filter_new, ["type"], title = "Select building",
    text = "Please select which building's hotspot you would like to edit")
  if not name :  # selection cancelled
    return [None, None]
  anim = select_anim(name, ["pre"])
  if not anim :  # selection cancelled
    return [None, None]
  return [name, anim]

def select_other() :
  name = select_impl(None, None, title = "Select item for comparison",
    text = "Please select item to overlay")
  if not name :  # selection cancelled
    return [None, None]
  anim = select_anim(name, ["pre", "old"])
  if not anim :  # selection cancelled
    return [None, None]
  return [name, anim]

