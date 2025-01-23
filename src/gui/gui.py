import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from config import ConfigurationManager

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sync Manager")
        self.config = ConfigurationManager.load_config()

        # Crear un Notebook (contiene las pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Crear las pestañas
        self.create_sync_tab()
        self.create_config_tab()

    def create_sync_tab(self):
        """Crear la pestaña para sincronización"""
        sync_tab = ttk.Frame(self.notebook)
        self.notebook.add(sync_tab, text="Sincronización")

        # Agregar contenido de la pestaña de sincronización
        tk.Label(sync_tab, text="Carpeta de sincronización:").pack(pady=10)

        self.folder_var = tk.StringVar(value=self.config.get("sync_folder", ""))
        self.folder_entry = tk.Entry(sync_tab, textvariable=self.folder_var, width=50)
        self.folder_entry.pack(pady=5)

        tk.Button(sync_tab, text="Seleccionar carpeta", command=self._select_folder).pack(pady=5)
        tk.Button(sync_tab, text="Guardar configuración", command=self._save_config).pack(pady=5)

    def create_config_tab(self):
        """Crear la pestaña para configuración"""
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="Configuración")

        # Agregar contenido de la pestaña de configuración
        tk.Label(config_tab, text="Configuración del sistema").pack(pady=10)
        tk.Button(config_tab, text="Iniciar sincronización", command=self._start_sync).pack(pady=5)
        tk.Button(config_tab, text="Detener sincronización", command=self._stop_sync).pack(pady=5)

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

    def _start_sync(self):
        """Inicia la sincronización (simulado en este caso)."""
        messagebox.showinfo("Sincronización", "Sincronización iniciada exitosamente.")

    def _stop_sync(self):
        """Detiene la sincronización (simulado en este caso)."""
        messagebox.showinfo("Sincronización", "Sincronización detenida exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()
