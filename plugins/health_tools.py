# plugins/health_tools.py — Health, Fitness & Wellness Tracker

import json, os
from datetime import datetime, timedelta, date
from database import _c

# ══ DB INIT ═══════════════════════════════════════════════════════════════════
def _init():
    with _c() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS water_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            ml INTEGER, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS sleep_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            hours REAL, quality TEXT, note TEXT, date TEXT DEFAULT(date('now')));
        CREATE TABLE IF NOT EXISTS workout_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise TEXT, sets INTEGER, reps INTEGER, weight_kg REAL,
            duration_min INTEGER, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS weight_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            weight_kg REAL, timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS calorie_log(id INTEGER PRIMARY KEY AUTOINCREMENT,
            food TEXT, calories INTEGER, meal TEXT, timestamp TEXT DEFAULT(datetime('now')));
        """)
_init()

# ══ BMI & BODY METRICS ════════════════════════════════════════════════════════
def bmi_calculate(weight_kg, height_cm):
    h  = float(height_cm) / 100
    w  = float(weight_kg)
    bmi = w / (h * h)
    if   bmi < 18.5: cat = "Underweight 🔵"
    elif bmi < 25:   cat = "Normal ✅"
    elif bmi < 30:   cat = "Overweight 🟡"
    else:            cat = "Obese 🔴"
    ideal_low  = 18.5 * h * h
    ideal_high = 24.9 * h * h
    return (f"BMI: {bmi:.1f} — {cat}\n"
            f"  Ideal weight range: {ideal_low:.1f}–{ideal_high:.1f} kg")

def calories_needed(weight_kg, height_cm, age, gender="male", activity="moderate"):
    w,h,a = float(weight_kg), float(height_cm), int(age)
    if gender.lower() == "male": bmr = 10*w + 6.25*h - 5*a + 5
    else:                        bmr = 10*w + 6.25*h - 5*a - 161
    multipliers = {"sedentary":1.2,"light":1.375,"moderate":1.55,"active":1.725,"very_active":1.9}
    tdee = bmr * multipliers.get(activity.lower(), 1.55)
    return (f"Daily Calorie Needs:\n"
            f"  BMR (base)     : {bmr:.0f} kcal\n"
            f"  TDEE ({activity}): {tdee:.0f} kcal\n"
            f"  Weight loss    : {tdee-500:.0f} kcal (-500)\n"
            f"  Weight gain    : {tdee+500:.0f} kcal (+500)")

def ideal_weight(height_cm, gender="male"):
    h = float(height_cm)
    # Devine formula
    if gender.lower() == "male": ideal = 50 + 2.3 * ((h/2.54) - 60)
    else:                        ideal = 45.5 + 2.3 * ((h/2.54) - 60)
    return f"Ideal weight for {height_cm}cm {gender}: {ideal:.1f} kg"

def water_goal(weight_kg):
    goal_ml = float(weight_kg) * 35
    return f"Daily water goal for {weight_kg}kg: {goal_ml:.0f} ml ({goal_ml/1000:.1f} L)"

# ══ WATER TRACKER ═════════════════════════════════════════════════════════════
def log_water(ml=250):
    with _c() as c: c.execute("INSERT INTO water_log(ml) VALUES(?)",(int(ml),))
    return f"💧 Logged {ml}ml of water."

def show_water_today():
    today = date.today().isoformat()
    with _c() as c:
        rows = c.execute("SELECT SUM(ml) as total, COUNT(*) as count FROM water_log WHERE DATE(timestamp)=?",(today,)).fetchone()
    total = rows["total"] or 0
    goal  = 2500
    pct   = min(total/goal*100, 100)
    bar   = "█" * int(pct/5) + "░" * (20 - int(pct/5))
    return f"💧 Water Today: {total}ml / {goal}ml\n  [{bar}] {pct:.0f}%\n  Logged {rows['count']} time(s)"

# ══ SLEEP TRACKER ══════════════════════════════════════════════════════════════
def log_sleep(hours, quality="good", note=""):
    with _c() as c: c.execute("INSERT INTO sleep_log(hours,quality,note) VALUES(?,?,?)",(float(hours),quality,note))
    rating = "😴 Great!" if float(hours)>=8 else "😐 OK" if float(hours)>=6 else "😩 Too little"
    return f"😴 Sleep logged: {hours}h ({quality}) — {rating}"

def show_sleep_week():
    with _c() as c:
        rows = c.execute("SELECT hours,quality,date FROM sleep_log ORDER BY id DESC LIMIT 7").fetchall()
    if not rows: return "No sleep logs yet."
    avg = sum(r["hours"] for r in rows) / len(rows)
    lines = [f"  {r['date']}  {r['hours']}h  [{r['quality']}]" for r in rows]
    return f"😴 Sleep (last 7 entries):\n"+"\n".join(lines)+f"\n  Average: {avg:.1f}h/night"

# ══ WORKOUT TRACKER ═══════════════════════════════════════════════════════════
def log_workout(exercise, sets=3, reps=10, weight_kg=0, duration_min=0):
    with _c() as c:
        c.execute("INSERT INTO workout_log(exercise,sets,reps,weight_kg,duration_min) VALUES(?,?,?,?,?)",
                  (exercise, int(sets), int(reps), float(weight_kg), int(duration_min)))
    vol = int(sets) * int(reps) * float(weight_kg)
    return f"💪 Logged: {exercise} — {sets}×{reps}" + (f" @ {weight_kg}kg (vol: {vol:.0f}kg)" if float(weight_kg)>0 else "")

def show_workouts(days=7):
    with _c() as c:
        rows = c.execute(
            "SELECT exercise,sets,reps,weight_kg,duration_min,timestamp FROM workout_log "
            "WHERE timestamp>=datetime('now',?) ORDER BY timestamp DESC",(f"-{days} days",)).fetchall()
    if not rows: return "No workouts logged."
    lines = [f"  💪 {r['exercise']:20} {r['sets']}×{r['reps']}" +
             (f" @{r['weight_kg']}kg" if r['weight_kg']>0 else "") +
             f"  [{r['timestamp'][:10]}]" for r in rows]
    return f"Workouts ({days} days):\n"+"\n".join(lines)

def workout_streak():
    with _c() as c:
        rows = c.execute("SELECT DISTINCT DATE(timestamp) as d FROM workout_log ORDER BY d DESC").fetchall()
    if not rows: return "No workout streak yet."
    dates = [date.fromisoformat(r["d"]) for r in rows]
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i-1] - dates[i]).days == 1: streak += 1
        else: break
    return f"🔥 Current workout streak: {streak} day(s)"

def personal_records():
    with _c() as c:
        rows = c.execute(
            "SELECT exercise, MAX(weight_kg) as max_w, MAX(reps) as max_r FROM workout_log GROUP BY exercise").fetchall()
    if not rows: return "No records yet."
    lines = [f"  🏆 {r['exercise']:25} Max weight: {r['max_w']}kg  Max reps: {r['max_r']}" for r in rows]
    return "Personal Records:\n" + "\n".join(lines)

# ══ WEIGHT TRACKER ════════════════════════════════════════════════════════════
def log_weight(weight_kg):
    with _c() as c: c.execute("INSERT INTO weight_log(weight_kg) VALUES(?)",(float(weight_kg),))
    return f"⚖️ Weight logged: {weight_kg}kg"

def show_weight_history():
    with _c() as c:
        rows = c.execute("SELECT weight_kg,timestamp FROM weight_log ORDER BY id DESC LIMIT 14").fetchall()
    if not rows: return "No weight logs."
    first, last = rows[-1]["weight_kg"], rows[0]["weight_kg"]
    change = last - first
    lines = [f"  {r['timestamp'][:10]}  {r['weight_kg']}kg" for r in rows]
    arrow = "📉" if change < 0 else "📈" if change > 0 else "➡️"
    return f"⚖️ Weight History:\n"+"\n".join(lines)+f"\n  Change: {change:+.1f}kg {arrow}"

# ══ CALORIE TRACKER ═══════════════════════════════════════════════════════════
def log_calories(food, calories, meal="snack"):
    with _c() as c:
        c.execute("INSERT INTO calorie_log(food,calories,meal) VALUES(?,?,?)",(food,int(calories),meal))
    return f"🍽️ Logged: {food} — {calories} kcal [{meal}]"

def show_calories_today():
    today = date.today().isoformat()
    with _c() as c:
        rows = c.execute("SELECT food,calories,meal FROM calorie_log WHERE DATE(timestamp)=?",(today,)).fetchall()
    if not rows: return "No calories logged today."
    total = sum(r["calories"] for r in rows)
    lines = [f"  {r['meal']:10} {r['food']:25} {r['calories']} kcal" for r in rows]
    return f"🍽️ Calories Today: {total} kcal\n"+"\n".join(lines)

# ══ HEALTH TIPS ═══════════════════════════════════════════════════════════════
def health_tip():
    TIPS = [
        "💧 Drink a glass of water every hour.",
        "🧘 Take 5 deep breaths — it lowers cortisol instantly.",
        "🚶 Walk for 10 minutes after meals — improves digestion.",
        "😴 Sleep 7–9 hours for optimal cognitive performance.",
        "💪 Do 10 push-ups right now. You have time.",
        "📵 No screens 30 minutes before bed improves sleep quality.",
        "🥗 Eat vegetables with every meal — aim for 5 colors per day.",
        "⏰ The 20-20-20 rule: every 20 min, look 20 feet away for 20 sec.",
        "🧠 Learning something new daily builds cognitive reserve.",
        "🏃 Even 15 minutes of exercise improves mood for hours.",
    ]
    import random
    return random.choice(TIPS)

def breathing_exercise(technique="4-7-8"):
    EXERCISES = {
        "4-7-8": "Inhale 4s → Hold 7s → Exhale 8s (repeat 4x) — reduces anxiety",
        "box":   "Inhale 4s → Hold 4s → Exhale 4s → Hold 4s (repeat) — improves focus",
        "wim":   "30 deep breaths → Hold → Breathe in → Hold 15s → Repeat 3x",
    }
    return f"🫁 Breathing: {technique}\n  {EXERCISES.get(technique.lower(), 'Unknown technique.')}"
