#!/usr/bin/env python3
# setup.py — JARVIS V4 One-Click Setup (Fixed & Enhanced)

import os
import sys
import subprocess

print("""
╔══════════════════════════════════════╗
║        JARVIS V4 — Setup Wizard      ║
╚══════════════════════════════════════╝
""")

# ──────────────────────────────────────────────────────────────
# Helper Function
# ──────────────────────────────────────────────────────────────
def install_package(package):
    """Install a Python package silently."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", package],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────
# Create Required Directories
# ──────────────────────────────────────────────────────────────
DIRECTORIES = [
    "logs", "data", "screenshots", "recordings",
    "backups", "downloads", "plugins"
]

for directory in DIRECTORIES:
    os.makedirs(directory, exist_ok=True)

print("✅ Directories created")


# ──────────────────────────────────────────────────────────────
# Check Python Version
# ──────────────────────────────────────────────────────────────
if sys.version_info < (3, 9):
    print(f"❌ Python 3.9+ required. You have: {sys.version}")
    sys.exit(1)

print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")


# ──────────────────────────────────────────────────────────────
# Upgrade pip
# ──────────────────────────────────────────────────────────────
print("\nUpgrading pip...")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("✅ pip upgraded")


# ──────────────────────────────────────────────────────────────
# Core Dependencies
# ──────────────────────────────────────────────────────────────
CORE = [
    "requests",
    "rich",
    "psutil",
    "flask",
    "pyperclip",
    "cryptography",
    "qrcode[pil]",
    "Pillow",
    "pyotp",
    "pyyaml",
    "beautifulsoup4",
    "python-dotenv"
]

print("\nInstalling core packages...")
for pkg in CORE:
    status = "✅" if install_package(pkg) else "⚠️"
    print(f"  {status} {pkg}")


# ──────────────────────────────────────────────────────────────
# Optional Dependencies
# ──────────────────────────────────────────────────────────────
OPTIONAL = {
    "SpeechRecognition": "Voice input",
    "pyttsx3": "Text-to-speech",
    "pyautogui": "Screenshots & media keys",
    "pygetwindow": "Window management",
    "keyboard": "Global hotkeys",
    "opencv-python": "Computer vision",
    "yt-dlp": "YouTube downloads",
    "speedtest-cli": "Speed test",
    "python-whois": "WHOIS lookups",
    "PyPDF2": "PDF tools",
    "pytesseract": "OCR",
    "paho-mqtt": "Smart home / MQTT",
    "GPUtil": "GPU monitoring",
    "torch": "Required for Whisper speech recognition"
}

print("\nInstalling optional packages (failures are OK)...")
for pkg, desc in OPTIONAL.items():
    status = "✅" if install_package(pkg) else "⚠️ (optional)"
    print(f"  {status} {pkg:<20} — {desc}")


# ──────────────────────────────────────────────────────────────
# PyAudio Installation Guidance (Windows)
# ──────────────────────────────────────────────────────────────
print("\nChecking PyAudio (required for microphone support)...")
if not install_package("pyaudio"):
    print("  ⚠️ PyAudio installation failed.")
    print("  Attempting installation via pipwin...")
    if install_package("pipwin"):
        subprocess.run(
            [sys.executable, "-m", "pipwin", "install", "pyaudio"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("  ✅ PyAudio installed via pipwin")
    else:
        print("  ⚠️ Install manually:")
        print("     pip install pipwin")
        print("     pipwin install pyaudio")
else:
    print("  ✅ PyAudio installed")


# ──────────────────────────────────────────────────────────────
# OCR Guidance
# ──────────────────────────────────────────────────────────────
print("\nChecking Tesseract OCR...")
print("  ⚠️ If OCR fails, install Tesseract from:")
print("     https://github.com/UB-Mannheim/tesseract/wiki")
print("     Default path: C:\\Program Files\\Tesseract-OCR\\")


# ──────────────────────────────────────────────────────────────
# Ollama Detection
# ──────────────────────────────────────────────────────────────
print("\nChecking Ollama...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=3)
    models = [m["name"] for m in response.json().get("models", [])]
    print(f"  ✅ Ollama running. Models: {models or 'none pulled yet'}")
    if not models:
        print("  ⚠️ Pull a model using: ollama pull gemma3")
except Exception:
    print("  ⚠️ Ollama not running.")
    print("     Start with: ollama serve")
    print("     Download from: https://ollama.com")


# ──────────────────────────────────────────────────────────────
# Completion Message
# ──────────────────────────────────────────────────────────────
print("""
╔══════════════════════════════════════╗
║        Setup Complete! 🚀            ║
║                                      ║
║   Run JARVIS:  python main.py        ║
║   Web Panel:   http://localhost:5000 ║
╚══════════════════════════════════════╝
""")