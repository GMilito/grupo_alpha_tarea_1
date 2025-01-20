from src.monitor.monitor import start_monitor
from src.sync.sync import SyncManager

if __name__ == "__main__":
    sync_manager = SyncManager()

    # Ruta de la carpeta a monitorear
    folder_to_monitor = sync_manager.sync_folder

    # Inicia el monitor, notificando al SyncManager cuando haya cambios
    start_monitor(folder_to_monitor, sync_manager.sync_new_file)
