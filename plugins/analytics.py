# plugins/analytics.py — Analytics, Statistics & Reporting

import os, json
from datetime import datetime, timedelta, date
from collections import Counter
from database import _c


# ══ COMMAND ANALYTICS ════════════════════════════════════════════════════════
def command_stats():
    with _c() as c:
        total = c.execute("SELECT COUNT(*) as n FROM command_history").fetchone()["n"]
        today = c.execute("SELECT COUNT(*) as n FROM command_history WHERE DATE(timestamp)=?",(date.today().isoformat(),)).fetchone()["n"]
        top   = c.execute("SELECT action, COUNT(*) as n FROM command_history GROUP BY action ORDER BY n DESC LIMIT 10").fetchall()
        week  = c.execute("SELECT DATE(timestamp) as d, COUNT(*) as n FROM command_history WHERE timestamp>=datetime('now','-7 days') GROUP BY d ORDER BY d").fetchall()

    lines  = [f"  {'Action':<35} {'Count':>6}"]
    lines += [f"  {r['action']:<35} {r['n']:>6}" for r in top]
    weekly = "\n".join(f"  {r['d']}: {'█'*min(r['n'],30)} {r['n']}" for r in week)
    return (f"📊 Command Statistics:\n"
            f"  Total commands: {total}  |  Today: {today}\n\n"
            f"  Top 10 Actions:\n" + "\n".join(lines) +
            f"\n\n  Activity (7 days):\n{weekly}")

def productivity_report():
    with _c() as c:
        tasks_done  = c.execute("SELECT COUNT(*) as n FROM tasks WHERE status='done'").fetchone()["n"]
        tasks_todo  = c.execute("SELECT COUNT(*) as n FROM tasks WHERE status='todo'").fetchone()["n"]
        reminders   = c.execute("SELECT COUNT(*) as n FROM reminders WHERE fired=1").fetchone()["n"]
        habits_rows = c.execute("SELECT name,streak FROM habits ORDER BY streak DESC LIMIT 5").fetchall()
        pomodoros   = c.execute("SELECT COUNT(*) as n, SUM(duration_min) as mins FROM pomodoro_log WHERE timestamp>=datetime('now','-7 days')").fetchone()
        expenses    = c.execute("SELECT SUM(amount) as total FROM expenses WHERE timestamp>=datetime('now','-7 days')").fetchone()

    habits_str = "\n".join(f"    🔥 {r['name']}: {r['streak']}d streak" for r in habits_rows)
    return (f"📈 Productivity Report (7 days):\n"
            f"  ✅ Tasks done  : {tasks_done}\n"
            f"  📋 Tasks todo  : {tasks_todo}\n"
            f"  ⏰ Reminders   : {reminders} completed\n"
            f"  🍅 Pomodoros   : {pomodoros['n'] or 0} sessions ({pomodoros['mins'] or 0} min)\n"
            f"  💸 Expenses    : ₹{expenses['total'] or 0:.2f}\n\n"
            f"  Top Habits:\n{habits_str}")

def weekly_summary():
    from plugins.health_tools import _init
    with _c() as c:
        cmd_count   = c.execute("SELECT COUNT(*) as n FROM command_history WHERE timestamp>=datetime('now','-7 days')").fetchone()["n"]
        task_count  = c.execute("SELECT COUNT(*) as n FROM tasks WHERE status='done' AND timestamp>=datetime('now','-7 days')").fetchone()["n"]

        try:
            water_avg = c.execute("SELECT AVG(daily_ml) as avg FROM (SELECT DATE(timestamp) as d, SUM(ml) as daily_ml FROM water_log GROUP BY d) WHERE d>=date('now','-7 days')").fetchone()["avg"]
        except: water_avg = 0
        try:
            sleep_avg = c.execute("SELECT AVG(hours) as avg FROM sleep_log WHERE date>=date('now','-7 days')").fetchone()["avg"]
        except: sleep_avg = 0

    return (f"📅 Weekly Summary:\n"
            f"  🤖 Commands used : {cmd_count}\n"
            f"  ✅ Tasks done     : {task_count}\n"
            f"  💧 Avg water/day  : {water_avg or 0:.0f}ml\n"
            f"  😴 Avg sleep      : {sleep_avg or 0:.1f}h/night")

