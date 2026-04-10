# plugins/system_tools.py — System, Network, GPU, Services, Registry, Git, Windows

import os, re, subprocess, socket, threading, hashlib, time
from datetime import datetime
from logger import log

def _ps():
    try: import psutil; return psutil
    except: return None

# ══ SYSTEM STATS ══════════════════════════════════════════════════════════════
def get_cpu():
    ps=_ps()
    if not ps: return "psutil not installed"
    freq=ps.cpu_freq()
    return f"{ps.cpu_percent(interval=1):.1f}%  |  {ps.cpu_count(logical=False)}C/{ps.cpu_count()}T  |  {freq.current:.0f}MHz" if freq else f"{ps.cpu_percent(interval=1):.1f}%"

def get_ram():
    ps=_ps()
    if not ps: return "psutil not installed"
    m=ps.virtual_memory(); swap=ps.swap_memory()
    return f"{m.percent:.1f}%  |  {m.used/1e9:.1f}/{m.total/1e9:.1f}GB  |  Swap:{swap.used/1e9:.1f}GB"

def get_disk(path="."):
    ps=_ps()
    if not ps: return "psutil not installed"
    try: d=ps.disk_usage(path); return f"{d.percent:.1f}%  |  {d.used/1e9:.1f}/{d.total/1e9:.1f}GB  |  Free:{d.free/1e9:.1f}GB"
    except: return "Disk info unavailable"

