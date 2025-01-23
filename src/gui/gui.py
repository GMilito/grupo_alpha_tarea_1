import tkinter as tk
from tkinter import filedialog, messagebox
from config.config_manager import ConfigurationManager
from sync.sync import SyncManager


class SyncApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sincronización de Archivos")
        self.window.geometry("500x300")
        
        # Inicializar configuración y SyncManager
        self.config = ConfigurationManager.load_config()
        self.sync_manager = SyncManager(self.window)

        # Crear la interfaz gráfica
        self.create_widgets()

    def create_widgets(self):
        # Etiqueta de título
        tk.Label(self.window, text="Sincronización de Archivos", font=("Arial", 16)).pack(pady=10)

        # Mostrar la carpeta configurada
        self.folder_label = tk.Label(self.window, text=f"Carpeta actual: {self.config.get('sync_folder', 'No configurada')}", wraplength=400)
        self.folder_label.pack(pady=5)

        # Botón para seleccionar la carpeta
        tk.Button(self.window, text="Seleccionar Carpeta", command=self.select_folder).pack(pady=10)

        # Botones para iniciar y detener la sincronización
        self.start_button = tk.Button(self.window, text="Iniciar Sincronización", command=self.start_sync)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.window, text="Detener Sincronización", command=self.stop_sync, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Área de mensajes informativos
        self.message_label = tk.Label(self.window, text="", fg="green")
        self.message_label.pack(pady=10)

    def select_folder(self):
        """Abrir un selector de carpetas y guardar la selección en config.json."""
        folder = filedialog.askdirectory()
        if folder:
            # Guardar en config.json
            self.config["sync_folder"] = folder
            ConfigurationManager.save_config(self.config)
            self.folder_label.config(text=f"Carpeta actual: {folder}")
            self.show_message("Carpeta de sincronización actualizada.", "green")

    def start_sync(self):
        """Inicia la sincronización de archivos."""
        if not self.config.get("sync_folder"):
            self.show_message("Por favor, configure una carpeta primero.", "red")
            return

        self.config["sync_active"] = True
        ConfigurationManager.save_config(self.config)
        self.sync_manager.update_config()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.show_message("Se ha iniciado la sincronización.", "green")

    def stop_sync(self):
        """Detiene la sincronización de archivos."""
        self.config["sync_active"] = False
        ConfigurationManager.save_config(self.config)
        self.sync_manager.update_config()

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.show_message("Se ha detenido la sincronización.", "red")

    def show_message(self, message, color):
        """Muestra un mensaje en la GUI."""
        self.message_label.config(text=message, fg=color)

    def run(self):
        """Inicia el bucle principal de la GUI."""
        self.window.mainloop()


# Ejemplo de uso
if __name__ == "__main__":
    app = SyncApp()
    app.run()
