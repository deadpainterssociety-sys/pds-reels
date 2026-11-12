"""Spanish voice samples for the Spanish-edition test (12 Nov 2026): the same ~28 s of our Madame X script read by
  - Kokoro's three Spanish voices (ef_dora, em_alex, em_santa)
  - Piper's native Spanish voices (Spain, Mexico, Argentina)
  - Chatterbox Multilingual (more natural delivery), taking its timbre from a Kokoro Spanish clip (synthetic, no real person)
Each sample goes to the private data release as es-sample-<name>.mp3 (Claude downloads them for Gigi).

usage: python automation/es_samples.py kokoro|piper <out_dir>     (main Python)
       .venv-cb/bin/python automation/es_samples.py chatterbox <out_dir>
       python automation/es_samples.py upload <out_dir>
"""
import glob, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pipeline"))

LINES = [("Un tirante. Solo un tirante casi acaba con la carrera de Sargent.", 0.8),
         ("París, 1884. John Singer Sargent es un joven retratista que empieza a hacerse un nombre.", 0.5),
         ("Su modelo: Virginie Gautreau, una belleza nacida en Estados Unidos, famosa por su piel pálida y empolvada.", 0.6),
         ("Y en el cuadro, el tirante derecho se le había caído del hombro.", 0.7),
         ("Los críticos se burlaron. Su madre le pidió que lo quitara. Y él… se negó.", 0.4)]
PIPER = ["es_ES-davefx-medium", "es_ES-sharvard-medium", "es_MX-claude-high", "es_MX-ald-medium", "es_AR-daniela-high"]


def join(parts, sr, path):
    import numpy as np, soundfile as sf
    a = np.concatenate(parts).astype("float32"); a = a / max(1e-6, float(abs(a).max())) * 0.89; sf.write(path, a, sr)
    print(os.path.basename(path), f"{len(a) / sr:.1f} s", flush=True)


def kokoro(out):
    import numpy as np
    from kokoro_onnx import Kokoro
    from paths import KOKORO_MODEL, KOKORO_VOICES
    k = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
    for v in ("ef_dora", "em_alex", "em_santa"):
        parts = []
        for t, p in LINES:
            a, sr = k.create(t, voice=v, speed=0.95, lang="es"); parts += [a, np.zeros(int(p * sr), dtype="float32")]
        join(parts, sr, f"{out}/kokoro_{v}.wav")
        a, sr = k.create("Hola. Te voy a contar la historia de un cuadro que escandalizó a todo París, y de un pintor que tuvo que huir.",
                         voice=v, speed=0.95, lang="es")
        join([a], sr, f"{out}/ref_{v}.wav")   # Chatterbox's timbre reference


def piper(out):
    import numpy as np, soundfile as sf
    d = f"{out}/piper-voices"; os.makedirs(d, exist_ok=True)
    for v in PIPER:
        try:
            subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir", d, v], check=True, capture_output=True)
            parts = []; sr = None
            for i, (t, p) in enumerate(LINES):
                f = f"{out}/_p{i}.wav"
                subprocess.run([sys.executable, "-m", "piper", "-m", f"{d}/{v}.onnx", "-f", f, "--", t], check=True, capture_output=True)
                a, sr = sf.read(f, dtype="float32"); parts += [a, np.zeros(int(p * sr), dtype="float32")]
            join(parts, sr, f"{out}/piper_{v}.wav")
        except subprocess.CalledProcessError as e: print("piper", v, "failed:", (e.stderr or b"")[-300:])


def chatterbox(out):
    import numpy as np, torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    torch.manual_seed(7)
    m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    for name, ref, cfg in (("chatterbox_alex", f"{out}/ref_em_alex.wav", 0.3), ("chatterbox_dora", f"{out}/ref_ef_dora.wav", 0.3),
                           ("chatterbox_default", None, 0.5)):
        parts = []
        for t, p in LINES:
            kw = {"audio_prompt_path": ref} if ref else {}
            w = m.generate(t.replace("…", "..."), language_id="es", exaggeration=0.45, cfg_weight=cfg, **kw)
            parts += [w.squeeze(0).numpy(), np.zeros(int(p * m.sr), dtype="float32")]
        join(parts, m.sr, f"{out}/{name}.wav")


def upload(out):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import release
    for f in sorted(glob.glob(f"{out}/*.wav")):
        name = os.path.basename(f)[:-4]
        if name.startswith(("ref_", "_p")): continue
        mp3 = f[:-4] + ".mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-af", "loudnorm=I=-16", "-b:a", "128k", mp3], check=True)
        release.data_put(f"es-sample-{name}.mp3", open(mp3, "rb").read(), "audio/mpeg"); print("uploaded", name)


if __name__ == "__main__":
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    {"kokoro": kokoro, "piper": piper, "chatterbox": chatterbox, "upload": upload}[sys.argv[1]](out)
