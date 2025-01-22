import time
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler

class FolderMonitor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.observer = Observer()

    def start(self):
        if not self.folder_path:
            raise ValueError("No se ha configurado una carpeta para monitorear.")
        
        event_handler = FileSystemEventHandler()
        event_handler.on_created = self._on_created
        self.observer.schedule(event_handler, self.folder_path, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def _on_created(self, event):
        print(f"Archivo creado: {event.src_path}")

    def _on_deleted(self, event):
        print(f"Archivo eliminado: {event.src_path}")

    def _on_modified(self, event):
        print(f"Archivo modificado: {event.src_path}")
