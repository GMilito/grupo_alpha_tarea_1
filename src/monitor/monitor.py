import time
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler
from bitacora import Bitacora  # Importa la clase Bitacora

class FolderMonitor:
    def __init__(self, folder_path, bitacora: Bitacora):
        """
        Inicializa el monitor de carpeta y la bitácora.
        :param folder_path: Ruta de la carpeta a monitorear.
        :param bitacora: Instancia de la clase Bitacora para registrar eventos.
        """
        self.folder_path = folder_path
        self.observer = Observer()
        self.bitacora = bitacora  # Guardamos la instancia de Bitacora

    def start(self):
        """
        Inicia el monitoreo de la carpeta.
        """
        if not self.folder_path:
            raise ValueError("No se ha configurado una carpeta para monitorear.")
        
        event_handler = FileSystemEventHandler()
        event_handler.on_created = self._on_created
        event_handler.on_deleted = self._on_deleted
        event_handler.on_modified = self._on_modified
        self.observer.schedule(event_handler, self.folder_path, recursive=True)
        self.observer.start()

    def stop(self):
        """
        Detiene el monitoreo de la carpeta.
        """
        self.observer.stop()
        self.observer.join()

    def _on_created(self, event):
        """
        Maneja el evento de creación de archivo.
        Registra el archivo creado en la bitácora.
        """
        print(f"Archivo creado: {event.src_path}")
        # Registrar el evento en la bitácora
        self.bitacora.registrar_archivo(event.src_path)

    def _on_deleted(self, event):
        """
        Maneja el evento de eliminación de archivo.
        Registra el archivo eliminado en la bitácora.
        """
        print(f"Archivo eliminado: {event.src_path}")
        # Registrar el evento en la bitácora
        self.bitacora.registrar_evento_personalizado(f"Archivo eliminado: {event.src_path}")

    def _on_modified(self, event):
        """
        Maneja el evento de modificación de archivo.
        Registra el archivo modificado en la bitácora.
        """
        print(f"Archivo modificado: {event.src_path}")
        # Registrar el evento en la bitácora
        self.bitacora.registrar_evento_personalizado(f"Archivo modificado: {event.src_path}")