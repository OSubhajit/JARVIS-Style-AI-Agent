# safety.py
from config import BLOCKED_KEYWORDS, CONFIRM_REQUIRED
from logger import log

def is_safe(user_input):
    low=user_input.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in low: log.warning(f"Blocked: '{kw}'"); return False
    return True

def is_allowed(action):
    FREE={"unknown","chat","remember_this","what_do_you_know","forget_this",
          "forget_everything","show_history","summarize_text","explain_topic"}
    from config import COMMANDS
    return action in FREE or action in COMMANDS

def needs_confirm(action): return action in CONFIRM_REQUIRED

def ask_confirm(action, speak_fn=None):
    if speak_fn: speak_fn(f"Confirm: {action.replace('_',' ')}?")
    ans=input(f"\n\033[93m[JARVIS ⚠️] '{action.replace('_',' ')}' — confirm? (yes/no): \033[0m").strip().lower()
    return ans in ("yes","y")
