# wl_graphics_re-export
High resolution images re-exported from old
[Widelands](https://github.com/widelands/widelands) models

None of the original work is by me. All Blender models and some of the Blender
Python scripts are from the [Widelands Media repository on
Launchpad](https://code.launchpad.net/widelands-media). All image files are
derived works of the Blender models.

I am to blame however for all the ugly shell and AWK scripts. I'll try to redo
them in Python eventually, but that's no guarantee that they will be any less
ugly.

I include the `.blend` models to show which version I used to render the
images. Some of them are re-saved with minor adjustments. I tried to indicate
that in the filenames. Some models have an accompanying `.info` file (plain
text), where I put some notes and reminders on what non-default settings I
used for rendering, or what I had to tweak.

## Background information

### Blender versions
I first try to render all models in Blender 2.79 (on Debian buster).

Blender 2.8+ dropped support for the blender_internal rendering engine, so all
textures need converting, and all lights give very different results than old
Blender versions, both with Eevee and with Cycles. Fixing this is way beyond
my (non-existing) knowledge of Blender.

Some models are incompatible even with 2.79. The problems I saw so far:
- particle effects: this sometimes results in glowing volume regions
- displaced geometry
- weird differences in animations

Fortunately Blender has an archive of all old releases
[here](https://download.blender.org/release/). I found it easiest to use the
w.ndows builds in wine. It even works from the console (no X running) with
environment variables, e.g.:
```
SCALE=7 wine /path/to/blender.exe -b building.blend -P render_settings_b249.py -o building -f 1
```
(However Blender 2.49- didn't load scripts from other directories, like
`-P ../script.py`, not even the official Debian build in a squeeze chroot.)

### Spritesheets
As opposed to `wl_create_spritesheet`, my scaling scripts keep the cropping
of all the scaled mipmaps in sync, and always leave an empty border of
1 pixel at the lowest scale to prevent bleeding over of scaling artifacts.
(EXAMPLE SCREENSHOT NEEDED HERE)

I have found that using more columns than rows of the animation steps
improves PNG compression by **a lot**. (EXAMPLE SIZE COMPARISON NEEDED HERE)

### Antialiasing
I try to use filters that cause minimal blurring. I have found that it gives
better results to use antialiasing in Blender too for creating the initial
high resolution rendered images. This could probably be disabled if I used
at least 12x scaled "originals" (3x scale, ie. 9x oversampling at the max
in-game scale of 4), but Blender has more information internally, and uses
higher quality sampling. See:
https://docs.blender.org/manual/ja/2.79/render/blender_render/settings/antialiasing.html

Now I aim for about 6x (1.5x 4), so I use 1000x1000 pixels for big buildings,
800x800 for medium and 600x600 for small. I expect that the original 400x400
will be fine for workers and animals.

I use the Mitchell-Netravali filter in Blender (see above link for a
demonstration of various filters) when I can, but I couldn't figure out how
to choose it in 2.49- from Python. It's there in the dialog, but the API
reference doesn't mention it, and I can't see console output like in 2.79.
*Any help would be kindly appreciated.*

For the in-game mipmap scales I use the Catmull-Rom (`catrom`) filter in
GraphicsMagick, to minimise further blurring. The resulting images at scale
1 are slightly more blurred than the old ones, but the old ones sometimes
have aliasing issues or stepped edges. Scales 2 and 4 are nice, sharp and
still antialiased with this process. (Scale 0.5 looks good too, but that's
so small that almost anything goes for it.)

