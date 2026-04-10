# plugins/productivity.py — Reminders, Tasks, Habits, Vault, TOTP, Pomodoro, etc.

import os, re, time, random, string, threading, smtplib, imaplib, email as email_lib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_HOST, SMTP_PORT,
                    IMAP_HOST, IMAP_PORT, VAULT_KEY_FILE, POMODORO_WORK, POMODORO_BREAK)
from database import *
from logger import log

# ══ REMINDERS ════════════════════════════════════════════════════════════════
def set_reminder(message, minutes, speak_fn=None):
    trigger=(datetime.now()+timedelta(minutes=minutes)).isoformat()
    rid=reminder_add(message,trigger)
    def _fire():
        time.sleep(minutes*60); reminder_fire(rid)
        print(f"\n\033[93m[JARVIS ⏰] REMINDER: {message}\033[0m")
        if speak_fn: speak_fn(f"Reminder: {message}")
    threading.Thread(target=_fire,daemon=True).start()
    return f"Reminder #{rid} set for {minutes}min: '{message}'"

def show_reminders():
    rows=reminder_all()
    if not rows: return "No active reminders."
    return "Active Reminders:\n"+"\n".join(f"  ⏳[{r['id']}] {r['trigger'][:16]} → {r['message']}" for r in rows)

def delete_reminder(rid):
    reminder_del(int(rid)); return f"Reminder #{rid} deleted."

def set_alarm(message, time_str, speak_fn=None):
    h,m=map(int,time_str.split(":")); now=datetime.now()
    target=now.replace(hour=h,minute=m,second=0,microsecond=0)
    if target<now: target+=timedelta(days=1)
    mins=int((target-now).total_seconds()/60)
    return set_reminder(f"⏰ ALARM: {message}",mins,speak_fn)

# ══ POMODORO ═════════════════════════════════════════════════════════════════
_pomo_state={"running":False,"task":"","start":None,"thread":None}

def start_pomodoro(task="Focus", speak_fn=None):
    if _pomo_state["running"]: return "Pomodoro already running."
    _pomo_state.update({"running":True,"task":task,"start":datetime.now()})
    def _run():
        if speak_fn: speak_fn(f"Pomodoro started. {POMODORO_WORK} minutes of focus. Go!")
        time.sleep(POMODORO_WORK*60)
        pomo_log(task,POMODORO_WORK)
        _pomo_state["running"]=False
        if speak_fn: speak_fn(f"Pomodoro complete! Take a {POMODORO_BREAK} minute break.")
        print(f"\n[JARVIS 🍅] Pomodoro done: {task}")
    _pomo_state["thread"]=threading.Thread(target=_run,daemon=True); _pomo_state["thread"].start()
    return f"🍅 Pomodoro started: '{task}' ({POMODORO_WORK} min)"

def stop_pomodoro():
    if not _pomo_state["running"]: return "No active Pomodoro."
    _pomo_state["running"]=False; return "Pomodoro stopped."

def pomodoro_status():
    if not _pomo_state["running"]: return "No active Pomodoro."
    elapsed=int((datetime.now()-_pomo_state["start"]).total_seconds()/60)
    remaining=POMODORO_WORK-elapsed
    return f"🍅 Pomodoro: '{_pomo_state['task']}' | Elapsed: {elapsed}min | Remaining: {remaining}min"

# ══ STOPWATCH ════════════════════════════════════════════════════════════════
def start_timer(label="default"): return f"Timer #{timer_start(label)} '{label}' started."
def stop_timer(tid):
    secs=timer_stop(int(tid)); m,s=divmod(int(secs),60)
    return f"Timer #{tid}: {m}m {s}s" if secs>0 else f"Timer #{tid} not found."

# ══ CALCULATOR ═══════════════════════════════════════════════════════════════
import math as _math
_SAFE={k:v for k,v in vars(_math).items() if not k.startswith("_")}
_SAFE.update({"abs":abs,"round":round,"min":min,"max":max,"sum":sum,"pow":pow,"int":int,"float":float,"hex":hex,"bin":bin,"oct":oct})

