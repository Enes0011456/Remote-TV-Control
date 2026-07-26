"""
TV Bağlantı Yöneticisi - Çoklu cihaz desteği
"""

import asyncio,socket,threading
from modules.data_manager import (
    get_devices, get_active_device, add_device,
    update_device_key, set_active_device
)

try:
    from pywebostv.connection import WebOSClient
    from pywebostv.controls import MediaControl, ApplicationControl, SystemControl, InputControl
    WEBOS_AVAILABLE = True
except ImportError:
    WEBOS_AVAILABLE = False


class TVConnection:
    """Tek bir TV cihazının bağlantı nesnesi"""

    def __init__(self, name, ip, key=""):
        self.name = name
        self.ip = ip
        self.key = key
        self.client = None
        self.media = None
        self.app_control = None
        self.system = None
        self.input_control = None
        self.connected = False

    def connect(self):
        if not WEBOS_AVAILABLE:
            raise RuntimeError("pywebostv kütüphanesi kurulu değil!")
        self.client = WebOSClient(self.ip)
        self.client.connect()
        store = {}
        if self.key:
            store["client_key"] = self.key
        for status in self.client.register(store):
            if status == WebOSClient.REGISTERED:
                # Kaydedilen key'i güncelle
                new_key = store.get("client_key", "")
                if new_key and new_key != self.key:
                    self.key = new_key
                    update_device_key(self.name, new_key)
                self.media = MediaControl(self.client)
                self.app_control = ApplicationControl(self.client)
                self.system = SystemControl(self.client)
                try:
                    self.input_control = InputControl(self.client)
                except Exception:
                    self.input_control = None
                self.connected = True
                return True
        return False

    def disconnect(self):
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass
        self.connected = False

    def is_alive(self):
        try:
            sock = socket.create_connection((self.ip, 3000), timeout=2)
            sock.close()
            return True
        except Exception:
            return False


class ConnectionManager:
    """Tüm TV bağlantılarını yöneten merkezi sınıf"""

    def __init__(self):
        self._connections = {}  # name -> TVConnection

    def connect_device(self, name, ip, key=""):
        conn = TVConnection(name, ip, key)
        success = conn.connect()
        if success:
            self._connections[name] = conn
        return success, conn

    def get_active(self):
        name, info = get_active_device()
        if not name:
            return None
        if name in self._connections and self._connections[name].connected:
            return self._connections[name]
        # Bağlı değilse yeniden bağlan
        ip = info.get("ip", "")
        key = info.get("key", "")
        success, conn = self.connect_device(name, ip, key)
        if success:
            return conn
        return None

    def connect_active(self):
        name, info = get_active_device()
        if not name:
            return False, "Kayıtlı aktif cihaz yok."
        ip = info.get("ip", "")
        key = info.get("key", "")
        success, conn = self.connect_device(name, ip, key)
        return success, conn if success else "Bağlantı başarısız."

    def disconnect_all(self):
        for conn in self._connections.values():
            conn.disconnect()
        self._connections.clear()

    def get_connection(self, name):
        return self._connections.get(name)

    def is_connected(self, name):
        conn = self._connections.get(name)
        return conn is not None and conn.connected

    def scan_network(self, base_ip="192.168.1", timeout=0.5):
        """Ağdaki WebOS cihazlarını tara"""
        found = []

        def check(ip):
            try:
                sock = socket.create_connection((ip, 3000), timeout=timeout)
                sock.close()
                found.append(ip)
            except Exception:
                pass

        threads = []
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            t = threading.Thread(target=check, args=(ip,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=timeout + 0.2)

        return found


# Global singleton
connection_manager = ConnectionManager()
