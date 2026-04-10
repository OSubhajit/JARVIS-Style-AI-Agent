# plugins/creative_tools.py — Creative Tools, Generators & Fun Utilities

import os, random, string, math, time, re


# ══ ASCII ART ═════════════════════════════════════════════════════════════════
def ascii_banner(text, style="block"):
    """Generate ASCII art banner from text."""
    try:
        import pyfiglet
        fonts = {"block":"block","slant":"slant","3d":"3-d","doom":"doom","big":"big","digital":"digital"}
        font  = fonts.get(style.lower(), "block")
        return pyfiglet.figlet_format(text, font=font)
    except ImportError:
        # Fallback: simple box banner
        border = "═" * (len(text) + 4)
        return f"╔{border}╗\n║  {text}  ║\n╚{border}╝"

def ascii_art_from_image(filename):
    """Convert image to ASCII art."""
    try:
        from PIL import Image
        img    = Image.open(filename).convert("L")
        w, h   = img.size
        new_w  = 80
        new_h  = int(h * new_w / w * 0.45)
        img    = img.resize((new_w, new_h))
        chars  = " .:-=+*#%@"
        result = ""
        for y in range(new_h):
            for x in range(new_w):
                pixel = img.getpixel((x, y))
                result += chars[int(pixel / 255 * (len(chars)-1))]
            result += "\n"
        return result
    except ImportError: return "Pillow not installed. pip install Pillow"
    except Exception as e: return f"ASCII art error: {e}"

def draw_box(text, style="single"):
    """Draw a decorative box around text."""
    STYLES = {
        "single":  ("┌","─","┐","│","└","┘"),
        "double":  ("╔","═","╗","║","╚","╝"),
        "rounded": ("╭","─","╮","│","╰","╯"),
        "thick":   ("┏","━","┓","┃","┗","┛"),
    }
    tl,h,tr,v,bl,br = STYLES.get(style,"single") if style in STYLES else STYLES["single"]
    lines  = text.splitlines()
    width  = max(len(l) for l in lines) + 4
    result = [f"{tl}{h*(width-2)}{tr}"]
    for line in lines:
        result.append(f"{v}  {line:<{width-4}}  {v}")
    result.append(f"{bl}{h*(width-2)}{br}")
    return "\n".join(result)

def progress_bar(value, total, label="Progress", width=40):
    pct  = min(value/max(total,1)*100, 100)
    done = int(pct/100*width)
    bar  = "█"*done + "░"*(width-done)
    return f"{label}: [{bar}] {value}/{total} ({pct:.1f}%)"

# ══ GENERATORS ════════════════════════════════════════════════════════════════
def random_color_palette(count=5):
    colors = []
    for _ in range(int(count)):
        r,g,b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        colors.append(f"  #{r:02X}{g:02X}{b:02X}  RGB({r:3},{g:3},{b:3})")
    return f"🎨 Random Palette ({count} colors):\n" + "\n".join(colors)

def generate_username(style="tech"):
    TECH_ADJ  = ["Cyber","Neural","Quantum","Binary","Digital","Pixel","Vector","Crypto"]
    TECH_NOUN = ["Ghost","Phantom","Ninja","Hawk","Wolf","Dragon","Eagle","Storm"]
    NORMAL_ADJ= ["Cool","Dark","Swift","Sharp","Bold","Neon","Ultra","Hyper"]
    NORMAL_NOUN=["Coder","Hacker","Builder","Dev","Maker","Wizard","Master","Pro"]
    adj  = random.choice(TECH_ADJ  if style=="tech" else NORMAL_ADJ)
    noun = random.choice(TECH_NOUN if style=="tech" else NORMAL_NOUN)
    num  = random.randint(0,99)
    return f"Username: {adj}{noun}{num}"

def generate_api_key(length=32):
    chars = string.ascii_letters + string.digits
    key   = "".join(random.SystemRandom().choice(chars) for _ in range(int(length)))
    return f"🔑 API Key: {key}"

def generate_uuid():
    import uuid
    return f"UUID: {uuid.uuid4()}"

def story_generator(genre="sci-fi", words=100):
    from plugins.advanced_ai import _ai
    SETTINGS = {"sci-fi":"a distant planet in 2150", "fantasy":"a mystical forest kingdom",
                "thriller":"a dark city at midnight", "romance":"a coastal town at sunset"}
    setting = SETTINGS.get(genre.lower(), "an unknown world")
    prompt  = f"""Write a {words}-word micro {genre} story set in {setting}.
Make it engaging with a twist ending."""
    return _ai(prompt)

