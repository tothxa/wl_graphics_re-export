#!/bin/sh

identify +ping -format '%f,%w,%h,%@\n' "$@" | tr 'x+' , | $(dirname $0)/awk/get_scale.awk