def calculate(expression):
    try:
        tokens=re.findall(r"[a-zA-Z_]+",expression.replace("e","X").replace("pi","X"))
        for t in tokens:
            if t!="X" and t not in _SAFE: return f"Unsafe: '{t}'"
        result=eval(expression,{"__builtins__":{}},_SAFE)
        return f"{expression} = {result}"
    except Exception as e: return f"Calc error: {e}"

# ══ UNIT CONVERTER ════════════════════════════════════════════════════════════
CONV={
    ("km","miles"):0.621371,("miles","km"):1.60934,("m","ft"):3.28084,("ft","m"):0.3048,
    ("cm","inches"):0.393701,("inches","cm"):2.54,("kg","lbs"):2.20462,("lbs","kg"):0.453592,
    ("g","oz"):0.035274,("oz","g"):28.3495,("kmh","mph"):0.621371,("mph","kmh"):1.60934,
    ("gb","mb"):1024,("mb","gb"):1/1024,("tb","gb"):1024,("gb","tb"):1/1024,
    ("sqm","sqft"):10.7639,("sqft","sqm"):0.092903,("ha","acres"):2.47105,("acres","ha"):0.404686,
    ("nm","mi"):1.15078,("mi","nm"):0.868976,("l","gal"):0.264172,("gal","l"):3.78541,
}

def convert_units(value, from_unit, to_unit):
    f,t=from_unit.lower().replace(" ",""),to_unit.lower().replace(" ","")
    if (f,t) in CONV: return f"{value} {from_unit} = {float(value)*CONV[(f,t)]:.5g} {to_unit}"
    if f in ("c","celsius") and t in ("f","fahrenheit"): return f"{value}°C = {float(value)*9/5+32:.2f}°F"
    if f in ("f","fahrenheit") and t in ("c","celsius"): return f"{value}°F = {(float(value)-32)*5/9:.2f}°C"
    if f in ("c","celsius") and t in ("k","kelvin"): return f"{value}°C = {float(value)+273.15:.2f}K"
    if f in ("k","kelvin") and t in ("c","celsius"): return f"{value}K = {float(value)-273.15:.2f}°C"
    return f"No conversion: {from_unit} → {to_unit}"

# ══ QR CODE ═══════════════════════════════════════════════════════════════════
def generate_qr(text, filename="qrcode.png"):
    try:
        import qrcode; img=qrcode.make(text); img.save(filename)
        return f"QR code saved: {filename}"
    except ImportError: return "qrcode not installed. pip install qrcode[pil]"
    except Exception as e: return f"QR error: {e}"

# ══ EMAIL ════════════════════════════════════════════════════════════════════
def send_email(to, subject, body):
    if not EMAIL_ADDRESS: return "Email not configured in config.py"
    try:
        msg=MIMEMultipart(); msg["From"]=EMAIL_ADDRESS; msg["To"]=to; msg["Subject"]=subject
        msg.attach(MIMEText(body,"plain"))
        with smtplib.SMTP(SMTP_HOST,SMTP_PORT) as s:
            s.ehlo(); s.starttls(); s.login(EMAIL_ADDRESS,EMAIL_PASSWORD); s.sendmail(EMAIL_ADDRESS,to,msg.as_string())
        return f"Email sent to: {to}"
    except Exception as e: return f"Email error: {e}"

def read_emails(limit=5):
    if not EMAIL_ADDRESS: return "Email not configured."
    try:
        m=imaplib.IMAP4_SSL(IMAP_HOST,IMAP_PORT); m.login(EMAIL_ADDRESS,EMAIL_PASSWORD); m.select("INBOX")
        _,msgs=m.search(None,"ALL"); ids=msgs[0].split()[-limit:]
        results=[]
        for eid in reversed(ids):
            _,data=m.fetch(eid,"(RFC822)"); msg=email_lib.message_from_bytes(data[0][1])
            results.append(f"  From: {msg['From']}\n  Subject: {msg['Subject']}\n  Date: {msg['Date']}")
        m.close(); m.logout()
        return "\n\n".join(results) if results else "No emails."
    except Exception as e: return f"Email read error: {e}"

