# plugins/media_tools.py — Media, Volume, Clipboard History, Screenshots

import os
from datetime import datetime
from config import SCREENSHOT_DIR
from database import clip_add, clip_all
from logger import log

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def _ag():
    try: import pyautogui; return pyautogui
    except: return None
def _pc():
    try: import pyperclip; return pyperclip
    except: return None

def play_pause():   ag=_ag(); return (ag.press("playpause"),"Play/Pause ▶⏸")[1] if ag else "pyautogui not installed"
def next_track():   ag=_ag(); return (ag.press("nexttrack"),"Next ⏭")[1] if ag else "pyautogui not installed"
def prev_track():   ag=_ag(); return (ag.press("prevtrack"),"Previous ⏮")[1] if ag else "pyautogui not installed"
def volume_mute():  ag=_ag(); return (ag.press("volumemute"),"Muted 🔇")[1] if ag else "pyautogui not installed"

def volume_up(amount=10):
    ag=_ag()
    if not ag: return "pyautogui not installed"
    for _ in range(max(1,int(amount)//2)): ag.press("volumeup")
    return f"Volume ↑ +{amount}"

def volume_down(amount=10):
    ag=_ag()
    if not ag: return "pyautogui not installed"
    for _ in range(max(1,int(amount)//2)): ag.press("volumedown")
    return f"Volume ↓ -{amount}"

def volume_set(level=50):
    try:
        os.system(f'PowerShell -c "[audio]::Volume={int(level)/100}"')
        return f"Volume → {level}%"
    except Exception as e: return f"Volume set error: {e}"

def show_clipboard():
    pc=_pc()
    if not pc: return "pyperclip not installed"
    content=pc.paste()
    return f"Clipboard ({len(content)} chars):\n{content[:300]}{'...' if len(content)>300 else ''}" if content else "Clipboard empty."

def copy_to_clipboard(text):
    pc=_pc()
    if not pc: return "pyperclip not installed"
    pc.copy(text); clip_add(text)
    return f"Copied: {text[:60]}{'...' if len(text)>60 else ''}"

def clear_clipboard():
    pc=_pc()
    if not pc: return "pyperclip not installed"
    pc.copy(""); return "Clipboard cleared."

def show_clipboard_history():
    rows=clip_all()
    if not rows: return "No clipboard history."
    lines=[f"  [{r['id']}] {r['timestamp'][:16]}  {r['content'][:60]}{'...' if len(r['content'])>60 else ''}" for r in rows]
    return f"Clipboard History ({len(rows)}):\n"+"\n".join(lines)

def take_screenshot(filename=None):
    ag=_ag()
    if not ag: return "pyautogui not installed"
    try:
        fn=filename or f"{SCREENSHOT_DIR}/ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        ag.screenshot(fn); return f"Screenshot: {fn}"
    except Exception as e: return f"Screenshot error: {e}"

def download_youtube(url, audio_only=False):
    try:
        import yt_dlp, os
        from config import DOWNLOAD_DIR
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        opts={"outtmpl":f"{DOWNLOAD_DIR}/%(title)s.%(ext)s","quiet":True,"no_warnings":True}
        if audio_only:
            opts.update({"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}]})
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url,download=True)
        return f"Downloaded: {info.get('title','video')}"
    except ImportError: return "yt-dlp not installed. pip install yt-dlp"
    except Exception as e: return f"Download error: {e}"

def shazam(filename=None):
    """Identify a song from audio file or current playing audio."""
    try:
        from shazamio import Shazam
        import asyncio
        async def _identify(f):
            shazam=Shazam(); out=await shazam.recognize(f)
            track=out.get("track",{})
            title=track.get("title","Unknown"); artist=track.get("subtitle","Unknown")
            return f"🎵 {title} — {artist}"
        if not filename:
            # Record 5 seconds of system audio
            return "Pass an audio file: shazam song.mp3"
        return asyncio.run(_identify(filename))
    except ImportError: return "shazamio not installed. pip install shazamio"
    except Exception as e: return f"Shazam error: {e}"
