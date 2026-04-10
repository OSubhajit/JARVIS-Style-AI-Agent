# plugins/dev_tools.py — Developer Tools: Code Runner, Docker, HTTP, Git, Formatters

import os, re, json, subprocess, hashlib, base64, time
from config import SANDBOX_TIMEOUT, DEFAULT_CODE_LANG
from logger import log

# ══ CODE RUNNER ═══════════════════════════════════════════════════════════════
def run_code(code, language=DEFAULT_CODE_LANG):
    lang=language.lower()
    try:
        if lang in ("python","py"):
            import subprocess, tempfile
            with tempfile.NamedTemporaryFile(mode="w",suffix=".py",delete=False) as f:
                f.write(code); fname=f.name
            r=subprocess.run(["python",fname],capture_output=True,text=True,timeout=SANDBOX_TIMEOUT)
            os.unlink(fname)
            out=r.stdout.strip(); err=r.stderr.strip()
            return f"Output:\n{out}" + (f"\nErrors:\n{err}" if err else "")

        elif lang in ("javascript","js","node"):
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w",suffix=".js",delete=False) as f:
                f.write(code); fname=f.name
            r=subprocess.run(["node",fname],capture_output=True,text=True,timeout=SANDBOX_TIMEOUT)
            os.unlink(fname)
            return r.stdout.strip() or r.stderr.strip()

        elif lang in ("bash","sh","shell"):
            r=subprocess.run(code,shell=True,capture_output=True,text=True,timeout=SANDBOX_TIMEOUT)
            return r.stdout.strip() or r.stderr.strip()

        else:
            return f"Language not supported: {lang}. Use python/js/bash"
    except subprocess.TimeoutExpired: return f"Code timed out after {SANDBOX_TIMEOUT}s"
    except Exception as e: return f"Run error: {e}"

# ══ HTTP CLIENT ═══════════════════════════════════════════════════════════════
def http_request(method="GET", url="", headers=None, body=None):
    try:
        import requests as req
        method=method.upper()
        kwargs={"timeout":15,"headers":headers or {}}
        if body:
            try: kwargs["json"]=json.loads(body)
            except: kwargs["data"]=body
        r=getattr(req,method.lower())(url,**kwargs)
        try: resp_body=json.dumps(r.json(),indent=2)[:1000]
        except: resp_body=r.text[:500]
        return (f"HTTP {method} {url}\n"
                f"  Status: {r.status_code} {r.reason}\n"
                f"  Time: {r.elapsed.total_seconds():.3f}s\n"
                f"  Body:\n{resp_body}")
    except Exception as e: return f"HTTP error: {e}"

# ══ JSON / DATA TOOLS ═════════════════════════════════════════════════════════
def format_json(text):
    try: return json.dumps(json.loads(text),indent=2)
    except Exception as e: return f"Invalid JSON: {e}"

def validate_yaml(text):
    try:
        import yaml; yaml.safe_load(text); return "✅ Valid YAML"
    except ImportError: return "pyyaml not installed."
    except Exception as e: return f"❌ Invalid YAML: {e}"

def regex_test(pattern, text):
    try:
        matches=re.findall(pattern,text)
        return f"Pattern: {pattern}\nMatches ({len(matches)}): {matches[:20]}"
    except Exception as e: return f"Regex error: {e}"

# ══ ENCODING / HASHING ════════════════════════════════════════════════════════
def encode_base64(text):
    return base64.b64encode(text.encode()).decode()

def decode_base64(text):
    try: return base64.b64decode(text.encode()).decode()
    except Exception as e: return f"Decode error: {e}"

def hash_text(text, algo="sha256"):
    try:
        h=hashlib.new(algo,text.encode())
        return f"{algo.upper()}: {h.hexdigest()}"
    except Exception as e: return f"Hash error: {e}"

# ══ LOCAL SERVER ══════════════════════════════════════════════════════════════
_server_proc=None
def serve_folder(path=".", port=8080):
    global _server_proc
    try:
        _server_proc=subprocess.Popen(
            ["python","-m","http.server",str(port)],
            cwd=path,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return f"🌐 Serving '{path}' at http://localhost:{port}"
    except Exception as e: return f"Server error: {e}"

def stop_server():
    global _server_proc
    if _server_proc: _server_proc.terminate(); _server_proc=None; return "Server stopped."
    return "No server running."

# ══ DOCKER ════════════════════════════════════════════════════════════════════
def _docker(args):
    try:
        r=subprocess.run(["docker"]+args,capture_output=True,text=True,timeout=20)
        return r.stdout.strip() or r.stderr.strip()
    except FileNotFoundError: return "Docker not installed."
    except Exception as e: return f"Docker error: {e}"

def docker_ps():   return _docker(["ps","--format","table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"])
def docker_start(name): return _docker(["start",name])
def docker_stop(name):  return _docker(["stop",name])
def docker_logs(name):  return _docker(["logs","--tail","30",name])

# ══ DEPENDENCY ANALYZER ═══════════════════════════════════════════════════════
def analyze_deps(requirements_file="requirements.txt"):
    try:
        import subprocess
        if not os.path.exists(requirements_file): return f"Not found: {requirements_file}"
        r=subprocess.run(["pip","check"],capture_output=True,text=True)
        r2=subprocess.run(["pip","list","--outdated","--format","columns"],capture_output=True,text=True)
        return f"Dependency conflicts:\n{r.stdout or 'None ✅'}\n\nOutdated packages:\n{r2.stdout[:500] or 'All up to date ✅'}"
    except Exception as e: return f"Analysis error: {e}"

# ══ AI CODE TOOLS ══════════════════════════════════════════════════════════════
def _ai(prompt):
    try:
        import requests
        from config import OLLAMA_URL, MODEL_NAME, AI_TIMEOUT
        r=requests.post(OLLAMA_URL,json={"model":MODEL_NAME,"prompt":prompt,"stream":False},timeout=AI_TIMEOUT)
        return r.json().get("response","").strip()
    except: return "AI unavailable."

def generate_readme(path="."):
    try:
        files=os.listdir(path)
        py_files=[f for f in files if f.endswith(".py")][:5]
        snippets=[]
        for f in py_files:
            with open(os.path.join(path,f)) as fp: snippets.append(f"# {f}\n"+fp.read()[:300])
        prompt=f"Generate a professional README.md for this Python project:\n\n"+"\n\n".join(snippets)
        return _ai(prompt)
    except Exception as e: return f"Error: {e}"

def generate_tests(filename):
    try:
        with open(filename) as f: code=f.read()
        prompt=f"Generate pytest unit tests for this Python code. Return only code:\n\n{code[:1500]}"
        tests=_ai(prompt)
        out=filename.replace(".py","_test.py")
        with open(out,"w") as f: f.write(tests)
        return f"Tests generated: {out}"
    except Exception as e: return f"Error: {e}"

def git_commit_message(path="."):
    try:
        diff=subprocess.run(["git","diff","--staged"],capture_output=True,text=True,cwd=path).stdout[:2000]
        if not diff: return "No staged changes."
        prompt=f"Write a concise git commit message (max 72 chars) for this diff:\n{diff}"
        return _ai(prompt)
    except Exception as e: return f"Error: {e}"

# ══ PACKAGE TOOLS ════════════════════════════════════════════════════════════
def install_package(package):
    try:
        r=subprocess.run(["pip","install","--break-system-packages",package],
            capture_output=True,text=True,timeout=60)
        return r.stdout.strip()[-200:] or r.stderr.strip()[-200:]
    except Exception as e: return f"Install error: {e}"
