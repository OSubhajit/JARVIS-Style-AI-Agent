# plugins/system_advanced.py — Deep OS: Registry, Drivers, Env Vars, Tasks, Fonts

import os, re, subprocess, platform, ctypes, sys
from datetime import datetime
from logger import log


def _run(cmd, shell=True, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=shell, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Error: {e}"


# ══ SYSTEM INFO ════════════════════════════════════════════════════════════════
def full_system_info():
    info = platform.uname()
    py   = sys.version.split()[0]
    try:
        import psutil
        mem  = psutil.virtual_memory()
        disk = psutil.disk_usage(".")
        cpu  = psutil.cpu_count()
        freq = psutil.cpu_freq()
        mem_str  = f"{mem.total/1e9:.1f} GB"
        disk_str = f"{disk.total/1e9:.1f} GB"
        cpu_str  = f"{cpu} cores @ {freq.current:.0f}MHz" if freq else f"{cpu} cores"
    except:
        mem_str = disk_str = cpu_str = "N/A"
    return (f"🖥️ Full System Info:\n"
            f"  OS       : {info.system} {info.release} ({info.machine})\n"
            f"  Hostname : {info.node}\n"
            f"  CPU      : {info.processor or cpu_str}\n"
            f"  RAM      : {mem_str}\n"
            f"  Disk     : {disk_str}\n"
            f"  Python   : {py}\n"
            f"  User     : {os.environ.get('USERNAME','N/A')}\n"
            f"  Drive    : {os.getcwd()}")

def os_version():
    return _run("ver") or platform.version()

def installed_updates():
    return _run("wmic qfe list brief /format:table")

def check_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return f"Running as {'Administrator ✅' if is_admin else 'Standard User ⚠️'}"
    except:
        return "Could not check admin status."

def system_locale():
    return _run("systeminfo | findstr /C:\"System Locale\" /C:\"Input Locale\" /C:\"Time Zone\"")

def bios_info():
    return _run("wmic bios get manufacturer,name,version,releasedate /format:list")


# ══ ENVIRONMENT VARIABLES ════════════════════════════════════════════════════
def list_env_vars(filter_str=""):
    env = os.environ
    if filter_str:
        items = [(k,v) for k,v in env.items() if filter_str.upper() in k.upper()]
    else:
        items = list(env.items())[:30]
    lines = [f"  {k:<30} = {v[:60]}" for k,v in sorted(items)]
    return f"Environment Variables ({len(items)}):\n" + "\n".join(lines)

def get_env_var(name):
    val = os.environ.get(name)
    return f"{name} = {val}" if val else f"'{name}' not found in environment."

def set_env_var_session(name, value):
    os.environ[name] = value
    return f"Session env var set: {name}={value}"

def get_path_entries():
    path = os.environ.get("PATH","")
    entries = [e.strip() for e in path.split(";") if e.strip()]
    exists  = [(e,"✅" if os.path.exists(e) else "❌") for e in entries]
    lines   = [f"  {s} {e}" for e,s in exists]
    return f"PATH entries ({len(entries)}):\n" + "\n".join(lines[:25])


# ══ SCHEDULED TASKS ════════════════════════════════════════════════════════════
def list_scheduled_tasks():
    return _run("schtasks /query /fo LIST /v | findstr /C:\"TaskName\" /C:\"Status\" /C:\"Next Run\"")

def create_scheduled_task(name, command, schedule="DAILY", time="09:00"):
    cmd = f'schtasks /create /tn "{name}" /tr "{command}" /sc {schedule} /st {time} /f'
    return _run(cmd)

def delete_scheduled_task(name):
    return _run(f'schtasks /delete /tn "{name}" /f')

def run_scheduled_task(name):
    return _run(f'schtasks /run /tn "{name}"')


# ══ DRIVERS ════════════════════════════════════════════════════════════════════
def list_drivers():
    return _run("driverquery /fo table | head -30")

def check_driver_issues():
    return _run('driverquery /si 2>&1 | findstr /i "not" | head -20')


# ══ DISK MANAGEMENT ════════════════════════════════════════════════════════════
def list_drives():
    return _run("wmic logicaldisk get caption,description,filesystem,freespace,size,volumename /format:list")

def check_disk_health():
    return _run("wmic diskdrive get status,model,size /format:list")

def disk_cleanup_analysis():
    try:
        import shutil, glob
        locations = {
            "Temp"    : os.environ.get("TEMP",""),
            "Recycle" : "C:\\$Recycle.Bin",
            "Prefetch": "C:\\Windows\\Prefetch",
        }
        lines = []
        total = 0
        for name, path in locations.items():
            if os.path.exists(path):
                size = sum(
                    os.path.getsize(os.path.join(dp,f))
                    for dp,_,fs in os.walk(path)
                    for f in fs
                    if os.path.exists(os.path.join(dp,f))
                )
                total += size
                lines.append(f"  {name:<15} {size/1024/1024:.1f} MB")
        return f"Disk Cleanup Analysis:\n" + "\n".join(lines) + f"\n  Total recoverable: {total/1024/1024:.1f} MB"
    except Exception as e:
        return f"Error: {e}"

def volume_shadow_copies():
    return _run("vssadmin list shadows /for=C: 2>&1 | head -20")


# ══ USER & ACCOUNT MANAGEMENT ════════════════════════════════════════════════
def list_users():
    return _run("net user")

def list_groups():
    return _run("net localgroup")

def current_user_info():
    return _run("whoami /all 2>&1 | head -20")

def logged_in_users():
    return _run("query user 2>&1")


# ══ FONTS ═════════════════════════════════════════════════════════════════════
def list_fonts():
    font_dir = "C:\\Windows\\Fonts"
    if not os.path.exists(font_dir):
        return "Fonts directory not found."
    fonts = [f for f in os.listdir(font_dir) if f.endswith((".ttf",".otf",".fon"))]
    return f"Installed fonts ({len(fonts)}):\n" + "\n".join(f"  {f}" for f in sorted(fonts)[:40])


# ══ CLIPBOARD (ADVANCED) ══════════════════════════════════════════════════════
def clipboard_to_file(filename="clipboard_dump.txt"):
    try:
        import pyperclip
        content = pyperclip.paste()
        with open(filename,"w",encoding="utf-8") as f: f.write(content)
        return f"Clipboard saved to: {filename} ({len(content)} chars)"
    except ImportError:
        return "pyperclip not installed."

def file_to_clipboard(filename):
    try:
        import pyperclip
        with open(filename,"r",encoding="utf-8") as f: content = f.read()
        pyperclip.copy(content)
        return f"File contents copied to clipboard: {filename}"
    except ImportError:
        return "pyperclip not installed."


# ══ POWER & PERFORMANCE ════════════════════════════════════════════════════════
def power_report():
    _run("powercfg /energy /output energy_report.html /duration 10")
    return "Power report generated: energy_report.html (takes ~60s). Check current dir."

def performance_baseline():
    try:
        import psutil, time
        cpu_samples = [psutil.cpu_percent(interval=0.5) for _ in range(6)]
        mem  = psutil.virtual_memory()
        disk = psutil.disk_io_counters()
        net  = psutil.net_io_counters()
        return (f"Performance Baseline:\n"
                f"  CPU avg : {sum(cpu_samples)/len(cpu_samples):.1f}%\n"
                f"  RAM used: {mem.percent:.1f}% ({mem.used/1e9:.1f} GB)\n"
                f"  Disk R/W: {disk.read_bytes/1e6:.1f}/{disk.write_bytes/1e6:.1f} MB total\n"
                f"  Net S/R : {net.bytes_sent/1e6:.1f}/{net.bytes_recv/1e6:.1f} MB total")
    except ImportError:
        return "psutil not installed."

def hibernate_enable():
    return _run("powercfg /hibernate on")

def hibernate_disable():
    return _run("powercfg /hibernate off")

def check_fast_boot():
    return _run("powercfg /query SCHEME_CURRENT SUB_SLEEP 9d7815a6-7ee4-497e-8888-515a05f02364")


# ══ NETWORK ADVANCED SYSTEM ═══════════════════════════════════════════════════
def reset_network_stack():
    cmds = ["netsh winsock reset","netsh int ip reset","ipconfig /flushdns","ipconfig /release","ipconfig /renew"]
    results = []
    for cmd in cmds[:2]:  # Only safe ones
        results.append(f"  {cmd}: {_run(cmd)[:50]}")
    return "Network stack reset (requires restart):\n" + "\n".join(results)

def wifi_available_networks():
    return _run("netsh wlan show networks mode=bssid")

def bluetooth_devices():
    return _run("pnputil /enum-devices /class Bluetooth")


# ══ WINDOWS FEATURES ══════════════════════════════════════════════════════════
def optional_features():
    return _run("dism /online /get-features /format:table 2>&1 | findstr \"Enabled\"| head -20")

def windows_activation_status():
    return _run("slmgr /xpr 2>&1")
