"""
TV Komut Çalıştırıcı - Tüm TV operasyonları burada
"""

import time
import threading
from modules.logger import log
from modules.data_manager import (
    get_profiles, save_profile, delete_profile,
    get_macros, set_macro, delete_macro,
    get_triggers, add_trigger, delete_trigger,
    get_reminders, add_reminder, mark_reminder_done,
    get_parental, save_parental,
    get_settings, set_module, get_active_device,
    is_module_enabled, log_usage, get_usage,
    add_device, remove_device, set_active_device, get_devices
)
from modules.theme import G, C, Y, R, W, B, A

#  Yardımcı 

def ok(msg):  print(f"{G()}[+] {msg}{W()}")
def warn(msg): print(f"{Y()}[!] {msg}{W()}")
def err(msg):  print(f"{R()}[-] {msg}{W()}")
def info(msg): print(f"{C()}[*] {msg}{W()}")


# Medya Kontrol

def cmd_ses(conn, args):
    if not args or not args[0].isdigit():
        err("Kullanım: ses [0-100]"); return
    seviye = int(args[0])
    seviye = max(0, min(100, seviye))
    conn.media.set_volume(seviye)
    log("MEDIA", f"Ses {seviye} olarak ayarlandı", conn.name)
    ok(f"Ses %{seviye} olarak ayarlandı.")

def cmd_ses_artir(conn, args):
    try:
        current = conn.media.get_volume()["volume"]
        new_vol = min(100, current + 5)
        conn.media.set_volume(new_vol)
        ok(f"Ses artırıldı: %{new_vol}")
        log("MEDIA", f"Ses artırıldı -> {new_vol}", conn.name)
    except Exception as e:
        err(f"Ses artırılamadı: {e}")

def cmd_ses_azalt(conn, args):
    try:
        current = conn.media.get_volume()["volume"]
        new_vol = max(0, current - 5)
        conn.media.set_volume(new_vol)
        ok(f"Ses azaltıldı: %{new_vol}")
        log("MEDIA", f"Ses azaltıldı -> {new_vol}", conn.name)
    except Exception as e:
        err(f"Ses azaltılamadı: {e}")

def cmd_mute(conn, args):
    conn.media.mute(True)
    log("MEDIA", "Mute aktif edildi", conn.name)
    warn("TV sessize alındı.")

def cmd_unmute(conn, args):
    conn.media.mute(False)
    log("MEDIA", "Mute kaldırıldı", conn.name)
    ok("Ses açıldı.")

def cmd_play(conn, args):
    conn.media.play()
    log("MEDIA", "Play", conn.name)
    ok("Oynatılıyor.")

def cmd_pause(conn, args):
    conn.media.pause()
    log("MEDIA", "Pause", conn.name)
    ok("Duraklatıldı.")

def cmd_stop(conn, args):
    conn.media.stop()
    log("MEDIA", "Stop", conn.name)
    ok("Durduruldu.")

def cmd_ileri(conn, args):
    conn.media.fast_forward()
    log("MEDIA", "Fast Forward", conn.name)
    ok("İleri sarılıyor.")

def cmd_geri(conn, args):
    conn.media.rewind()
    log("MEDIA", "Rewind", conn.name)
    ok("Geri sarılıyor.")

def cmd_kanal(conn, args):
    if not args:
        err("Kullanım: kanal [numara]"); return
    try:
        no = int(args[0])
        conn.media.channel_up() if args[0] == "+" else None
        conn.media.channel_down() if args[0] == "-" else None
        if args[0] not in ["+", "-"]:
            warn(f"Kanal değiştirme komutu gönderildi: {no}")
        log("MEDIA", f"Kanal: {args[0]}", conn.name)
    except Exception as e:
        err(f"Kanal değiştirilemedi: {e}")


#  Uygulama Kontrolü 

