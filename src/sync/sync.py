import os
import socket
from src.config.config_manager import ConfigurationManager
from src.log.logger import Logger

class SyncManager:
    def __init__(self):
        # Cargar configuración inicial
        self.update_config()

    def update_config(self):
        """
        Carga o actualiza la configuración desde el ConfigurationManager.
        """
        config = ConfigurationManager.load_config()
        self.sync_folder = config.get("sync_folder", "")
        self.clients = config.get("clients", [])
        self.sync_active = config.get("sync_active", False)
        Logger.log_info("Configuración actualizada: " + str(config))

    def validate_config(self):
        """
        Valida que la configuración actual sea válida.
        :return: True si es válida, False en caso contrario.
        """
        config = {
            "sync_folder": self.sync_folder,
            "clients": self.clients,
            "sync_active": self.sync_active
        }
        return ConfigurationManager.validate_config(config)

    def send_file(self, file_path):
        """
        Enviar un archivo a todos los clientes registrados.
        :param file_path: Ruta del archivo a sincronizar.
        """
        if not self.sync_active:
            Logger.log_info("La sincronización está desactivada.")
            return

        for client in self.clients:
            ip = client["ip"]
            port = client["port"]
            try:
                Logger.log_info(f"Conectando a {ip}:{port} para enviar {file_path}")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip, port))
                    with open(file_path, "rb") as file:
                        while chunk := file.read(1024):
                            sock.send(chunk)
                Logger.log_info(f"Archivo {file_path} enviado exitosamente a {ip}:{port}")
            except Exception as e:
                Logger.log_error(f"Error enviando {file_path} a {ip}:{port}: {e}")

    def sync_new_file(self, file_path):
        """
        Método de sincronización llamado cuando un nuevo archivo es detectado.
        :param file_path: Ruta del archivo detectado.
        """
        if not os.path.exists(file_path):
            Logger.log_error(f"El archivo {file_path} no existe.")
            return

        Logger.log_info(f"Iniciando sincronización del archivo: {file_path}")
        self.send_file(file_path)

    def save_client(self, ip, port):
        """
        Agrega un nuevo cliente a la configuración y guarda los cambios.
        :param ip: Dirección IP del cliente.
        :param port: Puerto del cliente.
        """
        self.clients.append({"ip": ip, "port": port})
        self._save_config()

    def _save_config(self):
        """
        Guarda la configuración actual en el archivo JSON.
        """
        config = {
            "sync_folder": self.sync_folder,
            "clients": self.clients,
            "sync_active": self.sync_active
        }
        try:
            ConfigurationManager.save_config(config)
            Logger.log_info("Configuración guardada: " + str(config))
        except Exception as e:
            Logger.log_error(f"Error al guardar configuración: {e}")
