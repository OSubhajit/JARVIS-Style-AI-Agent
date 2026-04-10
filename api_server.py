# api_server.py — JARVIS V4 REST API + Web Control Panel
# Access from browser: http://localhost:5000
# Access from phone (same WiFi): http://<your-pc-ip>:5000

import threading
from flask import Flask, request, jsonify, render_template_string
from config import API_HOST, API_PORT
from logger import log

app = Flask(__name__)
_execute_fn = None
_speak_fn   = None

# ── Web UI ────────────────────────────────────────────────────────────────────
UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JARVIS V4</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#05050f;color:#00d4ff;font-family:'Courier New',monospace;min-height:100vh}
.hdr{text-align:center;padding:24px 0 8px;border-bottom:1px solid #0ff2}
.hdr h1{font-size:2.2em;letter-spacing:6px;text-shadow:0 0 30px #00d4ff}
.hdr p{color:#444;font-size:.8em;margin-top:4px}
.body{max-width:900px;margin:0 auto;padding:20px}
.input-row{display:flex;gap:10px;margin:20px 0}
input{flex:1;padding:14px 18px;background:#0a0a1a;border:1px solid #00d4ff44;
  color:#00d4ff;border-radius:8px;font-size:1em;outline:none;transition:.2s}
input:focus{border-color:#00d4ff;box-shadow:0 0 12px #00d4ff33}
.btn{padding:14px 20px;background:transparent;border:1px solid #00d4ff;
  color:#00d4ff;border-radius:8px;cursor:pointer;font-family:inherit;
  font-size:.95em;transition:.2s;white-space:nowrap}
.btn:hover{background:#00d4ff;color:#000}
.btn.active{background:#00d4ff22}
.quick{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
.quick .btn{padding:7px 13px;font-size:.78em}
.response{background:#0a0a1a;border:1px solid #0ff2;border-radius:10px;
  padding:20px;min-height:130px;white-space:pre-wrap;font-size:.88em;
  line-height:1.7;margin-bottom:16px;max-height:400px;overflow-y:auto}
.status-bar{display:flex;justify-content:space-between;font-size:.75em;
  color:#444;margin-bottom:18px;padding:0 4px}
.status-bar span{color:#0f0}
.tabs{display:flex;gap:0;margin-bottom:16px;border-bottom:1px solid #0ff2}
.tab{padding:8px 18px;cursor:pointer;font-size:.85em;border-bottom:2px solid transparent;transition:.2s}
.tab.on{border-bottom-color:#00d4ff;color:#fff}
.tab:hover{color:#fff}
.panel{display:none}.panel.on{display:block}
.hist-item{padding:7px 10px;border-bottom:1px solid #0ff1;font-size:.82em;
  color:#666;cursor:pointer;transition:.2s}
.hist-item:hover{color:#00d4ff;background:#ffffff05}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.stat-card{background:#0a0a1a;border:1px solid #0ff2;border-radius:8px;padding:14px;text-align:center}
.stat-card .val{font-size:1.5em;font-weight:bold;color:#0ff}
.stat-card .lbl{font-size:.75em;color:#555;margin-top:4px}
@media(max-width:600px){.hdr h1{font-size:1.5em;letter-spacing:3px}.quick .btn{font-size:.72em}}
</style>
</head>
<body>
<div class="hdr">
  <h1>⚡ J.A.R.V.I.S V4</h1>
  <p>Maximum Edition — Remote Control Panel</p>
</div>
<div class="body">
  <div class="input-row">
    <input id="cmd" placeholder="Tell JARVIS what to do..." onkeydown="if(event.key==='Enter')send()">
    <button class="btn" onclick="send()">▶ Send</button>
    <button class="btn" id="voiceBtn" onclick="startVoice()">🎤</button>
  </div>

  <div class="quick">
    <button class="btn" onclick="q('system report')">📊 System</button>
    <button class="btn" onclick="q('get weather')">🌤️ Weather</button>
    <button class="btn" onclick="q('get news')">📰 News</button>
    <button class="btn" onclick="q('take a screenshot')">📸 Screenshot</button>
    <button class="btn" onclick="q('show reminders')">⏰ Reminders</button>
    <button class="btn" onclick="q('list tasks')">📋 Tasks</button>
    <button class="btn" onclick="q('what do you know')">🧠 Memory</button>
    <button class="btn" onclick="q('show habits')">🔥 Habits</button>
    <button class="btn" onclick="q('show expenses')">💸 Expenses</button>
    <button class="btn" onclick="q('git status')">🔧 Git</button>
    <button class="btn" onclick="q('list processes')">⚙️ Processes</button>
    <button class="btn" onclick="q('tell me a joke')">😄 Joke</button>
    <button class="btn" onclick="q('daily briefing')">☀️ Briefing</button>
    <button class="btn" onclick="q('show history')">📜 History</button>
  </div>

  <div class="status-bar">
    <span id="statusTxt">🟢 Connected</span>
    <span id="timeTxt"></span>
  </div>

  <div class="response" id="resp">JARVIS V4 ready. Type a command or tap a quick button...</div>

  <div class="tabs">
    <div class="tab on" onclick="showTab('history')">History</div>
    <div class="tab" onclick="showTab('stats')">Stats</div>
    <div class="tab" onclick="showTab('chain')">Chain Builder</div>
  </div>

  <div class="panel on" id="tab-history">
    <div id="histList"></div>
  </div>

  <div class="panel" id="tab-stats">
    <div class="stats" id="statsGrid">
      <div class="stat-card"><div class="val" id="s-total">-</div><div class="lbl">Total Commands</div></div>
      <div class="stat-card"><div class="val" id="s-today">-</div><div class="lbl">Today</div></div>
      <div class="stat-card"><div class="val" id="s-api">V4</div><div class="lbl">Version</div></div>
    </div>
  </div>

  <div class="panel" id="tab-chain">
    <div style="color:#666;font-size:.85em;margin-bottom:10px">Build a multi-step command:</div>
    <div id="chainSteps"></div>
    <div style="display:flex;gap:8px;margin-top:10px">
      <input id="chainInput" placeholder="Add step..." style="flex:1">
      <button class="btn" onclick="addChainStep()">+ Add</button>
      <button class="btn" onclick="runChain()">▶ Run Chain</button>
      <button class="btn" onclick="clearChain()">✕ Clear</button>
    </div>
  </div>
</div>

<script>
const hist=[];
const chain=[];

async function send(){
  const cmd=document.getElementById('cmd').value.trim();
  if(!cmd)return;
  document.getElementById('resp').textContent='⏳ Processing...';
  document.getElementById('statusTxt').textContent='🟡 Thinking...';
  hist.unshift({cmd,time:new Date().toLocaleTimeString()});
  renderHist();
  try{
    const r=await fetch('/api/command',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({command:cmd})});
    const d=await r.json();
    document.getElementById('resp').textContent=d.result||d.error||'No response';
    document.getElementById('statusTxt').textContent=d.success?'🟢 Done':'🔴 Error';
    updateStats(d);
  }catch(e){
    document.getElementById('resp').textContent='Connection error: '+e;
    document.getElementById('statusTxt').textContent='🔴 Disconnected';
  }
  document.getElementById('cmd').value='';
}

function q(cmd){document.getElementById('cmd').value=cmd;send();}

function renderHist(){
  document.getElementById('histList').innerHTML=
    hist.slice(0,20).map(h=>
      `<div class="hist-item" onclick="q('${h.cmd.replace(/'/g,"\\'")}')">
         <span style="color:#333">${h.time}</span>  ▸  ${h.cmd}
       </div>`).join('');
}

function showTab(name){
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.getElementById('tab-'+name).classList.add('on');
  event.target.classList.add('on');
  if(name==='stats')loadStats();
}

async function loadStats(){
  try{
    const r=await fetch('/api/history');
    const d=await r.json();
    document.getElementById('s-total').textContent=d.length||0;
    const today=new Date().toLocaleDateString();
    const todayCount=d.filter(x=>new Date(x.timestamp).toLocaleDateString()===today).length;
    document.getElementById('s-today').textContent=todayCount;
  }catch(e){}
}

function addChainStep(){
  const v=document.getElementById('chainInput').value.trim();
  if(!v)return;
  chain.push(v);
  document.getElementById('chainInput').value='';
  document.getElementById('chainSteps').innerHTML=
    chain.map((s,i)=>`<div style="padding:6px 10px;border-bottom:1px solid #0ff1;font-size:.85em">
      ${i+1}. ${s} <span style="color:#f44;cursor:pointer;float:right" onclick="chain.splice(${i},1);addChainStep()">✕</span>
    </div>`).join('');
}

async function runChain(){
  if(!chain.length)return;
  q(chain.join(' then '));
}

function clearChain(){chain.length=0;document.getElementById('chainSteps').innerHTML='';}

function updateStats(d){}

// Voice input
let recognition=null;
function startVoice(){
  if(!('webkitSpeechRecognition' in window||'SpeechRecognition' in window)){
    alert('Voice not supported in this browser. Use Chrome.'); return;
  }
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  recognition=new SR(); recognition.lang='en-IN'; recognition.interimResults=false;
  recognition.onstart=()=>{document.getElementById('voiceBtn').textContent='🔴';};
  recognition.onresult=(e)=>{
    document.getElementById('cmd').value=e.results[0][0].transcript;
    document.getElementById('voiceBtn').textContent='🎤';
    send();
  };
  recognition.onerror=()=>{document.getElementById('voiceBtn').textContent='🎤';};
  recognition.start();
}

// Clock
setInterval(()=>{
  document.getElementById('timeTxt').textContent=new Date().toLocaleTimeString();
},1000);
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(UI)


@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "Missing 'command'", "success": False}), 400
    command = data["command"]
    log.info(f"API: {command}")
    try:
        from interpreter import parse_intent
        intent = parse_intent(command)
        if "chain" in intent:
            results = []
            for step in intent["chain"]:
                r = _execute_fn(step.get("action","unknown"), step.get("params",{}), _speak_fn)
                results.append(r or "")
            result = "\n".join(results)
        else:
            result = _execute_fn(intent.get("action","unknown"), intent.get("params",{}), _speak_fn)
        return jsonify({"result": result, "intent": intent, "success": True})
    except Exception as e:
        log.error(f"API error: {e}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/status")
def api_status():
    import platform, datetime
    return jsonify({"status":"online","version":"4.0","time":datetime.datetime.now().isoformat(),"platform":platform.platform()})


@app.route("/api/history")
def api_history():
    from database import hist_get
    return jsonify([dict(r) for r in hist_get(50)])


@app.route("/api/memory")
def api_memory():
    from database import mem_all
    return jsonify([dict(r) for r in mem_all()])


@app.route("/api/reminders")
def api_reminders():
    from database import reminder_all
    return jsonify([dict(r) for r in reminder_all()])


@app.route("/api/tasks")
def api_tasks():
    from database import task_all
    return jsonify([dict(r) for r in task_all()])


def start_api(execute_fn, speak_fn=None):
    global _execute_fn, _speak_fn
    _execute_fn = execute_fn
    _speak_fn   = speak_fn
    def _run():
        import logging as _l
        _l.getLogger("werkzeug").setLevel(_l.ERROR)
        app.run(host=API_HOST, port=API_PORT, debug=False, use_reloader=False)
    threading.Thread(target=_run, daemon=True).start()
    log.info(f"API started: http://localhost:{API_PORT}")
    print(f"\n\033[92m[JARVIS 🌐] Web panel → http://localhost:{API_PORT}  (phone: same URL on WiFi)\033[0m")
