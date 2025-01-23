import logging
import os
import getpass
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Bitacora:
    def __init__(self, log_file="log.txt", max_size=5 * 1024 * 1024, backup_count=3):
        """
        Inicializa el sistema de bitácoras con soporte para archivos de log rotativos.
        
        :param log_file: El nombre del archivo de log donde se almacenarán los registros.
        :param max_size: El tamaño máximo del archivo de log antes de crear un archivo nuevo.
        :param backup_count: La cantidad de archivos de log antiguos que se deben conservar.
        """
        self.log_file = log_file
        self.logger = logging.getLogger("Bitacora")

        # Configuración del manejador de archivos rotativos
        handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _obtener_detalles_archivo(self, nombre_archivo):
        """
        Obtiene los detalles de un archivo, como la extensión y el usuario que lo agregó.

        :param nombre_archivo: El nombre del archivo.
        :return: Una tupla con la extensión del archivo y el usuario.
        """
        extension = os.path.splitext(nombre_archivo)[1]
        usuario = getpass.getuser()
        return extension, usuario

    def registrar_archivo(self, nombre_archivo):
        """
        Registra la adición de un nuevo archivo en la bitácora.
        
        :param nombre_archivo: El nombre del archivo agregado.
        """
        try:
            extension, usuario = self._obtener_detalles_archivo(nombre_archivo)
            mensaje = (
                f"Se ha agregado el nuevo archivo '{nombre_archivo}' "
                f"(Extensión: {extension}) por el usuario '{usuario}'."
            )
            self.logger.info(mensaje)
        except Exception as e:
            self.registrar_error(e)

    def registrar_error(self, excepcion):
        """
        Registra un error técnico ocurrido durante el proceso en la bitácora.

        :param excepcion: La excepción que ocurrió.
        """
        self.logger.error(f"Error ocurrido: {str(excepcion)}")

    def registrar_evento_personalizado(self, mensaje):
        """
        Registra un evento personalizado en la bitácora.

        :param mensaje: El mensaje del evento a registrar.
        """
        self.logger.info(mensaje)


# Ejemplo de uso
if __name__ == "__main__":
    bitacora = Bitacora()

    # Registro de un archivo
    bitacora.registrar_archivo("documento.txt")

    # Registro de un error
    try:
        raise ValueError("Prueba de error técnico.")
    except Exception as e:
        bitacora.registrar_error(e)

    # Registro de un evento personalizado
    bitacora.registrar_evento_personalizado("Sincronización completada con éxito.")
