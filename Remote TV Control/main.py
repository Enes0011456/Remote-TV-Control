#!/usr/bin/env python3
"""
Remote TV Control - Ana Giriş Noktası
Kullanım:
  python main.py          -> Terminal modu
  python main.py --gui    -> GUI modu
"""

import sys,asyncio

def main():
    if "--gui" in sys.argv:
        from modules.gui import launch_gui
        launch_gui()
    else:
        from modules.terminal import TerminalApp
        app = TerminalApp()
        asyncio.run(app.run())

if __name__ == "__main__":
    main()
###Nasıl oldunu biliyorum iyi hissediceksen eğer masaüstüne bu_senin_için.txt e yaz ben okuycam ve sende rahatlıcaksın :)