# plugins/advanced_ai.py — Advanced AI Features: RAG, Code Review, Debate, etc.

import os, re, json
from logger import log


def _ai(prompt, max_tokens=1000):
    try:
        import requests
        from config import OLLAMA_URL, MODEL_NAME, AI_TIMEOUT
        r = requests.post(OLLAMA_URL,
                          json={"model":MODEL_NAME,"prompt":prompt,"stream":False},
                          timeout=AI_TIMEOUT)
        return r.json().get("response","").strip()
    except Exception as e: return f"AI unavailable: {e}"


# ══ CODE INTELLIGENCE ═════════════════════════════════════════════════════════
def code_review(code, language="python"):
    prompt = f"""Review this {language} code. Identify:
1. Bugs or logical errors
2. Security vulnerabilities
3. Performance issues
4. Style/readability problems
5. Suggested improvements

Code:
```{language}
{code[:2000]}
```
Be concise and specific."""
    return _ai(prompt)

def explain_code(code, language="python"):
    prompt = f"""Explain this {language} code in simple terms.
What does it do? How does it work? Any notable patterns?

```{language}
{code[:2000]}
```"""
    return _ai(prompt)

def fix_code(code, error_msg=""):
    prompt = f"""Fix this code{' — Error: ' + error_msg if error_msg else ''}.
Return ONLY the corrected code with brief comment explaining the fix.

```
{code[:2000]}
```"""
    return _ai(prompt)

def translate_code(code, from_lang, to_lang):
    prompt = f"""Convert this {from_lang} code to {to_lang}.
Maintain the same logic and functionality.
Return ONLY the translated code.

```{from_lang}
{code[:2000]}
```"""
    return _ai(prompt)

def generate_code(description, language="python"):
    prompt = f"""Write {language} code for: {description}
Include comments. Make it production-ready."""
    return _ai(prompt)

def optimize_code(code, language="python"):
    prompt = f"""Optimize this {language} code for performance and readability.
Return the optimized version with comments explaining improvements.

```{language}
{code[:2000]}
```"""
    return _ai(prompt)

def add_docstrings(code, language="python"):
    prompt = f"""Add proper docstrings/comments to every function and class in this code.
Return the complete code with docstrings added.

```{language}
{code[:2000]}
```"""
    return _ai(prompt)


# ══ WRITING ASSISTANT ═════════════════════════════════════════════════════════
def write_email(context, tone="professional"):
    prompt = f"""Write a {tone} email for: {context}
Include: Subject line, greeting, body, closing.
Be concise and clear."""
    return _ai(prompt)

def improve_writing(text):
    prompt = f"""Improve this text for clarity, grammar, and impact.
Return the improved version only.

Text: {text[:1500]}"""
    return _ai(prompt)

def write_essay(topic, words=300):
    prompt = f"""Write a well-structured {words}-word essay on: {topic}
Include introduction, 2-3 body paragraphs, and conclusion."""
    return _ai(prompt)

def write_linkedin_post(topic):
    prompt = f"""Write an engaging LinkedIn post about: {topic}
Make it professional but relatable. Include relevant hashtags. Max 300 words."""
    return _ai(prompt)

def write_tweet(topic):
    prompt = f"""Write 3 Twitter/X posts about: {topic}
Each under 280 characters. Make them engaging and concise."""
    return _ai(prompt)

def summarize_text(text, sentences=3):
    prompt = f"""Summarize this text in {sentences} sentences.
Be concise and capture the key points only.

Text: {text[:3000]}"""
    return _ai(prompt)

def explain_topic(topic, level="beginner"):
    prompt = f"""Explain '{topic}' for a {level}.
Use simple language, analogies, and examples. Keep it under 200 words."""
    return _ai(prompt)

def translate_ai(text, target_language):
    prompt = f"""Translate to {target_language}. Return ONLY the translation.

Text: {text}"""
    return _ai(prompt)


# ══ REASONING & ANALYSIS ═════════════════════════════════════════════════════
def debate_topic(topic):
    prompt = f"""Present both sides of the debate: '{topic}'

FOR (arguments supporting):
[3 strong points]

AGAINST (arguments opposing):
[3 strong points]

VERDICT: Brief balanced conclusion."""
    return _ai(prompt)

def pros_cons(topic):
    prompt = f"""List pros and cons of: {topic}
Format as:
PROS:
• ...
CONS:
• ...
VERDICT: one sentence recommendation."""
    return _ai(prompt)

def fact_check(claim):
    prompt = f"""Analyze this claim: "{claim}"
Based on your knowledge:
1. Is this likely TRUE, FALSE, or PARTIALLY TRUE?
2. What evidence supports or refutes it?
3. Any important nuances?
Note: This is AI analysis, not verified fact-checking."""
    return _ai(prompt)

def what_if(scenario):
    prompt = f"""Analyze this 'what if' scenario: {scenario}
Consider likely outcomes, second-order effects, and interesting implications.
Keep it analytical and interesting."""
    return _ai(prompt)

def interview_prep(role, question=""):
    if question:
        prompt = f"""Give a strong answer to this {role} interview question: '{question}'
Structure: situation, action, result. Keep under 200 words."""
    else:
        prompt = f"""List 10 common interview questions for {role} with brief answer tips."""
    return _ai(prompt)

def study_plan(topic, days=7):
    prompt = f"""Create a {days}-day study plan for: {topic}
For each day include: what to study, resources type, and a practice task."""
    return _ai(prompt)


# ══ RAG (Retrieval-Augmented Generation) ════════════════════════════════════
def rag_index_file(filepath):
    """Index a text file for RAG queries."""
    try:
        os.makedirs("data/rag", exist_ok=True)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        index_path = f"data/rag/{os.path.basename(filepath)}.idx"
        with open(index_path, "w") as f:
            json.dump({"path": filepath, "content": content[:50000]}, f)
        return f"Indexed for RAG: {filepath} ({len(content)} chars)"
    except Exception as e: return f"RAG index error: {e}"

def rag_query(question, filepath=None):
    """Answer a question using indexed documents."""
    try:
        os.makedirs("data/rag", exist_ok=True)
        docs = []
        search_files = ([f"data/rag/{os.path.basename(filepath)}.idx"] if filepath
                        else [f"data/rag/{f}" for f in os.listdir("data/rag") if f.endswith(".idx")])
        for sf in search_files:
            if os.path.exists(sf):
                with open(sf) as f:
                    data = json.load(f)
                docs.append(data.get("content","")[:3000])
        if not docs: return "No documents indexed. Use 'index file <path>' first."
        context = "\n\n---\n\n".join(docs)
        prompt = f"""Answer this question using ONLY the context below.
If the answer isn't in the context, say 'Not found in documents.'

Context:
{context}

Question: {question}"""
        return _ai(prompt)
    except Exception as e: return f"RAG query error: {e}"

def daily_word():
    """Generate a word of the day with definition and usage."""
    prompt = """Give me a useful English word I should know.
Format:
WORD: [word]
PRONUNCIATION: [phonetic]
MEANING: [simple definition]
EXAMPLE: [natural sentence]
REMEMBER: [memory trick]"""
    return _ai(prompt)

def eli5(topic):
    """Explain like I'm 5."""
    prompt = f"""Explain '{topic}' like I'm 5 years old.
Use simple words, fun analogies, and avoid jargon. Max 100 words."""
    return _ai(prompt)