def get_battery():
    ps=_ps()
    if not ps: return "psutil not installed"
    b=ps.sensors_battery()
    if not b: return "No battery (desktop)"
    h,m=divmod(b.secsleft//60,60) if b.secsleft>0 else (0,0)
    return f"{b.percent:.0f}%  {'⚡Charging' if b.power_plugged else '🔋Discharging'}  |  ~{h}h{m}m"

def get_gpu():
    try:
        import GPUtil
        gpus=GPUtil.getGPUs()
        if not gpus: return "No GPU detected"
        g=gpus[0]
        return f"{g.name}  |  Load:{g.load*100:.0f}%  |  Mem:{g.memoryUsed:.0f}/{g.memoryTotal:.0f}MB  |  Temp:{g.temperature}°C"
    except ImportError: return "GPUtil not installed. Run: pip install gputil"
    except Exception as e: return f"GPU error: {e}"

def get_temp():
    try:
        import psutil
        temps=psutil.sensors_temperatures()
        if not temps: return "Temperature sensors not available on Windows (use HWMonitor)"
        lines=[]
        for name,entries in list(temps.items())[:3]:
            for e in entries[:2]: lines.append(f"  {name}/{e.label or 'core'}: {e.current:.0f}°C")
        return "Temperatures:\n"+"\n".join(lines)
    except Exception as e: return f"Temp error: {e}"

def system_report():
    ps=_ps()
    boot=datetime.fromtimestamp(ps.boot_time()).strftime("%Y-%m-%d %H:%M") if ps else "N/A"
    return (
        "╔═══════════════════ SYSTEM REPORT ═══════════════════╗\n"
        f"  🖥️  CPU     : {get_cpu()}\n  💾  RAM     : {get_ram()}\n"
        f"  💿  DISK    : {get_disk()}\n  🔋  BATTERY : {get_battery()}\n"
        f"  🎮  GPU     : {get_gpu()}\n  🌡️  TEMP    : {get_temp()}\n"
        f"  🕐  Uptime  : since {boot}\n  📅  Now     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "╚═════════════════════════════════════════════════════╝"
    )

def flush_memory():
    try: os.system("PowerShell -Command \"[System.GC]::Collect()\""); return "RAM standby memory flushed."
    except Exception as e: return f"Error: {e}"

def boot_analyzer():
    try:
        r=subprocess.run(["powercfg","/systempowerreport"],capture_output=True,text=True)
        r2=subprocess.run("wevtutil qe System /c:5 /rd:true /f:text /q:\"*[System[EventID=6013]]\"",
            capture_output=True,text=True,shell=True)
        uptime=re.findall(r"(\d+) second",r2.stdout)
        hours=int(uptime[0])//3600 if uptime else 0
        return f"System uptime: ~{hours} hours\nBoot report saved to system. Use Event Viewer for full boot analysis."
    except Exception as e: return f"Boot analyzer error: {e}"

# ══ PROCESSES ═════════════════════════════════════════════════════════════════
def list_processes():
    ps=_ps()
    if not ps: return "psutil not installed"
    procs=sorted([p.info for p in ps.process_iter(["pid","name","cpu_percent","memory_percent","status"])
                  if p.info.get("name")],key=lambda x:x.get("cpu_percent",0),reverse=True)
    lines=[f"{'PID':>7}  {'Name':<35}  {'CPU%':>5}  {'RAM%':>5}"]
    lines.append("-"*60)
    for p in procs[:20]:
        lines.append(f"{p['pid']:>7}  {p['name']:<35}  {p.get('cpu_percent',0):>5.1f}  {p.get('memory_percent',0):>5.1f}")
    return "\n".join(lines)

def kill_process(name):
    ps=_ps()
    if not ps: return "psutil not installed"
    killed=0
    for p in ps.process_iter(["name"]):
        try:
            if name.lower() in p.info["name"].lower(): p.kill(); killed+=1
        except: pass
    return f"Killed {killed} process(es) matching '{name}'"

# ══ SERVICES ══════════════════════════════════════════════════════════════════
def list_services():
    try:
        r=subprocess.run("sc query type= all state= all",capture_output=True,text=True,shell=True)
        services=re.findall(r"SERVICE_NAME: (.+)\n.+\n.+STATE.+: \d+\s+(\w+)",r.stdout)
        running=[f"  ✅ {n}" for n,s in services if "RUNNING" in s][:15]
        stopped=[f"  ⏹️ {n}" for n,s in services if "STOPPED" in s][:10]
        return f"Running ({len(running)}):\n"+"\n".join(running)+f"\n\nStopped (sample):\n"+"\n".join(stopped)
    except Exception as e: return f"Service error: {e}"

def start_service(name):
    try: subprocess.run(f"sc start {name}",shell=True,capture_output=True); return f"Service started: {name}"
    except Exception as e: return f"Error: {e}"

def stop_service(name):
    try: subprocess.run(f"sc stop {name}",shell=True,capture_output=True); return f"Service stopped: {name}"
    except Exception as e: return f"Error: {e}"

# ══ POWER ═════════════════════════════════════════════════════════════════════
def power_plan(plan="balanced"):
    plans={"balanced":"381b4222-f694-41f0-9685-ff5bb260df2e",
            "performance":"8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "saver":"a1841308-3541-4fab-bc81-f71556f20b4a"}
    guid=plans.get(plan.lower())
    if not guid: return f"Unknown plan. Use: balanced/performance/saver"
    os.system(f"powercfg /setactive {guid}")
    return f"Power plan set to: {plan}"

# ══ NETWORK ═══════════════════════════════════════════════════════════════════
def show_ip():
    try:
        r=subprocess.run("ipconfig",capture_output=True,text=True,timeout=5)
        lines=[l for l in r.stdout.splitlines() if any(k in l for k in ["IPv4","IPv6","Gateway","Adapter","Wi-Fi","Ethernet"])]
        return "\n".join(lines)
    except Exception as e: return f"IP error: {e}"

def show_wifi():
    try:
        r=subprocess.run("netsh wlan show interfaces",capture_output=True,text=True,timeout=5)
        return r.stdout.strip() or "No WiFi interface."
    except Exception as e: return f"WiFi error: {e}"

def ping_host(host="google.com"):
    try:
        r=subprocess.run(["ping","-n","4",host],capture_output=True,text=True,timeout=15)
        lines=[l for l in r.stdout.splitlines() if any(k in l for k in ["Reply","Request","Average","Packets","time="])]
        return "\n".join(lines) if lines else r.stdout.strip()
    except Exception as e: return f"Ping error: {e}"

def scan_ports(host="localhost",port_range="1-1024"):
    try:
        s,e=map(int,port_range.split("-")); open_p=[]; lock=threading.Lock()
        def chk(p):
            with socket.socket() as sock:
                sock.settimeout(0.3)
                if sock.connect_ex((host,p))==0:
                    with lock: open_p.append(p)
        threads=[threading.Thread(target=chk,args=(p,)) for p in range(s,min(e+1,s+500))]
        for t in threads: t.start()
        for t in threads: t.join()
        open_p.sort()
        return f"Open ports on {host}: {', '.join(map(str,open_p))}" if open_p else f"No open ports on {host} ({port_range})"
    except Exception as e: return f"Scan error: {e}"

def arp_scan():
    try:
        r=subprocess.run("arp -a",capture_output=True,text=True,shell=True)
        lines=[l.strip() for l in r.stdout.splitlines() if re.match(r"\s+\d{1,3}\.",l)]
        return "Devices on network:\n"+"\n".join(lines[:30]) if lines else "No ARP entries found."
    except Exception as e: return f"ARP error: {e}"

def network_speed():
    ps=_ps()
    if not ps: return "psutil not installed"
    n1=ps.net_io_counters(); time.sleep(1); n2=ps.net_io_counters()
    sent=(n2.bytes_sent-n1.bytes_sent)/1024
    recv=(n2.bytes_recv-n1.bytes_recv)/1024
    return f"Network Speed (1s sample):\n  ⬆️  Sent: {sent:.1f} KB/s\n  ⬇️  Recv: {recv:.1f} KB/s"

# ══ STARTUP ═══════════════════════════════════════════════════════════════════
def get_startup_apps():
    try:
        import winreg
        key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run")
        apps=[]; i=0
        while True:
            try: n,v,_=winreg.EnumValue(key,i); apps.append(f"  • {n}: {v}"); i+=1
            except OSError: break
        return "Startup apps:\n"+"\n".join(apps) if apps else "No startup apps."
    except Exception as e: return f"Startup error: {e}"

def add_to_startup(name,path):
    try:
        import winreg
        key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key,name,0,winreg.REG_SZ,path)
        return f"Added '{name}' to startup."
    except Exception as e: return f"Error: {e}"

def remove_from_startup(name):
    try:
        import winreg
        key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key,name); return f"Removed '{name}' from startup."
    except Exception as e: return f"Error: {e}"

