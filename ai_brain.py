# ai_brain.py — JARVIS V4 AI Brain (OpenRouter — free & powerful)
# Get your free API key at: https://openrouter.ai/keys
import requests
import json
import os
from logger import log

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

# Free key from https://openrouter.ai/keys  (no credit card needed)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

URL = "https://openrouter.ai/api/v1/chat/completions"

# Best FREE models on OpenRouter (ranked by capability):
#   "meta-llama/llama-3.3-70b-instruct:free"   ← top free model, very capable
#   "deepseek/deepseek-r1:free"                 ← strong reasoning
#   "google/gemma-3-27b-it:free"                ← Google's free model
#   "mistralai/mistral-7b-instruct:free"        ← fast & lightweight
MODEL = "meta-llama/llama-3-8b-instruct:free"
MAX_TOKENS = 1024
TEMPERATURE = 0.2

# OpenRouter recommends these extra headers for free-tier usage
EXTRA_HEADERS = {
    "HTTP-Referer": "http://localhost",   # your app's URL (any value works)
    "X-Title":      "JARVIS",             # your app's name
}

# Warn at startup once — not on every call
if not OPENROUTER_API_KEY:
    log.warning(
        "OPENROUTER_API_KEY env var is not set. "
        "Get a FREE key at https://openrouter.ai/keys then set it with:\n"
        "  Windows: set OPENROUTER_API_KEY=sk-or-...\n"
        "  Linux/Mac: export OPENROUTER_API_KEY=sk-or-..."
    )

# ══════════════════════════════════════════════════════════════════════════════
# SHORT-TERM MEMORY  (last N turns, in-process only)
# ══════════════════════════════════════════════════════════════════════════════
_memory: list = []
MAX_MEMORY = 5


def add_memory(user: str, ai: str) -> None:
    _memory.append({"user": user, "ai": ai})
    if len(_memory) > MAX_MEMORY:
        _memory.pop(0)


def get_memory() -> str:
    return "\n".join(f"User: {m['user']}\nAI: {m['ai']}" for m in _memory)


# ══════════════════════════════════════════════════════════════════════════════
# AVAILABLE ACTIONS  (shown to the model)
# ══════════════════════════════════════════════════════════════════════════════
AVAILABLE_ACTIONS = """
You can control a full system with these tools:

Web:
search_google, search_youtube, open_url, get_weather, get_news,
get_crypto_price, get_stock_price, translate_text, check_website,
download_file, speed_test, ip_geolocation, dns_lookup, whois_lookup,
check_breach, wifi_passwords, scrape_url

System:
show_cpu, show_ram, show_disk, show_battery, show_gpu, show_temp,
system_report, flush_memory, boot_analyzer, list_processes, kill_process,
list_services, start_service, stop_service, power_plan, show_ip, show_wifi,
ping_host, scan_ports, arp_scan, network_speed, get_startup_apps,
add_to_startup, remove_from_startup, clear_temp, empty_recycle_bin,
list_windows, focus_window, minimize_window, maximize_window, close_window

Files:
create_file, delete_file, read_file, write_to_file, rename_file, copy_file,
move_file, list_files, search_file, get_file_info, zip_files, unzip_file,
open_file, ocr_image, pdf_merge, pdf_split, pdf_to_text, find_duplicates,
batch_rename, organize_downloads, text_diff, image_resize, image_convert,
extract_metadata

Media:
play_pause, next_track, prev_track, volume_mute, volume_up, volume_down,
volume_set, show_clipboard, copy_to_clipboard, clear_clipboard,
clipboard_history, take_screenshot, download_youtube, shazam, screen_record

Development:
run_code, http_request, format_json, validate_yaml, regex_test,
encode_base64, decode_base64, hash_text, serve_folder, stop_server,
docker_ps, docker_start, docker_stop, docker_logs, analyze_deps,
generate_readme, generate_tests, git_status, git_pull, git_push, git_log,
git_diff, git_commit, git_commit_message, install_package

Automation:
record_macro, play_macro, list_macros, schedule_job, list_jobs, cancel_job,
backup_folder, restore_backup, file_watcher_start, rules_add, rules_list,
send_notification, send_push_notification, wake_on_lan

Productivity:
set_reminder, show_reminders, delete_reminder, set_alarm, start_timer,
stop_timer, start_pomodoro, stop_pomodoro, pomodoro_status, calculate,
convert_units, generate_qr, send_email, read_emails, add_alias, list_aliases,
remove_alias, generate_password, tell_joke, daily_briefing, get_time,
get_date, add_task, list_tasks, complete_task, delete_task, habit_track,
habit_show, mood_log, mood_show, log_expense, show_expenses,
start_focus, stop_focus

Security / Vault:
vault_add, vault_get, vault_list, vault_delete, clear_vault,
totp_add, totp_get, encrypt_file, decrypt_file, shred_file,
check_password_strength, file_integrity_check

Vision:
webcam_snapshot, motion_detect, face_recognize, scan_qr_webcam,
object_detect, color_picker, read_screen, intruder_alert

AI Tasks:
summarize_text, explain_topic, code_review, explain_code, fix_code,
generate_code, optimize_code, write_email, improve_writing, write_essay,
translate_code, chat

Memory:
remember_this, what_do_you_know, forget_this, forget_everything, show_history
"""

# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = f"""You are JARVIS AI — an advanced system-control agent running on a local PC.

{AVAILABLE_ACTIONS}

YOUR JOB:
- Understand the user's intent precisely
- Break complex requests into logical steps
- Choose the best matching action(s) from the list above
- Return ONLY valid JSON — no markdown, no prose, no explanations

