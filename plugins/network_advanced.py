# plugins/network_advanced.py — Advanced Network & Security Analysis

import os, re, socket, ssl, subprocess, threading, time, json
from datetime import datetime


# ══ SSL / TLS ═════════════════════════════════════════════════════════════════
def ssl_check(hostname, port=443):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(10)
            s.connect((hostname, int(port)))
            cert = s.getpeercert()
        subject   = dict(x[0] for x in cert.get("subject", []))
        issuer    = dict(x[0] for x in cert.get("issuer", []))
        not_after = cert.get("notAfter", "N/A")
        san       = [v for t,v in cert.get("subjectAltName",[]) if t=="DNS"]
        return (f"🔒 SSL Certificate: {hostname}\n"
                f"  CN      : {subject.get('commonName','N/A')}\n"
                f"  Issuer  : {issuer.get('organizationName','N/A')}\n"
                f"  Expires : {not_after}\n"
                f"  SANs    : {', '.join(san[:5])}")
    except ssl.SSLCertVerificationError as e: return f"❌ SSL Invalid: {e}"
    except Exception as e: return f"SSL check error: {e}"

def traceroute(host, max_hops=20):
    try:
        r = subprocess.run(["tracert","-h",str(max_hops),host],
                           capture_output=True, text=True, timeout=60)
        lines = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("Tracing")]
        return f"Traceroute to {host}:\n" + "\n".join(lines[:25])
    except Exception as e: return f"Traceroute error: {e}"

def subdomain_scan(domain, wordlist=None):
    """Fast subdomain enumeration using common names."""
    COMMON = ["www","mail","ftp","smtp","pop","imap","api","dev","staging",
              "admin","portal","vpn","remote","blog","shop","app","cdn","ns1","ns2"]
    found = []
    lock  = threading.Lock()
    def check(sub):
        full = f"{sub}.{domain}"
        try:
            socket.gethostbyname(full)
            with lock: found.append(full)
        except: pass
    threads = [threading.Thread(target=check, args=(s,)) for s in COMMON]
    for t in threads: t.start()
    for t in threads: t.join()
    found.sort()
    return (f"Subdomains of {domain} ({len(found)}):\n" +
            "\n".join(f"  ✅ {s}" for s in found)) if found else f"No common subdomains found for {domain}"

def mac_lookup(mac):
    """Look up vendor from MAC address OUI."""
    try:
        import requests
        oui = mac.replace(":","").replace("-","")[:6].upper()
        r   = requests.get(f"https://api.macvendors.com/{oui}", timeout=8)
        return f"MAC {mac} → Vendor: {r.text.strip()}" if r.ok else f"Unknown vendor for {oui}"
    except Exception as e: return f"MAC lookup error: {e}"

def network_interfaces():
    try:
        import psutil
        interfaces = psutil.net_if_addrs()
        lines = []
        for name, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    lines.append(f"  {name:<20} IPv4: {addr.address}  Mask: {addr.netmask}")
        return "Network Interfaces:\n" + "\n".join(lines) if lines else "No interfaces found."
    except ImportError: return "psutil not installed."

def open_connections():
    try:
        import psutil
        conns = psutil.net_connections(kind="inet")
        lines = []
        for c in conns[:20]:
            if c.status == "ESTABLISHED":
                laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
                raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
                pid   = c.pid or "-"
                lines.append(f"  {laddr:<25} → {raddr:<25}  PID:{pid}")
        return "Established connections:\n" + "\n".join(lines) if lines else "No active connections."
    except ImportError: return "psutil not installed."