def cmd_app(conn, args):
    if not args:
        err("Kullanım: app [isim]"); return
    hedef = " ".join(args).lower()

    # Ebeveyn kontrolü
    parental = get_parental()
    if parental.get("enabled"):
        locked = [x.lower() for x in parental.get("locked_apps", [])]
        if any(hedef in lk or lk in hedef for lk in locked):
            err(f"'{hedef}' uygulaması ebeveyn kontrolü tarafından kilitli!")
            log("PARENTAL", f"Engellenen uygulama açma girişimi: {hedef}", conn.name)
            return

    try:
        apps = conn.app_control.list_apps()
        for app in apps:
            if hedef in app.title.lower() or hedef in app.id.lower():
                conn.app_control.launch(app)
                log("APP", f"Uygulama açıldı: {app.title}", conn.name)
                ok(f"'{app.title}' açıldı.")
                return
        err(f"'{hedef}' uygulaması bulunamadı.")
    except Exception as e:
        err(f"Uygulama açılamadı: {e}")

def cmd_app_listesi(conn, args):
    try:
        apps = conn.app_control.list_apps()
        info("Yüklü uygulamalar:")
        for i, app in enumerate(apps, 1):
            print(f"  {C()}{i:2}. {W()}{app.title} {A()}({app.id}){W()}")
    except Exception as e:
        err(f"Uygulama listesi alınamadı: {e}")

def cmd_mesaj(conn, args):
    if not args:
        err("Kullanım: mesaj [metin]"); return
    metin = " ".join(args)
    conn.system.show_message(metin)
    log("SYSTEM", f"Mesaj gönderildi: {metin}", conn.name)
    ok(f"Ekranda mesaj gösterildi.")

def cmd_kapat(conn, args):
    warn("TV kapatılıyor...")
    log("SYSTEM", "TV kapatıldı", conn.name)
    conn.system.power_off()


#  Uzaktan Kumanda (Input) 

def cmd_tus(conn, args):
    if not conn.input_control:
        err("Input kontrolü bu TV'de desteklenmiyor."); return
    if not args:
        err("Kullanım: tus [yukari/asagi/sol/sag/ok/geri/home/menu]"); return
    tus_map = {
        "yukari": "UP", "asagi": "DOWN", "sol": "LEFT", "sag": "RIGHT",
        "ok": "ENTER", "geri": "BACK", "home": "HOME", "menu": "MENU",
        "kirmizi": "RED", "yesil": "GREEN", "sari": "YELLOW", "mavi": "BLUE"
    }
    tus = tus_map.get(args[0].lower())
    if not tus:
        err(f"Bilinmeyen tuş: {args[0]}. Seçenekler: {', '.join(tus_map.keys())}"); return
    try:
        conn.input_control.button(tus)
        ok(f"Tuş gönderildi: {tus}")
        log("INPUT", f"Tuş: {tus}", conn.name)
    except Exception as e:
        err(f"Tuş gönderilemedi: {e}")


# Profil Sistemi 

def cmd_profil(conn, args):
    if not args:
        # Profil listesi
        profiles = get_profiles()
        info("Kayıtlı Profiller:")
        for name, data in profiles.items():
            print(f"  {C()}{name:15}{W()} {data.get('description','')}")
        print(f"\n  {A()}Kullanım: profil [isim] | profil yeni [isim] | profil sil [isim]{W()}")
        return

    sub = args[0].lower()

    if sub == "yeni" and len(args) >= 2:
        profile_name = args[1].lower()
        info(f"'{profile_name}' profili oluşturuluyor...")
        print(f"  Ses seviyesi (0-100): ", end=""); vol = input().strip()
        print(f"  Açılacak uygulama (boş=yok): ", end=""); app = input().strip()
        print(f"  Açıklama: ", end=""); desc = input().strip()
        save_profile(profile_name, {
            "volume": int(vol) if vol.isdigit() else 20,
            "app": app or None,
            "description": desc
        })
        log("PROFILE", f"Profil oluşturuldu: {profile_name}", conn.name if conn else None)
        ok(f"'{profile_name}' profili kaydedildi.")
        return

    if sub == "sil" and len(args) >= 2:
        if delete_profile(args[1].lower()):
            ok(f"'{args[1]}' profili silindi.")
        else:
            err("Profil bulunamadı.")
        return

    # Profil uygula
    profiles = get_profiles()
    profile = profiles.get(sub)
    if not profile:
        err(f"'{sub}' profili bulunamadı."); return

    if conn:
        if "volume" in profile:
            conn.media.set_volume(profile["volume"])
        if profile.get("app"):
            cmd_app(conn, [profile["app"]])
        if profile.get("timer_minutes"):
            _start_timer(conn, profile["timer_minutes"], "kapat")
        log("PROFILE", f"Profil uygulandı: {sub}", conn.name)
    ok(f"'{sub}' profili uygulandı: {profile.get('description','')}")


