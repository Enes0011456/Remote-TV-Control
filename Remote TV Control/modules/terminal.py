"""
Terminal Uygulaması - Ana komut döngüsü
"""

import asyncio,os,sys

from modules.theme import (
    G, C, Y, R, W, B, A, set_theme, print_banner, THEMES
)
from modules.data_manager import (
    get_active_device, get_theme, set_theme as save_theme,
    get_settings, is_module_enabled
)
from modules.connection import connection_manager
from modules.commands import (
    cmd_ses, cmd_ses_artir, cmd_ses_azalt,
    cmd_mute, cmd_unmute, cmd_play, cmd_pause,
    cmd_stop, cmd_ileri, cmd_geri, cmd_kanal,
    cmd_app, cmd_app_listesi, cmd_mesaj, cmd_kapat,
    cmd_tus, cmd_profil, cmd_timer, cmd_tetik,
    cmd_makro, cmd_hatirlatici, cmd_ebeveyn,
    cmd_cihaz, cmd_ayarlar, cmd_istatistik,
    cmd_yardim, resolve_macro,
)
from modules.logger import log, get_logs, clear_logs


class TerminalApp:
    def __init__(self):
        self.conn = None
        self.running = True
        # Kaydedilmiş temayı yükle
        saved_theme = get_theme()
        set_theme(saved_theme)

    # Bağlantı 

    def _try_connect(self):
        name, info = get_active_device()
        if not name:
            return
        print(f"{Y()}[~] Kayıtlı cihaza bağlanılıyor: {name} @ {info.get('ip','?')}...{W()}")
        success, result = connection_manager.connect_active()
        if success:
            self.conn = result
            print(f"{G()}[+] Bağlantı başarılı: {name}{W()}\n")
            log("CONNECTION", f"Bağlantı kuruldu: {name}", name)
        else:
            print(f"{R()}[-] Bağlantı kurulamadı. 'baglan' komutuyla tekrar deneyin.{W()}\n")

    def _cmd_baglan(self, args):
        if args:
            # baglan [ad] [ip]
            if len(args) >= 2:
                from modules.data_manager import add_device
                add_device(args[0], args[1])
                print(f"{G()}[+] Cihaz eklendi: {args[0]} @ {args[1]}{W()}")
            # Belirtilen cihazı seç ve bağlan
            from modules.data_manager import set_active_device
            set_active_device(args[0])

        name, info = get_active_device()
        if not name:
            print(f"{R()}[-] Önce cihaz ekleyin: cihaz ekle [ad] [ip]{W()}")
            return

        print(f"{Y()}[~] Bağlanılıyor: {name} @ {info.get('ip','?')}...{W()}")
        print(f"{Y()}[~] TV'nizde 'İzin Ver' onayı çıkacak, onaylayın.{W()}")
        success, result = connection_manager.connect_active()
        if success:
            self.conn = result
            print(f"{G()}[+] Bağlantı başarılı!{W()}")
            log("CONNECTION", f"Bağlantı kuruldu: {name}", name)
            # Banner yenile
            print_banner(name, info.get("ip"), "2.0.0")
        else:
            print(f"{R()}[-] Bağlantı başarısız. TV açık ve aynı ağda mı?{W()}")

    # Komut Çözümleyici 

    def _dispatch(self, raw: str):
        raw = raw.strip()
        if not raw:
            return

        # Önce makro kontrolü
        macro_result = resolve_macro(raw.split()[0])
        if macro_result and raw == raw.split()[0]:
            raw = macro_result

        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        # Bağlantı gerektirmeyen komutlar
        no_conn_cmds = {
            "exit", "quit", "çıkış", "cikis",
            "cihaz", "baglan", "bağlan",
            "ayarlar", "yardim", "yardım", "help",
            "tema", "log", "logtemizle",
            "istatistik", "profil", "makro",
            "hatirlatici", "hatırlatıcı",
            "ebeveyn", "tetik", "clear", "cls",
        }

        # Bağlantı kontrolü
        if cmd not in no_conn_cmds and not self.conn:
            print(f"{Y()}[!] TV bağlı değil. 'baglan' komutuyla bağlanın.{W()}")
            return

        # Sistem 
        if cmd in ["exit", "quit", "çıkış", "cikis"]:
            print(f"{Y()}[~] Çıkılıyor...{W()}")
            connection_manager.disconnect_all()
            self.running = False

        elif cmd in ["clear", "cls"]:
            name, info = get_active_device()
            print_banner(
                name,
                info.get("ip") if info else None,
                "2.0.0"
            )

        elif cmd in ["yardim", "yardım", "help", "?"]:
            cmd_yardim()

        elif cmd == "log":
            lines = get_logs(int(args[0]) if args else 30)
            if lines:
                print(f"{C()}{'─'*60}{W()}")
                for line in lines:
                    print(line, end="")
                print(f"{C()}{'─'*60}{W()}")
            else:
                print(f"{Y()}[!] Log dosyası boş.{W()}")

        elif cmd == "logtemizle":
            clear_logs()
            print(f"{G()}[+] Loglar temizlendi.{W()}")

        elif cmd == "tema":
            if not args:
                print(f"{C()}[*] Mevcut tema: {get_theme()}")
                print(f"    Temalar: {', '.join(THEMES.keys())}{W()}")
            elif args[0] in THEMES:
                set_theme(args[0])
                save_theme(args[0])
                print(f"{G()}[+] Tema değiştirildi: {args[0]}{W()}")
                name, info = get_active_device()
                print_banner(name, info.get("ip") if info else None, "2.0.0")
            else:
                print(f"{R()}[-] Bilinmeyen tema. Seçenekler: {', '.join(THEMES.keys())}{W()}")

        # Cihaz Yönetimi 
        elif cmd in ["cihaz"]:
            cmd_cihaz(args)

        elif cmd in ["baglan", "bağlan"]:
            self._cmd_baglan(args)

        # Modül / Ayar 
        elif cmd == "ayarlar":
            cmd_ayarlar(args)

        elif cmd == "istatistik":
            cmd_istatistik(self.conn, args)

        # Medya 
        elif cmd == "ses":
            if args and args[0] in ["+", "artir", "artır"]:
                cmd_ses_artir(self.conn, args)
            elif args and args[0] in ["-", "azalt"]:
                cmd_ses_azalt(self.conn, args)
            else:
                cmd_ses(self.conn, args)

        elif cmd in ["ses+", "ses-artir"]:
            cmd_ses_artir(self.conn, args)

        elif cmd in ["ses-", "ses-azalt"]:
            cmd_ses_azalt(self.conn, args)

        elif cmd == "mute":
            cmd_mute(self.conn, args)

        elif cmd == "unmute":
            cmd_unmute(self.conn, args)

        elif cmd == "play":
            cmd_play(self.conn, args)

        elif cmd == "pause":
            cmd_pause(self.conn, args)

        elif cmd == "stop":
            cmd_stop(self.conn, args)

        elif cmd == "ileri":
            cmd_ileri(self.conn, args)

        elif cmd == "geri":
            cmd_geri(self.conn, args)

        elif cmd == "kanal":
            cmd_kanal(self.conn, args)

        # Uygulama 
        elif cmd == "app":
            cmd_app(self.conn, args)

        elif cmd == "applist":
            cmd_app_listesi(self.conn, args)

        elif cmd == "mesaj":
            cmd_mesaj(self.conn, args)

        elif cmd in ["kapat", "kill"]:
            cmd_kapat(self.conn, args)

        # Kumanda 
        elif cmd == "tus":
            cmd_tus(self.conn, args)

        #  Profil 
        elif cmd == "profil":
            cmd_profil(self.conn, args)

        #  Zamanlayıcı 
        elif cmd == "timer":
            cmd_timer(self.conn, args)

        #  Tetikleyici 
        elif cmd == "tetik":
            cmd_tetik(self.conn, args)

        # Makro 
        elif cmd == "makro":
            cmd_makro(self.conn, args)

        #  Hatırlatıcı 
        elif cmd in ["hatirlatici", "hatırlatıcı"]:
            cmd_hatirlatici(self.conn, args)

        #  Ebeveyn 
        elif cmd == "ebeveyn":
            cmd_ebeveyn(self.conn, args)

        else:
            print(f"{R()}[-] Bilinmeyen komut: '{cmd}'. 'yardim' yazın.{W()}")

    # Ana Döngü

    async def run(self):
        # Kayıtlı cihaza otomatik bağlanmayı dene
        name, info = get_active_device()
        print_banner(
            name,
            info.get("ip") if info else None,
            "2.0.0"
        )

        if name:
            self._try_connect()
        else:
            print(f"{Y()}[!] Kayıtlı cihaz yok. TV eklemek için:{W()}")
            print(f"    {G()}cihaz ekle [isim] [ip-adresi]{W()}")
            print(f"    {G()}baglan{W()}\n")

        loop = asyncio.get_event_loop()

        while self.running:
            try:
                prompt = f"{G()}tv{W()}@{C()}{name or 'bağlı-değil'}{W()}> "
                raw = await loop.run_in_executor(None, lambda: input(prompt))
                self._dispatch(raw)
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Y()}[~] Çıkılıyor...{W()}")
                connection_manager.disconnect_all()
                break
            except Exception as e:
                print(f"{R()}[-] Hata: {e}{W()}")
