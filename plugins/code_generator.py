# plugins/code_generator.py — Code Templates, Scaffolders & Project Generators

import os
from plugins.advanced_ai import _ai


# ══ PROJECT SCAFFOLDERS ═══════════════════════════════════════════════════════
def scaffold_flask_app(name, features="basic"):
    code = f'''# {name} — Flask App
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({{"status":"ok","time":datetime.now().isoformat()}})

@app.route("/api/data", methods=["GET","POST"])
def data():
    if request.method == "POST":
        body = request.get_json()
        return jsonify({{"received":body,"status":"ok"}})
    return jsonify({{"data":[],"status":"ok"}})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
'''
    fname = f"{name.lower().replace(' ','_')}_app.py"
    with open(fname,"w") as f: f.write(code)
    return f"Flask app scaffolded: {fname}"

def scaffold_fastapi_app(name):
    code = f'''# {name} — FastAPI App
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI(title="{name}", version="1.0.0")

class Item(BaseModel):
    name: str
    value: Optional[str] = None

items_db: List[Item] = []

@app.get("/")
def root():
    return {{"name":"{name}","time":datetime.now().isoformat()}}

@app.get("/items")
def get_items():
    return {{"items":items_db,"count":len(items_db)}}

@app.post("/items")
def create_item(item: Item):
    items_db.append(item)
    return {{"created":item,"total":len(items_db)}}

@app.get("/items/{{item_id}}")
def get_item(item_id: int):
    if item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.delete("/items/{{item_id}}")
def delete_item(item_id: int):
    if item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Not found")
    removed = items_db.pop(item_id)
    return {{"deleted":removed}}
'''
    fname = f"{name.lower().replace(' ','_')}_api.py"
    with open(fname,"w") as f: f.write(code)
    return f"FastAPI app scaffolded: {fname}"

def scaffold_cli_tool(name):
    code = f'''#!/usr/bin/env python3
"""
{name} — CLI Tool
Usage: python {name.lower()}.py [command] [options]
"""
import argparse, sys

def cmd_run(args):
    print(f"Running with: {{args}}")

def cmd_list(args):
    print("Listing items...")

def cmd_config(args):
    print(f"Config: key={{args.key}}, value={{args.value}}")

def main():
    parser = argparse.ArgumentParser(description="{name}")
    sub    = parser.add_subparsers(dest="command", help="Commands")

    # run command
    run_p = sub.add_parser("run", help="Run operation")
    run_p.add_argument("--input", "-i", help="Input file")
    run_p.add_argument("--output","-o", help="Output file")
    run_p.add_argument("--verbose","-v",action="store_true")

    # list command
    sub.add_parser("list", help="List items")

    # config command
    cfg_p = sub.add_parser("config", help="Set config")
    cfg_p.add_argument("key")
    cfg_p.add_argument("value", nargs="?", default="")

    args = parser.parse_args()
    if   args.command == "run":    cmd_run(args)
    elif args.command == "list":   cmd_list(args)
    elif args.command == "config": cmd_config(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
'''
    fname = f"{name.lower().replace(' ','_')}.py"
    with open(fname,"w") as f: f.write(code)
    return f"CLI tool scaffolded: {fname}"

def scaffold_sqlite_manager(name, table, columns):
    cols_def  = ", ".join(f"{c} TEXT" for c in columns.split(","))
    cols_list = ", ".join(c.strip() for c in columns.split(","))
    placeholders = ", ".join("?" for _ in columns.split(","))
    code = f'''# {name} — SQLite Manager
import sqlite3
from datetime import datetime

DB = "{name.lower()}.db"

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS {table}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {cols_def},
            created TEXT DEFAULT(datetime('now'))
        )""")
    print(f"Database initialized: {{DB}}")

def insert({cols_list}):
    with connect() as c:
        c.execute("INSERT INTO {table}({cols_list}) VALUES({placeholders})",
                  ({cols_list},))
    print(f"Record inserted.")

def get_all():
    with connect() as c:
        return c.execute("SELECT * FROM {table} ORDER BY id DESC").fetchall()

def get_by_id(record_id):
    with connect() as c:
        return c.execute("SELECT * FROM {table} WHERE id=?", (record_id,)).fetchone()

def delete(record_id):
    with connect() as c:
        c.execute("DELETE FROM {table} WHERE id=?", (record_id,))
    print(f"Record {{record_id}} deleted.")

def search(query):
    with connect() as c:
        first_col = "{columns.split(',')[0].strip()}"
        return c.execute(f"SELECT * FROM {table} WHERE {{first_col}} LIKE ?",
                         (f"%{{query}}%",)).fetchall()

if __name__ == "__main__":
    init()
    print("All records:", [dict(r) for r in get_all()])
'''
    fname = f"{name.lower()}_db.py"
    with open(fname,"w") as f: f.write(code)
    return f"SQLite manager scaffolded: {fname}"

