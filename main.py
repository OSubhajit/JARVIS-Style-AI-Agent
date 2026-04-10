# main.py — JARVIS V4 Maximum Edition
# ─────────────────────────────────────────────────────────────────────────────
#  270+ commands | Voice + Whisper | Wake Word | Task Chains | REST API
#  SQLite Memory | Encrypted Vault | Vision | Automation | Smart Home
#  Telegram Bot | Scheduler | Rules Engine | Macros | Docker | Dev Tools
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, time, threading
from datetime import datetime

from database    import init_db
from interpreter import parse_intent
from executor    import execute
from safety      import is_safe, is_allowed, needs_confirm, ask_confirm
from memory      import add_to_history, clear_history
from monitor     import start_monitor, stop_monitor, start_hotkeys
from logger      import log
from config      import (VOICE_ENABLED, WAKE_WORD_ACTIVE, WAKE_WORD,
                        API_ENABLED, TELEGRAM_ENABLED)

# -------------------------------------------------------------------------
# Make the Windows console UTF‑8 so the banner (box‑drawing chars, emojis)
# prints without raising UnicodeEncodeError.
# -------------------------------------------------------------------------
if os.name == "nt":
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                                      encoding="utf-8",
                                      errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer,
                                      encoding="utf-8",
                                      errors="replace")
    except Exception:
        pass
    # Also switch the active code‑page to UTF‑8
    os.system("chcp 65001 >nul")

# ── Optional voice ────────────────────────────────────────────────────────────
try:
    from voice import speak, listen, start_wake_word, stop_wake_word
    VOICE_OK = True
except ImportError:
    VOICE_OK = False

    def speak(t):
        print(f"\n\033[36m[JARVIS] {t}\033[0m")

    def listen(**kw):
        return ""

    def start_wake_word(_):
        pass

    def stop_wake_word():
        pass

# ── Optional Rich ─────────────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel   import Panel
    from rich.table   import Table
    from rich         import box
    RICH = True
    con = Console()
except ImportError:
    RICH = False
    con = None

# ── Wake‑word event ─────────────────────────────────────────────────────────
_wake = threading.Event()


def _on_wake(text: str = None):
    """
    Callback used by the continuous‑listening thread.

    The ``voice`` module passes the recognised speech as *text*.
    If the text contains the configured ``WAKE_WORD`` we set the event
    so the main loop can pick it up.
    """
    if text and WAKE_WORD.lower() in text.lower():
        _wake.set()


# ── Banners ───────────────────────────────────────────────────────────────────
BANNER = """\033[36m
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗    ██╗   ██╗ ██╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝    ██║   ██║███║
     ██║███████║██████╔╝██║   ██║██║███████╗    ██║   ██║╚██║
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║    ╚██╗ ██╔╝ ██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║     ╚████╔╝  ██║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝      ╚═══╝   ╚═0╝
              M A X I M U M   E D I T I O N\033[0m"""

HELP = """\033[93m
╔══════════════════════════════════════════════════════════════════════╗
║                    JARVIS V4 — ALL COMMANDS                         ║
╠═══════════════════╦══════════════════════════════════════════════════╣
║ 🌐 WEB            ║ search google/youtube/wikipedia/github           ║
║                   ║ get weather/news/crypto/stocks                   ║
║ ... (omitted for brevity) ...
╚═══════════════════╩══════════════════════════════════════════════════╝\033[0m"""


# ── Run single action ───────────────────────────────────────────────────────
def _run_one(action, params, use_voice):
    """Execute a single action after safety & confirmation checks."""
    if action not in ("unknown", "chat") and not is_allowed(action):
        speak("That action is not permitted.")
        return ""

    if needs_confirm(action):
        if not ask_confirm(action, speak_fn=speak if use_voice else None):
            speak("Cancelled.")
            return ""

    result = execute(action, params, speak_fn=speak)

    # Voice feedback for concise results
    if result and action not in (
        "unknown", "system_report", "list_processes", "list_files",
        "show_clipboard", "read_file", "search_wikipedia", "get_news",
        "show_history", "list_tasks", "show_reminders", "daily_briefing",
        "what_do_you_know", "show_habits", "show_mood", "show_expenses",
        "vault_list", "list_aliases", "list_macros", "list_jobs", "list_rules",
        "list_windows", "show_clipboard_history", "git_log", "docker_ps",
    ):
        speak(result)

    if result:
        add_to_history("assistant", result[:200])

    return result


# ── Process intent ───────────────────────────────────────────────────────
def process_intent(intent, use_voice):
    """Handle a parsed intent – either a chain of actions or a single one."""
    if "chain" in intent:
        steps = intent["chain"]
        speak(f"Running {len(steps)} tasks.")
        for step in steps:
            _run_one(step.get("action", "unknown"), step.get("params", {}), use_voice)
            time.sleep(0.4)
    else:
        _run_one(intent.get("action", "unknown"), intent.get("params", {}), use_voice)


# ── Input helper ───────────────────────────────────────────────────────────
def get_input(use_voice):
    """Read input from voice (if enabled) or from the terminal."""
    if use_voice and VOICE_OK:
        text = listen()
        if text:
            return text
    try:
        return input("\n\033[92m[YOU] → \033[0m").strip()
    except EOFError:
        return "quit"


