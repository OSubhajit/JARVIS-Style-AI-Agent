# plugins/text_tools.py — Text Processing, Analysis & Manipulation

import re, random, string, hashlib, base64
from collections import Counter


# ══ BASIC TEXT OPS ════════════════════════════════════════════════════════════
def word_count(text):
    words  = len(text.split())
    chars  = len(text)
    chars_no_space = len(text.replace(" ",""))
    lines  = text.count("\n") + 1
    sentences = len(re.findall(r'[.!?]+', text))
    return (f"📊 Text Statistics:\n"
            f"  Words      : {words}\n"
            f"  Characters : {chars} ({chars_no_space} without spaces)\n"
            f"  Lines      : {lines}\n"
            f"  Sentences  : {sentences}\n"
            f"  Avg word len: {chars_no_space/max(words,1):.1f} chars")

def case_upper(text):   return text.upper()
def case_lower(text):   return text.lower()
def case_title(text):   return text.title()
def case_camel(text):   words=text.split(); return words[0].lower()+"".join(w.title() for w in words[1:])
def case_snake(text):   return "_".join(text.lower().split())
def case_kebab(text):   return "-".join(text.lower().split())
def case_pascal(text):  return "".join(w.title() for w in text.split())
def case_reverse(text): return text[::-1]
def case_alternate(text): return "".join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(text))

def remove_duplicates(text):
    seen=set(); lines=[]
    for line in text.splitlines():
        if line not in seen: seen.add(line); lines.append(line)
    return "\n".join(lines)

def sort_lines(text, reverse=False):
    return "\n".join(sorted(text.splitlines(), reverse=reverse))

def remove_empty_lines(text):
    return "\n".join(l for l in text.splitlines() if l.strip())

def trim_whitespace(text):
    return "\n".join(l.strip() for l in text.splitlines())

def add_line_numbers(text):
    return "\n".join(f"{i+1:>4}  {l}" for i,l in enumerate(text.splitlines()))

def find_replace(text, find, replace):
    count = text.count(find)
    return text.replace(find, replace), f"Replaced {count} occurrence(s) of '{find}' → '{replace}'"

def extract_emails(text):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return f"Emails found ({len(emails)}):\n" + "\n".join(f"  • {e}" for e in emails) if emails else "No emails found."

def extract_urls(text):
    urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    return f"URLs found ({len(urls)}):\n" + "\n".join(f"  • {u}" for u in urls) if urls else "No URLs found."

def extract_phones(text):
    phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
    return f"Phone numbers ({len(phones)}):\n" + "\n".join(f"  • {p}" for p in phones) if phones else "No phone numbers found."

def extract_numbers(text):
    nums = re.findall(r'-?\d+\.?\d*', text)
    return f"Numbers ({len(nums)}): {nums[:30]}"

def count_words_freq(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    freq  = Counter(words).most_common(20)
    return "Word frequency:\n" + "\n".join(f"  {w:<20} {c}" for w,c in freq)

# ══ ENCODING ══════════════════════════════════════════════════════════════════
def rot13(text):
    return text.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))

def morse_encode(text):
    MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---',
             'K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-',
             'U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---',
             '3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'}
    result = " ".join(MORSE.get(c.upper(), '?') for c in text if c != ' ')
    return f"Morse: {result}"

def morse_decode(morse):
    MORSE = {'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I','.---':'J',
             '-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R','...':'S','-':'T',
             '..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z','-----':'0','.----':'1','..---':'2',
             '...--':'3','....-':'4','.....':'5','-....':'6','--...':'7','---..':'8','----.':'9'}
    return "".join(MORSE.get(code,'?') for code in morse.split())

def binary_encode(text):
    return " ".join(format(ord(c),'08b') for c in text)

def binary_decode(binary):
    try: return "".join(chr(int(b,2)) for b in binary.split())
    except: return "Invalid binary input."

