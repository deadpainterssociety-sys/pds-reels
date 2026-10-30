"""Cover / thumbnail in the 'Classic' style of Dead Painters Society (layout v2, 27 Oct 2026).
The painting fills the FULL WIDTH and the whole lower part of the frame (~bottom 2/3, from just under the question to the
bottom edge), cover-fitted around a focal point - never side margins. Vertical paintings get zoomed to the width
(top/bottom cropped), horizontal ones to the height (sides cropped). The top fades to black behind the text:
painter in spaced caps, italic work line, and an intriguing serif question with the loaded words in <i>italics</i>.
THE VIDEO MUST ANSWER THE QUESTION. Keep the question to 2 lines (a 3rd line would overlap the painting).
The same image becomes the video's first frame (finalize.py).

usage: python pipeline/cover.py <story> ["override question"]   -> out/cover.jpg (1080x1920)
story.json "cover": {question, name, work,
                     focus [x, y]  image point (0..1) to keep in view, default [0.5, 0.42]  (a face, the key detail)
                     zoom          extra zoom, default 1  (1.1-1.25 fills a dark, empty top with figures)
                     top           force the painting's top edge in px (default: just under the text)}
"""
import json, os, sys
from playwright.sync_api import sync_playwright
from paths import PUBLIC, story_dir

FONTS = os.path.join(PUBLIC, "fonts")
sdir = story_dir(sys.argv[1]); st = json.load(open(f"{sdir}/story.json")); cv = st["cover"]
rs = json.load(open(f"{sdir}/build/resolved.json"))
main = rs["images"][st["meta"]["image"]]
img = os.path.join(PUBLIC, main["src"]); asp = main["w"] / main["h"]
q = sys.argv[2] if len(sys.argv) > 2 else cv["question"]
out = f"{sdir}/out"; os.makedirs(out, exist_ok=True)
W, H = 1080, 1920
FF = "".join(f"@font-face{{font-family:'{a}';src:url('file://{FONTS}/{b}.woff2');font-weight:{c};font-style:{d}}}" for a, b, c, d in [
    ("Newsreader", "newsreader-latin-500-normal", 500, "normal"), ("Newsreader", "newsreader-latin-500-italic", 500, "italic"),
    ("Inter", "inter-latin-600-normal", 600, "normal")])
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{FF}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;background:#0b0a09;color:#F4F0E8}}
#box{{position:absolute;left:0;right:0;bottom:0;overflow:hidden}} #p{{position:absolute;filter:contrast(1.06)}}
#fade{{position:absolute;inset:0}}
.head{{position:absolute;left:90px;right:90px;top:250px;text-align:center}}
.q{{font:500 106px/1.06 Newsreader;letter-spacing:-1.5px;text-wrap:balance}} .q i{{font-style:italic}}
.cr{{margin-bottom:34px}} .name{{font:600 30px Inter;letter-spacing:7px;color:#CDBF9F}}
.work{{font:italic 500 40px Newsreader;color:#B9AE99;margin-top:8px}}
</style></head><body><div id="box"><img id="p" src="file://{img}"></div><div id="fade"></div>
<div class="head" id="head"><div class="cr"><div class="name">{cv['name']}</div><div class="work">{cv['work']}</div></div><div class="q">{q}</div></div>
<script>
(() => {{
const iw={main['w']}, ih={main['h']}, fx={cv.get('focus', [0.5, 0.42])[0]}, fy={cv.get('focus', [0.5, 0.42])[1]}, zoom={cv.get('zoom', 1.0)};
const qb=document.getElementById('head').getBoundingClientRect().bottom;
const top={cv.get('top', 'null')} ?? Math.round(Math.min(Math.max(qb - 30, 520), 760));   // painting starts just under the text
const bw={W}, bh={H}-top;
const box=document.getElementById('box'); box.style.top=top+'px';
const sc=Math.max(bw/iw, bh/ih)*zoom, dw=iw*sc, dh=ih*sc;                 // cover-fit: no empty margins anywhere
const x=Math.min(0, Math.max(bw-dw, bw*0.5 - fx*dw)), y=Math.min(0, Math.max(bh-dh, bh*0.45 - fy*dh));
Object.assign(document.getElementById('p').style,{{left:x+'px',top:y+'px',width:dw+'px',height:dh+'px'}});
const tp=top/{H}*100;
document.getElementById('fade').style.background=
 `linear-gradient(#0b0a09 0, #0b0a09 ${{tp}}%, rgba(11,10,9,.82) ${{tp+3}}%, rgba(11,10,9,0) ${{tp+14}}%, rgba(11,10,9,0) 84%, rgba(11,10,9,.6) 100%)`;
document.body.dataset.done='1';
}})();
</script></body></html>"""
fn = f"{sdir}/build/cover.html"; open(fn, "w").write(html)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + fn); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.reload(); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)   # re-run layout with fonts loaded
    pg.screenshot(path=f"{out}/cover.png"); br.close()
    if errs: sys.exit("cover page error: " + "; ".join(errs))
from PIL import Image
Image.open(f"{out}/cover.png").convert("RGB").save(f"{out}/cover.jpg", quality=93)
print("cover", f"{out}/cover.jpg")
