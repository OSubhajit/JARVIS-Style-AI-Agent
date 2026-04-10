# ⚡ J.A.R.V.I.S V4 — Maximum Edition

> A locally-running AI agent system inspired by Iron Man's JARVIS.  
> Built with Python + Ollama (Gemma3) · 270+ commands · Voice · Vision · REST API · Plugin Architecture

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Ollama](https://img.shields.io/badge/AI-Ollama%20%7C%20Gemma3-green)
![Flask](https://img.shields.io/badge/API-Flask-lightgrey?logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-informational?logo=windows)

---

## 📸 Overview

JARVIS V4 is a fully local AI agent that understands natural language, executes system commands, controls your PC, monitors your environment, and exposes a REST API with a web control panel — all running 100% offline via Ollama.

```
You: "jarvis, what's the weather in Hailakandi and remind me in 10 minutes to drink water"
JARVIS: fetches weather → sets reminder → speaks response
```

---

## 🚀 Quick Start

**Requirements:** Python 3.10+, [Ollama](https://ollama.com) installed

```bash
# 1. Clone the repo
git clone https://github.com/OSubhajit/JARVIS-Style-AI-Agent.git
cd JARVIS-Style-AI-Agent

# 2. Install all dependencies
python setup.py

# 3. Pull the AI model
ollama pull gemma3

# 4. Start Ollama
ollama serve

# 5. Launch JARVIS
python main.py
```

Web panel → **http://localhost:5000** (accessible from your phone on the same WiFi)

**Minimal install (core features only):**
```bash
pip install requests rich psutil flask pyperclip pyautogui cryptography python-dotenv
```

---

## 🗂️ Project Structure

```
JARVIS-Style-AI-Agent/
├── main.py              ← Entry point · REPL + voice loop
├── setup.py             ← Auto-installer
├── config.py            ← All settings (model, voice, API, keys)
├── interpreter.py       ← AI intent parser → structured JSON
├── executor.py          ← 150+ action router
├── database.py          ← SQLite backend (20 tables)
├── ai_brain.py          ← Ollama API wrapper
├── voice.py             ← Voice input (Whisper/Google) + TTS + wake word
├── api_server.py        ← Flask REST API + Web UI
├── monitor.py           ← System monitor · rules engine · hotkeys
├── safety.py            ← Input validation layer
├── memory.py            ← Persistent memory wrapper
├── agent.py             ← Autonomous agent loop
├── logger.py            ← Logging utility
├── requirements.txt
└── plugins/
    ├── web_tools.py         ← Weather, Wikipedia, News, Crypto, Stocks, Translate
    ├── file_tools.py        ← Files, PDF, OCR, Images, Zip, Duplicate finder
    ├── system_tools.py      ← System info, Network, Git, Windows, Services
    ├── productivity.py      ← Tasks, Habits, Vault, TOTP, Pomodoro, Email
    ├── media_tools.py       ← Volume, Clipboard history, YouTube download, Shazam
    ├── vision_tools.py      ← Webcam, Motion detection, Face detection, QR, Screen OCR
    ├── automation.py        ← Macros, Job scheduler, Rules engine, Backup, Wake-on-LAN
    ├── dev_tools.py         ← Code runner, HTTP client, Docker manager, AI dev tools
    ├── finance_tools.py     ← Crypto/stock prices, expense tracker, currency converter
    ├── health_tools.py      ← Health & fitness tracking
    ├── lifestyle_tools.py   ← Mood, habits, daily briefing, focus mode
    ├── network_advanced.py  ← ARP scan, WHOIS, DNS, IP geolocation, speed monitor
    ├── system_advanced.py   ← Boot analyzer, RAM flush, power plan, GPU monitor
    ├── science_tools.py     ← Unit conversion, calculations, constants
    ├── study_tools.py       ← Study timer, flashcards, notes
    ├── text_tools.py        ← Regex tester, Base64, hash, text utilities
    ├── code_generator.py    ← AI code generation, README/test generator
    ├── content_tools.py     ← Content creation tools
    ├── creative_tools.py    ← Creative writing, brainstorming
    ├── analytics.py         ← Usage analytics and stats
    ├── advanced_ai.py       ← Multi-step reasoning, AI chains
    └── mobile_remote.py     ← ADB phone control, Telegram bot, MQTT, Home Assistant
```

---

## ✨ Feature Highlights

### 🎙️ Voice & AI
- Wake word detection (`"Jarvis..."`)
- Online STT via Google Speech Recognition
- Offline STT via **OpenAI Whisper** (optional)
- Natural TTS responses via pyttsx3
- AI intent parsing via **Ollama + Gemma3** (fully local, no API key)
- Task chaining — one command triggers multiple actions

### 🖥️ System Control
- CPU, RAM, GPU, temperature monitoring
- Process manager, service manager
- Power plan switcher, RAM flush, boot analyzer
- Screen recorder, screenshot, clipboard history
- Global hotkeys, macro recorder

### 🔐 Security & Privacy
- Encrypted vault (Fernet encryption)
- TOTP 2FA code generator
- File encryption & shredder
- File integrity monitor
- Breach check via HaveIBeenPwned
- WiFi password extractor
- All AI runs **100% locally** — no data sent to the cloud

### 🌐 Web & Network
- Weather, Wikipedia, News search
- WHOIS, DNS lookup, IP geolocation
- ARP network scan, port scanner
- Internet speed test
- HTTP client (GET/POST/etc.)

### 📁 File & Media
- PDF merge, split, extract text
- Image resize, convert, EXIF metadata
- Duplicate file finder
- Auto-organize folder by file type
- YouTube download (via yt-dlp)
- Shazam song identification

### 💰 Finance & Productivity
- Crypto & stock price tracker
- Expense tracker
- Task manager, habit tracker, mood tracker
- Pomodoro timer, focus mode
- Daily briefing

### 🏠 Smart Home & Remote
- MQTT broker integration
- Home Assistant control
- Telegram bot (remote control from phone)
- ADB Android phone control
- Wake-on-LAN

### 🛠️ Developer Tools
- Python / JavaScript / Bash code runner
- Docker container manager
- Git integration
- AI-powered README & test generator
- Regex tester, Base64, hash utilities
- Local web server

---

## ⚙️ Configuration

Edit `config.py` to customize JARVIS:

| Key | Default | Description |
|---|---|---|
| `MODEL_NAME` | `gemma3` | Ollama model to use |
| `WAKE_WORD` | `jarvis` | Wake word to activate voice mode |
| `USE_WHISPER` | `False` | Enable offline Whisper STT |
| `WHISPER_MODEL` | `base` | Whisper model size (tiny/base/small/medium) |
| `VOICE_LANGUAGE` | `en-IN` | Speech recognition language |
| `API_ENABLED` | `True` | Enable Flask web panel |
| `API_PORT` | `5000` | Web panel port |
| `TELEGRAM_ENABLED` | `False` | Enable Telegram bot |
| `NTFY_ENABLED` | `False` | Enable push notifications |
| `DEFAULT_CITY` | `Hailakandi` | Default city for weather |
| `EMAIL_ADDRESS` | `""` | Gmail address for email features |
| `HA_URL` | `localhost:8123` | Home Assistant URL |
| `MQTT_BROKER` | `localhost` | MQTT broker address |

---

## 📊 Version History

| Feature | V1 | V2 | V3 | V4 |
|---|---|---|---|---|
| Basic commands | ✅ | ✅ | ✅ | ✅ |
| Voice + TTS | ✅ | ✅ | ✅ | ✅ |
| Wake word | ❌ | ✅ | ✅ | ✅ |
| Task chaining | ❌ | ✅ | ✅ | ✅ |
| SQLite memory | ❌ | ❌ | ✅ | ✅ |
| REST API + Web UI | ❌ | ❌ | ✅ | ✅ |
| Plugin system | ❌ | ❌ | ✅ | ✅ |
| Encrypted vault | ❌ | ❌ | ✅ | ✅ |
| Whisper offline STT | ❌ | ❌ | ❌ | ✅ |
| Computer vision | ❌ | ❌ | ❌ | ✅ |
| Face + motion detection | ❌ | ❌ | ❌ | ✅ |
| Macro recorder + scheduler | ❌ | ❌ | ❌ | ✅ |
| Telegram bot | ❌ | ❌ | ❌ | ✅ |
| ADB phone control | ❌ | ❌ | ❌ | ✅ |
| Smart Home (MQTT/HA) | ❌ | ❌ | ❌ | ✅ |
| Dev tools (Docker/Git/Code) | ❌ | ❌ | ❌ | ✅ |
| Finance + lifestyle tools | ❌ | ❌ | ❌ | ✅ |

---

## 🔌 REST API

Once running, the web panel is available at `http://localhost:5000`.

```bash
# Send a command via API
curl -X POST http://localhost:5000/command \
     -H "Content-Type: application/json" \
     -d '{"command": "what is the weather in Hailakandi"}'
```

---

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.com) with `gemma3` model pulled
- Windows (primary platform; Linux/Mac partially supported)
- Microphone (for voice features)
- Webcam (for vision features, optional)
- Tesseract OCR binary (for OCR features, optional)

---

## 👨‍💻 Author

**Subhajit Sarkar**  
CSE Student · Penetration Testing Enthusiast  
📍 Hailakandi, Assam, India  
🐙 [github.com/OSubhajit](https://github.com/OSubhajit)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
