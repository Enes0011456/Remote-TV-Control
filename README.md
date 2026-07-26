# Remote-TV-Control
Remote TV Control

Remote TV Control, akıllı televizyonları veya medya oynatıcıları uzaktan kontrol etmek, otomatikleştirmek ve terminal veya arayüz üzerinden yönetmek amacıyla geliştirilmiş Python tabanlı bir araçtır.

Ağ daki cihazın İpsini öğrenme yolu ve izlencek yol nedir hangi araç kullanılmalıdır :
Kullanılcak Araç : bettercap

İpsini öğrenme yolu ve izlencek yol Komutları :

sudo bettercap ile baslatın 

/net.probe on                yazın

/net.show                    ilede öğrendiniz İP yi bir kenara not edin ve uygulamyı baslatın

Remote TV Control/data       olusan kısımda olan 

Remote TV Control/data/devices.json da olan devices.json açın ve ip kısmına o not ettiniz ip yi girin ve kaydedip kapatın


🚀 Özellikler 

Uzaktan Erişim: Ağ üzerindeki uyumlu televizyon cihazlarına bağlanma ve komut gönderme.

Hızlı Komut Seti: Ses açma/kapama, kanal değiştirme, güç yönetimi ve medya kontrolleri.

Modüler Mimari: Farklı TV markaları ve protokolleriyle kolayca genişletilebilir altyapı.

Kolay Entegrasyon: Python betikleri veya otomasyon sistemleriyle uyumlu çalışma.

📦 Kurulum

Projeyi yerel ortamınıza klonlayın ve gerekli bağımlılıkları yükleyin:

Bash:

git clone https://github.com/Enes0011456/Remote-TV-Control

cd Remote-TV-Control-main

pip install -r requirements.txt

💻 Kullanım

Uygulamayı başlatmak ve temel komutları çalıştırmak için:

Bash
python3 main.py

🛠️ Proje Yapısı

main.py: Ana kontrol döngüsü ve arayüz yöneticisi.

config.json: Cihaz IP adresleri ve bağlantı ayarları.

controller.py: TV komut protokollerini işleyen mantık katmanı.