# Zamanlayıcı 

_timers = []

def _start_timer(conn, minutes, action_cmd):
    def _run():
        time.sleep(minutes * 60)
        if action_cmd == "kapat":
            cmd_kapat(conn, [])
        elif action_cmd.startswith("mesaj "):
            cmd_mesaj(conn, action_cmd[6:].split())
        warn(f"Zamanlayıcı tetiklendi: {action_cmd}")
    t = threading.Thread(target=_run, daemon=True)
    _timers.append(t)
    t.start()

def cmd_timer(conn, args):
    if len(args) < 2:
        err("Kullanım: timer [dakika] [kapat|mesaj metin]"); return
    try:
        dakika = int(args[0])
    except ValueError:
        err("Geçersiz dakika."); return
    action = " ".join(args[1:])
    _start_timer(conn, dakika, action)
    ok(f"{dakika} dakika sonra '{action}' çalışacak.")
    log("TIMER", f"Timer kuruldu: {dakika}dk -> {action}", conn.name if conn else None)


#  Tetikleyici Sistemi 

def cmd_tetik(conn, args):
    if not args:
        triggers = get_triggers()
        if not triggers:
            info("Kayıtlı tetikleyici yok.")
            return
        info("Tetikleyiciler:")
        for t in triggers:
            durum = f"{G()}[AKTİF]{W()}" if t.get("enabled") else f"{R()}[PASİF]{W()}"
            print(f"  {C()}#{t['id']}{W()} {durum} Koşul: {t['condition_type']}={t['condition_value']} -> {t['action']}")
        return

    sub = args[0].lower()
    if sub == "ekle" and len(args) >= 4:
        # tetik ekle [tip] [deger] [aksiyon]
        add_trigger(args[1], args[2], " ".join(args[3:]))
        ok("Tetikleyici eklendi.")
    elif sub == "sil" and len(args) >= 2:
        delete_trigger(int(args[1]))
        ok("Tetikleyici silindi.")
    else:
        info("Kullanım: tetik | tetik ekle [app/ses] [deger] [aksiyon] | tetik sil [id]")


# Makro & Kısayol 

def cmd_makro(conn, args):
    macros = get_macros()
    if not args:
        info("Kayıtlı Makrolar:")
        for k, v in macros.items():
            print(f"  {C()}{k:10}{W()} -> {v}")
        print(f"\n  {A()}Kullanım: makro ekle [kısayol] [komut] | makro sil [kısayol]{W()}")
        return
    sub = args[0].lower()
    if sub == "ekle" and len(args) >= 3:
        set_macro(args[1], " ".join(args[2:]))
        ok(f"'{args[1]}' makrosu eklendi.")
    elif sub == "sil" and len(args) >= 2:
        if delete_macro(args[1]):
            ok(f"'{args[1]}' makrosu silindi.")
        else:
            err("Makro bulunamadı.")
    else:
        err("Kullanım: makro ekle [kısayol] [komut] | makro sil [kısayol]")

def resolve_macro(cmd_str):
    """Tek kelime girdisini makro olarak çöz"""
    macros = get_macros()
    return macros.get(cmd_str)


# Not & Hatırlatıcı 

def cmd_hatirlatici(conn, args):
    reminders = get_reminders()
    if not args:
        info("Hatırlatıcılar:")
        pending = [r for r in reminders if not r.get("done")]
        if not pending:
            info("Bekleyen hatırlatıcı yok.")
            return
        for r in pending:
            print(f"  {C()}#{r['id']}{W()} [{r['time']}] {r['message']} ({r.get('device','all')})")
        return

    sub = args[0].lower()
    if sub == "ekle" and len(args) >= 3:
        # hatirlatici ekle [HH:MM] [mesaj...]
        add_reminder(" ".join(args[2:]), args[1])
        ok(f"Hatırlatıcı eklendi: {args[1]} - {' '.join(args[2:])}")
    elif sub == "sil" and len(args) >= 2:
        mark_reminder_done(int(args[1]))
        ok("Hatırlatıcı tamamlandı olarak işaretlendi.")
    else:
        err("Kullanım: hatirlatici | hatirlatici ekle [HH:MM] [mesaj] | hatirlatici sil [id]")