def clear_temp():
    import glob,shutil
    temp=os.environ.get("TEMP","C:/Windows/Temp"); count=0
    for f in glob.glob(os.path.join(temp,"*")):
        try:
            if os.path.isfile(f): os.remove(f)
            elif os.path.isdir(f): shutil.rmtree(f)
            count+=1
        except: pass
    return f"Cleared {count} items from {temp}"

def empty_recycle_bin():
    os.system("PowerShell.exe -NoProfile -Command Clear-RecycleBin -Force")
    return "Recycle bin emptied."

# ══ WINDOW MANAGEMENT ════════════════════════════════════════════════════════
def list_windows():
    try:
        import pygetwindow as gw
        return "Open windows:\n"+"\n".join(f"  • {w}" for w in gw.getAllTitles() if w.strip())
    except ImportError: return "pygetwindow not installed. Run: pip install pygetwindow"

def _win(title):
    import pygetwindow as gw; w=gw.getWindowsWithTitle(title); return w[0] if w else None

def focus_window(title):
    try: w=_win(title); return (w.activate(), f"Focused: {title}")[1] if w else f"Not found: {title}"
    except Exception as e: return f"Error: {e}"
def minimize_window(title):
    try: w=_win(title); return (w.minimize(), f"Minimized: {title}")[1] if w else f"Not found: {title}"
    except Exception as e: return f"Error: {e}"
def maximize_window(title):
    try: w=_win(title); return (w.maximize(), f"Maximized: {title}")[1] if w else f"Not found: {title}"
    except Exception as e: return f"Error: {e}"
def close_window(title):
    try: w=_win(title); return (w.close(), f"Closed: {title}")[1] if w else f"Not found: {title}"
    except Exception as e: return f"Error: {e}"

# ══ GIT ══════════════════════════════════════════════════════════════════════
def _git(args,path="."):
    try:
        r=subprocess.run(["git"]+args,capture_output=True,text=True,cwd=path,timeout=30)
        return r.stdout.strip() or r.stderr.strip() or "Done."
    except FileNotFoundError: return "Git not installed."
    except Exception as e: return f"Git error: {e}"

def git_status(p="."): return _git(["status","--short","--branch"],p)
def git_pull(p="."):   return _git(["pull"],p)
def git_push(p="."):   return _git(["push"],p)
def git_log(p="."):    return _git(["log","--oneline","-15"],p)
def git_diff(p="."):   return _git(["diff","--stat"],p)
def git_commit(msg,p="."): return _git(["commit","-am",msg],p)

# ══ SECURITY ══════════════════════════════════════════════════════════════════
def file_integrity_check(filepath):
    from database import integrity_add, integrity_all
    if filepath=="check":
        changed=[]; db={r["filepath"]:r["hash"] for r in integrity_all()}
        for fp,expected in db.items():
            if os.path.exists(fp):
                current=_md5(fp)
                if current!=expected: changed.append(f"  ⚠️ CHANGED: {fp}")
            else: changed.append(f"  ❌ MISSING: {fp}")
        return ("Integrity check passed ✅" if not changed else "⚠️ CHANGES DETECTED:\n"+"\n".join(changed))
    if os.path.exists(filepath):
        h=_md5(filepath); integrity_add(filepath,h)
        return f"Baseline recorded for: {filepath}\n  MD5: {h}"
    return f"File not found: {filepath}"

def _md5(f):
    h=hashlib.md5()
    with open(f,"rb") as fp:
        for chunk in iter(lambda:fp.read(8192),b""): h.update(chunk)
    return h.hexdigest()

def shred_file(filepath,passes=3):
    try:
        size=os.path.getsize(filepath)
        with open(filepath,"rb+") as f:
            for _ in range(passes):
                f.seek(0); f.write(os.urandom(size))
        os.remove(filepath)
        return f"Securely shredded: {filepath} ({passes} passes)"
    except Exception as e: return f"Shred error: {e}"

def check_password_strength(password):
    score=0; tips=[]
    if len(password)>=8: score+=1
    else: tips.append("Use at least 8 characters")
    if len(password)>=16: score+=1
    if re.search(r"[A-Z]",password): score+=1
    else: tips.append("Add uppercase letters")
    if re.search(r"[a-z]",password): score+=1
    if re.search(r"\d",password): score+=1
    else: tips.append("Add numbers")
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]",password): score+=1
    else: tips.append("Add symbols")
    strength=["Very Weak","Weak","Fair","Good","Strong","Very Strong"][min(score,5)]
    result=f"Password strength: {strength} ({score}/6)"
    if tips: result+="\nTips: "+", ".join(tips)
    return result
