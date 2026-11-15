// Breakout safari, watching by eye (interactive sessions, built-in browser): paste this whole file into the browser
// tool's javascript_exec on a https://www.youtube.com/watch?v=<id> page (viewport 1800x1300 helps), then take a
// screenshot: a timestamped frame sheet appears over the page; call __show('big') and screenshot again for 4 large frames
// (hook, 30 %, 65 %, end) whose captions are readable. Returns duration, views and any auto-transcript.
const sleep = ms => new Promise(r => setTimeout(r, ms));
let v; for (let i = 0; i < 40 && !(v = document.querySelector('video.html5-main-video')); i++) await sleep(250);
for (let i = 0; i < 40 && !(v.duration > 0); i++) await sleep(250);
v.muted = true; v.pause(); const d = v.duration;
document.querySelector('#description-inline-expander #expand, tp-yt-paper-button#expand')?.click(); await sleep(800);
const btn = [...document.querySelectorAll('button, ytd-button-renderer')].find(b => /show transcript/i.test(b.innerText || b.getAttribute('aria-label') || ''));
if (btn) (btn.querySelector('button') || btn).click(); await sleep(2500);
const segs = [...document.querySelectorAll('ytd-transcript-segment-renderer, transcript-segment-view-model')].map(s => s.innerText.replace(/\s+/g, ' ').trim());
const grab = async (ts, cols, H0) => {
  const W = Math.floor(H0 * v.videoWidth / v.videoHeight); const c = document.createElement('canvas');
  c.width = W * cols; c.height = (H0 + 18) * Math.ceil(ts.length / cols); const g = c.getContext('2d');
  g.fillStyle = '#111'; g.fillRect(0, 0, c.width, c.height);
  for (let i = 0; i < ts.length; i++) {
    v.currentTime = ts[i]; await new Promise(r => { v.addEventListener('seeked', r, { once: true }); setTimeout(r, 3000); }); await sleep(150);
    const x = (i % cols) * W, y = Math.floor(i / cols) * (H0 + 18); g.drawImage(v, x, y + 18, W, H0);
    g.fillStyle = '#ffd400'; g.font = '15px sans-serif'; g.fillText(ts[i].toFixed(1) + 's', x + 3, y + 14);
  }
  return c;
};
const ts = [0, 0.5, 1, 1.5, 2, 3]; for (let i = 1; i <= 12; i++) { const t = 3 + (d - 3.3) * i / 12; ts.push(+t.toFixed(1)); }
const sheet = await grab(ts, 9, 380);
const big = await grab([0.6, +(d * 0.3).toFixed(1), +(d * 0.65).toFixed(1), +(d - 0.4).toFixed(1)], 4, 1250);
document.querySelectorAll('canvas[data-k]').forEach(e => e.remove()); sheet.dataset.k = 'sheet'; big.dataset.k = 'big';
for (const c of [big, sheet]) { Object.assign(c.style, { position: 'fixed', left: '0', top: '0', zIndex: 2147483647, width: '1800px', height: 'auto', background: '#000' }); document.body.appendChild(c); }
window.__show = k => document.querySelectorAll('canvas[data-k]').forEach(e => e.style.display = (e.dataset.k === k ? 'block' : 'none'));
window.__show('sheet');
({ dur: d, views: document.querySelector('#info span, ytd-watch-info-text')?.innerText?.slice(0, 60), title: document.title, transcript: segs.join(' | ') })
