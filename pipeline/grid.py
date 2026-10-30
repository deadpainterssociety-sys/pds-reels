"""Gridded copy of an image for picking points (faces, details) as 0..1 coordinates - open the output with your image viewer
(Claude: Read it). Points go in story.json images.<name>.points as [x, y].

usage: python pipeline/grid.py <image> [--crop x0,y0,x1,y1] [--bright 2.2] [--step 0.1] [--width 1200]
       -> build/grids/<name>[_crop].jpg (path printed). With --crop the labels stay in FULL-image coordinates,
          so you can zoom into a dark corner and read precise points (use --step 0.01 or 0.02 there)."""
import os, sys
from PIL import Image, ImageDraw, ImageEnhance

a = sys.argv; src = a[1]
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
crop = [float(v) for v in opt("--crop", "0,0,1,1").split(",")]; bright = float(opt("--bright", "1")); step = float(opt("--step", "0.1"))
width = int(opt("--width", "1200"))
im = Image.open(src).convert("RGB"); W, H = im.size
x0, y0, x1, y1 = crop
c = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
if bright != 1: c = ImageEnhance.Brightness(c).enhance(bright)
s = width / c.width; c = c.resize((width, round(c.height * s)))
d = ImageDraw.Draw(c)
def lines(lo, hi, horizontal):
    k = round(lo / step) * step
    while k <= hi + 1e-9:
        if k >= lo - 1e-9:
            if horizontal:
                y = (k - y0) / (y1 - y0) * c.height; d.line([(0, y), (c.width, y)], fill=(255, 40, 40)); d.text((3, y + 2), f"{k:.2f}", fill=(0, 255, 255))
            else:
                x = (k - x0) / (x1 - x0) * c.width; d.line([(x, 0), (x, c.height)], fill=(255, 40, 40)); d.text((x + 3, 3), f"{k:.2f}", fill=(255, 255, 0))
        k += step
lines(x0, x1, False); lines(y0, y1, True)
out = os.path.join("build", "grids"); os.makedirs(out, exist_ok=True)
name = os.path.splitext(os.path.basename(src))[0] + ("" if crop == [0, 0, 1, 1] else "_crop")
fn = os.path.join(out, name + ".jpg"); c.save(fn, quality=88); print(fn)
