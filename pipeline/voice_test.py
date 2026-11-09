"""Voice test for Telegram: the opening of a Short Gigi already knows, in up to four versions of the cloned voice.
Runs in Chatterbox's environment (automation/voice_env.sh) after pipeline/voice_ref.py has cut the reference clips.

usage: <venv>/bin/python pipeline/voice_test.py <refs_dir> <out_dir> [story=gericault-medusa] [lines=6] [only=n]
       (the voice workflow runs one version per machine: only=1..4)
       -> out_dir/v1.mp3 … + variants.json [{n, label, note, model, ref, exaggeration, cfg, cpu_per_s, match, file}]
"""
import json, os, subprocess, sys, time
import soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tts_clone as C
from paths import story_dir

VARIANTS = [   # label, model, reference clip, exaggeration, cfg, what to listen for
    ("A", "original", "ref1.wav", 0.5, 0.5, "balanced (Chatterbox's defaults)"),
    ("B", "original", "ref1.wav", 0.7, 0.3, "more expressive and a little slower"),
    ("C", "turbo", "ref1.wav", 0.5, 0.5, "Turbo model: about 2.5× quicker to make, a bit plainer"),
    ("D", "original", "ref2.wav", 0.5, 0.5, "same as A from another stretch of your recording"),
]


def main(refs, out, slug="gericault-medusa", n=6, only=None):
    os.makedirs(out, exist_ok=True)
    story = json.load(open(os.path.join(story_dir(slug), "story.json")))
    say, respell, skip = C.words_of(story)
    lines = story["lines"][:n]; res = []
    for k, (label, model, ref, ex, cfg, note) in enumerate(VARIANTS, 1):
        rp = os.path.join(refs, ref)
        if (only and k != only) or not os.path.exists(rp): continue
        cv = {**C.settings(), "model": model, "exaggeration": ex, "cfg": cfg}
        v = C.Voice(cv, rp, os.path.join(out, "cache"), say, respell, skip)
        t0 = time.time(); print(f"== {label}: {model} {ref} ex {ex} cfg {cfg}", flush=True)
        full, tl, weak = C.render(v, lines, say, cv, 0.6)
        wav = os.path.join(out, f"v{k}.wav"); sf.write(wav, full, C.SR)
        mp3 = os.path.join(out, f"v{k}.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "44100", "-b:a", "160k", mp3], check=True)
        h = C.heard(full) or ""
        want = [C.norm(w) for ln in tl for w in ln["text"].split()]
        got = [C.norm(w) for w in h.split()]
        import difflib
        match = sum(b.size for b in difflib.SequenceMatcher(a=want, b=got, autojunk=False).get_matching_blocks()) / max(1, len(want))
        res.append({"n": k, "label": label, "note": note, "model": model, "ref": ref, "exaggeration": ex, "cfg": cfg,
                    "seconds": round(len(full) / C.SR, 1), "cpu_per_s": round(v.secs / max(0.1, v.audio_s), 1),
                    "make_s": round(time.time() - t0), "match": round(match, 2), "heard": h, "file": os.path.basename(mp3)})
        print(json.dumps(res[-1]), flush=True)
    json.dump(res, open(os.path.join(out, "variants.json"), "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2] if len(a) > 2 else "gericault-medusa", int(a[3]) if len(a) > 3 else 6, int(a[4]) if len(a) > 4 else None)
