# database.py — JARVIS V4 Complete SQLite Layer

import sqlite3, os, json
from datetime import datetime
from config import DATABASE_FILE

os.makedirs("data", exist_ok=True)

def _c():
    c = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _c() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE, value TEXT, created TEXT DEFAULT(datetime('now')), updated TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS conversation(id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT, content TEXT, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT, trigger TEXT, fired INTEGER DEFAULT 0, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS aliases(id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT UNIQUE, command TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS command_history(id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT, action TEXT, success INTEGER DEFAULT 1, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS vault(id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT UNIQUE, encrypted TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS timers(id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT, started TEXT, stopped TEXT, duration REAL);
        CREATE TABLE IF NOT EXISTS clipboard_history(id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, streak INTEGER DEFAULT 0, last_done TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS mood_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT, note TEXT, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, status TEXT DEFAULT 'todo', priority TEXT DEFAULT 'medium',
            due TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL, category TEXT, note TEXT, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS macros(id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, actions TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS scheduled_jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, command TEXT, interval_sec INTEGER, last_run TEXT, active INTEGER DEFAULT 1,
            created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS rules(id INTEGER PRIMARY KEY AUTOINCREMENT,
            condition TEXT, action TEXT, active INTEGER DEFAULT 1, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS totps(id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT UNIQUE, secret TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS app_usage(id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT, duration_sec REAL, date TEXT DEFAULT(date('now')));
        CREATE TABLE IF NOT EXISTS pomodoro_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT, duration_min INTEGER, completed INTEGER DEFAULT 1,
            timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS file_integrity(id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE, hash TEXT, checked TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, dest TEXT, size_bytes INTEGER, timestamp TEXT DEFAULT(datetime('now')));
        """)

# ── Generic helpers ───────────────────────────────────────────────────────────
def mem_set(k,v):
    with _c() as c: c.execute("INSERT INTO memories(key,value,updated) VALUES(?,?,datetime('now')) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated=datetime('now')",(k.lower(),v))
def mem_get(k):
    with _c() as c:
        r=c.execute("SELECT value FROM memories WHERE key=?",(k.lower(),)).fetchone(); return r["value"] if r else None
def mem_all():
    with _c() as c: return c.execute("SELECT key,value,updated FROM memories ORDER BY updated DESC").fetchall()
def mem_del(k):
    with _c() as c: c.execute("DELETE FROM memories WHERE key=?",(k.lower(),))
def mem_clear():
    with _c() as c: c.execute("DELETE FROM memories")

def convo_add(role,content):
    with _c() as c: c.execute("INSERT INTO conversation(role,content) VALUES(?,?)",(role,content))
def convo_get(limit=30):
    with _c() as c: return list(reversed(c.execute("SELECT role,content FROM conversation ORDER BY id DESC LIMIT ?",(limit,)).fetchall()))
def convo_clear():
    with _c() as c: c.execute("DELETE FROM conversation")

def reminder_add(msg,trigger):
    with _c() as c: return c.execute("INSERT INTO reminders(message,trigger) VALUES(?,?)",(msg,trigger)).lastrowid
def reminder_all():
    with _c() as c: return c.execute("SELECT * FROM reminders WHERE fired=0 ORDER BY trigger").fetchall()
def reminder_fire(rid):
    with _c() as c: c.execute("UPDATE reminders SET fired=1 WHERE id=?",(rid,))
def reminder_del(rid):
    with _c() as c: c.execute("DELETE FROM reminders WHERE id=?",(rid,))

def alias_add(a,cmd):
    with _c() as c: c.execute("INSERT INTO aliases(alias,command) VALUES(?,?) ON CONFLICT(alias) DO UPDATE SET command=excluded.command",(a.lower(),cmd))
def alias_get(a):
    with _c() as c:
        r=c.execute("SELECT command FROM aliases WHERE alias=?",(a.lower(),)).fetchone(); return r["command"] if r else None
def alias_all():
    with _c() as c: return c.execute("SELECT alias,command FROM aliases ORDER BY alias").fetchall()
def alias_del(a):
    with _c() as c: c.execute("DELETE FROM aliases WHERE alias=?",(a.lower(),))

def hist_add(inp,action,ok=True):
    with _c() as c:
        c.execute("INSERT INTO command_history(input,action,success) VALUES(?,?,?)",(inp,action,int(ok)))
        c.execute("DELETE FROM command_history WHERE id NOT IN (SELECT id FROM command_history ORDER BY id DESC LIMIT 500)")
def hist_get(n=20):
    with _c() as c: return c.execute("SELECT input,action,timestamp FROM command_history ORDER BY id DESC LIMIT ?",(n,)).fetchall()

def vault_add(label,enc):
    with _c() as c: c.execute("INSERT INTO vault(label,encrypted) VALUES(?,?) ON CONFLICT(label) DO UPDATE SET encrypted=excluded.encrypted",(label.lower(),enc))
def vault_get(label):
    with _c() as c:
        r=c.execute("SELECT encrypted FROM vault WHERE label=?",(label.lower(),)).fetchone(); return r["encrypted"] if r else None
def vault_all():
    with _c() as c: return c.execute("SELECT label,created FROM vault ORDER BY label").fetchall()
def vault_del(label):
    with _c() as c: c.execute("DELETE FROM vault WHERE label=?",(label.lower(),))
def vault_clear():
    with _c() as c: c.execute("DELETE FROM vault")

def timer_start(label="default"):
    with _c() as c: return c.execute("INSERT INTO timers(label,started) VALUES(?,datetime('now'))",(label,)).lastrowid
def timer_stop(tid):
    with _c() as c:
        c.execute("UPDATE timers SET stopped=datetime('now'),duration=(julianday('now')-julianday(started))*86400 WHERE id=?",(tid,))
        r=c.execute("SELECT duration FROM timers WHERE id=?",(tid,)).fetchone(); return r["duration"] if r else 0

def clip_add(content):
    with _c() as c:
        from config import CLIPBOARD_HISTORY
        c.execute("INSERT INTO clipboard_history(content) VALUES(?)",(content,))
        c.execute("DELETE FROM clipboard_history WHERE id NOT IN (SELECT id FROM clipboard_history ORDER BY id DESC LIMIT ?)",(CLIPBOARD_HISTORY,))
def clip_all():
    with _c() as c: return c.execute("SELECT id,content,timestamp FROM clipboard_history ORDER BY id DESC").fetchall()

def habit_track(name):
    with _c() as c:
        today=datetime.now().date().isoformat()
        r=c.execute("SELECT * FROM habits WHERE name=?",(name,)).fetchone()
        if not r: c.execute("INSERT INTO habits(name,streak,last_done) VALUES(?,1,?)",(name,today))
        elif r["last_done"]!=today:
            from datetime import timedelta
            yesterday=(datetime.now().date()-timedelta(days=1)).isoformat()
            streak=r["streak"]+1 if r["last_done"]==yesterday else 1
            c.execute("UPDATE habits SET streak=?,last_done=? WHERE name=?",(streak,today,name))
def habit_all():
    with _c() as c: return c.execute("SELECT name,streak,last_done FROM habits ORDER BY streak DESC").fetchall()

def mood_add(mood,note=""):
    with _c() as c: c.execute("INSERT INTO mood_log(mood,note) VALUES(?,?)",(mood,note))
def mood_all(days=7):
    with _c() as c: return c.execute("SELECT mood,note,timestamp FROM mood_log WHERE timestamp>=datetime('now',?) ORDER BY timestamp DESC",(f"-{days} days",)).fetchall()

def task_add(title,priority="medium",due=None):
    with _c() as c: return c.execute("INSERT INTO tasks(title,priority,due) VALUES(?,?,?)",(title,priority,due)).lastrowid
def task_all(status=None):
    with _c() as c:
        if status: return c.execute("SELECT * FROM tasks WHERE status=? ORDER BY id DESC",(status,)).fetchall()
        return c.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
def task_done(tid):
    with _c() as c: c.execute("UPDATE tasks SET status='done' WHERE id=?",(tid,))
def task_del(tid):
    with _c() as c: c.execute("DELETE FROM tasks WHERE id=?",(tid,))

def expense_add(amount,category,note=""):
    with _c() as c: c.execute("INSERT INTO expenses(amount,category,note) VALUES(?,?,?)",(amount,category,note))
def expense_all(days=30):
    with _c() as c: return c.execute("SELECT * FROM expenses WHERE timestamp>=datetime('now',?) ORDER BY timestamp DESC",(f"-{days} days",)).fetchall()

def macro_save(name,actions):
    with _c() as c: c.execute("INSERT INTO macros(name,actions) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET actions=excluded.actions",(name,json.dumps(actions)))
def macro_get(name):
    with _c() as c:
        r=c.execute("SELECT actions FROM macros WHERE name=?",(name,)).fetchone()
        return json.loads(r["actions"]) if r else None
def macro_all():
    with _c() as c: return c.execute("SELECT name,created FROM macros ORDER BY name").fetchall()

def job_add(name,command,interval_sec):
    with _c() as c: c.execute("INSERT INTO scheduled_jobs(name,command,interval_sec) VALUES(?,?,?)",(name,command,interval_sec))
def job_all():
    with _c() as c: return c.execute("SELECT * FROM scheduled_jobs WHERE active=1").fetchall()
def job_del(name):
    with _c() as c: c.execute("UPDATE scheduled_jobs SET active=0 WHERE name=?",(name,))

def rule_add(condition,action):
    with _c() as c: c.execute("INSERT INTO rules(condition,action) VALUES(?,?)",(condition,action))
def rule_all():
    with _c() as c: return c.execute("SELECT * FROM rules WHERE active=1").fetchall()

def totp_add(label,secret):
    with _c() as c: c.execute("INSERT INTO totps(label,secret) VALUES(?,?) ON CONFLICT(label) DO UPDATE SET secret=excluded.secret",(label,secret))
def totp_get(label):
    with _c() as c:
        r=c.execute("SELECT secret FROM totps WHERE label=?",(label,)).fetchone(); return r["secret"] if r else None
def totp_all():
    with _c() as c: return c.execute("SELECT label,created FROM totps ORDER BY label").fetchall()

def integrity_add(path,hash_val):
    with _c() as c: c.execute("INSERT INTO file_integrity(filepath,hash) VALUES(?,?) ON CONFLICT(filepath) DO UPDATE SET hash=excluded.hash,checked=datetime('now')",(path,hash_val))
def integrity_all():
    with _c() as c: return c.execute("SELECT filepath,hash,checked FROM file_integrity").fetchall()

def pomo_log(task,duration,completed=True):
    with _c() as c: c.execute("INSERT INTO pomodoro_log(task,duration_min,completed) VALUES(?,?,?)",(task,duration,int(completed)))
