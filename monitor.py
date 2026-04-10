# monitor.py — System Monitor + Rules Engine + Global Hotkeys
import threading, time
from config import CPU_ALERT, RAM_ALERT, DISK_ALERT, TEMP_ALERT, MON_INTERVAL, HOTKEYS
from logger import log

_running=False

def _loop(speak_fn=None, execute_fn=None):
    try: import psutil
    except ImportError: log.warning("psutil not installed."); return
    from plugins.automation import evaluate_rules
    while _running:
        try:
            cpu=psutil.cpu_percent(interval=2); ram=psutil.virtual_memory().percent
            disk=psutil.disk_usage(".").percent
            # Check CPU / RAM / Disk thresholds
            for val,thresh,label in [(cpu,CPU_ALERT,"CPU"),(ram,RAM_ALERT,"RAM"),(disk,DISK_ALERT,"Disk")]:
                if val>thresh:
                    msg=f"⚠️ {label} at {val:.0f}%"
                    log.warning(msg); print(f"\n\033[93m[JARVIS] {msg}\033[0m")
                    if speak_fn: speak_fn(msg)
            # Check temperature (psutil.sensors_temperatures — Linux/Mac; skipped on Windows)
            try:
                temps=psutil.sensors_temperatures()
                if temps:
                    for name,entries in temps.items():
                        for entry in entries:
                            if entry.current and entry.current>TEMP_ALERT:
                                msg=f"⚠️ Temp ({name}) at {entry.current:.0f}°C"
                                log.warning(msg); print(f"\n\033[93m[JARVIS] {msg}\033[0m")
                                if speak_fn: speak_fn(msg)
            except (AttributeError, Exception):
                pass  # sensors_temperatures not available on Windows — safe to skip
            # Run rules engine
            if execute_fn: evaluate_rules(execute_fn)
        except Exception as e: log.debug(f"Monitor: {e}")
        time.sleep(MON_INTERVAL)

def start_monitor(speak_fn=None, execute_fn=None):
    global _running; _running=True
    threading.Thread(target=_loop,args=(speak_fn,execute_fn),daemon=True).start()
    log.info("Monitor started.")

def stop_monitor():
    global _running; _running=False

def start_hotkeys(action_cb):
    try:
        import keyboard
        for hotkey,action in HOTKEYS.items():
            keyboard.add_hotkey(hotkey, lambda a=action: action_cb(a))
        threading.Thread(target=keyboard.wait,daemon=True).start()
        log.info(f"Hotkeys: {list(HOTKEYS.keys())}")
    except ImportError: log.warning("keyboard not installed. pip install keyboard")
    except Exception as e: log.warning(f"Hotkeys: {e}")
