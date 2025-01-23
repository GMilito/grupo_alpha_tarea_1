import json
import os

CONFIG_FILE = "config.json"

class ConfigurationManager:
    @staticmethod
    def load_config():
        """
        Carga la configuración desde el archivo config.json.
        Si el archivo no existe, crea uno con valores por defecto.
        """
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "sync_folder": "",
                "clients": []
            }
            ConfigurationManager.save_config(default_config)
            return default_config

        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error al leer el archivo de configuración: {e}")
            return {
                "sync_folder": "",
                "clients": []
            }

    @staticmethod
    def save_config(config):
        """
        Guarda la configuración en el archivo config.json.

        :param config: Diccionario con la configuración a guardar.
        """
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")

    @staticmethod
    def add_client(host, port):
        """
        Añade un nuevo cliente a la lista de clientes en la configuración.

        :param host: Dirección IP o nombre del host del cliente.
        :param port: Puerto del cliente.
        """
        config = ConfigurationManager.load_config()
        clients = config.get("clients", [])

        # Evitar duplicados
        for client in clients:
            if client["host"] == host and client["port"] == port:
                print(f"El cliente {host}:{port} ya está en la lista.")
                return

        # Añadir el nuevo cliente
        clients.append({"host": host, "port": port})
        config["clients"] = clients
        ConfigurationManager.save_config(config)
        print(f"Cliente {host}:{port} añadido correctamente.")

    @staticmethod
    def remove_client(host, port):
        """
        Elimina un cliente de la lista de clientes en la configuración.

        :param host: Dirección IP o nombre del host del cliente.
        :param port: Puerto del cliente.
        """
        config = ConfigurationManager.load_config()
        clients = config.get("clients", [])

        updated_clients = [client for client in clients if not (client["host"] == host and client["port"] == port)]

        if len(clients) == len(updated_clients):
            print(f"El cliente {host}:{port} no se encontró en la lista.")
            return

        config["clients"] = updated_clients
        ConfigurationManager.save_config(config)
        print(f"Cliente {host}:{port} eliminado correctamente.")