# ══ TASKS ════════════════════════════════════════════════════════════════════
def add_task(title, priority="medium", due=None): return f"Task #{task_add(title,priority,due)} added: '{title}'"
def list_tasks(status=None):
    rows=task_all(status)
    if not rows: return "No tasks."
    icons={"todo":"📋","doing":"⚙️","done":"✅"}
    lines=[f"  {icons.get(r['status'],'•')}[{r['id']}] {r['title']} [{r['priority']}]" for r in rows]
    return "Tasks:\n"+"\n".join(lines)
def complete_task(tid): task_done(int(tid)); return f"Task #{tid} marked done ✅"
def delete_task(tid): task_del(int(tid)); return f"Task #{tid} deleted."

# ══ HABITS ═══════════════════════════════════════════════════════════════════
def track_habit(name): habit_track(name); return f"Habit tracked: '{name}'"
def show_habits():
    rows=habit_all()
    if not rows: return "No habits tracked."
    return "Habits:\n"+"\n".join(f"  🔥[{r['streak']}d] {r['name']} — last: {r['last_done']}" for r in rows)

# ══ MOOD ═════════════════════════════════════════════════════════════════════
def log_mood(mood, note=""):
    mood_add(mood,note)
    moods={"happy":"😊","sad":"😢","angry":"😤","tired":"😴","excited":"🤩","stressed":"😰","calm":"😌"}
    return f"Mood logged: {moods.get(mood.lower(),'📝')} {mood} — {note}"

def show_mood():
    rows=mood_all(7)
    if not rows: return "No mood logs this week."
    return "Mood Log (7 days):\n"+"\n".join(f"  {r['mood']:10} | {r['timestamp'][:10]} | {r['note']}" for r in rows)

# ══ EXPENSES ═════════════════════════════════════════════════════════════════
def log_expense(amount, category="general", note=""):
    expense_add(float(amount),category,note)
    return f"Expense logged: ₹{amount} [{category}] {note}"

def show_expenses():
    rows=expense_all(30)
    if not rows: return "No expenses this month."
    total=sum(r["amount"] for r in rows)
    cats={}
    for r in rows: cats[r["category"]]=cats.get(r["category"],0)+r["amount"]
    lines=[f"  {cat}: ₹{amt:.2f}" for cat,amt in sorted(cats.items(),key=lambda x:-x[1])]
    return f"Expenses (30 days): ₹{total:.2f}\n"+"\n".join(lines)

# ══ VAULT ════════════════════════════════════════════════════════════════════
def _fernet():
    try:
        from cryptography.fernet import Fernet
        os.makedirs("data",exist_ok=True)
        if not os.path.exists(VAULT_KEY_FILE):
            with open(VAULT_KEY_FILE,"wb") as f: f.write(Fernet.generate_key())
        with open(VAULT_KEY_FILE,"rb") as f: return Fernet(f.read())
    except ImportError: return None

def vault_store(label, password):
    f=_fernet()
    if not f: return "cryptography not installed. pip install cryptography"
    vault_add(label,f.encrypt(password.encode()).decode()); return f"Stored: {label}"

def vault_retrieve(label):
    f=_fernet()
    if not f: return "cryptography not installed."
    enc=vault_get(label)
    if not enc: return f"Not found: {label}"
    return f"🔐 {label}: {f.decrypt(enc.encode()).decode()}"

def vault_list_all():
    rows=vault_all()
    return "Vault:\n"+"\n".join(f"  🔐 {r['label']} (saved {r['created'][:10]})" for r in rows) if rows else "Vault empty."

def vault_remove(label): vault_del(label); return f"Removed: {label}"
def vault_wipe(): vault_clear(); return "Vault wiped."

def encrypt_file(filename):
    f=_fernet()
    if not f: return "cryptography not installed."
    try:
        with open(filename,"rb") as fp: data=fp.read()
        enc=f.encrypt(data)
        out=filename+".enc"
        with open(out,"wb") as fp: fp.write(enc)
        return f"Encrypted: {out}"
    except Exception as e: return f"Encrypt error: {e}"

