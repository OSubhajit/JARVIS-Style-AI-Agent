# plugins/mobile_remote.py — ADB, Telegram, Push Notifications

import os, subprocess, threading
from logger import log

# ══ ADB ═══════════════════════════════════════════════════════════════════════
def _adb(args):
    try:
        r=subprocess.run(["adb"]+args,capture_output=True,text=True,timeout=30)
        return r.stdout.strip() or r.stderr.strip()
    except FileNotFoundError: return "ADB not installed. Download Android Platform Tools."
    except Exception as e: return f"ADB error: {e}"

def adb_devices(): return _adb(["devices"])
def adb_screenshot(output="adb_screenshot.png"):
    _adb(["shell","screencap","-p","/sdcard/ss.png"])
    _adb(["pull","/sdcard/ss.png",output])
    return f"Phone screenshot saved: {output}"
def adb_install(apk): return _adb(["install",apk])
def adb_send_text(text): return _adb(["shell","input","text",text.replace(" ","%s")])
def adb_tap(x,y): return _adb(["shell","input","tap",str(x),str(y)])
def adb_swipe(x1,y1,x2,y2): return _adb(["shell","input","swipe",str(x1),str(y1),str(x2),str(y2)])
def adb_list_apps(): return _adb(["shell","pm","list","packages","-3"])
def adb_open_app(package): return _adb(["shell","monkey","-p",package,"-c","android.intent.category.LAUNCHER","1"])
def adb_battery(): return _adb(["shell","dumpsys","battery"])

# ══ TELEGRAM BOT ═════════════════════════════════════════════════════════════
_tg_bot=None

def start_telegram_bot(execute_fn=None):
    from config import TELEGRAM_ENABLED, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    if not TELEGRAM_ENABLED: return "Telegram disabled. Set TELEGRAM_ENABLED=True and TELEGRAM_TOKEN in config.py"
    try:
        from telegram import Update
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

        async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            chat_id=str(update.effective_chat.id)
            if TELEGRAM_CHAT_ID and chat_id!=TELEGRAM_CHAT_ID:
                await update.message.reply_text("Unauthorized.")
                return
            text=update.message.text
            log.info(f"Telegram: {text}")
            if execute_fn:
                from interpreter import parse_intent
                intent=parse_intent(text)
                result=execute_fn(intent.get("action","unknown"),intent.get("params",{}))
                await update.message.reply_text(result or "Done.")
            else:
                await update.message.reply_text(f"Echo: {text}")

        app=ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        def _run(): app.run_polling()
        threading.Thread(target=_run,daemon=True).start()
        return "📱 Telegram bot started. Send messages to control JARVIS remotely."
    except ImportError: return "python-telegram-bot not installed. pip install python-telegram-bot"
    except Exception as e: return f"Telegram error: {e}"

def telegram_send(message, chat_id=None):
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    if not TELEGRAM_TOKEN: return "Telegram not configured."
    try:
        import requests
        target=chat_id or TELEGRAM_CHAT_ID
        r=requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id":target,"text":message})
        return f"Telegram sent ✅" if r.ok else f"Telegram error: {r.text}"
    except Exception as e: return f"Telegram send error: {e}"

# ══ PUSH NOTIFICATIONS (ntfy.sh) ═════════════════════════════════════════════
def send_push_notification(title, body="", priority="default", tags=""):
    from config import NTFY_ENABLED, NTFY_TOPIC
    if not NTFY_ENABLED: return "ntfy disabled. Set NTFY_ENABLED=True in config.py. Free at ntfy.sh"
    try:
        import requests
        headers={"Title":title,"Priority":priority}
        if tags: headers["Tags"]=tags
        r=requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",data=body.encode(),headers=headers,timeout=10)
        return f"Push notification sent: {title}" if r.ok else f"ntfy error: {r.text}"
    except Exception as e: return f"Push error: {e}"

# ══ SMART HOME ════════════════════════════════════════════════════════════════
def mqtt_publish(topic, message, broker=None):
    from config import MQTT_BROKER, MQTT_PORT
    try:
        import paho.mqtt.client as mqtt
        c=mqtt.Client(); c.connect(broker or MQTT_BROKER, MQTT_PORT, 10)
        c.publish(topic,message); c.disconnect()
        return f"MQTT: {topic} = {message}"
    except ImportError: return "paho-mqtt not installed. pip install paho-mqtt"
    except Exception as e: return f"MQTT error: {e}"

def mqtt_subscribe(topic, duration=10, broker=None):
    from config import MQTT_BROKER, MQTT_PORT
    try:
        import paho.mqtt.client as mqtt
        messages=[]; done=threading.Event()
        def on_msg(client,userdata,msg):
            messages.append(f"  {msg.topic}: {msg.payload.decode()}")
            if len(messages)>=10: done.set()
        c=mqtt.Client()
        c.on_message=on_msg
        c.connect(broker or MQTT_BROKER, MQTT_PORT, 10)
        c.subscribe(topic); c.loop_start()
        done.wait(timeout=duration); c.loop_stop(); c.disconnect()
        return f"MQTT messages on '{topic}':\n"+"\n".join(messages) if messages else f"No messages on '{topic}' in {duration}s"
    except ImportError: return "paho-mqtt not installed."
    except Exception as e: return f"MQTT error: {e}"

def ha_toggle(entity_id):
    from config import HA_URL, HA_TOKEN
    if not HA_TOKEN: return "Home Assistant not configured. Set HA_URL and HA_TOKEN in config.py"
    try:
        import requests
        r=requests.post(f"{HA_URL}/api/services/homeassistant/toggle",
            headers={"Authorization":f"Bearer {HA_TOKEN}","Content-Type":"application/json"},
            json={"entity_id":entity_id},timeout=10)
        return f"HA toggled: {entity_id}" if r.ok else f"HA error: {r.text}"
    except Exception as e: return f"HA error: {e}"

def ha_state(entity_id):
    from config import HA_URL, HA_TOKEN
    if not HA_TOKEN: return "Home Assistant not configured."
    try:
        import requests
        r=requests.get(f"{HA_URL}/api/states/{entity_id}",
            headers={"Authorization":f"Bearer {HA_TOKEN}"},timeout=10).json()
        return f"{entity_id}: {r.get('state','unknown')} ({r.get('last_changed','')})"
    except Exception as e: return f"HA error: {e}"
