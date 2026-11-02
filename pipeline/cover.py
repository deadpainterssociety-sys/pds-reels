"""Cover / thumbnail in the 'Classic' style of Dead Painters Society (layout v3, 2 Nov 2026).
A CLOSE-UP of the painting fills the whole 9:16 frame: usually the main character's face or bust, or the key scene,
never the whole painting (too generic). The top of the painting itself is darkened with a smooth, long, translucent veil
(no black band) behind the text: painter in spaced caps, italic work line, and an intriguing serif question with the
loaded words in <i>italics</i>. The text sits low enough to survive TikTok's and Instagram's 3:4 profile-grid crop
(which cuts ~240 px off the top and bottom). THE VIDEO MUST ANSWER THE QUESTION. Keep the question to 2 lines.
The same image becomes the video's first frame (finalize.py).

usage: python pipeline/cover.py <story> ["override question"] [--style A]   -> out/cover.jpg (1080x1920)
story.json "cover": {question, name, work,
                     focus [x, y]  image point (0..1) of the close-up subject (a face, a bust, the key detail)
                     span          how much of the painting's HEIGHT the frame shows: 0.3 tight face … 0.45 bust (default)
                                   … 0.6 half figure / small scene (1 = the whole height)
                     at            where the focus lands, as a fraction of the frame height (default 0.6: under the text)}
config.json "cover_style": one of STYLES below (Gigi's chosen finish).
"""
import json, os, sys, math, tempfile
from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright
from paths import PUBLIC, ROOT, story_dir

W, H = 1080, 1920
FONTS = os.path.join(PUBLIC, "fonts")
# text_top: px from the top to the painter's name · veil: max darkness of the top veil · hold/end: % of the height where the
# veil starts to fade / is gone · blur: px of frosted blur under the veil (0 = none) · tint: veil colour · tight: × span
STYLES = {
    "A": dict(label="Veil", text_top=350, veil=0.66, hold=14, end=52, blur=0, tint=(11, 10, 9), bottom=0.35, tight=1.0),
    "B": dict(label="Long veil", text_top=370, veil=0.72, hold=18, end=62, blur=0, tint=(11, 10, 9), bottom=0.35, tight=1.0),
    "C": dict(label="Frosted veil", text_top=370, veil=0.52, hold=18, end=56, blur=14, tint=(11, 10, 9), bottom=0.35, tight=1.0),
    "D": dict(label="Long veil, tight close-up", text_top=370, veil=0.72, hold=18, end=62, blur=0, tint=(11, 10, 9), bottom=0.35, tight=0.68),
    "E": dict(label="Warm frosted, tight close-up", text_top=380, veil=0.60, hold=16, end=58, blur=8, tint=(26, 17, 10), bottom=0.45, tight=0.68),
}
DEFAULT_STYLE = "D"   # chosen by Gigi, 2 Nov 2026


def closeup(src, iw, ih, focus, span, at, out):
    """crop the painting around `focus` so it shows `span` of its height in a 9:16 frame, focus at height `at`"""
    im = Image.open(src).convert("RGB"); iw, ih = im.size
    a = W / H
    vh = min(ih, max(0.12, span) * ih); vw = vh * a
    if vw > iw: vw, vh = iw, iw / a                      # a tall, narrow painting: show its full width
    x0 = min(max(focus[0] * iw - 0.5 * vw, 0), iw - vw); y0 = min(max(focus[1] * ih - at * vh, 0), ih - vh)
    c = im.crop((round(x0), round(y0), round(x0 + vw), round(y0 + vh)))
    up = W / c.width
    c = c.resize((W, H), Image.LANCZOS)
    if up > 1.15: c = c.filter(ImageFilter.UnsharpMask(radius=2, percent=int(min(90, 40 * up)), threshold=2))
    c.save(out, quality=95)
    return up


