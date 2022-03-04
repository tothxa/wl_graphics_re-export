#!/usr/bin/lua

local lfs = require"lfs"

function pop_textdomain() end
function push_textdomain() end
function pgettext() end
function _() end

dirname = ""

path = {}
function path.dirname()
  return dirname
end
path.list_files = _  -- used by soldiers to get level icons
include = _          -- used by Amazon and Frisian immovables only (rare trees and berry bushes)

descriptions = {}
function descriptions:new(def)
  if def.animations then
    for name, anim in pairs(def.animations) do
      print(def.name .."_".. name .." 1x1 ".. anim.hotspot[1] ..",".. anim.hotspot[2] .." ".. dirname)
    end
  end
  if def.spritesheets then
    for name, sprsh in pairs(def.spritesheets) do
      print(def.name .."_".. name .." ".. sprsh.columns .."x".. sprsh.rows .." ".. sprsh.hotspot[1] ..",".. sprsh.hotspot[2] .." ".. dirname)
    end
  end
end

for i, type in ipairs { "constructionsite", "dismantlesite", "militarysite", "productionsite",
    "trainingsite", "warehouse", "carrier", "ferry", "immovable", "ship", "soldier", "ware",
    "worker" } do
  descriptions["new_"..type.."_type"] = descriptions.new
end

wl = {}
function wl.Descriptions()
  return descriptions
end

local skip_chars = 0

function do_dir(dir)
  -- print("entering directory ".. dir)
  for name in lfs.dir(dir) do
    if name ~= "." and name ~= ".." then
      local fullname = dir .."/".. name
      if name == "init.lua" then
        -- print("parsing ".. fullname)
        dirname = string.sub(dir, skip_chars)
        dofile(fullname)
      else
        local attr = lfs.attributes(fullname)
        if attr.mode == "directory" then
          do_dir(fullname)
        end
      end
    end
  end
end

for i,dir in ipairs(arg) do
  skip_chars = string.len(dir) + 2  -- skip the '/' too
  do_dir(dir)
end