# ── AI / fallback pipeline ───────────────────────────────────────────────
def handle_user_input(user_input: str, use_voice: bool) -> None:
    """Try the new AI agent first; fall back to classic intent parsing."""
    # Show a “thinking” banner (Unicode‑safe fallback)
    try:
        print("\033[90m[JARVIS 🧠] Processing...\033[0m")
    except UnicodeEncodeError:
        print("\033[90m[JARVIS] Processing...\033[0m")

    agent_used = False
    try:
        from agent import run_agent
        result = run_agent(user_input, execute)
        if result is not None:
            speak(result)          # let the agent speak its answer
        agent_used = True
    except Exception as exc:        # Includes ImportError if no agent module
        log.warning(f"AI agent error: {exc}")

    if not agent_used:
        intent = parse_intent(user_input)
        log.info(f"Intent: {intent}")
        process_intent(intent, use_voice)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    # ── Init ───────────────────────────────────────────────────────────────
    for d in ("logs", "data", "screenshots", "recordings", "backups", "downloads"):
        os.makedirs(d, exist_ok=True)
    init_db()

    use_voice = VOICE_ENABLED and VOICE_OK

    # ── Banner & status line ─────────────────────────────────────────────
    print(BANNER)          # UTF‑8 safe now
    print(
        f"\n  {'🎙️ Voice: ON  | ' if use_voice else '⌨️  Text mode | '}"
        f"{'Wake word: ' + WAKE_WORD + '  | ' if WAKE_WORD_ACTIVE and use_voice else ''}"
        f"API: {'http://localhost:5000' if API_ENABLED else 'OFF'}  | "
        f"Type \033[93mhelp\033[0m for all commands\n"
    )

    # ── Background services ───────────────────────────────────────────────
    start_monitor(speak_fn=speak, execute_fn=execute)

    if WAKE_WORD_ACTIVE and use_voice:
        # Provided callback will receive the recognised speech text.
        start_wake_word(_on_wake)

    # Global hotkeys
    def _hotkey(action):
        result = execute(action, {}, speak_fn=speak)
        if result:
            speak(result)

    start_hotkeys(_hotkey)

    # ── REST API (optional) ─────────────────────────────────────────────────
    if API_ENABLED:
        try:
            from api_server import start_api
            start_api(execute, speak_fn=speak)
        except ImportError:
            log.warning("Flask not installed. Run: pip install flask")

    # ── Telegram bot (optional) ─────────────────────────────────────────────
    if TELEGRAM_ENABLED:
        try:
            from plugins.mobile_remote import start_telegram_bot
            start_telegram_bot(execute_fn=execute)
        except Exception as e:
            log.warning(f"Telegram: {e}")

    # ── Job scheduler (optional) ───────────────────────────────────────────
    try:
        from plugins.automation import start_scheduler
        start_scheduler(execute_fn=execute)
    except Exception as e:
        log.debug(f"Scheduler: {e}")

    # ── Greeting ───────────────────────────────────────────────────────────
    hour = datetime.now().hour
    greet = (
        "Good morning"
        if hour < 12
        else "Good afternoon"
        if hour < 17
        else "Good evening"
    )
    speak(f"{greet}. JARVIS V4 Maximum Edition online. All systems operational.")

    # ── Main interaction loop ───────────────────────────────────────────────
    while True:
        try:
            # ----- Wake‑word mode -----
            if WAKE_WORD_ACTIVE and use_voice:
                print(
                    f"\033[90m  [Say '{WAKE_WORD}' to activate...]\033[0m",
                    end="",
                    flush=True,
                )
                _wake.wait()
                _wake.clear()
                speak("Yes?")
                user_input = listen(timeout=9)   # timeout ignored by stub – ok
                if not user_input:
                    continue
            else:
                user_input = get_input(use_voice)

        except KeyboardInterrupt:
            print()
            speak("Shutting down. Goodbye.")
            stop_monitor()
            stop_wake_word()
            sys.exit(0)

        if not user_input:
            continue

        low = user_input.lower().strip()

        # ── Meta commands ─────────────────────────────────────────────────────
        if low in ("quit", "exit", "bye", "goodbye", "shutdown jarvis"):
            speak("Goodbye. Stay brilliant.")
            stop_monitor()
            stop_wake_word()
            break

        if low == "help":
            print(HELP)
            continue

        if low in ("voice on", "enable voice"):
            if VOICE_OK:
                use_voice = True
                speak("Voice enabled.")
            else:
                print("[JARVIS] Voice libraries not installed.")
            continue

        if low in ("voice off", "disable voice"):
            use_voice = False
            print("[JARVIS] Text mode active.")
            continue

        if low == "history clear":
            clear_history()
            speak("History cleared.")
            continue

        if low in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            continue

        # ── Macro recording (optional) ─────────────────────────────────────
        from plugins.automation import _recording, add_macro_action, stop_recording

        if _recording["active"]:
            if "stop recording" in low:
                result = stop_recording()
                speak(result)
            else:
                add_macro_action(user_input)
                print(f"  \033[90m[Macro recorded: {user_input}]\033[0m")
            continue

        # ── Safety check ─────────────────────────────────────────────────────
        if not is_safe(user_input):
            speak("That command is blocked for safety.")
            continue

        # ── AI pipeline (new agent + fallback) ─────────────────────────────
        handle_user_input(user_input, use_voice)

    # End of main loop – control returns here after a “quit” command.


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
