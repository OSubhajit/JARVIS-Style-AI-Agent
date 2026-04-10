# logger.py
import logging, os
os.makedirs("logs", exist_ok=True)

class CF(logging.Formatter):
    C={"DEBUG":"\033[94m","INFO":"\033[92m","WARNING":"\033[93m","ERROR":"\033[91m","CRITICAL":"\033[95m"}
    R="\033[0m"
    def format(self,r): r.levelname=f"{self.C.get(r.levelname,'')}{r.levelname}{self.R}"; return super().format(r)

def get_logger(name="JARVIS"):
    logger=logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(logging.DEBUG)
    ch=logging.StreamHandler(); ch.setFormatter(CF("%(asctime)s [%(levelname)s] %(message)s","%H:%M:%S")); ch.setLevel(logging.INFO)
    fh=logging.FileHandler("logs/jarvis.log",encoding="utf-8"); fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")); fh.setLevel(logging.DEBUG)
    logger.addHandler(ch); logger.addHandler(fh)
    return logger

log=get_logger()
