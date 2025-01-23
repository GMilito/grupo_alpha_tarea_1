import socket
import threading
from config import ConfigurationManager
from monitor import FolderMonitor
import time

class SyncManager:
    def __init__(self, sync_folder):
        self.sync_folder = sync_folder
        self.monitor = None
        self.monitor_thread = None
        self.is_monitoring = False

    def start_monitor(self):
        """Inicia el monitoreo de la carpeta de sincronización."""
        if not self.sync_folder:
            print("No se ha configurado una carpeta de sincronización.")
            return

        self.monitor = FolderMonitor(self.sync_folder)
        self.monitor_thread = threading.Thread(target=self._start_monitor, daemon=True)
        self.monitor_thread.start()

    def _start_monitor(self):
        """Inicia el monitor en un hilo separado."""
        try:
            print(f"Iniciando el monitoreo en la carpeta: {self.sync_folder}")
            self.monitor.start()
        except Exception as e:
            print(f"Error al iniciar el monitoreo: {e}")

    def stop_monitor(self):
        """Detiene el monitoreo."""
        if self.monitor:
            self.monitor.stop()

    def send_sync_folder(self, host, port):
        """Envía la carpeta de sincronización a los clientes a través de un socket."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                message = f"Carpeta de sincronización: {self.sync_folder}"
                s.sendall(message.encode())
                print(f"Carpeta de sincronización enviada a {host}:{port}")
        except Exception as e:
            print(f"Error al enviar la carpeta de sincronización: {e}")


def start_sync_server():
    """Inicia el servidor de socket que envía la carpeta de sincronización a los clientes."""
    host = 'localhost'  # Dirección local o IP del servidor
    port = 12345  # Puerto de conexión

    # Cargar la configuración y obtener la carpeta de sincronización
    config = ConfigurationManager.load_config()
    sync_folder = config.get("sync_folder", "")

    # Iniciar el SyncManager con la carpeta configurada
    sync_manager = SyncManager(sync_folder)

    # Iniciar el monitoreo (opcional)
    sync_manager.start_monitor()

    # Enviar la carpeta de sincronización a los clientes
    sync_manager.send_sync_folder(host, port)

    # Mantener el servidor funcionando mientras se monitorea
    while True:
        time.sleep(1)


if __name__ == "__main__":
    start_sync_server()
