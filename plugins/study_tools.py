# plugins/study_tools.py — Study Tools, Flashcards, Notes, Learning

import os, json, random, re
from datetime import datetime, timedelta, date
from database import _c


# ══ DB INIT ═══════════════════════════════════════════════════════════════════
def _init():
    with _c() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS flashcards(id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck TEXT, question TEXT, answer TEXT,
            ease REAL DEFAULT 2.5, interval_days INTEGER DEFAULT 1,
            next_review TEXT DEFAULT(date('now')), reviews INTEGER DEFAULT 0,
            created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, content TEXT, tags TEXT,
            pinned INTEGER DEFAULT 0, created TEXT DEFAULT(datetime('now')),
            updated TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS study_sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT, duration_min INTEGER, notes TEXT,
            timestamp TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS vocab(id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT, meaning TEXT, example TEXT, language TEXT DEFAULT 'english',
            mastered INTEGER DEFAULT 0, created TEXT DEFAULT(datetime('now')));
        """)
_init()


# ══ FLASHCARD SYSTEM (Spaced Repetition) ════════════════════════════════════
def add_flashcard(deck, question, answer):
    with _c() as c:
        c.execute("INSERT INTO flashcards(deck,question,answer) VALUES(?,?,?)",
                  (deck, question, answer))
    return f"🃏 Flashcard added to deck '{deck}'"

def review_flashcard(deck="default"):
    today = date.today().isoformat()
    with _c() as c:
        card = c.execute(
            "SELECT * FROM flashcards WHERE deck=? AND next_review<=? ORDER BY RANDOM() LIMIT 1",
            (deck, today)
        ).fetchone()
    if not card:
        return f"✅ No cards due in deck '{deck}'. Come back later!"
    return (f"🃏 Flashcard Review — Deck: {deck}\n"
            f"  ID: {card['id']}\n\n"
            f"  Q: {card['question']}\n\n"
            f"  [Answer hidden — type 'reveal card {card['id']}']")

def reveal_card(card_id):
    with _c() as c:
        card = c.execute("SELECT * FROM flashcards WHERE id=?", (int(card_id),)).fetchone()
    if not card: return f"Card #{card_id} not found."
    return f"🃏 Answer:\n  {card['answer']}\n\nRate difficulty: 'rate card {card_id} [easy/good/hard/fail]'"

def rate_card(card_id, rating):
    """Spaced repetition algorithm (SM-2 simplified)."""
    rating_map = {"easy":5,"good":4,"hard":3,"fail":0}
    q = rating_map.get(rating.lower(), 3)
    with _c() as c:
        card = c.execute("SELECT * FROM flashcards WHERE id=?", (int(card_id),)).fetchone()
        if not card: return f"Card #{card_id} not found."
        ease     = max(1.3, card["ease"] + 0.1*(q-5))
        if q < 3:
            interval = 1
        elif card["reviews"] == 0:
            interval = 1
        elif card["reviews"] == 1:
            interval = 6
        else:
            interval = int(card["interval_days"] * ease)
        next_rev = (date.today() + timedelta(days=interval)).isoformat()
        c.execute(
            "UPDATE flashcards SET ease=?,interval_days=?,next_review=?,reviews=reviews+1 WHERE id=?",
            (ease, interval, next_rev, int(card_id))
        )
    return f"✅ Card rated '{rating}'. Next review: {next_rev} (in {interval} day(s))"

def list_decks():
    with _c() as c:
        rows = c.execute(
            "SELECT deck, COUNT(*) as total, "
            "SUM(CASE WHEN next_review<=date('now') THEN 1 ELSE 0 END) as due "
            "FROM flashcards GROUP BY deck"
        ).fetchall()
    if not rows: return "No flashcard decks yet."
    lines = [f"  📚 {r['deck']:<30} {r['total']} cards  |  {r['due']} due today" for r in rows]
    return "Flashcard Decks:\n" + "\n".join(lines)

def export_deck(deck, filename=None):
    with _c() as c:
        rows = c.execute("SELECT question,answer FROM flashcards WHERE deck=?", (deck,)).fetchall()
    if not rows: return f"Deck '{deck}' is empty."
    fn = filename or f"{deck}_flashcards.json"
    with open(fn,"w") as f:
        json.dump([{"q":r["question"],"a":r["answer"]} for r in rows], f, indent=2)
    return f"Exported {len(rows)} cards → {fn}"

def import_deck(filename, deck_name="imported"):
    try:
        with open(filename) as f: data = json.load(f)
        with _c() as c:
            for card in data:
                c.execute("INSERT INTO flashcards(deck,question,answer) VALUES(?,?,?)",
                          (deck_name, card.get("q","?"), card.get("a","?")))
        return f"Imported {len(data)} cards into deck '{deck_name}'"
    except Exception as e: return f"Import error: {e}"


# ══ NOTES SYSTEM ══════════════════════════════════════════════════════════════
def add_note(title, content, tags=""):
    with _c() as c:
        c.execute("INSERT INTO notes(title,content,tags) VALUES(?,?,?)", (title,content,tags))
    return f"📝 Note saved: '{title}'"

def get_note(title_or_id):
    with _c() as c:
        if str(title_or_id).isdigit():
            note = c.execute("SELECT * FROM notes WHERE id=?", (int(title_or_id),)).fetchone()
        else:
            note = c.execute("SELECT * FROM notes WHERE LOWER(title) LIKE ?",
                             (f"%{title_or_id.lower()}%",)).fetchone()
    if not note: return f"Note not found: {title_or_id}"
    return (f"📝 Note #{note['id']}: {note['title']}\n"
            f"  Tags: {note['tags'] or 'none'}  |  {note['created'][:10]}\n"
            f"{'─'*50}\n{note['content']}")

def list_notes(tag=""):
    with _c() as c:
        if tag:
            rows = c.execute("SELECT id,title,tags,created FROM notes WHERE tags LIKE ? ORDER BY id DESC",
                             (f"%{tag}%",)).fetchall()
        else:
            rows = c.execute("SELECT id,title,tags,created FROM notes ORDER BY id DESC").fetchall()
    if not rows: return "No notes found."
    lines = [f"  [{r['id']:>3}] {r['title']:<40} [{r['tags'] or ''}] {r['created'][:10]}" for r in rows]
    return f"📝 Notes ({len(rows)}):\n" + "\n".join(lines)

def search_notes(query):
    with _c() as c:
        rows = c.execute(
            "SELECT id,title,content,created FROM notes WHERE "
            "LOWER(title) LIKE ? OR LOWER(content) LIKE ?",
            (f"%{query.lower()}%", f"%{query.lower()}%")
        ).fetchall()
    if not rows: return f"No notes matching '{query}'"
    lines = []
    for r in rows:
        snippet = r["content"][:80].replace("\n"," ")+"..."
        lines.append(f"  [{r['id']}] {r['title']}\n       {snippet}")
    return f"Search results for '{query}':\n" + "\n".join(lines)

def update_note(note_id, content):
    with _c() as c:
        c.execute("UPDATE notes SET content=?,updated=datetime('now') WHERE id=?",
                  (content, int(note_id)))
    return f"✅ Note #{note_id} updated."

def delete_note(note_id):
    with _c() as c:
        c.execute("DELETE FROM notes WHERE id=?", (int(note_id),))
    return f"🗑️ Note #{note_id} deleted."

def pin_note(note_id):
    with _c() as c:
        c.execute("UPDATE notes SET pinned=1-pinned WHERE id=?", (int(note_id),))
    return f"📌 Note #{note_id} pin toggled."

def export_notes(filename="notes_export.md"):
    with _c() as c:
        rows = c.execute("SELECT * FROM notes ORDER BY pinned DESC, id DESC").fetchall()
    if not rows: return "No notes to export."
    lines = [f"# JARVIS Notes Export\n*{datetime.now().strftime('%Y-%m-%d')}*\n"]
    for r in rows:
        pin = "📌 " if r["pinned"] else ""
        lines.append(f"## {pin}{r['title']}\n*{r['created'][:10]}*  |  Tags: {r['tags'] or 'none'}\n\n{r['content']}\n\n---\n")
    with open(filename,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    return f"📤 Exported {len(rows)} notes → {filename}"


# ══ STUDY SESSIONS ════════════════════════════════════════════════════════════
def log_study_session(subject, duration_min, notes=""):
    with _c() as c:
        c.execute("INSERT INTO study_sessions(subject,duration_min,notes) VALUES(?,?,?)",
                  (subject, int(duration_min), notes))
    return f"📚 Study session logged: {subject} — {duration_min} min"

def show_study_stats():
    with _c() as c:
        total = c.execute("SELECT SUM(duration_min) as t, COUNT(*) as n FROM study_sessions").fetchone()
        week  = c.execute(
            "SELECT subject, SUM(duration_min) as mins FROM study_sessions "
            "WHERE timestamp>=datetime('now','-7 days') GROUP BY subject ORDER BY mins DESC"
        ).fetchall()
    total_h = (total["t"] or 0) // 60
    total_m = (total["t"] or 0) % 60
    lines   = [f"  📖 {r['subject']:<30} {r['mins']//60}h {r['mins']%60}m" for r in week]
    return (f"📚 Study Statistics:\n"
            f"  Total time  : {total_h}h {total_m}m ({total['n']} sessions)\n\n"
            f"  This week by subject:\n" + "\n".join(lines))

def study_streak():
    with _c() as c:
        rows = c.execute(
            "SELECT DISTINCT DATE(timestamp) as d FROM study_sessions ORDER BY d DESC"
        ).fetchall()
    if not rows: return "No study streak yet."
    dates  = [date.fromisoformat(r["d"]) for r in rows]
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i-1] - dates[i]).days == 1: streak += 1
        else: break
    return f"🔥 Study streak: {streak} day(s)"


# ══ VOCABULARY BUILDER ════════════════════════════════════════════════════════
def add_vocab(word, meaning, example="", language="english"):
    with _c() as c:
        c.execute("INSERT INTO vocab(word,meaning,example,language) VALUES(?,?,?,?)",
                  (word.lower(), meaning, example, language))
    return f"📖 Vocabulary added: {word} — {meaning}"

def quiz_vocab(language="english"):
    with _c() as c:
        card = c.execute(
            "SELECT * FROM vocab WHERE language=? AND mastered=0 ORDER BY RANDOM() LIMIT 1",
            (language,)
        ).fetchone()
    if not card: return f"✅ All {language} vocabulary mastered!"
    return (f"📖 Vocabulary Quiz:\n"
            f"  Word: {card['word'].upper()}\n"
            f"  [Type 'reveal vocab {card['id']}' to see meaning]")

def reveal_vocab(vocab_id):
    with _c() as c:
        v = c.execute("SELECT * FROM vocab WHERE id=?", (int(vocab_id),)).fetchone()
    if not v: return "Not found."
    return (f"📖 {v['word'].upper()}\n"
            f"  Meaning : {v['meaning']}\n"
            f"  Example : {v['example'] or 'N/A'}\n"
            f"  [Type 'master vocab {vocab_id}' when you know it]")

def master_vocab(vocab_id):
    with _c() as c:
        c.execute("UPDATE vocab SET mastered=1 WHERE id=?", (int(vocab_id),))
    return f"✅ Vocabulary #{vocab_id} mastered!"

def show_vocab(language="english"):
    with _c() as c:
        rows = c.execute("SELECT * FROM vocab WHERE language=? ORDER BY id DESC", (language,)).fetchall()
    if not rows: return f"No vocabulary in '{language}'"
    mastered = sum(1 for r in rows if r["mastered"])
    lines = [f"  {'✅' if r['mastered'] else '📖'} {r['word']:<25} {r['meaning'][:50]}" for r in rows]
    return (f"Vocabulary ({language}) — {mastered}/{len(rows)} mastered:\n" +
            "\n".join(lines[:30]))


# ══ QUIZ GENERATOR ════════════════════════════════════════════════════════════
def generate_quiz(topic, num_questions=5):
    from plugins.advanced_ai import _ai
    prompt = f"""Generate a {num_questions}-question multiple choice quiz on: {topic}

Format each question EXACTLY like this:
Q1: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]

