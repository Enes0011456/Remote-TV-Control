"""
Log Yöneticisi - Tüm komut ve olayları dosyaya kaydeder
"""

import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR  = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "tv_log.txt")

os.makedirs(LOG_DIR, exist_ok=True)


def log(event_type, message, device=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_str = f"[{device}]" if device else "[GLOBAL]"
    line = f"[{now}] {device_str} [{event_type.upper()}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def get_logs(last_n=50):
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-last_n:]
    except Exception:
        return []


def clear_logs():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
        return True
    except Exception:
        return False
