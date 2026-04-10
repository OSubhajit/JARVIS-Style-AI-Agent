# interpreter.py — JARVIS V4 AI Intent Parser
import json, requests
from config import OLLAMA_URL, MODEL_NAME, AI_TIMEOUT, COMMANDS
from memory import recall_all_fmt, get_history_prompt, add_to_history
from database import alias_get, hist_add
from logger import log

PROMPT = """You are JARVIS V4, an advanced AI system agent.
Convert the user's instruction into a structured JSON action plan.

Available actions (partial list — use exact names):
{actions}

Conversation history:
{history}

{memories}

RULES — respond ONLY with valid JSON, zero extra text:
1. Single:  {{"action":"<name>","params":{{}}}}
2. Chain:   {{"chain":[{{"action":"a","params":{{}}}},{{"action":"b","params":{{}}}}]}}
3. Chat:    {{"action":"chat","params":{{"reply":"<answer>"}}}}
4. Memory:  {{"action":"remember_this","params":{{"key":"name","value":"Subhajit"}}}}
5. Unknown: {{"action":"unknown","params":{{}}}}

Key param formats:
search_google/youtube/github → {{"query":"..."}}
get_weather → {{"city":"..."}}
get_crypto_price/get_stock_price → {{"symbol":"BTC"}}
translate_text → {{"text":"...","target":"hi"}}
create_file → {{"filename":"x.txt","content":"..."}}
delete/read/write_to_file → {{"filename":"x.txt"}}
run_code → {{"code":"print('hi')","language":"python"}}
http_request → {{"method":"GET","url":"https://..."}}
hash_text → {{"text":"hello","algo":"sha256"}}
encode/decode_base64 → {{"text":"..."}}
calculate → {{"expression":"2**10"}}
convert_units → {{"value":100,"from":"km","to":"miles"}}
set_reminder → {{"message":"...","minutes":10}}
set_alarm → {{"message":"...","time":"07:30"}}
start_timer/stop_timer → {{"label":"workout"}} / {{"id":1}}
start_pomodoro → {{"task":"coding"}}
generate_qr → {{"text":"https://x.com","filename":"qr.png"}}
send_email → {{"to":"a@b.com","subject":"...","body":"..."}}
vault_add → {{"label":"gmail","password":"secret"}}
vault_get/vault_delete → {{"label":"gmail"}}
totp_add → {{"label":"github","secret":"BASE32SECRET"}}
totp_get → {{"label":"github"}}
encrypt/decrypt_file → {{"filename":"x.txt"}}
shred_file → {{"filename":"x.txt","passes":3}}
add_task → {{"title":"...","priority":"high"}}
complete_task/delete_task → {{"id":1}}
track_habit → {{"name":"workout"}}
log_mood → {{"mood":"happy","note":"..."}}
log_expense → {{"amount":150,"category":"food","note":"lunch"}}
add_alias → {{"alias":"ss","command":"take screenshot"}}
backup_folder → {{"source":"./data","dest":"./backups"}}
schedule_job → {{"name":"daily-report","command":"system report","interval_sec":86400}}
add_rule → {{"condition":"cpu > 85","action":"close chrome"}}
record_macro → {{"name":"morning"}}
play_macro → {{"name":"morning"}}
webcam_snapshot/face_recognize/scan_qr_webcam/read_screen → {{}}
scan_ports → {{"host":"localhost","ports":"1-1024"}}
ping_host → {{"host":"google.com"}}
kill_process → {{"process":"chrome.exe"}}
git_commit → {{"msg":"fix: update config"}}
docker_start/stop/logs → {{"name":"container_name"}}
download_youtube → {{"url":"https://youtube.com/...","audio_only":false}}
download_file → {{"url":"https://..."}}
translate_text → {{"text":"hello","target":"hi"}}
wake_on_lan → {{"mac":"AA:BB:CC:DD:EE:FF"}}
mqtt_publish → {{"topic":"home/light","message":"ON"}}
ha_toggle → {{"entity_id":"light.living_room"}}
telegram_send → {{"message":"hello"}}
send_notification → {{"title":"Alert","body":"..."}}
ip_geolocation → {{"ip":"8.8.8.8"}}
check_breach → {{"email":"user@example.com"}}
image_resize → {{"filename":"img.jpg","width":800,"height":600}}
summarize_text → {{"text":"..."}}
explain_topic → {{"topic":"..."}}
forget_this → {{"key":"name"}}
show_history → {{"limit":10}}
"""

def build_prompt(user_input):
    actions="\n".join(f"  {k}" for k in list(COMMANDS.keys())[:80])
    return PROMPT.format(actions=actions,history=get_history_prompt(),
                         memories=recall_all_fmt() or "")+f'\n\nUser: "{user_input}"\nJSON:'

def _clean(raw):
    raw=raw.replace("```json","").replace("```","").strip()
    s,e=raw.find("{"),raw.rfind("}")+1
    return raw[s:e] if s!=-1 and e>s else raw

def parse_intent(user_input):
    alias=alias_get(user_input.lower().strip())
    if alias: user_input=alias
    prompt=build_prompt(user_input)
    raw=""  # ensure defined even if response parsing fails
    try:
        r=requests.post(OLLAMA_URL,json={"model":MODEL_NAME,"prompt":prompt,"stream":False},timeout=AI_TIMEOUT)
        raw=r.json().get("response","").strip()
        intent=json.loads(_clean(raw))
        add_to_history("user",user_input)
        hist_add(user_input,intent.get("action","unknown"))
        log.debug(f"Intent: {intent}")
        return intent
    except json.JSONDecodeError:
        log.warning(f"JSON fail: {raw[:200]}")
        return {"action":"unknown","params":{}}
    except requests.exceptions.ConnectionError:
        log.error("Ollama not running.")
        return {"action":"chat","params":{"reply":"Ollama is not running. Start with: ollama serve"}}
    except Exception as e:
        log.error(f"Interpreter: {e}")
        return {"action":"unknown","params":{}}
