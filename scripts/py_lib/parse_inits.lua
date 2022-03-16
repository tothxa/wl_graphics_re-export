function ignore() end
pop_textdomain = ignore
push_textdomain = ignore
pgettext = ignore
include = ignore  -- used by Amazon and Frisian immovables only (rare trees and berry bushes)

function _(arg)
  return arg
end

path = {}
function path.dirname()
  return python.eval("dir") .. "/"
end
path.list_files = ignore  -- used by soldiers to get level icons

size_and_crop_base=python.eval("size_and_crop_base")

function anim_sprsh_common(anim, name, animdir, cols, rows)
  ret = {}
  if anim.directory then
    animdir = anim.directory
  end
  if string.sub(animdir, -1) ~= "/" then
    animdir = animdir .. "/"
  end
  if anim.basename then
    name = anim.basename
  end
  dirs = { "" }
  if anim.directional then
    dirs = { "_se", "_e", "_ne", "_nw", "_w", "_sw" }
  end
  for i, d in ipairs(dirs) do
    n_d = name .. d
    box = size_and_crop_base(animdir .. n_d, cols, rows)
    if box then
      box.hot_x = anim.hotspot[1]
      box.hot_y = anim.hotspot[2]
      ret[n_d] = box
    end
  end
  return ret
end

function parse_anims(def)
  imgs = {}
  if def.animations then
    for name, anim in pairs(def.animations) do
      for k, v in pairs(anim_sprsh_common(anim, name, def.animation_directory, 1, 1)) do
        imgs[k] = v
      end
    end
  end
  if def.spritesheets then
    for name, sprsh in pairs(def.spritesheets) do
      for k, v in pairs(anim_sprsh_common(sprsh, name, def.animation_directory,
                                          sprsh.columns, sprsh.rows)) do
        imgs[k] = v
      end
    end
  end
  return imgs
end

typemap = {}
sizemap = {}

descriptions = {}
items = {}

descriptions.new_resource_type = ignore
descriptions.new_terrain_type = ignore

function descriptions:new_static(def)
  sz = def.size
  if sz == "medium" or sz == "mine" or sz == "none" then
    sz = "small"
  end
  if sz == "port" then
    sz = "big"
  end
  items[def.name] = { old = parse_anims(def) }
  sizemap[def.name] = sz
  typemap[def.name] = "static"
end

moving_items = {}
function descriptions:new_moving(def)
  items[def.name] = { old = parse_anims(def) }
  typemap[def.name] = "moving"
end

ships = {}
function descriptions:new_ship_type(def)
  items[def.name] = { old = parse_anims(def) }
  typemap[def.name] = "ship"
end

for i, type in ipairs { "constructionsite", "dismantlesite", "militarysite",
    "productionsite", "trainingsite", "warehouse", "immovable" } do
  descriptions["new_"..type.."_type"] = descriptions.new_static
end

for i, type in ipairs { "carrier", "ferry", "soldier", "ware", "worker", "critter" } do
  descriptions["new_"..type.."_type"] = descriptions.new_moving
end

wl = {}
function wl.Descriptions()
  return descriptions
end
