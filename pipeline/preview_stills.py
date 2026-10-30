"""Cheap visual QA before the long render: one still per shot (at its midpoint) + any extra times, as a contact sheet.
usage: python pipeline/preview_stills.py <story> [t1,t2,...]   -> out/stills.jpg
Check: framing on the subject, captions not covering faces/key details, overlays readable, nothing blurry or black."""
import json, os, sys, subprocess, glob
from PIL import Image, ImageDraw
from paths import STUDIO, story_dir

sdir = story_dir(sys.argv[1]); rs = json.load(open(os.path.join(sdir, "build", "resolved.json")))
sh = rs["shots"]; ends = [s["t"] for s in sh[1:]] + [rs["duration"]]
times = sorted({round((s["t"] + e) / 2, 2) for s, e in zip(sh, ends)} | {float(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else [])})
odir = os.path.join(sdir, "build", "stills")
subprocess.run(["node", "stills.mjs", rs["slug"], ",".join(map(str, times)), odir], cwd=STUDIO, check=True)
fs = sorted(glob.glob(os.path.join(odir, "*.jpg")), key=lambda f: float(os.path.basename(f)[:-4]))
cols, tw, th = 8, 270, 480
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (16, 16, 16)); d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    x, y = (i % cols) * tw, (i // cols) * (th + 22)
    sheet.paste(Image.open(f).resize((tw, th)), (x, y + 22)); d.text((x + 4, y + 4), os.path.basename(f)[:-4] + "s", fill=(255, 220, 0))
os.makedirs(os.path.join(sdir, "out"), exist_ok=True)
sheet.save(os.path.join(sdir, "out", "stills.jpg"), quality=85); print("stills ->", os.path.join(sdir, "out", "stills.jpg"))
