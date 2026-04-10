# memory.py
from database import (mem_set,mem_get,mem_all,mem_del,mem_clear,
                      convo_add,convo_get,convo_clear)
from config import MAX_CONVERSATION_LEN

def remember(k,v): mem_set(k,v)
def recall(k): return mem_get(k)
def recall_all_fmt():
    rows=mem_all()
    if not rows: return ""
    return "User facts:\n"+"\n".join(f"- {r['key']}: {r['value']}" for r in rows[:15])
def forget(k): mem_del(k)
def forget_all(): mem_clear()
def add_to_history(role,content): convo_add(role,content)
def get_history_prompt():
    rows=convo_get(MAX_CONVERSATION_LEN)
    if not rows: return "No history."
    return "\n".join(("User" if r["role"]=="user" else "JARVIS")+": "+r["content"] for r in rows)
def clear_history(): convo_clear()
