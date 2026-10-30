"""Procedural textures used by the reel engine (generated, so there is nothing to license).
usage: python pipeline/textures.py   -> studio/public/tex/grain.png (film grain tile), plaster.jpg (bare wall for the 'peel' shot)"""
import os
import numpy as np
from PIL import Image, ImageFilter
from paths import PUBLIC

tex = os.path.join(PUBLIC, "tex"); os.makedirs(tex, exist_ok=True)
rng = np.random.default_rng(3)
# film grain: 512x512 tile, mid-grey noise (used with mix-blend-mode: overlay)
g = np.clip(128 + rng.normal(0, 38, (512, 512)), 0, 255).astype(np.uint8)
Image.fromarray(g, "L").filter(ImageFilter.GaussianBlur(0.45)).save(os.path.join(tex, "grain.png"))
# plaster wall 1080x1920: multi-octave value noise in warm grey, with a cleaner 'ghost' rectangle where a painting hung
W, H = 1080, 1920
def noise(scale):
    s = rng.random((H // scale + 2, W // scale + 2))
    return np.asarray(Image.fromarray((s * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
n = 0.5 * noise(240) + 0.25 * noise(60) + 0.15 * noise(16) + 0.1 * noise(4)
img = np.array([0.62, 0.58, 0.52]) * (0.75 + 0.45 * (n[..., None] - 0.5))
yy, xx = np.mgrid[0:H, 0:W]
rect = ((xx > 40) & (xx < 1040) & (yy > 60) & (yy < 1860)).astype(np.uint8) * 255
rect = np.asarray(Image.fromarray(rect).filter(ImageFilter.GaussianBlur(25))).astype(np.float32) / 255
img = img * (0.82 + 0.22 * rect[..., None])
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(tex, "plaster.jpg"), quality=90)
print("textures ->", tex)
