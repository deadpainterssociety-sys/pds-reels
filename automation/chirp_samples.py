"""Google Cloud Text-to-Speech "Chirp 3: HD" voice auditions (12 Nov 2026). Needs the secret GOOGLE_TTS_KEY (an API key
restricted to the Cloud Text-to-Speech API, in Gigi's Google Cloud project). The key travels in a header, never in a URL,
so it can't end up in a log.

usage: python automation/chirp_samples.py reels <out_dir>              one MP3 per locale: every Chirp 3 HD voice says its
                                                                       own number, then the opening of our Madame X story
       python automation/chirp_samples.py full <out_dir> <voice>...    the full ~30 s sample for chosen voices
                                                                       (e.g. es-US-Chirp3-HD-Charon)
Results go to the private data release (chirp-*.mp3, chirp-index.json).
"""
import base64, json, os, subprocess, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FEMALE = "Achernar Aoede Autonoe Callirrhoe Despina Erinome Gacrux Kore Laomedeia Leda Pulcherrima Sulafat Vindemiatrix Zephyr".split()
MALE = "Achird Algenib Algieba Alnilam Charon Enceladus Fenrir Iapetus Orus Puck Rasalgethi Sadachbia Sadaltager Schedar Umbriel Zubenelgenubi".split()
TEXT = {
    "es": ["Un tirante. [pause short] Solo un tirante casi acaba con la carrera de Sargent.",
           "París, 1884. John Singer Sargent es un joven retratista que empieza a hacerse un nombre.",
           "Su modelo: Virginie Gautreau, una belleza nacida en Estados Unidos, famosa por su piel pálida y empolvada.",
           "Y en el cuadro, el tirante derecho se le había caído del hombro. [pause]",
           "Los críticos se burlaron. Su madre le pidió que lo quitara. Y él… [pause short] se negó."],
    "en": ["One strap on this dress nearly ended Sargent's career. [pause]",
           "Paris, 1884. John Singer Sargent was a rising young portrait painter.",
           "His model: Virginie Gautreau, an American-born beauty, famous for her pale, powdered skin.",
           "And in his version, her right strap had slipped off her shoulder. [pause]",
           "Critics mocked it. Her mother asked him to take it down. He… [pause short] refused."]}
LOCALES = ["es-US", "es-ES", "en-GB"]


def synth(voice, markup, rate=1.0):
    body = {"input": {"markup": markup}, "voice": {"languageCode": voice.split("-Chirp")[0], "name": voice},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000, "speakingRate": rate}}
    rq = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize", data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json", "X-Goog-Api-Key": os.environ["GOOGLE_TTS_KEY"]})
    try: return base64.b64decode(json.load(urllib.request.urlopen(rq, timeout=120))["audioContent"])
    except urllib.error.HTTPError as e: raise RuntimeError(f"Text-to-Speech {voice}: HTTP {e.code} {e.read().decode()[:300]}")


def wav_concat(files, out, gap=0.7):
    lst = out + ".txt"; sil = out + ".sil.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(gap), sil], check=True)
    open(lst, "w").write("".join(f"file '{f}'\nfile '{sil}'\n" for f in files))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-af", "loudnorm=I=-16",
                    "-b:a", "128k", out], check=True)


def reels(out):
    import release
    index = {}
    for loc in LOCALES:
        lang = loc[:2]; files = []; index[loc] = []
        for n, v in enumerate(MALE + FEMALE, 1):
            name = f"{loc}-Chirp3-HD-{v}"; who = "hombre" if v in MALE else "mujer"
            intro = f"Voz {n}." if lang == "es" else f"Voice {n}."
            try: audio = synth(name, f"{intro} [pause short] {TEXT[lang][0]}")
            except RuntimeError as e: print(e); continue
            f = f"{out}/{loc}_{n:02d}.wav"; open(f, "wb").write(audio); files.append(f)
            index[loc].append({"n": n, "voice": name, "gender": "male" if v in MALE else "female"})
        mp3 = f"{out}/chirp-reel-{loc}.mp3"; wav_concat(files, mp3)
        release.data_put(f"chirp-reel-{loc}.mp3", open(mp3, "rb").read(), "audio/mpeg"); print(loc, len(files), "voices")
    release.data_put("chirp-index.json", json.dumps(index, indent=1))


def full(out, voices):
    import release
    for v in voices:
        lang = v[:2]; files = []
        for i, line in enumerate(TEXT[lang]):
            f = f"{out}/{v}_{i}.wav"; open(f, "wb").write(synth(v, line)); files.append(f)
        mp3 = f"{out}/chirp-full-{v}.mp3"; wav_concat(files, mp3, gap=0.35)
        release.data_put(f"chirp-full-{v}.mp3", open(mp3, "rb").read(), "audio/mpeg"); print("full", v)


if __name__ == "__main__":
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    reels(out) if sys.argv[1] == "reels" else full(out, sys.argv[3:])
