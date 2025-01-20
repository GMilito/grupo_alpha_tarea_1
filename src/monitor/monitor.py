import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.log.logger import Logger


class FolderMonitor(FileSystemEventHandler):
    """
    Clase que monitorea una carpeta para detectar nuevos archivos.
    """
    def __init__(self, sync_callback):
        """
        Inicializa el monitor de carpetas.
        :param sync_callback: Función a ejecutar cuando se detecta un nuevo archivo.
        """
        super().__init__()
        self.sync_callback = sync_callback

    def on_created(self, event):
        """
        Se llama automáticamente cuando se crea un archivo en la carpeta monitoreada.
        :param event: Evento de creación de archivo generado por watchdog.
        """
        if not event.is_directory:  # Ignorar directorios
            Logger.log_info(f"Nuevo archivo detectado: {event.src_path}")
            self.sync_callback(event.src_path)


def start_monitor(folder_path, sync_callback):
    """
    Inicia el monitoreo de una carpeta específica.
    :param folder_path: Ruta de la carpeta a monitorear.
    :param sync_callback: Función a ejecutar cuando se detecta un nuevo archivo.
    """
    observer = Observer()
    event_handler = FolderMonitor(sync_callback)
    observer.schedule(event_handler, folder_path, recursive=False)  # No monitorear subcarpetas
    observer.start()

    Logger.log_info(f"Monitor iniciado en la carpeta: {folder_path}")
    print(f"Monitor iniciado en la carpeta: {folder_path}")

    try:
        while True:
            time.sleep(1)  # Mantener el proceso vivo
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    Logger.log_info("Monitor detenido.")
