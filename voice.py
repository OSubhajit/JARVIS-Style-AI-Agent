# voice.py — Voice, TTS, Whisper, Wake-Word Handling (Enhanced for JARVIS V4)

import threading
import speech_recognition as sr
import time
from config import *
from logger import log

# =========================
# TEXT-TO-SPEECH ENGINE
# =========================
_engine = None
_tts_lock = threading.Lock()


def _eng():
    """Initialize or reuse the pyttsx3 engine."""
    global _engine
    if _engine is None:
        import pyttsx3

        _engine = pyttsx3.init()
        _engine.setProperty("rate", SPEECH_RATE)
        _engine.setProperty("volume", SPEECH_VOLUME)

        # Select the best available voice (Windows-friendly)
        try:
            voices = _engine.getProperty("voices")
            preferred_voice = None

            for voice in voices:
                name = voice.name.lower()
                if "zira" in name:  # Preferred female voice
                    preferred_voice = voice.id
                    break
                elif "david" in name:  # Preferred male voice
                    preferred_voice = voice.id

            if preferred_voice:
                _engine.setProperty("voice", preferred_voice)

        except Exception as e:
            log.debug(f"Voice selection failed: {e}")

    return _engine


def speak(text):
    """Speak the given text and log it."""
    if not text:
        return

    print(f"\n[JARVIS 🔊] {text}")
    log.info(f"Speech: {text}")

    def _s():
        with _tts_lock:
            try:
                engine = _eng()
                engine.say(text)
                engine.runAndWait()
            except Exception as ex:
                log.error(f"TTS Error: {ex}")

    threading.Thread(target=_s, daemon=True).start()


# =========================
# SPEECH RECOGNITION
# =========================
_rec = sr.Recognizer()
_rec.energy_threshold = 300
_rec.pause_threshold = 0.8
_rec.dynamic_energy_threshold = True


# =========================
# WHISPER (LOAD ONCE)
# =========================
_whisper_model = None


def load_whisper():
    """Load Whisper model once if enabled."""
    global _whisper_model

    if USE_WHISPER and _whisper_model is None:
        try:
            import whisper

            print("[JARVIS] Loading Whisper model...")
            _whisper_model = whisper.load_model(WHISPER_MODEL)
            print("[JARVIS] Whisper model loaded.")

        except Exception as e:
            log.warning(f"Whisper load failed: {e}")
            _whisper_model = None


def _whisper_transcribe(audio_data):
    """Transcribe audio using Whisper."""
    global _whisper_model

    if _whisper_model is None:
        return None

    try:
        import tempfile
        import wave
        import os

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            filename = f.name

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data.get_wav_data())

        result = _whisper_model.transcribe(filename)
        os.unlink(filename)

        return result.get("text", "").strip()

    except Exception as e:
        log.warning(f"Whisper transcription error: {e}")
        return None


# =========================
# NOISE CALIBRATION
# =========================
_noise_calibrated = False


def _calibrate_noise():
    """Calibrate ambient noise once at startup."""
    global _noise_calibrated

    if _noise_calibrated:
        return

    try:
        with sr.Microphone() as src:
            print("[JARVIS] Calibrating microphone noise level...")
            _rec.adjust_for_ambient_noise(src, duration=1.5)
            print("[JARVIS] Microphone ready.")
            _noise_calibrated = True

    except Exception as e:
        log.warning(f"Noise calibration failed: {e}")
        _noise_calibrated = True  # Avoid repeated attempts


# =========================
# LISTEN ONCE
# =========================
def listen_once():
    """Capture a single utterance from the microphone."""
    _calibrate_noise()

    try:
        with sr.Microphone() as src:
            print("[JARVIS 🏙] Listening...")
            audio = _rec.listen(src, timeout=5, phrase_time_limit=10)
    except sr.WaitTimeoutError:
        return ""
    except Exception as e:
        log.debug(f"Microphone error: {e}")
        return ""

    # Try Whisper first
    if USE_WHISPER:
        text = _whisper_transcribe(audio)
        if text:
            print("[YOU 🎤]", text)
            return text

    # Fallback to Google Speech Recognition
    try:
        text = _rec.recognize_google(audio, language=VOICE_LANGUAGE)
        print("[YOU 🎤]", text)
        return text

    except sr.UnknownValueError:
        log.debug("Speech not recognized.")
        return ""

    except sr.RequestError as e:
        log.warning(f"Google Speech API error: {e}")
        return ""

    except Exception as e:
        log.debug(f"Speech recognition error: {e}")
        return ""


# =========================
# CONTINUOUS LISTENING
# =========================
_running = False
_callback = None


def _loop():
    """Background listening loop."""
    while _running:
        try:
            text = listen_once()
            if text and _callback:
                _callback(text)
        except Exception as e:
            log.debug(f"Voice loop error: {e}")

        time.sleep(0.2)  # Prevent CPU overload


def start_listening(callback):
    """Start continuous listening in a background thread."""
    global _running, _callback

    _callback = callback
    _running = True

    load_whisper()

    threading.Thread(target=_loop, daemon=True).start()
    print("[JARVIS] Continuous listening started...")


def stop_listening():
    """Stop continuous listening."""
    global _running
    _running = False


# =========================
# COMPATIBILITY WRAPPER
# =========================
def listen(timeout=None, **kwargs):
    """
    Compatibility wrapper expected by main.py.
    The timeout parameter is accepted but handled internally.
    """
    return listen_once()


# =========================
# WAKE-WORD COMPATIBILITY
# =========================
start_wake_word = start_listening
stop_wake_word = stop_listening