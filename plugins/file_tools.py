# plugins/file_tools.py — Complete File Operations

import os, shutil, zipfile, hashlib, json, re
from datetime import datetime
from logger import log

# ══ BASIC FILE OPS ════════════════════════════════════════════════════════════
def create_file(filename, content=""):
    try:
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename,"w",encoding="utf-8") as f: f.write(content or f"# Created by JARVIS — {datetime.now()}\n")
        return f"Created: {filename}"
    except Exception as e: return f"Error: {e}"

def delete_file(filename):
    try: os.remove(filename); return f"Deleted: {filename}"
    except FileNotFoundError: return f"Not found: {filename}"
    except Exception as e: return f"Error: {e}"

def read_file(filename):
    try:
        with open(filename,"r",encoding="utf-8",errors="replace") as f: content=f.read()
        lines=content.splitlines(); preview="\n".join(lines[:60])
        return preview+(f"\n... [{len(lines)-60} more lines]" if len(lines)>60 else "")
    except Exception as e: return f"Read error: {e}"

def write_to_file(filename, content):
    try:
        with open(filename,"a",encoding="utf-8") as f: f.write(content+"\n")
        return f"Written to: {filename}"
    except Exception as e: return f"Write error: {e}"

def rename_file(old,new):
    try: os.rename(old,new); return f"Renamed: {old} → {new}"
    except Exception as e: return f"Error: {e}"

def copy_file(src,dst):
    try: shutil.copy2(src,dst); return f"Copied: {src} → {dst}"
    except Exception as e: return f"Error: {e}"

def move_file(src,dst):
    try: shutil.move(src,dst); return f"Moved: {src} → {dst}"
    except Exception as e: return f"Error: {e}"

def open_file(filename):
    try: os.startfile(filename); return f"Opened: {filename}"
    except Exception as e: return f"Error: {e}"

def list_files(path="."):
    try:
        items=sorted(os.listdir(path))
        lines=[]
        for item in items:
            full=os.path.join(path,item)
            icon="📁" if os.path.isdir(full) else "📄"
            try:
                sz=os.path.getsize(full)
                size=f"{sz/1024:.1f}KB" if sz<1048576 else f"{sz/1048576:.1f}MB"
            except: size="?"
            lines.append(f"  {icon} {item:<45} {size}")
        return f"📂 {path}:\n"+("\n".join(lines) if lines else "  (empty)")
    except Exception as e: return f"Error: {e}"

def search_file(query, path="."):
    results=[]
    for root,_,files in os.walk(path):
        for f in files:
            if query.lower() in f.lower(): results.append(os.path.join(root,f))
    return f"Found {len(results)} file(s):\n"+"\n".join(results[:30]) if results else f"No files matching '{query}'"

def get_file_info(filename):
    try:
        s=os.stat(filename); sz=s.st_size
        return (f"📄 {filename}\n  Size: {sz:,} bytes ({sz/1024:.1f} KB)\n"
                f"  Modified: {datetime.fromtimestamp(s.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  MD5: {_md5(filename)}\n  Type: {_mime(filename)}")
    except Exception as e: return f"Error: {e}"

def _md5(f):
    h=hashlib.md5()
    with open(f,"rb") as fp:
        for chunk in iter(lambda:fp.read(8192),b""): h.update(chunk)
    return h.hexdigest()

def _mime(f):
    ext=os.path.splitext(f)[1].lower()
    TYPES={".py":"Python",".txt":"Text",".pdf":"PDF",".jpg":"JPEG Image",".png":"PNG Image",
           ".zip":"ZIP Archive",".mp3":"Audio",".mp4":"Video",".docx":"Word Document",
           ".xlsx":"Excel",".json":"JSON",".html":"HTML",".csv":"CSV"}
    return TYPES.get(ext,"Unknown")

def text_diff(file1, file2):
    try:
        import difflib
        with open(file1) as f1, open(file2) as f2:
            lines1,lines2=f1.readlines(),f2.readlines()
        diff=list(difflib.unified_diff(lines1,lines2,fromfile=file1,tofile=file2,n=3))
        return "".join(diff[:60]) if diff else "Files are identical."
    except Exception as e: return f"Diff error: {e}"

# ══ COMPRESSION ═══════════════════════════════════════════════════════════════
def zip_files(files, output="archive.zip"):
    try:
        with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                if os.path.exists(f): zf.write(f)
        return f"Zipped {len(files)} file(s) → {output}"
    except Exception as e: return f"Zip error: {e}"

def unzip_file(filename, dest="."):
    try:
        with zipfile.ZipFile(filename,"r") as zf: zf.extractall(dest)
        return f"Extracted {filename} → {dest}"
    except Exception as e: return f"Unzip error: {e}"

# ══ PDF TOOLS ═════════════════════════════════════════════════════════════════
def pdf_merge(files, output="merged.pdf"):
    try:
        from PyPDF2 import PdfMerger
        merger=PdfMerger()
        for f in files: merger.append(f)
        merger.write(output); merger.close()
        return f"Merged {len(files)} PDFs → {output}"
    except ImportError: return "PyPDF2 not installed. Run: pip install PyPDF2"
    except Exception as e: return f"PDF merge error: {e}"