# Ebeveyn Kontrolü 

def cmd_ebeveyn(conn, args):
    p = get_parental()
    if not args:
        durum = f"{G()}AKTİF{W()}" if p.get("enabled") else f"{R()}PASİF{W()}"
        info(f"Ebeveyn Kontrolü: {durum}")
        print(f"  Kilitli uygulamalar: {', '.join(p.get('locked_apps', [])) or 'Yok'}")
        print(f"  Günlük limit: {p.get('daily_limit_minutes', 0)} dakika")
        print(f"  Engelli saatler: {', '.join(p.get('blocked_hours', [])) or 'Yok'}")
        print(f"\n  {A()}Komutlar: ebeveyn aç|kapat|kilitle [app]|serbest [app]|limit [dk]|saat [HH-HH]{W()}")
        return

    sub = args[0].lower()
    if sub == "aç":
        p["enabled"] = True
        save_parental(p); ok("Ebeveyn kontrolü aktifleştirildi.")
    elif sub == "kapat":
        p["enabled"] = False
        save_parental(p); ok("Ebeveyn kontrolü devre dışı.")
    elif sub == "kilitle" and len(args) >= 2:
        app = args[1].lower()
        if app not in p["locked_apps"]:
            p["locked_apps"].append(app)
        save_parental(p); ok(f"'{app}' kilitlendi.")
    elif sub == "serbest" and len(args) >= 2:
        app = args[1].lower()
        p["locked_apps"] = [x for x in p["locked_apps"] if x != app]
        save_parental(p); ok(f"'{app}' kilidi kaldırıldı.")
    elif sub == "limit" and len(args) >= 2:
        p["daily_limit_minutes"] = int(args[1])
        save_parental(p); ok(f"Günlük limit {args[1]} dakika olarak ayarlandı.")
    elif sub == "saat" and len(args) >= 2:
        p["blocked_hours"].append(args[1])
        save_parental(p); ok(f"Engelli saat aralığı eklendi: {args[1]}")
    else:
        err("Bilinmeyen ebeveyn komutu.")


# Cihaz Yönetimi 

def cmd_cihaz(args):
    devices = get_devices()
    if not args:
        info("Kayıtlı Cihazlar:")
        active = devices.get("active")
        for name, info_d in devices.get("list", {}).items():
            marker = f"{G()}[AKTİF]{W()}" if name == active else "       "
            print(f"  {marker} {C()}{name:15}{W()} {info_d['ip']}")
        print(f"\n  {A()}Komutlar: cihaz ekle [ad] [ip] | cihaz sil [ad] | cihaz sec [ad] | cihaz listesi{W()}")
        return

    sub = args[0].lower()
    if sub == "ekle" and len(args) >= 3:
        add_device(args[1], args[2])
        ok(f"'{args[1]}' cihazı eklendi: {args[2]}")
        log("DEVICE", f"Cihaz eklendi: {args[1]} @ {args[2]}")
    elif sub == "sil" and len(args) >= 2:
        if remove_device(args[1]):
            ok(f"'{args[1]}' silindi.")
        else:
            err("Cihaz bulunamadı.")
    elif sub in ["sec", "seç"] and len(args) >= 2:
        if set_active_device(args[1]):
            ok(f"Aktif cihaz: '{args[1]}'")
            log("DEVICE", f"Aktif cihaz değişti: {args[1]}")
        else:
            err("Cihaz bulunamadı.")
    elif sub == "listesi":
        cmd_cihaz([])
    else:
        err("Kullanım: cihaz [ekle/sil/sec/listesi]")


# Ekstra Ayarlar (Modül Aç/Kapa) 

