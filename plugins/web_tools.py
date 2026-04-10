# plugins/web_tools.py — Web Intelligence: Weather,Wiki,News,Crypto,Stocks,Translate,Scraper,Download,Speed

import os, re, json, time, socket, threading, xml.etree.ElementTree as ET
from config import DEFAULT_CITY, NEWS_SOURCES, DOWNLOAD_DIR

def _req():
    import requests
    return requests

def get_weather(city=DEFAULT_CITY):
    try: return _req().get(f"https://wttr.in/{city.replace(' ','+')}?format=4",timeout=10).text.strip()
    except Exception as e: return f"Weather error: {e}"

def search_wikipedia(query):
    try:
        r=_req().get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ','_')}",
            timeout=10,headers={"User-Agent":"JARVIS/4.0"}).json()
        extract=r.get("extract","No article found.")
        return extract[:800]+("..." if len(extract)>800 else "")
    except Exception as e: return f"Wikipedia error: {e}"

def get_news(limit=6):
    for url in NEWS_SOURCES:
        try:
            r=_req().get(url,timeout=8); root=ET.fromstring(r.content)
            items=[i.findtext("title","").strip() for i in root.findall(".//item")[:limit] if i.findtext("title")]
            if items: return "\n".join(f"• {t}" for t in items)
        except: continue
    return "Could not fetch news."

def get_crypto_price(symbol="BTC"):
    COINS={"BTC":"bitcoin","ETH":"ethereum","BNB":"binancecoin","SOL":"solana",
           "XRP":"ripple","ADA":"cardano","DOGE":"dogecoin","MATIC":"matic-network"}
    try:
        cid=COINS.get(symbol.upper(),symbol.lower())
        r=_req().get(f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd,inr",timeout=10).json()
        coin=list(r.values())[0] if r else {}
        return f"{symbol}: ${coin.get('usd','N/A')} USD  |  ₹{coin.get('inr','N/A')} INR" if coin else f"Not found: {symbol}"
    except Exception as e: return f"Crypto error: {e}"

def get_stock_price(symbol="AAPL"):
    try:
        r=_req().get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d",
            headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
        m=r["chart"]["result"][0]["meta"]
        p=m.get("regularMarketPrice",0); ch=m.get("regularMarketChangePercent",0)
        return f"{symbol}: ${p:.2f}  {'📈' if ch>=0 else '📉'} {ch:+.2f}%"
    except Exception as e: return f"Stock error: {e}"

def translate_text(text, target="hi"):
    try:
        r=_req().get("https://api.mymemory.translated.net/get",
            params={"q":text,"langpair":f"en|{target}"},timeout=10).json()
        return r["responseData"]["translatedText"]
    except Exception as e: return f"Translation error: {e}"

def check_website(url):
    try:
        if not url.startswith("http"): url="https://"+url
        start=time.time(); r=_req().get(url,timeout=10)
        elapsed=time.time()-start
        return f"{url}\n  Status: {r.status_code}  |  Response: {elapsed:.2f}s  |  {'✅ Online' if r.status_code<400 else '⚠️ Issue'}"
    except Exception as e: return f"{url} — ❌ Offline ({e})"

def download_file(url, dest=None):
    try:
        import requests
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        fname=dest or os.path.join(DOWNLOAD_DIR, url.split("/")[-1].split("?")[0] or "download")
        r=requests.get(url, stream=True, timeout=30)
        total=int(r.headers.get("content-length",0)); downloaded=0
        with open(fname,"wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk); downloaded+=len(chunk)
        return f"Downloaded: {fname} ({downloaded/1024:.1f} KB)"
    except Exception as e: return f"Download error: {e}"

def download_youtube(url, audio_only=False):
    try:
        import yt_dlp
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        opts={"outtmpl":f"{DOWNLOAD_DIR}/%(title)s.%(ext)s","quiet":True}
        if audio_only: opts.update({"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3"}]})
        with yt_dlp.YoutubeDL(opts) as ydl: info=ydl.extract_info(url,download=True)
        return f"Downloaded: {info.get('title','video')}"
    except ImportError: return "yt-dlp not installed. Run: pip install yt-dlp"
    except Exception as e: return f"YT-DLP error: {e}"

