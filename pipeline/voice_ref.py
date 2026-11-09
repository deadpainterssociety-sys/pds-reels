"""Cut the best reference clips out of a voice recording, for Chatterbox. The model listens to the first 10 s of a clip
(the first 6 s set the speaking style), so a long recording doesn't make the clone closer: it gives more stretches to
choose from. A good clip is ~10-12 s of continuous, clean speech in the narration style, starting at the start of a
phrase and ending in a pause.

usage: python pipeline/voice_ref.py <recording (any format ffmpeg reads)> <out_dir> [n=3]
       -> out_dir/ref1.wav … refN.wav (24 kHz mono) + report.json {speech_s, noise_db, snr_db, clips: [...]}
"""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf

SR, HOP = 24000, 0.02


def runs(mask):
    """[(start, end)) index runs where mask is True"""
    d = np.diff(np.concatenate([[0], mask.astype(int), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def main(src, out, n=3):
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, "a.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-af", "highpass=f=70", w], check=True)
        a = sf.read(w, dtype="float32")[0]
    total = len(a) / SR
    h = int(HOP * SR); nf = len(a) // h
    rms = np.sqrt(np.mean(a[: nf * h].reshape(nf, h) ** 2, axis=1) + 1e-10); db = 20 * np.log10(rms)
    noise, loud = np.percentile(db, 10), np.percentile(db, 95)
    thr = noise + max(6.0, 0.3 * (loud - noise))
    v = db > thr
    for s, e in runs(~v):                        # holes inside words (< 120 ms) count as speech
        if e - s < 6 and s > 0: v[s:e] = True
    for s, e in runs(v):                         # clicks and breaths (< 100 ms) don't
        if e - s < 5: v[s:e] = False
    speech_s = v.sum() * HOP
    rep = {"recording_s": round(total, 1), "speech_s": round(speech_s, 1), "noise_db": round(float(noise), 1),
           "snr_db": round(float(loud - noise), 1), "clips": []}
    if speech_s < 12:
        rep["error"] = f"only {speech_s:.0f} s of speech found (need at least 12 s)"
        json.dump(rep, open(os.path.join(out, "report.json"), "w"), indent=1); print(rep); return rep
    pauses = [(s, e) for s, e in runs(~v) if e - s >= 12]          # ≥ 240 ms: a place to start or end a clip
    onsets = [e for s, e in pauses if e < nf]
    if v[0]: onsets = [0] + onsets
    peak = np.abs(a)
    cands = []
    for o in onsets:
        ends = [s for s, e in pauses if o + int(10.0 / HOP) <= s <= o + int(13.0 / HOP)]
        if not ends: continue
        e = ends[0]                                            # the first pause after 10 s: as short as it can be
        seg = v[o:e]; inner = [(s2 - s1) for s1, s2 in runs(~seg)]
        longest = max(inner, default=0) * HOP
        vf = seg.mean()
        if longest > 1.2 or vf < 0.6: continue
        s0, s1 = max(0, (o - 5) * h), min(len(a), (e + 8) * h)
        clip_frac = float((peak[s0:s1] > 0.98).mean())
        local_noise = float(np.percentile(db[max(0, o - 50): e + 50], 10))
        snr = float(np.percentile(db[o:e][seg], 60) - local_noise)
        sc = snr + 12 * vf - 6 * max(0.0, longest - 0.6) - 400 * clip_frac
        cands.append((sc, s0, s1, {"start_s": round(s0 / SR, 2), "len_s": round((s1 - s0) / SR, 2), "speech": round(float(vf), 2),
                                   "longest_pause_s": round(longest, 2), "snr_db": round(snr, 1), "clipped": round(clip_frac, 4)}))
    cands.sort(key=lambda c: -c[0]); chosen = []
    for c in cands:
        if all(c[2] <= x[1] or c[1] >= x[2] for x in chosen): chosen.append(c)
        if len(chosen) == n: break
    for k, (sc, s0, s1, info) in enumerate(chosen, 1):
        clip = a[s0:s1].copy(); clip *= 0.89 / max(1e-6, np.abs(clip).max())
        f = int(0.01 * SR); clip[:f] *= np.linspace(0, 1, f); clip[-f:] *= np.linspace(1, 0, f)
        sf.write(os.path.join(out, f"ref{k}.wav"), clip, SR, subtype="PCM_16")
        rep["clips"].append({"file": f"ref{k}.wav", "score": round(sc, 1), **info})
    if not chosen: rep["error"] = "no 10-13 s stretch of continuous speech found (pauses too long?)"
    json.dump(rep, open(os.path.join(out, "report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