def mood_trends():
    with _c() as c:
        rows = c.execute("SELECT mood, COUNT(*) as n FROM mood_log WHERE timestamp>=datetime('now','-30 days') GROUP BY mood ORDER BY n DESC").fetchall()
    if not rows: return "No mood data in last 30 days."
    total = sum(r["n"] for r in rows)
    lines = [f"  {r['mood']:<15} {'█'*r['n']:<20} {r['n']} ({r['n']/total*100:.0f}%)" for r in rows]
    return "😊 Mood Distribution (30 days):\n" + "\n".join(lines)

def habit_analytics():
    with _c() as c:
        rows = c.execute("SELECT name, streak, last_done, created FROM habits ORDER BY streak DESC").fetchall()
    if not rows: return "No habits tracked."
    lines = []
    for r in rows:
        bar  = "🟩" * min(r["streak"], 20) + "⬜" * max(0, 20-r["streak"])
        lines.append(f"  {r['name']:<25} {bar} {r['streak']}d")
    return "🔥 Habit Analytics:\n" + "\n".join(lines)

def expense_breakdown():
    with _c() as c:
        rows = c.execute(
            "SELECT category, SUM(amount) as total FROM expenses "
            "WHERE timestamp>=datetime('now','-30 days') GROUP BY category ORDER BY total DESC"
        ).fetchall()
    if not rows: return "No expenses logged."
    grand = sum(r["total"] for r in rows)
    lines = []
    for r in rows:
        pct = r["total"]/grand*100
        bar = "█" * int(pct/5)
        lines.append(f"  {r['category']:<20} {bar:<20} ₹{r['total']:.2f} ({pct:.0f}%)")
    return f"💸 Expense Breakdown (30 days) — Total: ₹{grand:.2f}:\n" + "\n".join(lines)

def sleep_analytics():
    with _c() as c:
        rows = c.execute("SELECT hours, quality, date FROM sleep_log ORDER BY id DESC LIMIT 30").fetchall()
    if not rows: return "No sleep data."
    avg  = sum(r["hours"] for r in rows) / len(rows)
    best = max(rows, key=lambda r: r["hours"])
    worst= min(rows, key=lambda r: r["hours"])
    good = sum(1 for r in rows if r["quality"] == "good")
    return (f"😴 Sleep Analytics (last {len(rows)} entries):\n"
            f"  Average   : {avg:.1f}h\n"
            f"  Best night: {best['hours']}h on {best['date']}\n"
            f"  Worst     : {worst['hours']}h on {worst['date']}\n"
            f"  Good sleep: {good}/{len(rows)} nights")

def ascii_bar_chart(data_dict, title="Chart", width=30):
    """Render a simple ASCII bar chart from a dict."""
    if not data_dict: return "No data to chart."
    max_val = max(data_dict.values()) or 1
    lines   = [f"📊 {title}:"]
    for label, val in data_dict.items():
        bar_len = int(val / max_val * width)
        bar     = "█" * bar_len + "░" * (width - bar_len)
        lines.append(f"  {str(label):<20} [{bar}] {val}")
    return "\n".join(lines)

def generate_report(report_type="daily"):
    if report_type == "daily":
        from plugins.productivity import show_reminders, list_tasks
        from plugins.web_tools import get_weather
        sections = [
            f"📅 Daily Report — {datetime.now().strftime('%A, %B %d %Y')}",
            "─" * 50,
            get_weather(),
            "─" * 50,
            show_reminders(),
            list_tasks("todo"),
        ]
        return "\n\n".join(sections)
    elif report_type == "weekly":
        return weekly_summary()
    else:
        return command_stats()

def disk_usage_breakdown():
    try:
        import os, shutil
        total,used,free = shutil.disk_usage(".")
        items = []
        for entry in sorted(os.scandir("."), key=lambda e: -(os.path.getsize(e.path) if e.is_file() else 0)):
            try:
                sz = os.path.getsize(entry.path) if entry.is_file() else sum(
                    os.path.getsize(os.path.join(dp,f))
                    for dp,_,fs in os.walk(entry.path) for f in fs)
                items.append((entry.name, sz))
            except: pass
        items.sort(key=lambda x:-x[1])
        lines = [f"  {'📁' if os.path.isdir(n) else '📄'} {n:<35} {sz/1024:.1f}KB" for n,sz in items[:15]]
        return (f"💿 Disk Usage:\n  Total:{total/1e9:.1f}GB  Used:{used/1e9:.1f}GB  Free:{free/1e9:.1f}GB\n\n"
                f"Current directory:\n"+"\n".join(lines))
    except Exception as e: return f"Disk error: {e}"
