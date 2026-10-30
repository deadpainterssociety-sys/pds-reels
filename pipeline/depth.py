"""Depth map for the 2.5D parallax (Depth Anything V2, ONNX on CPU). Near = white. Blurred on purpose:
a soft map gives a smooth 'living painting' parallax without tearing at edges.
usage: python pipeline/depth.py <image.jpg> <out_depth.png>   (DEPTH_MODEL=vits|vitb|vitl, default vits — the only commercially licensed one)"""
import os, sys
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
from paths import DEPTH_DIR

src, out = sys.argv[1], sys.argv[2]
size = os.environ.get("DEPTH_MODEL", "vits")   # vits: Apache-2.0. vitb/vitl: CC-BY-NC-4.0 -> avoid on monetised channels
im = Image.open(src).convert("RGB")
x = np.asarray(im.resize((518, 518), Image.BICUBIC)).astype(np.float32) / 255
x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
sess = ort.InferenceSession(os.path.join(DEPTH_DIR, f"depth_anything_v2_{size}.onnx"), providers=["CPUExecutionProvider"])
d = sess.run(None, {sess.get_inputs()[0].name: x})[0].squeeze()
lo, hi = np.percentile(d, 2), np.percentile(d, 98)
d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)
s = 1024 / max(im.size)
dm = Image.fromarray((d * 255).astype(np.uint8)).resize((round(im.width * s), round(im.height * s)), Image.BICUBIC)
dm.filter(ImageFilter.GaussianBlur(5)).convert("RGB").save(out)
print(f"depth {os.path.basename(out)} {dm.size} ({size})")
