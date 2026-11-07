"""Score + SFX cut to the story's own timeline, mixed under the narration.

usage: python pipeline/score.py <story>    -> build/mix.wav (+ studio/public/stories/<slug>/audio.wav)

story.json "music": {
  "chords": [[38,45,50], ...]  MIDI voicings, one per bar (default D minor: Dm  Dm(maj7)  Bb  A)
  "bar": 5.0, "transpose": -2  (transpose per story so consecutive reels don't sound identical)
  "sections": {"cold": [a,b], "choir": [a,b], "drop": [a,b]}
        cold  = pad ducked + thin cold high drone (backstory / flashback)
        choir = eerie choir swell (the big reveal / emotional peak)
        drop  = near-silence (a comic beat: "Almost nobody cares.")
  "heartbeat": [a,b]  accelerating heartbeat (tension before a reveal)
}
Automatic SFX: whoosh on every cut ("whoosh": false on a shot to skip), "hit": "big" -> reverse sting + big impact
(+ flash/shake in the video), "hit": "small" -> small impact, tick on every map pin.
Extra cues: "sfx": [{"at": anchor, "fx": "chime|impact|impact_big|whoosh|tick|riser|sting|shutter|heartbeat|pop", "gain": 0.5}]
Loudness: the mono mix is normalised to -14 LUFS (≈ -11 LUFS once written as identical stereo channels).
"""
import json, os, sys, shutil
import numpy as np, soundfile as sf
from scipy import signal
import pyloudnorm as pyln
import sound as S
from paths import PUBLIC, story_dir

SR = S.SR
sdir = story_dir(sys.argv[1])
rs = json.load(open(os.path.join(sdir, "build", "resolved.json")))
v, vsr = sf.read(os.path.join(sdir, "build", "voice.wav"), dtype="float32")
v = signal.resample_poly(v, SR, vsr); D = len(v) / SR
M = rs.get("music", {})
t = np.arange(len(v)) / SR


def mask(a, b, fade=0.6):
    m = ((t >= a) & (t < b)).astype(float); k = int(fade * SR) | 1
    return signal.fftconvolve(m, np.hanning(k) / np.hanning(k).sum(), mode="same")   # FFT: same result, fast on 10-minute mixes


tr = M.get("transpose", 0); bar = M.get("bar", 5.0)
seq = M.get("chords", [[38, 45, 50], [38, 45, 49], [34, 41, 50], [33, 40, 49]])
segs = sorted(M.get("segments", []), key=lambda g: g["t"])   # long-form: a new progression per chapter, same instruments
def seg_at(x):
    g = [s for s in segs if s["t"] <= x + 1e-6]
    return (g[-1].get("chords", seq), g[-1].get("transpose", tr), g[-1]["t"]) if g else (seq, tr, 0.0)
music = np.zeros(len(t)); drone = np.zeros(len(t))
for i in range(int(D / bar) + 2):
    sq, tp, t0 = seg_at(i * bar); j = int(round((i * bar - t0) / bar))
    S.place(music, S.pad([n + tp for n in sq[j % len(sq)]], bar * 1.5, 900), i * bar, 0.55)
for k, g in enumerate([{"t": 0.0, "chords": seq, "transpose": tr}] + segs):   # sub drone on each section's root, crossfaded
    a = g["t"]; b = segs[k]["t"] if k < len(segs) else D + 1
    root = g.get("chords", seq)[0][0] + g.get("transpose", tr) - 12
    drone += np.sin(2 * np.pi * S.midi(root) * t) * 0.16 * mask(a, b, 2.0)
music += drone
sec = M.get("sections", {})
if "cold" in sec:
    m = mask(*sec["cold"]); music *= 1 - 0.65 * m
    music += S.lp((np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 233.1 * t)) * 0.03, 1800) * m
if "choir" in sec:
    ch = S.choir(D, transpose=tr)[: len(t)]; music += np.pad(ch, (0, len(t) - len(ch))) * mask(*sec["choir"], 1.2) * 1.4
if "heartbeat" in M:
    a, b = M["heartbeat"]; tt = a
    while tt < b: S.place(music, S.heartbeat(), tt, 0.9); tt += max(0.5, 0.86 - 0.08 * (tt - a))
music = S.reverb(music, 2.6, 0.3)
if "drop" in sec: music *= 1 - 0.85 * mask(*sec["drop"], 0.25)
music /= np.abs(music).max() + 1e-9

fx = np.zeros(len(t))
for i, (ct, hit, wh) in enumerate(rs["cuts"]):
    if hit == "big": S.place(fx, S.sting_reverse(), ct - 0.95, 0.5); S.place(fx, S.impact(True), ct, 0.95)
    elif hit == "small": S.place(fx, S.impact(False), ct, 0.5)
    elif wh and i > 0: S.place(fx, S.whoosh(0.45), ct - 0.3, 0.22)
for sh in rs["shots"]:
    if sh.get("kind") == "map":
        for p in sh["map"]["pins"]: S.place(fx, S.tick() * 2, p["t"], 0.6)
FX = {"chime": S.chime, "impact": lambda: S.impact(False), "impact_big": lambda: S.impact(True), "whoosh": lambda: S.whoosh(0.6),
      "tick": lambda: S.tick() * 2, "riser": lambda: S.riser(1.6), "sting": S.sting_reverse, "shutter": S.camera_shutter,
      "heartbeat": S.heartbeat, "pop": S.pop, "snip": S.snip}
for x in rs["sfx"]:
    lead = 1.6 if x["fx"] == "riser" else 0.95 if x["fx"] == "sting" else 0   # risers/stings END on the anchor
    S.place(fx, FX[x["fx"]](), x["t"] - lead, x["gain"])
fx /= max(1.0, np.abs(fx).max())

mix = v + music * 10 ** (M.get("music_db", -12) / 20) * S.duck_env(v) + fx * 10 ** (M.get("fx_db", -6.5) / 20)
fade = int(0.8 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
mix *= 10 ** ((-14.0 - pyln.Meter(SR).integrated_loudness(mix)) / 20)
mix = np.where(np.abs(mix) > 0.7, np.sign(mix) * (0.7 + 0.28 * np.tanh((np.abs(mix) - 0.7) / 0.28)), mix)   # soft clip
out = os.path.join(sdir, "build", "mix.wav")
sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR)
pub = os.path.join(PUBLIC, rs["audio"]); os.makedirs(os.path.dirname(pub), exist_ok=True); shutil.copy(out, pub)
print(f"mix {D:.1f} s, peak {np.abs(mix).max():.2f}")
