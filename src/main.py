from config import ConfigurationManager
from log import Logger
from sync import SyncManager
from monitor import FolderMonitor
from gui import SyncApp
import threading
from tkinter import filedialog, Tk

def main():
    """
    Punto de entrada principal del programa.
    Orquesta la inicialización de módulos y la GUI.
    """
    # Configurar el logger
    Logger.configure_logger()
    Logger.log_info("El sistema está iniciando...")

    # Cargar configuración inicial
    config = ConfigurationManager.load_config()
    sync_folder = config.get("sync_folder", "")
    sync_active = config.get("sync_active", False)

    # Inicializar la ventana Tkinter (root)
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter

    # Si no se ha configurado una carpeta, abrir la interfaz de selección
    if not sync_folder:
        Logger.log_info("No se ha configurado una carpeta de sincronización. Solicitando al usuario.")
        print("No se ha configurado una carpeta de sincronización. Por favor, seleccione una.")

        # Crear una ventana de selección de carpeta
        sync_folder = filedialog.askdirectory(title="Seleccione la carpeta de sincronización")

        if sync_folder:  # Si se seleccionó una carpeta
            config["sync_folder"] = sync_folder
            ConfigurationManager.save_config(config)
            Logger.log_info(f"Carpeta de sincronización configurada: {sync_folder}")
        else:  # Si no se seleccionó una carpeta
            Logger.log_error("El usuario no seleccionó una carpeta. Terminando el programa.")
            print("Error: Debe configurar una carpeta de sincronización para continuar.")
            return

    # Inicializar SyncManager con root
    sync_manager = SyncManager(sync_folder)

    # Iniciar monitor en un hilo separado
    def monitor_thread():
        try:
            Logger.log_info(f"Iniciando el monitor en la carpeta: {sync_folder}")
            FolderMonitor(sync_manager.sync_new_file).start(sync_folder)
        except Exception as e:
            Logger.log_error(f"Error en el monitor: {e}")

    monitor_thread_running = False
    monitor_thread_instance = None

    # Iniciar GUI
    def start_sync():
        """
        Inicia la sincronización activando el monitor.
        """
        nonlocal monitor_thread_running, monitor_thread_instance
        if not monitor_thread_running:
            config["sync_active"] = True
            ConfigurationManager.save_config(config)
            sync_manager.update_config()

            # Iniciar el monitor en un hilo separado
            monitor_thread_instance = threading.Thread(target=monitor_thread, daemon=True)
            monitor_thread_instance.start()
            monitor_thread_running = True

            Logger.log_info("Sincronización iniciada.")

    def stop_sync():
        """
        Detiene la sincronización y el monitor.
        """
        nonlocal monitor_thread_running, monitor_thread_instance
        if monitor_thread_running:
            config["sync_active"] = False
            ConfigurationManager.save_config(config)
            sync_manager.update_config()

            # Detener el hilo del monitor
            if monitor_thread_instance:
                monitor_thread_instance.join(timeout=1)
            monitor_thread_running = False

            Logger.log_info("Sincronización detenida.")

    # Iniciar la aplicación gráfica
    app = SyncApp()
    app.start_sync = start_sync
    app.stop_sync = stop_sync
    app.run()


if __name__ == "__main__":
    main()
