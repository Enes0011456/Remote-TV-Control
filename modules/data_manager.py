"""
Veri Yöneticisi - Tüm JSON dosyalarını okur/yazar
"""

import json,os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Dosya yolları
DEVICES_FILE    = os.path.join(DATA_DIR, "devices.json")
SETTINGS_FILE   = os.path.join(DATA_DIR, "settings.json")
PROFILES_FILE   = os.path.join(DATA_DIR, "profiles.json")
MACROS_FILE     = os.path.join(DATA_DIR, "macros.json")
TRIGGERS_FILE   = os.path.join(DATA_DIR, "triggers.json")
REMINDERS_FILE  = os.path.join(DATA_DIR, "reminders.json")
PARENTAL_FILE   = os.path.join(DATA_DIR, "parental.json")
SHORTCUTS_FILE  = os.path.join(DATA_DIR, "shortcuts.json")
USAGE_FILE      = os.path.join(DATA_DIR, "usage.json")

os.makedirs(DATA_DIR, exist_ok=True)

# Varsayılan Veriler

DEFAULTS = {
    DEVICES_FILE: {
        "active": None,
        "list": {}
    },
    SETTINGS_FILE: {
        "theme": "matrix",
        "modules": {
            "media_control":      {"enabled": True,  "scope": "all"},
            "monitoring":         {"enabled": True,  "scope": "all"},
            "automation":         {"enabled": True,  "scope": "all"},
            "profiles":           {"enabled": True,  "scope": "all"},
            "parental":           {"enabled": False, "scope": "all"},
            "remote_control":     {"enabled": True,  "scope": "all"},
            "network_scanner":    {"enabled": True,  "scope": "all"},
            "triggers":           {"enabled": True,  "scope": "all"},
            "macros":             {"enabled": True,  "scope": "all"},
            "remote_access":      {"enabled": False, "scope": "all"},
            "reminders":          {"enabled": True,  "scope": "all"},
            "security":           {"enabled": True,  "scope": "all"},
        }
    },
    PROFILES_FILE: {
        "sinema": {
            "volume": 20,
            "app": "netflix",
            "description": "Sinema Modu - Düşük ışık, yüksek ses kalitesi"
        },
        "oyun": {
            "volume": 40,
            "app": None,
            "description": "Oyun Modu - Düşük gecikme ayarları"
        },
        "uyku": {
            "volume": 10,
            "app": None,
            "timer_minutes": 30,
            "description": "Uyku Modu - 30dk sonra kapanır"
        }
    },
    MACROS_FILE: {
        "n": "app netflix",
        "y": "app youtube",
        "q": "kapat",
        "m": "mute"
    },
    TRIGGERS_FILE: [],
    REMINDERS_FILE: [],
    PARENTAL_FILE: {
        "enabled": False,
        "locked_apps": [],
        "blocked_hours": [],
        "daily_limit_minutes": 0,
        "pin": "1234"
    },
    SHORTCUTS_FILE: {},
    USAGE_FILE: {}
}


def _load(path):
    if not os.path.exists(path):
        _save(path, DEFAULTS.get(path, {}))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULTS.get(path, {})


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Cihaz İşlemleri

def get_devices():
    return _load(DEVICES_FILE)

def save_devices(data):
    _save(DEVICES_FILE, data)

def add_device(name, ip, key=""):
    d = get_devices()
    d["list"][name] = {"ip": ip, "key": key, "added": datetime.now().isoformat()}
    if not d["active"]:
        d["active"] = name
    save_devices(d)

def remove_device(name):
    d = get_devices()
    if name in d["list"]:
        del d["list"][name]
        if d["active"] == name:
            d["active"] = next(iter(d["list"]), None)
        save_devices(d)
        return True
    return False

def set_active_device(name):
    d = get_devices()
    if name in d["list"]:
        d["active"] = name
        save_devices(d)
        return True
    return False

def get_active_device():
    d = get_devices()
    name = d.get("active")
    if name and name in d["list"]:
        return name, d["list"][name]
    return None, None

def update_device_key(name, key):
    d = get_devices()
    if name in d["list"]:
        d["list"][name]["key"] = key
        save_devices(d)


# Ayar İşlemleri 

def get_settings():
    return _load(SETTINGS_FILE)

def save_settings(data):
    _save(SETTINGS_FILE, data)

def is_module_enabled(module_name, device_name=None):
    s = get_settings()
    m = s.get("modules", {}).get(module_name, {})
    if not m.get("enabled", True):
        return False
    scope = m.get("scope", "all")
    if scope == "all":
        return True
    # scope = liste halinde cihaz adları
    if isinstance(scope, list) and device_name:
        return device_name in scope
    return True

def set_module(module_name, enabled, scope="all"):
    s = get_settings()
    if "modules" not in s:
        s["modules"] = {}
    s["modules"][module_name] = {"enabled": enabled, "scope": scope}
    save_settings(s)

def get_theme():
    return get_settings().get("theme", "matrix")

def set_theme(theme):
    s = get_settings()
    s["theme"] = theme
    save_settings(s)


#  Profil İşlemleri

def get_profiles():
    return _load(PROFILES_FILE)

def save_profile(name, data):
    p = get_profiles()
    p[name] = data
    _save(PROFILES_FILE, p)

def delete_profile(name):
    p = get_profiles()
    if name in p:
        del p[name]
        _save(PROFILES_FILE, p)
        return True
    return False


# Makro İşlemleri

def get_macros():
    return _load(MACROS_FILE)

def set_macro(key, command):
    m = get_macros()
    m[key] = command
    _save(MACROS_FILE, m)

def delete_macro(key):
    m = get_macros()
    if key in m:
        del m[key]
        _save(MACROS_FILE, m)
        return True
    return False


# Tetikleyici İşlemleri

def get_triggers():
    return _load(TRIGGERS_FILE)

def add_trigger(condition_type, condition_value, action, device="all"):
    t = get_triggers()
    t.append({
        "id": len(t) + 1,
        "condition_type": condition_type,
        "condition_value": condition_value,
        "action": action,
        "device": device,
        "enabled": True,
        "created": datetime.now().isoformat()
    })
    _save(TRIGGERS_FILE, t)

def delete_trigger(trigger_id):
    t = get_triggers()
    t = [x for x in t if x.get("id") != trigger_id]
    _save(TRIGGERS_FILE, t)


# Hatırlatıcı İşlemleri

def get_reminders():
    return _load(REMINDERS_FILE)

def add_reminder(message, time_str, device="all"):
    r = get_reminders()
    r.append({
        "id": len(r) + 1,
        "message": message,
        "time": time_str,
        "device": device,
        "done": False,
        "created": datetime.now().isoformat()
    })
    _save(REMINDERS_FILE, r)

def mark_reminder_done(reminder_id):
    r = get_reminders()
    for item in r:
        if item.get("id") == reminder_id:
            item["done"] = True
    _save(REMINDERS_FILE, r)


# Ebeveyn Kontrolü 

def get_parental():
    return _load(PARENTAL_FILE)

def save_parental(data):
    _save(PARENTAL_FILE, data)


# Kullanım İstatistikleri 

def log_usage(device_name, minutes=0):
    u = _load(USAGE_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    if device_name not in u:
        u[device_name] = {}
    u[device_name][today] = u[device_name].get(today, 0) + minutes
    _save(USAGE_FILE, u)

def get_usage(device_name=None):
    u = _load(USAGE_FILE)
    if device_name:
        return u.get(device_name, {})
    return u
