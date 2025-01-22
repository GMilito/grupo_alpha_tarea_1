import tkinter as tk
from tkinter import filedialog, messagebox
from config_manager import ConfigurationManager
from monitor import FolderMonitor
import threading

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sync Manager")
        self.config = ConfigurationManager.load_config()
        self.monitor = None
        self.monitor_thread = None
        self.is_monitoring = False

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets de la interfaz gráfica."""
        tk.Label(self.root, text="Carpeta de sincronización:").pack(pady=5)
        
        self.folder_var = tk.StringVar(value=self.config.get("sync_folder", ""))
        self.folder_entry = tk.Entry(self.root, textvariable=self.folder_var, width=50)
        self.folder_entry.pack(pady=5)

        tk.Button(self.root, text="Seleccionar carpeta", command=self._select_folder).pack(pady=5)
        tk.Button(self.root, text="Guardar configuración", command=self._save_config).pack(pady=5)

        self.monitor_button = tk.Button(self.root, text="Iniciar monitor", command=self._toggle_monitor)
        self.monitor_button.pack(pady=10)

    def _select_folder(self):
        """Permite al usuario seleccionar una carpeta."""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def _save_config(self):
        """Guarda la configuración en config.json."""
        self.config["sync_folder"] = self.folder_var.get()
        ConfigurationManager.save_config(self.config)
        messagebox.showinfo("Información", "Configuración guardada correctamente.")

    def _toggle_monitor(self):
        """Inicia o detiene el monitoreo de la carpeta."""
        if not self.is_monitoring:
            folder = self.folder_var.get()
            if not folder:
                messagebox.showerror("Error", "Por favor, seleccione una carpeta.")
                return

            self.monitor = FolderMonitor(folder)
            self.monitor_thread = threading.Thread(target=self._start_monitor, daemon=True)
            self.monitor_thread.start()
            self.is_monitoring = True
            self.monitor_button.config(text="Detener monitor")
        else:
            self.monitor.stop()
            self.is_monitoring = False
            self.monitor_button.config(text="Iniciar monitor")

    def _start_monitor(self):
        """Inicia el monitor en un hilo separado."""
        try:
            self.monitor.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.is_monitoring = False

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()