def pdf_split(filename, output_dir="."):
    try:
        from PyPDF2 import PdfReader, PdfWriter
        reader=PdfReader(filename)
        os.makedirs(output_dir, exist_ok=True)
        for i,page in enumerate(reader.pages):
            writer=PdfWriter(); writer.add_page(page)
            out=os.path.join(output_dir,f"page_{i+1}.pdf")
            with open(out,"wb") as f: writer.write(f)
        return f"Split into {len(reader.pages)} pages in {output_dir}"
    except ImportError: return "PyPDF2 not installed."
    except Exception as e: return f"PDF split error: {e}"

def pdf_to_text(filename):
    try:
        from PyPDF2 import PdfReader
        reader=PdfReader(filename); text=""
        for page in reader.pages: text+=page.extract_text()+"\n"
        return text[:2000]+("..." if len(text)>2000 else "")
    except ImportError: return "PyPDF2 not installed."
    except Exception as e: return f"PDF error: {e}"

# ══ OCR ═══════════════════════════════════════════════════════════════════════
def ocr_image(filename):
    try:
        import pytesseract; from PIL import Image
        text=pytesseract.image_to_string(Image.open(filename))
        return f"OCR:\n{text.strip()}" if text.strip() else "No text found."
    except ImportError: return "pytesseract/pillow not installed. pip install pytesseract pillow"
    except Exception as e: return f"OCR error: {e}"

# ══ IMAGE TOOLS ═══════════════════════════════════════════════════════════════
def image_resize(filename, width, height, output=None):
    try:
        from PIL import Image
        img=Image.open(filename); img_resized=img.resize((int(width),int(height)))
        out=output or filename.replace(".",f"_{width}x{height}.")
        img_resized.save(out); return f"Resized to {width}x{height}: {out}"
    except ImportError: return "Pillow not installed."
    except Exception as e: return f"Image resize error: {e}"

def image_convert(filename, output_format="png"):
    try:
        from PIL import Image
        img=Image.open(filename)
        out=os.path.splitext(filename)[0]+"."+output_format
        img.save(out); return f"Converted to {output_format}: {out}"
    except ImportError: return "Pillow not installed."
    except Exception as e: return f"Convert error: {e}"

def extract_metadata(filename):
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img=Image.open(filename)
        exif=img._getexif()
        if not exif: return f"No EXIF metadata in {filename}"
        data={TAGS.get(k,k):str(v) for k,v in exif.items() if k in TAGS}
        lines=[f"  {k}: {v}" for k,v in list(data.items())[:20]]
        return "EXIF Metadata:\n"+"\n".join(lines)
    except ImportError: return "Pillow not installed."
    except Exception as e: return f"Metadata error: {e}"

# ══ FILE UTILITIES ════════════════════════════════════════════════════════════
def find_duplicates(path="."):
    hashes={}; duplicates=[]
    for root,_,files in os.walk(path):
        for f in files:
            full=os.path.join(root,f)
            try:
                h=_md5(full)
                if h in hashes: duplicates.append(f"  🔁 {full}\n     (duplicate of {hashes[h]})")
                else: hashes[h]=full
            except: pass
    if not duplicates: return "No duplicate files found."
    return f"Found {len(duplicates)} duplicate(s):\n"+"\n".join(duplicates[:20])

def batch_rename(path, pattern, replacement):
    try:
        files=os.listdir(path); count=0
        for f in files:
            if re.search(pattern,f):
                new=re.sub(pattern,replacement,f)
                os.rename(os.path.join(path,f),os.path.join(path,new)); count+=1
        return f"Renamed {count} files matching '{pattern}' → '{replacement}'"
    except Exception as e: return f"Batch rename error: {e}"

def organize_downloads(path=None):
    from config import DOWNLOAD_DIR
    path=path or DOWNLOAD_DIR
    os.makedirs(path, exist_ok=True)
    CATS={
        "Images":    [".jpg",".jpeg",".png",".gif",".webp",".bmp",".svg",".ico"],
        "Videos":    [".mp4",".avi",".mkv",".mov",".wmv",".flv"],
        "Audio":     [".mp3",".wav",".flac",".aac",".ogg"],
        "Documents": [".pdf",".doc",".docx",".txt",".odt",".rtf",".md"],
        "Spreadsheets":[".xls",".xlsx",".csv"],
        "Archives":  [".zip",".rar",".7z",".tar",".gz"],
        "Code":      [".py",".js",".html",".css",".java",".cpp",".c",".json"],
        "Executables":[".exe",".msi",".apk"],
    }
    moved=0
    for f in os.listdir(path):
        full=os.path.join(path,f)
        if os.path.isfile(full):
            ext=os.path.splitext(f)[1].lower()
            for cat,exts in CATS.items():
                if ext in exts:
                    dest_dir=os.path.join(path,cat)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(full,os.path.join(dest_dir,f)); moved+=1; break
    return f"Organized {moved} files in {path}"

def file_watch(filepath, callback_action=""):
    """One-shot: check if file changed since last check."""
    try:
        h=_md5(filepath)
        watch_file=f"data/.watch_{os.path.basename(filepath)}.hash"
        if os.path.exists(watch_file):
            with open(watch_file) as f: old=f.read().strip()
            with open(watch_file,"w") as f: f.write(h)
            return f"✅ Unchanged: {filepath}" if h==old else f"⚠️ CHANGED: {filepath}\nPrevious MD5: {old}\nCurrent MD5:  {h}"
        with open(watch_file,"w") as f: f.write(h)
        return f"Now watching: {filepath} (MD5: {h})"
    except Exception as e: return f"Watch error: {e}"