def meme_text(top, bottom):
    """Format meme-style text."""
    border = "═" * max(len(top), len(bottom), 30)
    return f"┌{border}┐\n  {top.upper().center(len(border))}\n\n  {bottom.upper().center(len(border))}\n└{border}┘"

def rhyme_words(word):
    """Simple rhyme finder using ending pattern."""
    from plugins.advanced_ai import _ai
    return _ai(f"List 10 words that rhyme with '{word}'. Return only the words, one per line.")

def haiku_generator(topic):
    from plugins.advanced_ai import _ai
    return _ai(f"Write a haiku (5-7-5 syllables) about: {topic}")

def acronym_generator(word):
    from plugins.advanced_ai import _ai
    return _ai(f"Create a creative acronym where each letter of '{word.upper()}' stands for something. Make it meaningful.")

# ══ MATH & SCIENCE ════════════════════════════════════════════════════════════
def number_facts(n):
    from plugins.advanced_ai import _ai
    return _ai(f"Tell me 3 interesting mathematical or historical facts about the number {n}.")

def prime_check(n):
    n = int(n)
    if n < 2: return f"{n} is NOT prime."
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return f"{n} is NOT prime (divisible by {i})."
    return f"{n} IS prime ✅"

def fibonacci(n):
    seq = [0,1]
    for _ in range(int(n)-2): seq.append(seq[-1]+seq[-2])
    return f"Fibonacci({n}): {', '.join(map(str,seq[:int(n)]))}"

def factorize(n):
    n   = int(n)
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0: factors.append(d); n //= d
        d += 1
    if n > 1: factors.append(n)
    return f"Prime factors of {int(n) if not factors else int(d)}: {factors}" if factors else f"{n} is prime"

def base_convert(number, from_base=10, to_base=2):
    try:
        decimal = int(str(number), int(from_base))
        if   int(to_base)==2:  result=bin(decimal)[2:]
        elif int(to_base)==8:  result=oct(decimal)[2:]
        elif int(to_base)==16: result=hex(decimal)[2:].upper()
        else: result=str(decimal)
        return f"{number} (base {from_base}) = {result} (base {to_base})"
    except Exception as e: return f"Conversion error: {e}"

def statistics_calc(numbers_str):
    try:
        import statistics
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', numbers_str)]
        if not nums: return "No numbers found."
        return (f"Statistics for {len(nums)} values:\n"
                f"  Min    : {min(nums)}\n  Max    : {max(nums)}\n"
                f"  Mean   : {statistics.mean(nums):.4f}\n"
                f"  Median : {statistics.median(nums)}\n"
                f"  Stdev  : {statistics.stdev(nums):.4f}" if len(nums)>1 else
                f"  Sum    : {sum(nums)}")
    except Exception as e: return f"Stats error: {e}"

# ══ UTILITY ═══════════════════════════════════════════════════════════════════
def countdown_timer(seconds, speak_fn=None):
    import threading
    def _run():
        time.sleep(int(seconds))
        msg = f"Countdown complete! {seconds}s elapsed."
        print(f"\n[JARVIS ⏱️] {msg}")
        if speak_fn: speak_fn(msg)
    threading.Thread(target=_run, daemon=True).start()
    return f"⏱️ Countdown: {seconds}s started."

def stopwatch_lap(label="lap"):
    ts = time.time()
    return f"⏱️ Stopwatch mark [{label}]: {datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')[:12]}"

def timezone_convert(time_str, from_tz, to_tz):
    try:
        from datetime import datetime
        import re
        return f"Timezone conversion requires pytz. pip install pytz\nManual: IST = UTC+5:30"
    except Exception as e: return f"TZ error: {e}"

def world_clock():
    zones = {"IST (Hailakandi)":5.5,"UTC":0,"EST":-5,"PST":-8,"CET":1,"JST":9,"AEST":10}
    from datetime import datetime, timezone, timedelta
    now = datetime.utcnow()
    lines = []
    for name, offset in zones.items():
        tz_time = now + timedelta(hours=offset)
        lines.append(f"  {name:<22} {tz_time.strftime('%H:%M  %a %b %d')}")
    return "🌍 World Clock:\n" + "\n".join(lines)
