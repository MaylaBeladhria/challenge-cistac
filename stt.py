"""Optional local speech-to-text for reading aloud (faster-whisper, runs on this computer).

Privacy by design: the recording is processed IN MEMORY and never written to disk; only the transcript
(which the parent can edit) and the accuracy are kept. No cloud service is called.
Install:  pip install faster-whisper      (first use downloads the model once, ~150 MB for base.en)
Deliberately NO prompt biasing toward the target sentence: that would 'auto-correct' the child's mistakes.
"""
import io
import os

_MODELS = {}


def available():
    if os.getenv("DISABLE_VOICE") == "1":
        return False
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False


def transcribe(audio_bytes, model_name=None):
    """Returns (text, error). Never raises."""
    try:
        from faster_whisper import WhisperModel
        name = model_name or os.getenv("WHISPER_MODEL", "base.en")
        if name not in _MODELS:
            _MODELS[name] = WhisperModel(name, device="cpu", compute_type="int8")
        segments, _ = _MODELS[name].transcribe(io.BytesIO(audio_bytes), language="en", beam_size=1,
                                               vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip(), None
    except Exception as e:  # missing package, model download failed, unreadable audio...
        return "", f"{type(e).__name__}: {e}"