def bandwidth_monitor(duration=5):
    try:
        import psutil
        t0 = psutil.net_io_counters()
        time.sleep(duration)
        t1 = psutil.net_io_counters()
        sent = (t1.bytes_sent - t0.bytes_sent) / duration / 1024
        recv = (t1.bytes_recv - t0.bytes_recv) / duration / 1024
        pkts_s = (t1.packets_sent - t0.packets_sent) / duration
        pkts_r = (t1.packets_recv - t0.packets_recv) / duration
        return (f"Bandwidth ({duration}s avg):\n"
                f"  ⬆️  Upload   : {sent:.1f} KB/s  ({pkts_s:.0f} pkts/s)\n"
                f"  ⬇️  Download : {recv:.1f} KB/s  ({pkts_r:.0f} pkts/s)")
    except ImportError: return "psutil not installed."

def firewall_status():
    try:
        r = subprocess.run("netsh advfirewall show allprofiles state",
                           capture_output=True, text=True, shell=True)
        return "Firewall Status:\n" + "\n".join(
            f"  {l.strip()}" for l in r.stdout.splitlines() if l.strip())
    except Exception as e: return f"Firewall error: {e}"

def shared_folders():
    try:
        r = subprocess.run("net share", capture_output=True, text=True, shell=True)
        return "Shared Folders:\n" + r.stdout.strip()
    except Exception as e: return f"Error: {e}"

def check_port_open(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=3):
            return f"✅ {host}:{port} is OPEN"
    except: return f"❌ {host}:{port} is CLOSED / FILTERED"

def dns_records(domain):
    """Get multiple DNS record types."""
    try:
        import subprocess
        results = []
        for rtype in ["A","MX","NS","TXT","CNAME"]:
            r = subprocess.run(f"nslookup -type={rtype} {domain}",
                               capture_output=True, text=True, shell=True, timeout=10)
            lines = [l.strip() for l in r.stdout.splitlines()
                     if l.strip() and not l.startswith("Server") and not l.startswith("Address")]
            if lines: results.append(f"  {rtype}: {' | '.join(lines[:2])}")
        return f"DNS Records for {domain}:\n" + "\n".join(results) if results else "No records found."
    except Exception as e: return f"DNS error: {e}"

def http_headers(url):
    try:
        import requests
        if not url.startswith("http"): url = "https://" + url
        r = requests.head(url, timeout=10, allow_redirects=True)
        headers = dict(r.headers)
        important = ["Server","Content-Type","X-Frame-Options","Content-Security-Policy",
                     "Strict-Transport-Security","X-XSS-Protection","X-Content-Type-Options"]
        lines = [f"  {k}: {headers.get(k,'—')}" for k in important]
        return f"HTTP Headers: {url}\n  Status: {r.status_code}\n" + "\n".join(lines)
    except Exception as e: return f"Headers error: {e}"

def find_my_public_ip():
    try:
        import requests
        ip = requests.get("https://api.ipify.org", timeout=8).text.strip()
        return f"Your public IP: {ip}"
    except Exception as e: return f"Error: {e}"

def reverse_dns(ip):
    try:
        host = socket.gethostbyaddr(ip)[0]
        return f"Reverse DNS: {ip} → {host}"
    except Exception as e: return f"Reverse DNS error: {e}"

def port_to_service(port):
    SERVICES = {
        20:"FTP Data",21:"FTP Control",22:"SSH",23:"Telnet",25:"SMTP",
        53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",
        445:"SMB",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",
        6379:"Redis",8080:"HTTP Alt",8443:"HTTPS Alt",27017:"MongoDB",
        1883:"MQTT",5000:"Flask/Dev",
    }
    return f"Port {port} → {SERVICES.get(int(port), 'Unknown service')}"

def vpn_check():
    """Heuristic VPN detection based on IP info."""
    try:
        import requests
        r = requests.get("https://ipapi.co/json/", timeout=10).json()
        org  = r.get("org","")
        host = r.get("hostname","")
        vpn_hints = any(k in (org+host).lower() for k in ["vpn","tunnel","proxy","hosting","datacenter"])
        return (f"VPN Status (heuristic):\n"
                f"  IP: {r.get('ip')}  Org: {org}\n"
                f"  {'⚠️ Possible VPN/proxy detected' if vpn_hints else '✅ Likely direct connection'}")
    except Exception as e: return f"VPN check error: {e}"