def veil_css(s):
    """a smooth (smoothstep) fade from s.veil at the top to 0 at s.end% — many stops, so no visible band"""
    r, g, b = s["tint"]; stops = [f"rgba({r},{g},{b},{s['veil']:.3f}) 0%", f"rgba({r},{g},{b},{s['veil']:.3f}) {s['hold']}%"]
    for i in range(1, 13):
        t = i / 12; k = t * t * (3 - 2 * t)
        stops.append(f"rgba({r},{g},{b},{s['veil'] * (1 - k):.3f}) {s['hold'] + t * (s['end'] - s['hold']):.1f}%")
    bot = f"linear-gradient(to top, rgba({r},{g},{b},{s['bottom']}) 0%, rgba({r},{g},{b},0) 24%)"
    return f"linear-gradient(to bottom, {', '.join(stops)}), {bot}"


def render(img_path, cover, question, out_jpg, style=DEFAULT_STYLE):
    s = STYLES[style]
    tmp = tempfile.mkdtemp(); crop = os.path.join(tmp, "crop.jpg")
    span = float(cover.get("span", 0.45)) * s["tight"]
    up = closeup(img_path, 0, 0, cover.get("focus", [0.5, 0.42]), span, float(cover.get("at", 0.6)), crop)
    if up > 2.4: print(f"!! the close-up is upscaled {up:.1f}x: it may look soft (use a bigger image or a larger span)")
    FF = "".join(f"@font-face{{font-family:'{a}';src:url('file://{FONTS}/{b}.woff2');font-weight:{c};font-style:{d}}}" for a, b, c, d in [
        ("Newsreader", "newsreader-latin-500-normal", 500, "normal"), ("Newsreader", "newsreader-latin-500-italic", 500, "italic"),
        ("Inter", "inter-latin-600-normal", 600, "normal")])
    end = s["end"]
    blur = (f'<img id="bl" src="file://{crop}" style="position:absolute;left:-60px;top:-60px;width:{W + 120}px;height:{H + 120}px;'
            f'filter:blur({s["blur"]}px);-webkit-mask-image:linear-gradient(to bottom,#000 0%,#000 {s["hold"]}%,transparent {end - 4}%)">') if s["blur"] else ""
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{FF}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;background:#0b0a09;color:#F4F0E8}}
#p{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;filter:contrast(1.05)}}
#veil{{position:absolute;inset:0;background:{veil_css(s)}}}
.head{{position:absolute;left:90px;right:90px;top:{s['text_top']}px;text-align:center;text-shadow:0 2px 26px rgba(0,0,0,.55),0 1px 3px rgba(0,0,0,.35)}}
.q{{font:500 106px/1.06 Newsreader;letter-spacing:-1.5px;text-wrap:balance}} .q i{{font-style:italic}}
.cr{{margin-bottom:34px}} .name{{font:600 30px Inter;letter-spacing:7px;color:#E2D6BC}}
.work{{font:italic 500 40px Newsreader;color:#D2C7B2;margin-top:8px}}
</style></head><body><img id="p" src="file://{crop}">{blur}<div id="veil"></div>
<div class="head"><div class="cr"><div class="name">{cover['name']}</div><div class="work">{cover['work']}</div></div><div class="q">{question}</div></div>
</body></html>"""
    fn = os.path.join(tmp, "cover.html"); open(fn, "w").write(html)
    png = os.path.join(tmp, "cover.png")
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + fn); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        pg.screenshot(path=png); br.close()
        if errs: sys.exit("cover page error: " + "; ".join(errs))
    Image.open(png).convert("RGB").save(out_jpg, quality=93)
    return out_jpg


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    style = sys.argv[sys.argv.index("--style") + 1] if "--style" in sys.argv else None
    if style: args = [a for a in args if a != style]
    sdir = story_dir(args[0]); st = json.load(open(f"{sdir}/story.json")); cv = st["cover"]
    try: cfg = json.load(open(os.path.join(ROOT, "config.json")))
    except (OSError, ValueError): cfg = {}
    style = style or cv.get("style") or cfg.get("cover_style", DEFAULT_STYLE)
    rs = json.load(open(f"{sdir}/build/resolved.json"))
    img = os.path.join(PUBLIC, rs["images"][st["meta"]["image"]]["src"])
    out = f"{sdir}/out"; os.makedirs(out, exist_ok=True)
    render(img, cv, args[1] if len(args) > 1 else cv["question"], f"{out}/cover.jpg", style)
    Image.open(f"{out}/cover.jpg").save(f"{out}/cover.png")
    print("cover", f"{out}/cover.jpg", "style", style)
