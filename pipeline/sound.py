"""Procedural sound primitives: every note and effect is synthesised with numpy/scipy, so there is nothing to license
and no copyright claim risk. Imported by score.py."""
import numpy as np
from scipy import signal

SR = 44100
rng = np.random.default_rng(7)


def t_(d): return np.arange(int(d * SR)) / SR
def midi(m): return 440 * 2 ** ((m - 69) / 12)


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a_, d_, r_ = int(a * SR), int(d * SR), int(r * SR)
    e = np.concatenate([np.linspace(0, 1, a_), np.linspace(1, s, d_), np.full(max(0, n - a_ - d_ - r_), s), np.linspace(s, 0, r_)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def lp(x, f, order=2):
    b, a = signal.butter(order, min(f, SR / 2 - 100) / (SR / 2), "low"); return signal.lfilter(b, a, x)
def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high"); return signal.lfilter(b, a, x)
def bp(x, lo, hi):
    b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return signal.lfilter(b, a, x)


def reverb(x, secs=2.2, mix=0.3, damp=4000):
    n = int(secs * SR)
    ir = lp(rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n)), damp); ir /= np.abs(ir).sum() / 40
    wet = signal.fftconvolve(x, ir)[: len(x)]
    wet *= np.abs(x).max() / (np.abs(wet).max() + 1e-9)
    return x * (1 - mix) + wet * mix


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(clip) <= 0: return
    if i < 0: clip = clip[-i:]; i = 0
    j = min(len(buf), i + len(clip)); buf[i:j] += clip[: j - i] * gain


def saw(f, d):
    t = t_(d); return 2 * ((t * f) % 1) - 1


# ---------- instruments ----------
def pad(notes, d, bright=1200):
    x = np.zeros(int(d * SR))
    for m in notes:
        for det in (-0.12, 0.0, 0.11): x += saw(midi(m) * 2 ** (det / 12), d)
    return lp(x, bright, 2) * env_adsr(len(x), 1.2, 0.3, 0.9, 1.4) / (len(notes) * 3)


def kick(d=0.5, f0=150, f1=42):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def heartbeat():
    x = np.zeros(int(0.9 * SR)); place(x, kick(0.3, 90, 40), 0, 1); place(x, kick(0.3, 80, 38), 0.24, 0.7)
    return lp(x, 300)


def choir(D, seq=((50, 57, 62, 65), (48, 55, 62, 64), (46, 53, 58, 62), (45, 52, 57, 61)), transpose=0):
    """sustained additive 'voices' with vibrato — eerie bed for the big moment"""
    x = np.zeros(int(D * SR))
    for i in range(int(D / 6) + 2):
        tt = t_(7.5); y = np.zeros_like(tt)
        for m in seq[i % len(seq)]:
            f = midi(m + transpose); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * tt + m)
            for h, a in ((1, 1), (2, .45), (3, .25), (4, .12), (5, .08)):
                y += a * np.sin(2 * np.pi * f * h * np.cumsum(vib) / SR)
        place(x, bp(y, 250, 3200) * env_adsr(len(y), 1.6, 0.2, 0.9, 2.0) / 8, i * 6, 0.5)
    return reverb(x, 3.5, 0.45)


# ---------- effects ----------
def whoosh(d=0.7, up=True):
    t = t_(d); n = rng.standard_normal(len(t))
    sweep = np.linspace(300, 4500, len(t)) if up else np.linspace(4500, 300, len(t))
    out = np.zeros_like(n)
    for i in range(0, len(n), 512):
        f = sweep[i]; seg = n[max(0, i - 2048): i + 512]
        out[i:i + 512] = bp(seg, f * 0.6, min(f * 1.6, 18000))[-len(out[i:i + 512]):]
    return out * np.sin(np.linspace(0, np.pi, len(t))) ** 2 * 0.9


def impact(big=True):
    d = 2.8 if big else 1.2; t = t_(d)
    x = kick(d, 110, 30) * (1.2 if big else 0.8) + lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 9) * 0.6
    return reverb(x, 2.5 if big else 1.0, 0.35)


def riser(d=2.5):
    t = t_(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(n), 1024):
        f = 400 + 7600 * (i / len(n)) ** 2; seg = n[max(0, i - 2048): i + 1024]
        out[i:i + 1024] = bp(seg, f * 0.7, min(f * 1.4, 19000))[-len(out[i:i + 1024]):]
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.15
    return (out * 0.8 + tone) * (t / d) ** 2


def tick():
    t = t_(0.04); return hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 200) * 0.5


def typekey():
    t = t_(0.05); return bp(rng.standard_normal(len(t)), 1800, 6000) * np.exp(-t * 140) * rng.uniform(0.3, 0.6)


def camera_shutter():
    x = np.zeros(int(0.25 * SR)); place(x, tick() * 1.6, 0); place(x, typekey() * 2, 0.07); return reverb(x, 0.4, 0.2)


def snip():
    """scissors: a metallic shear (swept band-passed noise + faint ring) closing on a click"""
    d = 0.32; t = t_(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(n), 256):
        f = 2500 + 5000 * (i / len(n)); seg = n[max(0, i - 1024): i + 256]
        out[i:i + 256] = bp(seg, f * 0.8, min(f * 1.3, 18000))[-len(out[i:i + 256]):]
    shear = out * np.sin(np.linspace(0, np.pi, len(t))) ** 1.5 * 0.55
    ring = np.sin(2 * np.pi * 3150 * t) * np.exp(-t * 18) * 0.08 + np.sin(2 * np.pi * 4720 * t) * np.exp(-t * 22) * 0.05
    x = shear + ring; place(x, tick() * 2.2, d - 0.04)
    return reverb(x, 0.5, 0.18) * 0.4


def sting_reverse():
    x = impact(False)[: int(1.0 * SR)][::-1]; return x * np.linspace(0, 1, len(x)) ** 2


def chime():
    x = np.zeros(int(1.2 * SR))
    for k, m in enumerate([76, 83, 88]):
        tt = t_(1.0); place(x, np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * 5) * 0.4, k * 0.07)
    return reverb(x, 1.2, 0.3)


def pop():
    t = t_(0.09); f = 900 + 700 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * 0.6


def duck_env(voice, depth_db=-10, att=0.03, rel=0.35):
    """gain curve that dips the music under the narration (attack 30 ms, release 350 ms)"""
    e = np.convolve(np.abs(voice), np.ones(int(0.02 * SR)) / int(0.02 * SR), mode="same")
    on = (e > 0.02).astype(float); out = np.zeros_like(on)
    a_c, r_c = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR)); v = 0
    for i in range(0, len(on), 64):
        tgt = on[i]; c = a_c if tgt > v else r_c
        v = tgt + (v - tgt) * c ** 64; out[i:i + 64] = v
    return 1 - (1 - 10 ** (depth_db / 20)) * out