def hex_encode(text):     return text.encode().hex()
def hex_decode(hex_str):
    try: return bytes.fromhex(hex_str).decode()
    except: return "Invalid hex input."

# ══ TEXT GENERATION ═══════════════════════════════════════════════════════════
_LOREM = ("Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
          "tempor incididunt ut labore et dolore magna aliqua Ut enim ad minim veniam "
          "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat")

def lorem_ipsum(words=50):
    base = _LOREM.split() * (words // 20 + 1)
    return " ".join(base[:words])

def random_sentence():
    subjects = ["The cat","A developer","JARVIS","The robot","An AI","The system","A hacker","The user"]
    verbs    = ["quickly processes","efficiently handles","smartly analyzes","boldly executes","carefully monitors"]
    objects  = ["complex data","network packets","voice commands","encrypted files","system resources","the task"]
    return f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}."

def random_quote():
    QUOTES = [
        "The only way to do great work is to love what you do. — Steve Jobs",
        "Code is like humor. When you have to explain it, it's bad. — Cory House",
        "First, solve the problem. Then, write the code. — John Johnson",
        "Experience is the name everyone gives to their mistakes. — Oscar Wilde",
        "In theory, theory and practice are the same. In practice, they're not.",
        "The best error message is the one that never shows up. — Thomas Fuchs",
        "Before software can be reusable, it first has to be usable. — Ralph Johnson",
        "Simplicity is the soul of efficiency. — Austin Freeman",
        "It's not a bug, it's an undocumented feature.",
        "Talk is cheap. Show me the code. — Linus Torvalds",
    ]
    return random.choice(QUOTES)

def random_name():
    FIRST = ["Aarav","Priya","Arjun","Neha","Vikram","Ananya","Rohan","Shreya","Dev","Kavya","Rahul","Ishita"]
    LAST  = ["Sharma","Patel","Singh","Kumar","Gupta","Joshi","Mehta","Shah","Rao","Nair","Verma","Agarwal"]
    return f"{random.choice(FIRST)} {random.choice(LAST)}"

def random_color():
    r,g,b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
    return f"RGB({r}, {g}, {b})  HEX: #{r:02X}{g:02X}{b:02X}"

def random_number(min_val=1, max_val=100):
    return str(random.randint(int(min_val), int(max_val)))

def flip_coin():    return random.choice(["Heads 🪙", "Tails 🪙"])
def roll_dice(sides=6): return f"🎲 Rolled {sides}-sided die: {random.randint(1,int(sides))}"

# ══ ANALYSIS ═════════════════════════════════════════════════════════════════
def readability_score(text):
    words     = len(text.split())
    sentences = max(len(re.findall(r'[.!?]+', text)), 1)
    syllables = sum(max(len(re.findall(r'[aeiou]', w, re.I)), 1) for w in text.split())
    fk = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    level = "Easy" if fk<30 else "Moderate" if fk<60 else "Difficult"
    return f"Readability: {level} (Flesch-Kincaid: {fk:.1f})"

def detect_language(text):
    """Simple heuristic language detection."""
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    if hindi_chars > 3: return "Hindi (Devanagari script detected)"
    common_en = {"the","a","an","is","are","was","were","and","or","but","in","on"}
    words = set(text.lower().split())
    match = len(common_en & words)
    return "English" if match >= 2 else "Unknown / Mixed"

def palindrome_check(text):
    clean = re.sub(r'[^a-zA-Z0-9]','',text).lower()
    is_p  = clean == clean[::-1]
    return f"'{text}' is {'a palindrome ✅' if is_p else 'NOT a palindrome ❌'}"

def anagram_check(text1, text2):
    c1 = Counter(re.sub(r'[^a-z]','',text1.lower()))
    c2 = Counter(re.sub(r'[^a-z]','',text2.lower()))
    return f"'{text1}' and '{text2}' are {'anagrams ✅' if c1==c2 else 'NOT anagrams ❌'}"