def scaffold_class(class_name, attributes, methods):
    attr_list = [a.strip() for a in attributes.split(",")]
    meth_list = [m.strip() for m in methods.split(",")]
    init_args = ", ".join(attr_list)
    init_body = "\n        ".join(f"self.{a} = {a}" for a in attr_list)
    meths_code= "\n\n".join(
        f"    def {m}(self):\n        \"\"\"TODO: implement {m}\"\"\"\n        pass"
        for m in meth_list
    )
    repr_parts= ", ".join(f"{a}={{self.{a}}}" for a in attr_list)
    code = f'''class {class_name}:
    """{class_name} class."""

    def __init__(self, {init_args}):
        {init_body}

    def __repr__(self):
        return f"{class_name}({repr_parts})"

    def __eq__(self, other):
        return isinstance(other, {class_name}) and self.__dict__ == other.__dict__

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

{meths_code}
'''
    fname = f"{class_name.lower()}.py"
    with open(fname,"w") as f: f.write(code)
    return f"Class scaffolded: {fname}"

def scaffold_test_file(target_file):
    try:
        module = os.path.splitext(os.path.basename(target_file))[0]
        code = f'''# Tests for {module}
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from {module} import *


class Test{module.title().replace("_","")}:
    """Test suite for {module}."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    def teardown_method(self):
        """Clean up after each test."""
        pass

    def test_basic_import(self):
        """Test that module imports successfully."""
        assert True

    def test_placeholder(self):
        """Replace with actual tests."""
        # Arrange
        expected = None
        # Act
        result = None
        # Assert
        assert result == expected


# Edge case tests
class TestEdgeCases:
    def test_empty_input(self):
        pass

    def test_none_input(self):
        pass

    def test_boundary_values(self):
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        fname = f"test_{module}.py"
        with open(fname,"w") as f: f.write(code)
        return f"Test file scaffolded: {fname}"
    except Exception as e:
        return f"Error: {e}"

def scaffold_dockerfile(app_type="python", port=5000):
    templates = {
        "python": f'''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
''',
        "node": f'''FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE {port}
USER node
CMD ["node", "index.js"]
''',
        "flask": f'''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
EXPOSE {port}
CMD ["gunicorn", "--bind", "0.0.0.0:{port}", "--workers", "4", "app:app"]
''',
    }
    content = templates.get(app_type.lower(), templates["python"])
    with open("Dockerfile","w") as f: f.write(content)
    # Also create .dockerignore
    dockerignore = "__pycache__/\n*.pyc\n.env\n.git\nlogs/\ndata/\n*.db\n"
    with open(".dockerignore","w") as f: f.write(dockerignore)
    return f"Dockerfile created for {app_type} app on port {port}"

def scaffold_env_file(variables):
    lines = [f"# Environment variables — {datetime.now().strftime('%Y-%m-%d')}",
             "# DO NOT commit this file to git\n"]
    for var in variables.split(","):
        v = var.strip()
        lines.append(f"{v.upper()}=your_{v.lower()}_here")
    content = "\n".join(lines)
    with open(".env.example","w") as f: f.write(content)
    return f".env.example created with {len(variables.split(','))} variables"

def generate_gitignore(project_type="python"):
    templates = {
        "python": "__pycache__/\n*.py[cod]\n*.pyo\n.env\nvenv/\n.venv/\ndist/\nbuild/\n*.egg-info/\n.pytest_cache/\nlogs/\n*.log\ndata/*.db\n",
        "node":   "node_modules/\nnpm-debug.log*\n.env\ndist/\nbuild/\n.DS_Store\ncoverage/\n",
        "general":".env\n*.log\n*.db\n.DS_Store\nThumbs.db\nbuild/\ndist/\n",
    }
    content = templates.get(project_type.lower(), templates["general"])
    with open(".gitignore","w") as f: f.write(content)
    return f".gitignore created for {project_type} project"

def ai_generate_module(description, language="python"):
    result = _ai(f"Write a complete, production-ready {language} module for: {description}\n"
                 f"Include: imports, docstrings, error handling, example usage at bottom.\n"
                 f"Return ONLY the code.")
    fname = "ai_generated_module.py"
    with open(fname,"w") as f: f.write(result)
    return f"AI module generated: {fname}\n\nPreview:\n{result[:300]}..."
