"""YouTube thumbnails (1280x720) for long-form videos, in the Shorts' cover style D: an extreme close-up of the painting.
Variant A: no text (what the leaders' top videos use). Variant B: the same close-up with at most three words in the
DPS serif, on a long translucent veil from the left. Test both with YouTube's Test & Compare.

usage: python pipeline/thumb.py <story>   -> out/thumb_a.jpg, out/thumb_b.jpg
story.json "youtube": {"thumbnail": {"image": key, "focus": [x, y], "span": 0.2 (share of the painting's height shown),
                                     "at": [0.62, 0.45] (where the focus lands in the frame), "words": "HIS DINING ROOM"}}
"""
import json, os, sys, tempfile
from PIL import Image, ImageEnhance, ImageFilter
from playwright.sync_api import sync_playwright
from paths import PUBLIC, story_dir

W, H = 1280, 720
FONTS = os.path.join(PUBLIC, "fonts")


def crop(src, focus, span, at, out):
    im = Image.open(src).convert("RGB"); iw, ih = im.size
    vh = min(ih, span * ih); vw = vh * W / H
    if vw > iw: vw, vh = iw, iw * H / W
    x0 = min(max(focus[0] * iw - at[0] * vw, 0), iw - vw); y0 = min(max(focus[1] * ih - at[1] * vh, 0), ih - vh)
    c = im.crop((round(x0), round(y0), round(x0 + vw), round(y0 + vh))); up = W / c.width
    c = c.resize((W, H), Image.LANCZOS)
    if up > 1.1: c = c.filter(ImageFilter.UnsharpMask(radius=2, percent=int(min(110, 50 * up)), threshold=2))
    c = ImageEnhance.Contrast(c).enhance(1.12); c = ImageEnhance.Brightness(c).enhance(1.06)
    c.save(out, quality=96)
    return up


def render(crop_path, words, out_jpg):
    FF = "".join(f"@font-face{{font-family:'{a}';src:url('file://{FONTS}/{b}.woff2');font-weight:{c};font-style:{d}}}" for a, b, c, d in [
        ("Newsreader", "newsreader-latin-600-normal", 600, "normal"), ("Newsreader", "newsreader-latin-600-italic", 600, "italic")])
    text = ""
    if words:
        w = words.split(); first, rest = w[0], " ".join(w[1:])
        text = f'<div class="t">{first} <i>{rest.lower()}</i></div>'
    veil = ("linear-gradient(to right, rgba(11,10,9,.82) 0%, rgba(11,10,9,.70) 28%, rgba(11,10,9,.30) 50%, rgba(11,10,9,0) 64%)" if words else "none")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{FF}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;background:#0b0a09}}
#p{{position:absolute;inset:0;width:{W}px;height:{H}px}}
#v{{position:absolute;inset:0;background:radial-gradient(ellipse 80% 85% at 58% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%), {veil}}}
.t{{position:absolute;left:70px;top:50%;transform:translateY(-50%);width:520px;color:#F4F0E8;font:600 118px/0.98 Newsreader;letter-spacing:-2px;
   text-transform:none;text-shadow:0 4px 28px rgba(0,0,0,.6)}} .t i{{font-style:italic;display:block}}
</style></head><body><img id="p" src="file://{crop_path}"><div id="v"></div>{text}</body></html>"""
    tmp = tempfile.mkdtemp(); fn = os.path.join(tmp, "t.html"); open(fn, "w").write(html); png = os.path.join(tmp, "t.png")
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + fn); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300); pg.screenshot(path=png); br.close()
    Image.open(png).convert("RGB").save(out_jpg, quality=92)


if __name__ == "__main__":
    sdir = story_dir(sys.argv[1]); st = json.load(open(f"{sdir}/story.json")); th = st["youtube"]["thumbnail"]
    rs = json.load(open(f"{sdir}/build/resolved.json"))
    src = os.path.join(PUBLIC, rs["images"][th["image"]]["src"])
    out = f"{sdir}/out"; os.makedirs(out, exist_ok=True); tmp = tempfile.mkdtemp()
    a = os.path.join(tmp, "a.jpg"); up = crop(src, th["focus"], th.get("span", 0.22), th.get("at", [0.5, 0.42]), a)
    render(a, "", f"{out}/thumb_a.jpg")
    b = os.path.join(tmp, "b.jpg"); crop(src, th["focus"], th.get("span", 0.22), th.get("at_b", [0.7, 0.42]), b)
    render(b, th.get("words", ""), f"{out}/thumb_b.jpg")
    print(f"thumbnails -> {out}/thumb_a.jpg, thumb_b.jpg (close-up upscaled {up:.1f}x)")