def speed_test():
    try:
        import speedtest
        st=speedtest.Speedtest(); st.get_best_server()
        dl=st.download()/1e6; ul=st.upload()/1e6
        ping=st.results.ping
        return f"Internet Speed:\n  ⬇️  Download : {dl:.1f} Mbps\n  ⬆️  Upload   : {ul:.1f} Mbps\n  🏓 Ping     : {ping:.0f} ms"
    except ImportError: return "speedtest-cli not installed. Run: pip install speedtest-cli"
    except Exception as e: return f"Speed test error: {e}"

def ip_geolocation(ip=""):
    try:
        url=f"https://ipapi.co/{ip}/json/" if ip else "https://ipapi.co/json/"
        r=_req().get(url,timeout=10).json()
        return (f"IP: {r.get('ip')}\n  City: {r.get('city')}, {r.get('region')}, {r.get('country_name')}\n"
                f"  ISP: {r.get('org')}\n  Timezone: {r.get('timezone')}")
    except Exception as e: return f"Geolocation error: {e}"

def dns_lookup(domain):
    try:
        import socket
        ip=socket.gethostbyname(domain)
        return f"{domain} → {ip}"
    except Exception as e: return f"DNS error: {e}"

def whois_lookup(domain):
    try:
        import whois
        w=whois.whois(domain)
        return (f"Domain: {w.domain_name}\n  Registrar: {w.registrar}\n"
                f"  Created: {w.creation_date}\n  Expires: {w.expiration_date}")
    except ImportError: return "python-whois not installed. Run: pip install python-whois"
    except Exception as e: return f"WHOIS error: {e}"

def check_breach(email):
    try:
        r=_req().get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={"User-Agent":"JARVIS","hibp-api-key":"free"},timeout=10)
        if r.status_code==200:
            breaches=r.json(); names=[b["Name"] for b in breaches[:5]]
            return f"⚠️ {email} found in {len(breaches)} breach(es):\n" + "\n".join(f"  • {n}" for n in names)
        elif r.status_code==404: return f"✅ {email} not found in any known breaches."
        return f"Could not check (status {r.status_code}). HIBP requires a paid API key for full access."
    except Exception as e: return f"Breach check error: {e}"

def get_wifi_passwords():
    try:
        import subprocess
        profiles=subprocess.run("netsh wlan show profiles",capture_output=True,text=True).stdout
        names=re.findall(r"All User Profile\s+:\s+(.+)",profiles)
        results=[]
        for name in names:
            detail=subprocess.run(f'netsh wlan show profile name="{name.strip()}" key=clear',capture_output=True,text=True).stdout
            pwd=re.search(r"Key Content\s+:\s+(.+)",detail)
            results.append(f"  📶 {name.strip()}: {pwd.group(1).strip() if pwd else '(hidden/no password)'}")
        return "Saved WiFi Passwords:\n"+"\n".join(results) if results else "No saved WiFi profiles found."
    except Exception as e: return f"WiFi password error: {e}"

def scrape_url(url, selector=""):
    try:
        from bs4 import BeautifulSoup
        r=_req().get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=15)
        soup=BeautifulSoup(r.text,"html.parser")
        if selector:
            items=soup.select(selector)
            return "\n".join(i.get_text(strip=True) for i in items[:20])
        text=soup.get_text(separator="\n",strip=True)
        lines=[l for l in text.splitlines() if len(l)>20]
        return "\n".join(lines[:30])
    except ImportError: return "beautifulsoup4 not installed. Run: pip install beautifulsoup4"
    except Exception as e: return f"Scrape error: {e}"
