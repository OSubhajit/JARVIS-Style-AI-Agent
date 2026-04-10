# plugins/automation.py — Macros, Scheduler, Rules Engine, Backup, Auto-organize

import os, json, time, shutil, zipfile, threading
from datetime import datetime
from database import macro_save, macro_get, macro_all, job_add, job_all, job_del, rule_add, rule_all
from logger import log

# ══ MACRO RECORDER ════════════════════════════════════════════════════════════
_recording = {"active": False, "name": "", "actions": []}

def record_macro(name):
    _recording.update({"active": True, "name": name, "actions": []})
    return f"🔴 Recording macro '{name}'... Speak commands. Say 'stop recording' to finish."

def add_macro_action(action_str):
    if _recording["active"]: _recording["actions"].append(action_str)

def stop_recording():
    if not _recording["active"]: return "Not recording."
    name=_recording["name"]; actions=_recording["actions"][:]
    _recording["active"]=False
    macro_save(name,actions)
    return f"Macro '{name}' saved with {len(actions)} action(s)."

def play_macro(name, execute_fn=None):
    actions=macro_get(name)
    if not actions: return f"Macro not found: {name}"
    results=[]
    for action_str in actions:
        if execute_fn:
            from interpreter import parse_intent
            intent=parse_intent(action_str)
            r=execute_fn(intent.get("action","unknown"),intent.get("params",{}))
            results.append(r or "")
            time.sleep(0.5)
    return f"Macro '{name}' executed ({len(actions)} steps):\n"+"\n".join(results)

def list_macros():
    rows=macro_all()
    return "Macros:\n"+"\n".join(f"  📼 {r['name']} (saved {r['created'][:10]})" for r in rows) if rows else "No macros saved."

# ══ JOB SCHEDULER ════════════════════════════════════════════════════════════
_scheduler_running=False
_scheduler_thread=None

def schedule_job(name, command, interval_sec):
    job_add(name,command,int(interval_sec))
    return f"Job '{name}' scheduled every {interval_sec}s: {command}"

def list_jobs():
    rows=job_all()
    return "Scheduled Jobs:\n"+"\n".join(f"  ⚙️ [{r['id']}] {r['name']}: '{r['command']}' every {r['interval_sec']}s" for r in rows) if rows else "No jobs."

def cancel_job(name): job_del(name); return f"Job '{name}' cancelled."

def start_scheduler(execute_fn=None):
    global _scheduler_running, _scheduler_thread
    _scheduler_running=True
    def _loop():
        import sqlite3
        last_run={}
        while _scheduler_running:
            try:
                jobs=job_all()
                now=time.time()
                for job in jobs:
                    jid=job["id"]; interval=job["interval_sec"]; cmd=job["command"]
                    if now-last_run.get(jid,0)>=interval:
                        last_run[jid]=now
                        log.info(f"Scheduler: running job '{job['name']}'")
                        if execute_fn:
                            from interpreter import parse_intent
                            intent=parse_intent(cmd)
                            execute_fn(intent.get("action","unknown"),intent.get("params",{}))
            except Exception as e: log.error(f"Scheduler error: {e}")
            time.sleep(5)
    _scheduler_thread=threading.Thread(target=_loop,daemon=True)
    _scheduler_thread.start()
    log.info("Job scheduler started.")

def stop_scheduler():
    global _scheduler_running; _scheduler_running=False

# ══ RULES ENGINE ══════════════════════════════════════════════════════════════
# Rule format: "if cpu > 80 then close_window Chrome"
def add_rule(condition, action): rule_add(condition,action); return f"Rule added: IF {condition} THEN {action}"
def list_rules():
    rows=rule_all()
    return "Rules:\n"+"\n".join(f"  📏[{r['id']}] IF {r['condition']} THEN {r['action']}" for r in rows) if rows else "No rules."

def evaluate_rules(execute_fn=None):
    """Evaluate all active rules. Called from monitor loop."""
    try:
        import psutil
        ctx={"cpu":psutil.cpu_percent(),"ram":psutil.virtual_memory().percent,"disk":psutil.disk_usage(".").percent}
    except: ctx={}
    fired=[]
    for rule in rule_all():
        try:
            cond=rule["condition"].replace("cpu","ctx['cpu']").replace("ram","ctx['ram']").replace("disk","ctx['disk']")
            if eval(cond,{"__builtins__":{}},{"ctx":ctx}):
                action=rule["action"]
                fired.append(f"Rule fired: {rule['condition']} → {action}")
                if execute_fn:
                    from interpreter import parse_intent
                    intent=parse_intent(action)
                    execute_fn(intent.get("action","unknown"),intent.get("params",{}))
        except: pass
    return fired

# ══ BACKUP ════════════════════════════════════════════════════════════════════
def backup_folder(source, dest_dir=None):
    from config import BACKUP_DIR
    from database import backups
    dest_dir=dest_dir or BACKUP_DIR
    os.makedirs(dest_dir,exist_ok=True)
    try:
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        name=os.path.basename(source.rstrip("/\\"))
        out=os.path.join(dest_dir,f"{name}_backup_{ts}.zip")
        with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
            for root,_,files in os.walk(source):
                for f in files:
                    full=os.path.join(root,f)
                    zf.write(full,os.path.relpath(full,source))
        size=os.path.getsize(out)
        return f"Backup: {out}\n  Size: {size/1024:.1f} KB"
    except Exception as e: return f"Backup error: {e}"

def restore_backup(backup_file, dest="."):
    try:
        with zipfile.ZipFile(backup_file,"r") as zf: zf.extractall(dest)
        return f"Restored {backup_file} → {dest}"
    except Exception as e: return f"Restore error: {e}"

# ══ FILE WATCHER ══════════════════════════════════════════════════════════════
_watched_files={}

def file_watcher_start(filepath, speak_fn=None):
    import hashlib
    def _watch():
        def md5(f):
            h=hashlib.md5()
            with open(f,"rb") as fp:
                for c in iter(lambda:fp.read(8192),b""): h.update(c)
            return h.hexdigest()
        try: last=md5(filepath)
        except: return
        while filepath in _watched_files:
            time.sleep(3)
            try:
                curr=md5(filepath)
                if curr!=last:
                    msg=f"File changed: {filepath}"
                    print(f"\n[JARVIS 📁] {msg}")
                    if speak_fn: speak_fn(msg)
                    last=curr
            except: pass
    _watched_files[filepath]=True
    threading.Thread(target=_watch,daemon=True).start()
    return f"Watching: {filepath}"

def file_watcher_stop(filepath):
    _watched_files.pop(filepath,None); return f"Stopped watching: {filepath}"

# ══ NOTIFICATION PUSH ═════════════════════════════════════════════════════════
def send_notification(title, message=""):
    from config import NTFY_ENABLED, NTFY_TOPIC
    if not NTFY_ENABLED: return "ntfy notifications disabled. Set NTFY_ENABLED=True and NTFY_TOPIC in config.py"
    try:
        import requests
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={"Title":title,"Priority":"default","Tags":"computer"})
        return f"Notification sent: {title}"
    except Exception as e: return f"Notification error: {e}"

# ══ WAKE ON LAN ════════════════════════════════════════════════════════════════
def wake_on_lan(mac_address):
    try:
        import socket
        mac=mac_address.replace(":","").replace("-","")
        magic=bytes.fromhex("FF"*6 + mac*16)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(magic, ("<broadcast>", 9))
        return f"Magic packet sent to: {mac_address}"
    except Exception as e: return f"WoL error: {e}"
