"""Shared paths. Everything is relative to the kit root, so the folder can live anywhere (laptop, cloud box, GitHub runner).
Override the model folder with REELS_MODELS=/path if the models are cached elsewhere."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, "pipeline")
STUDIO = os.path.join(ROOT, "studio")
PUBLIC = os.path.join(STUDIO, "public")
STORIES = os.path.join(ROOT, "stories")
MODELS = os.environ.get("REELS_MODELS", os.path.join(ROOT, "models"))
KOKORO_MODEL = os.path.join(MODELS, "kokoro", "kokoro-v1.0.onnx")
KOKORO_VOICES = os.path.join(MODELS, "kokoro", "voices-v1.0.bin")
ASR_DIR = os.path.join(MODELS, "asr")            # encoder.int8.onnx, decoder.int8.onnx, joiner.int8.onnx, tokens.txt
DEPTH_DIR = os.path.join(MODELS, "depth")        # depth_anything_v2_<size>.onnx


def story_dir(arg):
    """accept a slug ('goya-saturn') or a path ('stories/goya-saturn')"""
    d = arg if os.path.isdir(arg) else os.path.join(STORIES, arg)
    d = os.path.abspath(d)
    if not os.path.exists(os.path.join(d, "story.json")): sys.exit(f"no story.json in {d}")
    return d
