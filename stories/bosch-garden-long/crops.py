"""Details of the triptych cut from the Prado's 30000 px file (src/garden_hr.jpg, Commons "The Garden of Earthly Delights by
Bosch High Resolution.jpg", public domain), so every close-up is sharp. Boxes are fractions of the whole triptych.
usage: python stories/bosch-garden-long/crops.py      -> src/<name>.jpg for every box below (garden_hr itself is not shipped)"""
import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
BOX = {   # name: (x0, y0, x1, y1, longest side to keep)
    "garden": (0.0064, 0.0176, 0.9933, 0.9888, 7680),       # the whole open triptych, inside the black seams
    "left": (0.0075, 0.0185, 0.2330, 0.9880, 7200),          # Eden
    "eden": (0.0820, 0.5960, 0.1840, 0.7010, 3840),          # God presents Eve to Adam: the three faces
    "centre": (0.2420, 0.0185, 0.7590, 0.9880, 7200),        # the garden
    "hell": (0.7700, 0.0185, 0.9925, 0.9880, 7200),          # Hell
    "fire": (0.7700, 0.0185, 0.9925, 0.2500, 3840),          # the burning city at the top of Hell
    "ears": (0.7760, 0.2400, 0.8650, 0.3500, 3840),          # the ears and the knife
    "treeman": (0.8150, 0.2500, 0.9350, 0.5300, 3840),       # the tree-man: disk, face, tavern
    "instruments": (0.7700, 0.5850, 0.8650, 0.7750, 3840),   # lute, harp, hurdy-gurdy, the songbook, the sinner's backside
    "pignun": (0.9150, 0.8350, 0.9925, 0.9850, 3840),        # the pig in a nun's veil and her document
    "prince": (0.9050, 0.5950, 0.9900, 0.7900, 3840),        # the bird-headed prince on his throne
}

OTHER = {   # name: (source file in src/, x0, y0, x1, y1) — fractions of that file
    "signature": ("haywain.jpg", 0.5600, 0.8200, 0.7300, 0.9650),   # "jheronimus bosch", painted on The Haywain (Prado)
}

if __name__ == "__main__":
    for name, (f, x0, y0, x1, y1) in OTHER.items():
        im = Image.open(os.path.join(HERE, "src", f)); W, H = im.size
        im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H))).save(os.path.join(HERE, "src", f"{name}.jpg"), quality=93)
        print(name, "from", f)
    src = Image.open(os.path.join(HERE, "src", "garden_hr.jpg")); src.load(); W, H = src.size
    for name, (x0, y0, x1, y1, lg) in BOX.items():
        im = src.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
        s = lg / max(im.size)
        if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(os.path.join(HERE, "src", f"{name}.jpg"), quality=93); print(f"{name}: {im.width}x{im.height}")