RESPONSE FORMAT — choose one:

Single action:
{{"plan":[{{"action":"search_google","params":{{"query":"Python tutorials"}}}}],"danger":false,"confidence":0.95}}

Multi-step chain:
{{"plan":[{{"action":"take_screenshot","params":{{}}}},{{"action":"send_email","params":{{"to":"me@email.com","subject":"Screenshot","body":"See attached"}}}}],"danger":true,"confidence":0.85}}

Conversational reply (when no action matches):
{{"plan":[{{"action":"chat","params":{{"reply":"<your helpful answer here>"}}}}],"danger":false,"confidence":0.9}}

RULES:
- Set danger=true for: delete, kill, send_email, shutdown, shred, clear_vault, wipe, format
- confidence is 0.0–1.0 — how certain you are the action matches the user's intent
- If the user just wants to chat, use the "chat" action with a helpful reply
- NEVER output anything outside the JSON object — no extra text
"""


# ══════════════════════════════════════════════════════════════════════════════
# API CALL  (with smart retry)
# ══════════════════════════════════════════════════════════════════════════════
def call_ai(user_input: str, retries: int = 2):
    if not OPENROUTER_API_KEY:
        log.error("OPENROUTER_API_KEY is not set — cannot call AI.")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        **EXTRA_HEADERS,
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject recent context so the model remembers short history
    ctx = get_memory()
    if ctx:
        messages.append({"role": "user", "content": f"Recent context:\n{ctx}"})
        messages.append({"role": "assistant", "content": "Got it."})

    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    for attempt in range(1, retries + 1):
        try:
            res = requests.post(URL, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status == 401:
                log.error("OpenRouter: invalid API key. Check OPENROUTER_API_KEY.")
                return None
            if status == 402:
                log.error("OpenRouter: insufficient credits. Get free key at openrouter.ai/keys")
                return None
            if status == 429:
                log.warning(f"OpenRouter: rate limited (attempt {attempt}). Retrying...")
            else:
                log.warning(f"OpenRouter HTTP {status} on attempt {attempt}: {e}")

        except requests.exceptions.ConnectionError:
            log.error("Cannot reach OpenRouter API. Check your internet connection.")
            return None

        except requests.exceptions.Timeout:
            log.warning(f"OpenRouter timeout on attempt {attempt}.")

        except Exception as e:
            log.warning(f"OpenRouter call error attempt {attempt}: {e}")

    log.error(f"OpenRouter: all {retries} attempts failed.")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# JSON PARSER  (robust — handles code fences and trailing prose)
# ══════════════════════════════════════════════════════════════════════════════
def parse_json(text: str):
    if not text:
        return None
    # Strip markdown fences
    text = text.replace("```json", "").replace("```", "").strip()
    # Direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass
    # Try to find the outermost { ... }
    try:
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
# ACTION NORMALISER
# ══════════════════════════════════════════════════════════════════════════════
_ACTION_ALIASES = {
    "open_browser":    "open_url",
    "google":          "search_google",
    "youtube":         "search_youtube",
    "screenshot":      "take_screenshot",
    "cpu":             "show_cpu",
    "ram":             "show_ram",
    "disk":            "show_disk",
    "reboot":          "restart",
    "notify":          "send_notification",
    "push":            "send_push_notification",
    "snap":            "webcam_snapshot",
}


def normalize_action(action: str) -> str:
    if not action:
        return "chat"
    a = action.lower().strip()
    return _ACTION_ALIASES.get(a, a)


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _chat_reply(msg: str) -> list:
    return [{"action": "chat", "params": {"reply": msg},
             "danger": False, "confidence": 0.0}]


def _api_unavailable() -> list:
    return _chat_reply(
        "AI is unavailable right now. "
        "Check your OPENROUTER_API_KEY or internet connection. "
        "Get a free key at https://openrouter.ai/keys"
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def ask_ai(user_input: str) -> list:
    """
    Call OpenRouter (free LLM), parse the response, return list of action dicts.

    Each dict:
        action     (str)   — JARVIS action name
        params     (dict)  — action parameters
        danger     (bool)  — whether the action is destructive
        confidence (float) — model's self-reported confidence 0.0–1.0
    """
    log.info(f"[AI INPUT] {user_input}")

    response = call_ai(user_input)
    if not response:
        return _api_unavailable()

    # Extract content from OpenRouter's (OpenAI-compatible) response
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        log.error(f"Unexpected OpenRouter response structure: {e} | raw: {response}")
        return _chat_reply("Unexpected response from AI.")

    parsed = parse_json(content)
    if not parsed:
        log.warning(f"Could not parse AI JSON: {content[:300]}")
        return _chat_reply("I didn't understand — could you rephrase that?")

    plan       = parsed.get("plan", [])
    danger     = bool(parsed.get("danger", False))
    confidence = float(parsed.get("confidence", 0.8))

    if not plan:
        # Valid JSON but no plan — model may have replied conversationally
        reply = parsed.get("reply") or parsed.get("message") or "I'm not sure how to help with that."
        return _chat_reply(reply)

    results = []
    for step in plan:
        raw_action = step.get("action", "")
        action     = normalize_action(raw_action)
        params     = step.get("params", {})
        if not isinstance(params, dict):
            params = {}

        # Per-step overrides if model provides them, else fall back to top-level
        step_danger     = bool(step.get("danger", danger))
        step_confidence = float(step.get("confidence", confidence))

        results.append({
            "action":     action,
            "params":     params,
            "danger":     step_danger,
            "confidence": step_confidence,
        })

    add_memory(user_input, str(results))
    log.info(f"[AI OUTPUT] {results}")
    return results