def decrypt_file(filename):
    f=_fernet()
    if not f: return "cryptography not installed."
    try:
        with open(filename,"rb") as fp: data=fp.read()
        dec=f.decrypt(data)
        out=filename.replace(".enc","")
        with open(out,"wb") as fp: fp.write(dec)
        return f"Decrypted: {out}"
    except Exception as e: return f"Decrypt error: {e}"

# ══ TOTP ════════════════════════════════════════════════════════════════════
def totp_add_key(label, secret):
    totp_add(label,secret); return f"TOTP key stored: {label}"

def totp_get_code(label):
    try:
        import pyotp
        secret=totp_get(label)
        if not secret: return f"No TOTP key for: {label}"
        totp=pyotp.TOTP(secret)
        return f"🔑 {label}: {totp.now()}  (valid {30-int(time.time())%30}s)"
    except ImportError: return "pyotp not installed. pip install pyotp"
    except Exception as e: return f"TOTP error: {e}"

# ══ ALIASES ══════════════════════════════════════════════════════════════════
def add_alias(a,cmd): alias_add(a,cmd); return f"Alias: '{a}' → '{cmd}'"
def list_aliases():
    rows=alias_all()
    return "Aliases:\n"+"\n".join(f"  '{r['alias']}' → '{r['command']}'" for r in rows) if rows else "No aliases."
def remove_alias(a): alias_del(a); return f"Alias removed: {a}"

# ══ PASSWORD GEN ══════════════════════════════════════════════════════════════
def generate_password(length=16, symbols=True):
    chars=string.ascii_letters+string.digits+(string.punctuation if symbols else "")
    pwd="".join(random.SystemRandom().choice(chars) for _ in range(max(8,int(length))))
    strength="Strong 💪" if int(length)>=16 and symbols else "Medium"
    return f"Password ({strength}):\n  {pwd}"

# ══ FOCUS MODE ════════════════════════════════════════════════════════════════
_focus_active=False
def start_focus(minutes=25, speak_fn=None):
    global _focus_active
    _focus_active=True
    if speak_fn: speak_fn(f"Focus mode on for {minutes} minutes. Stay locked in.")
    def _end():
        time.sleep(int(minutes)*60); global _focus_active; _focus_active=False
        if speak_fn: speak_fn("Focus session complete. Great work!")
        print(f"\n[JARVIS 🎯] Focus session ended.")
    threading.Thread(target=_end,daemon=True).start()
    return f"🎯 Focus mode: {minutes} minutes"

def stop_focus():
    global _focus_active; _focus_active=False; return "Focus mode ended."

# ══ JOKES ════════════════════════════════════════════════════════════════════
JOKES=["Why do Java devs wear glasses? Because they don't C#.",
       "A SQL query walks into a bar. Walks up to two tables: 'Can I join you?'",
       "Why do programmers prefer dark mode? Light attracts bugs.",
       "There are 10 kinds of people: those who understand binary and those who don't.",
       "How do you comfort a JavaScript bug? You console it.",
       "Why was the developer broke? He used up all his cache.",
       "A programmer's wife: 'Get milk; if they have eggs, get a dozen.' He returned with 12 gallons.",
       "What's a computer's favorite snack? Microchips.",
       "Why did the programmer quit? They didn't get arrays.",
       "How does a computer get drunk? It takes screenshots."]
def tell_joke(): return random.choice(JOKES)

# ══ DAILY BRIEFING ════════════════════════════════════════════════════════════
def daily_briefing(speak_fn=None):
    from plugins.web_tools import get_weather, get_news
    now=datetime.now()
    greeting=f"Good {'morning' if now.hour<12 else 'afternoon' if now.hour<17 else 'evening'}."
    date_str=f"Today is {now.strftime('%A, %B %d')}."
    weather=get_weather(); news=get_news(3)
    reminders=show_reminders(); tasks=list_tasks("todo")
    habits=show_habits()
    brief=(f"{greeting} {date_str}\n\n🌤️ Weather:\n{weather}\n\n"
           f"📰 Headlines:\n{news}\n\n⏰ {reminders}\n\n📋 {tasks}\n\n🔥 {habits}")
    if speak_fn:
        speak_fn(greeting); speak_fn(date_str); speak_fn(f"Weather: {weather}")
    return brief
