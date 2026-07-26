"""
Tema Sistemi - Terminal renk temaları
"""

THEMES = {
    "matrix": {
        "primary":   "\033[92m",   # Parlak yeşil
        "secondary": "\033[96m",   # Cyan
        "warning":   "\033[93m",   # Sarı
        "error":     "\033[91m",   # Kırmızı
        "bold":      "\033[1m",
        "reset":     "\033[0m",
        "accent":    "\033[32m",   # Koyu yeşil
    },
    "kirmizi": {
        "primary":   "\033[91m",
        "secondary": "\033[95m",
        "warning":   "\033[93m",
        "error":     "\033[31m",
        "bold":      "\033[1m",
        "reset":     "\033[0m",
        "accent":    "\033[35m",
    },
    "mavi": {
        "primary":   "\033[94m",
        "secondary": "\033[96m",
        "warning":   "\033[93m",
        "error":     "\033[91m",
        "bold":      "\033[1m",
        "reset":     "\033[0m",
        "accent":    "\033[34m",
    },
    "mor": {
        "primary":   "\033[95m",
        "secondary": "\033[94m",
        "warning":   "\033[93m",
        "error":     "\033[91m",
        "bold":      "\033[1m",
        "reset":     "\033[0m",
        "accent":    "\033[35m",
    },
    "beyaz": {
        "primary":   "\033[97m",
        "secondary": "\033[37m",
        "warning":   "\033[93m",
        "error":     "\033[91m",
        "bold":      "\033[1m",
        "reset":     "\033[0m",
        "accent":    "\033[36m",
    },
}

_current_theme = "matrix"

def set_theme(name):
    global _current_theme
    if name in THEMES:
        _current_theme = name
        return True
    return False

def t(key):
    """Mevcut temadan renk kodu döndür"""
    return THEMES.get(_current_theme, THEMES["matrix"]).get(key, "")

# Kısayol fonksiyonlar
def G(): return t("primary")
def C(): return t("secondary")
def Y(): return t("warning")
def R(): return t("error")
def W(): return t("reset")
def B(): return t("bold")
def A(): return t("accent")

BANNER = r"""
 ██████╗  ▓█████  ███▄ ▄███▄   ▒█████  ▄▄▄█████▓▓█████     ▄████▄   ▒█████   ███▄    █ ▄▄▄█████▓ ██▀███   ▒█████   ██▓    
▒██  ██▒  ▓█   ▀ ▓██▒▀█▀ ██▒ ▒██▒  ██▒▓  ██▒ ▓▒▓█   ▀    ▒██▀ ▀█  ▒██▒  ██▒ ██ ▀█   █ ▓  ██▒ ▓▒▓██ ▒ ██▒▒██▒  ██▒▓██▒    
░██████▒▒ ▒███   ▓██    ▓██░ ▒██░  ██▒▒ ▓██░ ▒░▒███      ▒▓█    ▄ ▒██░  ██▒▓██  ▀█ ██▒▒ ▓██░ ▒░▓██ ░▄█ ▒▒██░  ██▒▒██░    
▓██  ██▒░ ▒▓█  ▄ ▒██    ▒██  ▒██   ██░░ ▓██▓ ░ ▒▓█  ▄    ▒▓▓▄ ▄██▒▒██   ██░▓██▒  ▐▌██▒░ ▓██▓ ░ ▒██▀▀█▄  ▒██   ██░▒██░    
▒██  ██▒▒ ░▒████▒▒██▒   ░██▒ ░ ████▓▒░  ▒██▒ ░ ░▒████▒   ▒ ▓███▀ ░░ ████▓▒░▒██░   ▓██░  ▒██▒ ░ ░██▓ ▒██▒░ ████▓▒░░██████▒
░▓▓  ▓▒▒░ ░░ ▒░ ░░ ▒░   ░  ░ ░ ▒░▒░▒░   ▒ ░░   ░░ ▒░ ░   ░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒   ▒ ░░   ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░▓  ░
 ░▒   ░░   ░ ░  ░░  ░      ░   ░ ▒ ▒░     ░     ░ ░  ░     ░  ▒     ░ ▒ ▒░ ░ ░░   ░ ▒░    ░      ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░ ▒  ░
 ░    ░      ░   ░      ░    ░ ░ ░ ▒    ░         ░      ░          ░ ░ ▒     ░   ░ ░   ░        ░░   ░ ░ ░ ░ ▒    ░ ░   
 ░           ░  ░       ░        ░ ░              ░  ░   ░ ░            ░ ░           ░              ░         ░      ░  ░
                                                         ░                                                           
"""

def print_banner(device_name=None, device_ip=None, version="2.0.0"):
    import os
    os.system('clear')
    print(f"{R()}{BANNER}{W()}")
    print(f"{C()}/* ++{'─'*108}++ */")
    print(f"/* || {G()}Tool Name: {W()}Remote TV Control (v{version}){' '*(91-len(version))}{C()}|| */")
    status_line = f"Bypass System Active {G()}[AUTHORIZED TOKEN INJECTED]{W()}"
    print(f"/* || {G()}Status:    {Y()}{status_line}{' '*54}{C()}|| */")
    ip_show = device_ip or "N/A"
    name_show = device_name or "Bağlı Değil"
    line = f"{name_show} @ {ip_show}"
    

    #-----------------------------------------------------------------------------------------------------
    ####Bundan pek emin değilim çünkü jsonda ipyi tutuyor ve dısarda ip belli olsun istemiyorum
    #O yüzden burası iptal
    #print(f"/* || {G()}Target:    {W()}{line}{' '*(99-len(line))}{C()}|| */")
    #-----------------------------------------------------------------------------------------------------
    
    print(f"/* ++{'─'*108}++ */{W()}\n")
