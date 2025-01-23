import logging
import os
from datetime import datetime

class Logger:
    """
    Clase para manejar el registro de eventos y errores del sistema.
    """
    LOG_FILE = "log.txt"  # Archivo donde se almacenarán los logs

    @staticmethod
    def configure_logger():
        """
        Configura el sistema de logging para usar un archivo con un formato estándar.
        """
        logging.basicConfig(
            filename=Logger.LOG_FILE,
            level=logging.INFO,  # Nivel mínimo de registro
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def log_info(message):
        """
        Registra un mensaje informativo en la bitácora.
        :param message: Mensaje a registrar.
        """
        logging.info(message)

    @staticmethod
    def log_error(message):
        """
        Registra un mensaje de error en la bitácora.
        :param message: Mensaje a registrar.
        """
        logging.error(message)

    @staticmethod
    def log_file_added(file_path):
        """
        Registra que se ha agregado un nuevo archivo a la carpeta de sincronización.
        :param file_path: Ruta del archivo agregado.
        """
        try:
            file_name = os.path.basename(file_path)
            extension = os.path.splitext(file_name)[1]  # Obtener la extensión del archivo
            user = os.getlogin()  # Obtener el usuario del sistema operativo
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = f"Se ha agregado el nuevo archivo {file_name} (usuario: {user}, extensión: {extension})"
            logging.info(message)
        except Exception as e:
            Logger.log_error(f"Error registrando archivo {file_path}: {e}")