Generate all {num_questions} questions."""
    return _ai(prompt)

def explain_wrong_answer(question, your_answer, correct_answer):
    from plugins.advanced_ai import _ai
    prompt = f"""Quiz question: {question}
Student answered: {your_answer}
Correct answer: {correct_answer}

Briefly explain why {correct_answer} is correct and why {your_answer} is wrong. Max 100 words."""
    return _ai(prompt)

def summarize_for_study(text, style="bullet"):
    from plugins.advanced_ai import _ai
    if style == "bullet":
        prompt = f"Summarize for studying — use bullet points, bold key terms:\n\n{text[:3000]}"
    else:
        prompt = f"Create a concise study summary with sections:\n\n{text[:3000]}"
    return _ai(prompt)

def create_mind_map(topic):
    from plugins.advanced_ai import _ai
    prompt = f"""Create a text-based mind map for: {topic}

Format:
{topic.upper()}
├── Main Branch 1
│   ├── Sub-topic A
│   └── Sub-topic B
├── Main Branch 2
│   ├── Sub-topic C
│   └── Sub-topic D
└── Main Branch 3
    └── Sub-topic E

Make it comprehensive."""
    return _ai(prompt)

def mnemonics_generator(items):
    from plugins.advanced_ai import _ai
    return _ai(f"Create a memorable mnemonic/acronym to remember these items: {items}")
