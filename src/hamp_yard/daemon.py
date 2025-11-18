# daemon.py
import time
import logging
import yaml
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .base_plugin import PluginManager

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, daemon):
        self.daemon = daemon
    
    def on_created(self, event):
        if not event.is_directory:
            self.daemon.process_file(event.src_path)

class FileMonitorDaemon:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.plugin_manager = PluginManager()
        self.observers = []
        self.event_handler = FileEventHandler(self)
        
        self.setup_logging()
        self.load_plugins()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("FileMonitorDaemon")
    
    def load_plugins(self):
        """Загружает все плагины"""
        # Встроенные плагины
        self.plugin_manager.discover_plugins('hamp_yard.plugins')
        
        # Внешние плагины через entry points
        self.plugin_manager.discover_external_plugins()
        
        self.logger.info(f"Loaded plugins: {self.plugin_manager.list_plugins()}")
    
    def load_config(self):
        """Загружает конфигурацию из YAML файла"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            self.logger.info("Configuration loaded")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = {}
    
    def process_file(self, file_path: str):
        """Обрабатывает файл с помощью соответствующего плагина"""
        folder_config = self.get_folder_config(file_path)
        if not folder_config:
            return
        
        plugin_name = folder_config.get('plugin')
        if not plugin_name:
            self.logger.warning(f"No plugin configured for {file_path}")
            return
        
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            self.logger.error(f"Plugin '{plugin_name}' not found for {file_path}")
            return
        
        if plugin.can_handle(file_path):
            self.logger.info(f"Processing {file_path} with {plugin_name}")
            success = plugin.process(file_path, folder_config)
            if success:
                self.logger.info(f"Successfully processed {file_path}")
            else:
                self.logger.error(f"Failed to process {file_path}")
        else:
            self.logger.warning(f"Plugin {plugin_name} cannot handle {file_path}")
    
    def get_folder_config(self, file_path: str) -> dict:
        """Находит конфигурацию для папки файла"""
        file_path = Path(file_path)
        
        for folder, config in self.config.get('folders', {}).items():
            if file_path.is_relative_to(folder):
                return config
        
        return None
    
    def setup_observers(self):
        """Настраивает наблюдатели для всех папок в конфиге"""
        for folder in self.config.get('folders', {}).keys():
            observer = Observer()
            observer.schedule(self.event_handler, folder, recursive=True)
            self.observers.append(observer)
            self.logger.info(f"Monitoring folder: {folder}")
    
    def start(self):
        """Запускает демон"""
        self.logger.info("Starting File Monitor Daemon")
        
        self.load_config()
        self.setup_observers()
        
        # Запускаем всех наблюдателей
        for observer in self.observers:
            observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Останавливает демон"""
        self.logger.info("Stopping File Monitor Daemon")
        for observer in self.observers:
            observer.stop()
            observer.join()
    
    def reload_config(self):
        """Перезагружает конфигурацию"""
        self.logger.info("Reloading configuration")
        
        # Останавливаем текущих наблюдателей
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        
        # Загружаем новую конфигурацию
        self.load_config()
        self.setup_observers()
        
        # Запускаем новых наблюдателей
        for observer in self.observers:
            observer.start()

def main():
    daemon = FileMonitorDaemon()
    daemon.start()

if __name__ == "__main__":
    main()
