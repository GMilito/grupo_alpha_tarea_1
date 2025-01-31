import os
import shutil
import platform
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import logging
from datetime import datetime

CONFIG_FILE = "config.json"
observer = None  
is_backing_up = False

# Configurar el logging para consola y archivo
log_file = "backup_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)  

SO = platform.system()
USER = os.getenv("USERNAME") if SO == "Windows" else os.getenv("USER")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"source_folders": [], "destination_folder": ""}

def save_config():
    config = {"source_folders": source_folders, "destination_folder": destination_folder}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def add_source_folder():
    folder = filedialog.askdirectory(title="Selecciona una carpeta de origen")
    if folder and folder not in source_folders:
        source_folders.append(folder)
        update_listbox()
        save_config()

def remove_source_folder():
    selected = listbox.curselection()
    if selected:
        folder = source_folders[selected[0]]
        source_folders.remove(folder)
        update_listbox()
        save_config()

def select_destination_folder():
    global destination_folder
    folder = filedialog.askdirectory(title="Selecciona la carpeta de destino")
    if folder:
        destination_folder = folder
        dest_label.config(text=f"Destino: {destination_folder}")
        save_config()

def update_listbox():
    listbox.delete(0, tk.END)
    for folder in source_folders:
        listbox.insert(tk.END, folder)

def get_destination_path(source, src_path):
    """Convierte la ruta de origen en la ruta de respaldo"""
    relative_path = os.path.relpath(src_path, source)
    dest_path = os.path.join(destination_folder, relative_path)
    return dest_path

def sync_folders():
    global is_backing_up
    is_backing_up = True
    update_status_label("🔄 Sincronizando archivos...", "blue")

    for source in source_folders:
        if not os.path.exists(source):
            continue
        for root_dir, _, files in os.walk(source):
            for file in files:
                src_path = os.path.join(root_dir, file)
                dest_path = get_destination_path(source, src_path)

                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                try:
                    if os.path.exists(dest_path):
                        src_mtime = os.path.getmtime(src_path)
                        dest_mtime = os.path.getmtime(dest_path)
                        if src_mtime <= dest_mtime:
                            continue  

                    shutil.copy2(src_path, dest_path)
                    print(f"✅ Archivo sincronizado: {src_path} -> {dest_path}")

                except PermissionError as e:
                    print(f"⚠️ Archivo bloqueado: {src_path} - {e}")
                    continue  

    remove_deleted_files()
    is_backing_up = False
    update_status_label("🟢 Monitoreo activo - Esperando cambios", "green")

def remove_deleted_files():
    for source in source_folders:
        source_folder_name = os.path.basename(source)
        dest_source_folder = os.path.join(destination_folder, source_folder_name)

        if not os.path.exists(dest_source_folder):
            continue

        for root_dir, _, files in os.walk(dest_source_folder):
            for file in files:
                dest_path = os.path.join(root_dir, file)
                relative_path = os.path.relpath(dest_path, dest_source_folder)
                src_path = os.path.join(source, relative_path)

                if not os.path.exists(src_path):
                    os.remove(dest_path)
                    print(f"🗑️ Archivo eliminado del destino: {dest_path}")

class BackupHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.backup_file(event.src_path)
        
        
    def on_moved(self, event):
        """Actualizar nombres de archivos y carpetas si son renombrados"""
        if event.is_directory:
            logging.info(f"📁 Carpeta renombrada/movida: {event.src_path} -> {event.dest_path}")
        else:
            logging.info(f"📄 Archivo renombrado/movido: {event.src_path} -> {event.dest_path}")

        self.rename_file_or_folder(event.src_path, event.dest_path)    

    def on_created(self, event):
        if not event.is_directory:
            self.backup_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.delete_file(event.src_path)

    def backup_file(self, src_path):
        """Realiza la copia de respaldo solo si el archivo ha cambiado"""
        if src_path.endswith(".tmp"):
            logging.warning(f"Archivo temporal ignorado: {src_path}")
            return

        if not os.path.exists(src_path):
            logging.warning(f"Archivo no encontrado (posible archivo temporal eliminado): {src_path}")
            return

        for source in source_folders:
            if src_path.startswith(source):
                dest_path = get_destination_path(source, src_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                try:
                    if os.path.exists(dest_path):
                        src_mtime = os.path.getmtime(src_path)
                        dest_mtime = os.path.getmtime(dest_path)
                        if src_mtime <= dest_mtime:
                            return  

                    shutil.copy2(src_path, dest_path)
                    logging.info(f"✅ Archivo respaldado: {src_path} -> {dest_path}")

                except PermissionError as e:
                    logging.error(f"⚠️ Permiso denegado al acceder a {src_path}: {e}")
                    continue

    def delete_file(self, src_path):
        for source in source_folders:
            if src_path.startswith(source):
                dest_path = get_destination_path(source, src_path)

                if os.path.exists(dest_path):
                    os.remove(dest_path)
                    print(f"🗑️ Archivo eliminado en destino: {dest_path}")

    def rename_file_or_folder(self, old_path, new_path):
        """Renombra archivos y carpetas en la copia de seguridad"""
        for source in source_folders:
            if old_path.startswith(source):
                old_dest_path = get_destination_path(source, old_path)
                new_dest_path = get_destination_path(source, new_path)

                if os.path.exists(old_dest_path):
                    try:
                        os.rename(old_dest_path, new_dest_path)
                        logging.info(f"🔄 {old_dest_path} renombrado a {new_dest_path}")
                    except PermissionError as e:
                        logging.error(f"⚠️ No se pudo renombrar {old_dest_path}: {e}")

def update_status_label(text, color):
    status_label.config(text=text, fg=color)
    root.update_idletasks()  

def start_monitoring():
    global observer
    if not destination_folder:
        messagebox.showerror("Error", "Selecciona una carpeta de destino.")
        return
    if not source_folders:
        messagebox.showerror("Error", "Añade al menos una carpeta de origen.")
        return

    threading.Thread(target=sync_folders, daemon=True).start()

    observer = Observer()
    event_handler = BackupHandler()
    for folder in source_folders:
        if os.path.exists(folder):
            observer.schedule(event_handler, folder, recursive=True)

    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    update_status_label("🟢 Monitoreo activo - Esperando cambios", "green")
    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)
    print("🚀 Monitoreo iniciado.")

def stop_monitoring():
    global observer
    if observer:
        observer.stop()
        observer.join()
        observer = None
    update_status_label("🔴 Monitoreo detenido", "red")
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)
    print("🛑 Monitoreo detenido.")

config = load_config()
source_folders = config["source_folders"]
destination_folder = config["destination_folder"]

root = tk.Tk()
root.title("Respaldo y Sincronización Automática")
root.geometry("500x500")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="📂 Carpetas de Origen:").grid(row=0, column=0, columnspan=2)

listbox = tk.Listbox(frame, width=50, height=8)
listbox.grid(row=1, column=0, columnspan=2, pady=5)
update_listbox()

btn_add = tk.Button(frame, text="➕ Agregar", command=add_source_folder)
btn_add.grid(row=2, column=0, pady=5)

btn_remove = tk.Button(frame, text="➖ Quitar", command=remove_source_folder)
btn_remove.grid(row=2, column=1, pady=5)

dest_label = tk.Label(root, text=f"📁 Destino: {destination_folder or 'No seleccionado'}")
dest_label.pack(pady=5)

btn_dest = tk.Button(root, text="📂 Seleccionar Destino", command=select_destination_folder)
btn_dest.pack(pady=5)

status_label = tk.Label(root, text="🔴 Monitoreo detenido", fg="red")
status_label.pack(pady=10)

start_btn = tk.Button(root, text="▶️ Iniciar", command=start_monitoring)
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="⏹️ Detener", command=stop_monitoring, state=tk.DISABLED)
stop_btn.pack(pady=5)



root.mainloop()
