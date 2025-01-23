import socket
import threading
import os
from datetime import datetime
from config import ConfigurationManager
from monitor import FolderMonitor
import logging

# Configuración del logger (bitácora de operaciones)
LOG_FILE = "sync_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class SyncManager:
    def __init__(self, sync_folder):
        self.sync_folder = sync_folder
        self.monitor = None
        self.monitor_thread = None
        self.is_monitoring = False

    def log_event(self, message):
        """Registra eventos en la bitácora."""
        logging.info(message)

    def log_error(self, error):
        """Registra errores en la bitácora."""
        logging.error(f"Error: {error}")

    def start_monitor(self):
        """Inicia el monitoreo de la carpeta de sincronización."""
        if not self.sync_folder:
            self.log_error("No se ha configurado una carpeta de sincronización.")
            return

        try:
            self.monitor = FolderMonitor(self.sync_folder, self.log_new_file)
            self.monitor_thread = threading.Thread(target=self._start_monitor, daemon=True)
            self.monitor_thread.start()
            self.is_monitoring = True
            self.log_event("Se ha iniciado la sincronización.")
            print("Sincronización iniciada.")
        except Exception as e:
            self.log_error(f"Error al iniciar el monitoreo: {e}")
            print("Error al iniciar la sincronización.")

    def _start_monitor(self):
        """Ejecuta el monitor en un hilo separado."""
        try:
            self.monitor.start()
        except Exception as e:
            self.log_error(f"Error al monitorear la carpeta: {e}")

    def stop_monitor(self):
        """Detiene el monitoreo."""
        if self.monitor:
            self.monitor.stop()
            self.is_monitoring = False
            self.log_event("Se ha detenido la sincronización.")
            print("Sincronización detenida.")

    def log_new_file(self, file_path):
        """Registra el evento de un nuevo archivo copiado."""
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1]
        user = os.getlogin()
        self.log_event(f"Se ha agregado el nuevo archivo '{file_name}' por el usuario '{user}'. Extensión: '{file_extension}'.")

    def replicate_file(self, file_path, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                file_name = os.path.basename(file_path)
                s.sendall(file_name.encode())  # Enviar el nombre del archivo
                with open(file_path, "rb") as f:
                    while (chunk := f.read(1024)):
                        s.sendall(chunk)
            self.log_event(f"Archivo '{file_name}' replicado a {host}:{port}.")
        except Exception as e:
            self.log_error(f"Error replicando archivo '{file_path}': {e}")
            
    def sync_new_file(self, file_path):
        """
        Método llamado cuando se detecta un nuevo archivo en la carpeta de sincronización.
        Se encarga de replicar el archivo a otros equipos.

        :param file_path: Ruta completa del archivo nuevo detectado.
        """
        try:
            # Registrar en la bitácora
            self.log_new_file(file_path)

            # Cargar los clientes de la configuración
            config = ConfigurationManager.load_config()
            clients = config.get("clients", [])

            # Verificar si hay clientes configurados
            if not clients:
                self.log_event("No hay clientes configurados para replicar los archivos.")
                return

            # Replicar el archivo a cada cliente
            for client in clients:
                host = client.get("host")
                port = client.get("port")
                if host and port:
                    self.replicate_file(file_path, host, port)
                else:
                    self.log_error(f"Cliente inválido en la configuración: {client}")
        except Exception as e:
            self.log_error(f"Error al sincronizar el archivo '{file_path}': {e}")

    def log_new_file(self, file_path):
        """
        Registra la creación de un archivo nuevo en la bitácora.
        
        :param file_path: Ruta completa del archivo nuevo detectado.
        """
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1]
        user = os.getlogin()
        self.log_event(f"Se ha agregado el nuevo archivo '{file_name}' por el usuario '{user}'. Extensión: '{file_extension}'.")



def start_sync_server():
    """Inicia el servidor de sincronización."""
    host = "localhost"
    port = 12345

    # Cargar la configuración y obtener la carpeta de sincronización
    config = ConfigurationManager.load_config()
    sync_folder = config.get("sync_folder", "")

    if not sync_folder:
        print("Error: No se ha configurado una carpeta de sincronización.")
        return

    # Crear el SyncManager
    sync_manager = SyncManager(sync_folder)

    # Iniciar el monitoreo
    sync_manager.start_monitor()

    # Simular el envío de archivos a clientes conectados
    # (En un escenario real, un cliente solicitaría los archivos a través del socket)
    while True:
        try:
            # Mantener el servidor funcionando (simulación)
            print("Servidor de sincronización ejecutándose. Presione Ctrl+C para salir.")
            threading.Event().wait(10)  # Mantenerlo activo cada 10 segundos
        except KeyboardInterrupt:
            print("Deteniendo el servidor...")
            sync_manager.stop_monitor()
            break


if __name__ == "__main__":
    start_sync_server()
