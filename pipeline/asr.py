"""Speech recogniser (NVIDIA Parakeet TDT 0.6b via sherpa-onnx, runs on CPU). Used for two jobs:
1. word timestamps for captions and cuts, 2. a 'does a listener hear what we wrote?' check.
v3 is multilingual (25 European languages incl. English and Spanish); v2 is English-only. setup.sh installs v3."""
import os
import numpy as np
from scipy import signal
import sherpa_onnx
from paths import ASR_DIR

_rec = None


def recognizer():
    global _rec
    if _rec is None:
        _rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=os.path.join(ASR_DIR, "encoder.int8.onnx"), decoder=os.path.join(ASR_DIR, "decoder.int8.onnx"),
            joiner=os.path.join(ASR_DIR, "joiner.int8.onnx"), tokens=os.path.join(ASR_DIR, "tokens.txt"),
            model_type="nemo_transducer", num_threads=2)
    return _rec


def transcribe(audio, sr):
    """-> (text, words[{w, s, e}]) with times in seconds relative to the clip"""
    a16 = audio if sr == 16000 else signal.resample_poly(audio, 16000, sr).astype(np.float32)
    st = recognizer().create_stream(); st.accept_waveform(16000, a16); recognizer().decode_stream(st)
    r = st.result; words, cur = [], None
    for tok, ts in zip(r.tokens, r.timestamps):
        if tok.startswith("▁") or tok.startswith(" ") or cur is None:
            if cur: words.append(cur)
            cur = {"w": tok.lstrip("▁ "), "s": float(ts)}
        else:
            cur["w"] += tok
    if cur: words.append(cur)
    dur = len(a16) / 16000
    for i, w in enumerate(words): w["e"] = words[i + 1]["s"] if i + 1 < len(words) else dur
    return r.text, words
