import socket
import os
import logging

# Configuración de la bitácora para el cliente
LOG_FILE = "client_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class FileReceiver:
    def __init__(self, sync_folder, host='0.0.0.0', port=5000):
        """
        Inicializa el cliente para recibir archivos.
        
        :param sync_folder: Carpeta de sincronización donde se guardarán los archivos recibidos.
        :param host: Dirección IP del cliente (por defecto 0.0.0.0 para aceptar todas las conexiones).
        :param port: Puerto donde escucha el cliente.
        """
        self.host = host
        self.port = port
        self.sync_folder = sync_folder

        # Crear la carpeta de sincronización, si no existe
        if not os.path.exists(self.sync_folder):
            os.makedirs(self.sync_folder)

    def log_event(self, message):
        """Registra eventos en la bitácora."""
        logging.info(message)

    def log_error(self, error):
        """Registra errores en la bitácora."""
        logging.error(f"Error: {error}")

    def start(self):
        """Inicia el cliente para recibir archivos."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.host, self.port))
                server_socket.listen(5)
                self.log_event(f"Cliente escuchando en {self.host}:{self.port} para recibir archivos.")

                while True:
                    conn, addr = server_socket.accept()
                    self.log_event(f"Conexión establecida con {addr}.")
                    self._receive_file(conn)
        except Exception as e:
            self.log_error(f"Error en el cliente: {e}")

    def _receive_file(self, conn):
        """Recibe un archivo del servidor y lo guarda en la carpeta de sincronización."""
        try:
            # Recibir el nombre del archivo
            file_name = conn.recv(1024).decode()
            if not file_name:
                self.log_error("No se recibió el nombre del archivo.")
                return
            
            file_path = os.path.join(self.sync_folder, file_name)

            # Abrir un archivo para escritura binaria
            with open(file_path, 'wb') as file:
                self.log_event(f"Recibiendo archivo: {file_name}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    file.write(data)
            
            self.log_event(f"Archivo '{file_name}' recibido y guardado en {self.sync_folder}.")
        except Exception as e:
            self.log_error(f"Error al recibir archivo: {e}")
        finally:
            conn.close()
