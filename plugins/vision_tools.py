# plugins/vision_tools.py — Computer Vision: Webcam, Motion, Face, OCR Screen, QR

import os
from datetime import datetime
from config import CAMERA_INDEX, SCREENSHOT_DIR, MOTION_SENSITIVITY
from logger import log

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def _cv():
    try: import cv2; return cv2
    except ImportError: return None

def _np():
    try: import numpy as np; return np
    except ImportError: return None

# ══ WEBCAM ════════════════════════════════════════════════════════════════════
def webcam_snapshot(filename=None):
    cv2=_cv()
    if not cv2: return "opencv-python not installed. pip install opencv-python"
    try:
        cap=cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened(): return "Cannot open camera."
        ret,frame=cap.read(); cap.release()
        if not ret: return "Failed to capture frame."
        fn=filename or f"{SCREENSHOT_DIR}/webcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(fn,frame); return f"Webcam snapshot: {fn}"
    except Exception as e: return f"Webcam error: {e}"

def motion_detect(duration=10, sensitivity=MOTION_SENSITIVITY):
    cv2=_cv(); np=_np()
    if not cv2: return "opencv-python not installed."
    try:
        import time
        cap=cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened(): return "Cannot open camera."
        _,prev=cap.read(); detected=0; start=time.time()
        while time.time()-start<duration:
            _,curr=cap.read()
            if cv2 and np:
                diff=cv2.absdiff(prev,curr)
                gray=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
                _,thresh=cv2.threshold(gray,sensitivity,255,cv2.THRESH_BINARY)
                if np.sum(thresh)>50000:
                    detected+=1
                    fn=f"{SCREENSHOT_DIR}/motion_{datetime.now().strftime('%H%M%S')}.jpg"
                    cv2.imwrite(fn,curr)
            prev=curr
        cap.release()
        return f"Motion detected {detected} times in {duration}s" if detected>0 else f"No motion detected in {duration}s"
    except Exception as e: return f"Motion error: {e}"

def face_recognize():
    cv2=_cv()
    if not cv2: return "opencv-python not installed."
    try:
        face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
        cap=cv2.VideoCapture(CAMERA_INDEX)
        _,frame=cap.read(); cap.release()
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces=face_cascade.detectMultiScale(gray,1.1,4)
        if len(faces)==0: return "No faces detected."
        fn=f"{SCREENSHOT_DIR}/faces_{datetime.now().strftime('%H%M%S')}.jpg"
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imwrite(fn,frame)
        return f"Detected {len(faces)} face(s). Saved: {fn}"
    except Exception as e: return f"Face detection error: {e}"

def scan_qr_webcam():
    cv2=_cv()
    if not cv2: return "opencv-python not installed."
    try:
        cap=cv2.VideoCapture(CAMERA_INDEX)
        detector=cv2.QRCodeDetector()
        import time; start=time.time(); result=""
        while time.time()-start<10:
            _,frame=cap.read()
            data,_,_=detector.detectAndDecode(frame)
            if data: result=data; break
        cap.release()
        return f"QR Code: {result}" if result else "No QR code detected in 10s."
    except Exception as e: return f"QR scan error: {e}"

def object_detect(filename=None):
    """Detect objects using YOLO or fallback to basic detection."""
    cv2=_cv()
    if not cv2: return "opencv-python not installed."
    if filename:
        try:
            img=cv2.imread(filename)
            if img is None: return f"Cannot open image: {filename}"
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
            faces=face_cascade.detectMultiScale(gray,1.1,4)
            return f"Basic detection in {filename}:\n  Faces found: {len(faces)}"
        except Exception as e: return f"Object detect error: {e}"
    return webcam_snapshot()

def color_picker(x=None, y=None):
    """Pick color from screen at coordinates or center."""
    try:
        import pyautogui; from PIL import ImageColor
        screenshot=pyautogui.screenshot()
        if x is None or y is None:
            import pyautogui as pg
            x,y=pg.size(); x,y=x//2,y//2
        pixel=screenshot.getpixel((int(x),int(y)))
        r,g,b=pixel[:3]
        hex_color=f"#{r:02x}{g:02x}{b:02x}".upper()
        return f"Color at ({x},{y}):\n  RGB: ({r}, {g}, {b})\n  HEX: {hex_color}"
    except ImportError: return "pyautogui/pillow not installed."
    except Exception as e: return f"Color picker error: {e}"

def read_screen():
    """OCR the current screen."""
    try:
        import pyautogui; import pytesseract; from PIL import Image
        screenshot=pyautogui.screenshot()
        text=pytesseract.image_to_string(screenshot)
        lines=[l.strip() for l in text.splitlines() if len(l.strip())>3]
        return "Screen text:\n"+"\n".join(lines[:40]) if lines else "No readable text on screen."
    except ImportError: return "pyautogui/pytesseract not installed."
    except Exception as e: return f"Screen read error: {e}"

def intruder_alert(duration=30, speak_fn=None):
    """Monitor webcam for motion and alert."""
    cv2=_cv(); np=_np()
    if not cv2: return "opencv-python not installed."
    def _watch():
        cap=cv2.VideoCapture(CAMERA_INDEX)
        _,prev=cap.read()
        import time; start=time.time()
        while time.time()-start<duration:
            _,curr=cap.read()
            diff=cv2.absdiff(prev,curr)
            gray=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
            _,thresh=cv2.threshold(gray,MOTION_SENSITIVITY,255,cv2.THRESH_BINARY)
            if np.sum(thresh)>80000:
                fn=f"{SCREENSHOT_DIR}/intruder_{datetime.now().strftime('%H%M%S')}.jpg"
                cv2.imwrite(fn,curr)
                alert=f"⚠️ INTRUDER DETECTED! Saved: {fn}"
                print(f"\n\033[91m[JARVIS 🚨] {alert}\033[0m")
                if speak_fn: speak_fn("Intruder detected! Motion alert triggered!")
            prev=curr; time.sleep(0.5)
        cap.release()
    import threading
    threading.Thread(target=_watch,daemon=True).start()
    return f"🔍 Intruder detection active for {duration}s. Camera is watching..."

def take_screenshot(filename=None):
    try:
        import pyautogui
        os.makedirs(SCREENSHOT_DIR,exist_ok=True)
        fn=filename or f"{SCREENSHOT_DIR}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(fn); return f"Screenshot: {fn}"
    except ImportError: return "pyautogui not installed."
    except Exception as e: return f"Screenshot error: {e}"

def screen_record(duration=10, filename=None):
    cv2=_cv()
    if not cv2: return "opencv-python not installed."
    try:
        import pyautogui, numpy as np
        from config import RECORDING_DIR
        os.makedirs(RECORDING_DIR,exist_ok=True)
        fn=filename or f"{RECORDING_DIR}/recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        size=pyautogui.size()
        out=cv2.VideoWriter(fn,cv2.VideoWriter_fourcc(*"XVID"),10.0,(size.width,size.height))
        import time; start=time.time()
        while time.time()-start<duration:
            img=pyautogui.screenshot()
            frame=np.array(img); frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            out.write(frame)
        out.release(); return f"Recorded {duration}s → {fn}"
    except Exception as e: return f"Recording error: {e}"