def cmd_ayarlar(args):
    settings = get_settings()
    modules = settings.get("modules", {})

    if not args:
        info("Ekstra Ayarlar (Modüller):")
        print(f"\n  {'Modül':<25} {'Durum':<12} {'Kapsam'}")
        print(f"  {'─'*50}")
        for mod, cfg in modules.items():
            durum = f"{G()}[AKTİF ✓]{W()}" if cfg.get("enabled") else f"{R()}[PASİF ✗]{W()}"
            scope = cfg.get("scope", "all")
            scope_str = f"{Y()}Tüm Cihazlar{W()}" if scope == "all" else f"{C()}{scope}{W()}"
            print(f"  {C()}{mod:<25}{W()} {durum:<20} {scope_str}")
        print(f"\n  {A()}Kullanım: ayarlar [modül] aç|kapat [all|cihaz_adi]{W()}")
        return

    mod_name = args[0].lower()
    if mod_name not in modules:
        err(f"Modül bulunamadı: {mod_name}"); return

    if len(args) >= 2:
        action = args[1].lower()
        scope = args[2] if len(args) >= 3 else "all"
        enabled = action in ["aç", "ac", "on", "enable"]
        set_module(mod_name, enabled, scope)
        durum = "aktifleştirildi" if enabled else "devre dışı bırakıldı"
        ok(f"'{mod_name}' modülü {durum} (kapsam: {scope})")
        log("SETTINGS", f"Modül {mod_name}: {durum}, kapsam={scope}")


#  İstatistik

def cmd_istatistik(conn, args):
    usage = get_usage()
    if not usage:
        info("Henüz kullanım verisi yok."); return
    info("Kullanım İstatistikleri:")
    for device, days in usage.items():
        total = sum(days.values())
        print(f"\n  {C()}{device}{W()} - Toplam: {total} dakika")
        for date, mins in sorted(days.items())[-7:]:
            bar = "█" * (mins // 10)
            print(f"    {date}: {bar} {mins}dk")


# Yardım 

def cmd_yardim():
    print(f"""
{B()}╔══ KOMUT REHBERİ ══════════════════════════════════════════╗{W()}

{C()}[ MEDYA ]{W()}
  ses [0-100]       Ses ayarla          ses+ / ses-      Artır/Azalt
  mute / unmute     Sessize al/aç       play / pause     Oynat/Durdur
  stop / ileri / geri                   kanal [+/-/no]

{C()}[ UYGULAMA ]{W()}
  app [isim]        Uygulama aç         applist          Tüm uygulamalar
  mesaj [metin]     Ekranda mesaj göster

{C()}[ KUMANDA ]{W()}
  tus [yukari/asagi/sol/sag/ok/geri/home/menu]

{C()}[ PROFİL ]{W()}
  profil            Profil listesi      profil [isim]    Profil uygula
  profil yeni [ad]  Yeni profil         profil sil [ad]  Sil

{C()}[ ZAMANLAYICI ]{W()}
  timer [dk] kapat|mesaj [metin]

{C()}[ MAKRO ]{W()}
  makro             Makro listesi       makro ekle [k] [komut]
  makro sil [k]     Makro sil

{C()}[ TETİKLEYİCİ ]{W()}
  tetik             Listele             tetik ekle [tip] [deger] [aksiyon]
  tetik sil [id]

{C()}[ HATIRLATICI ]{W()}
  hatirlatici       Listele             hatirlatici ekle [HH:MM] [mesaj]

{C()}[ EBEVEYN KONTROLÜ ]{W()}
  ebeveyn           Durum               ebeveyn aç|kapat
  ebeveyn kilitle|serbest [app]         ebeveyn limit [dk]

{C()}[ CİHAZ YÖNETİMİ ]{W()}
  cihaz             Listele             cihaz ekle [ad] [ip]
  cihaz sil [ad]    cihaz sec [ad]      baglan

{C()}[ SİSTEM ]{W()}
  ayarlar           Modül aç/kapa       istatistik       Kullanım
  log               Son loglar          tema [isim]      Tema değiştir
  gui               GUI paneli aç       clear            Ekranı temizle
  kapat / kill      TV kapat            exit             Çıkış

{C()}[ TEMALAR ]{W()}
  matrix | kirmizi | mavi | mor | beyaz
{B()}╚═══════════════════════════════════════════════════════════╝{W()}
""")
