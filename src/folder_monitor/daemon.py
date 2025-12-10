"""
File monitoring daemon with plugin support.
"""
import time
import logging
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from folder_monitor.base_plugin import PluginManager, FileProcessorPlugin


class PluginEventHandler(FileSystemEventHandler):
    """Handler for file system events specific to a plugin."""
    
    def __init__(self, plugin: FileProcessorPlugin, config: dict) -> None:
        """
        Initialize the event handler.
        
        Args:
            plugin: The plugin instance to handle events.
            config: Configuration for the monitored folder.
        """
        self.plugin = plugin
        self.config = config
    
    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle file creation events.
        
        Args:
            event: The file system event.
        """
        if not event.is_directory:
            self._process_file(str(event.src_path))

    def _process_file(self, file_path: str) -> None:
        """Process the file with the plugin."""
        if self.plugin.can_handle(file_path):
            self.plugin.logger.info(f"Processing {file_path}")
            try:
                success = self.plugin.process(file_path, self.config)
                if success:
                    self.plugin.logger.info(f"Successfully processed {file_path}")
                else:
                    self.plugin.logger.error(f"Failed to process {file_path}")
            except Exception as e:
                self.plugin.logger.error(f"Exception while processing {file_path}: {e}", exc_info=True)
                self.plugin.on_error(file_path, e)


class FileMonitorDaemon:
    """
    Main daemon class for monitoring files and processing them with plugins.
    
    Attributes:
        plugin_manager: Plugin manager instance.
        observers: List of watchdog observers.
        logger: Logger instance.
    """
    
    def __init__(self) -> None:
        """Initialize the file monitor daemon."""
        self.plugin_manager = PluginManager()
        self.observers = []
        self.logger: logging.Logger
        
        self.setup_logging()
        self.load_plugins()
        self.setup_observers()
    
    def setup_logging(self) -> None:
        """Configure logging for the daemon."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("FileMonitorDaemon")
    
    def load_plugins(self) -> None:
        """Load all available plugins and their configurations."""
        self.plugin_manager.discover_plugins('folder_monitor.plugins')
        self.plugin_manager.discover_external_plugins()
        
        # Initialize configs for all plugins
        for name, plugin in self.plugin_manager.plugins.items():
            try:
                plugin.load_config()
            except Exception as e:
                self.logger.error(f"Failed to load config for plugin {name}: {e}")

        self.logger.info(f"Loaded plugins: {self.plugin_manager.list_plugins()}")
    
    def setup_observers(self) -> None:
        """Set up file system observers for all configured folders from all plugins."""
        for name, plugin in self.plugin_manager.plugins.items():
            folders = plugin.get_watch_folders()
            for folder_config in folders:
                path_str = folder_config.get('path')
                if not path_str:
                    continue
                
                path = Path(path_str)
                if not path.exists():
                    self.logger.warning(f"Folder does not exist: {path} (Plugin: {name})")
                    continue
                
                recursive = folder_config.get('recursive', False)
                
                observer = Observer()
                handler = PluginEventHandler(plugin, folder_config)
                
                observer.schedule(
                    handler, 
                    str(path), 
                    recursive=recursive
                )
                self.observers.append(observer)
                self.logger.info(f"Monitoring folder: {path} with plugin {name}")
    
    def start(self) -> None:
        """Start the daemon and begin monitoring."""
        self.logger.info("Starting File Monitor Daemon")
        
        for observer in self.observers:
            observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        """Stop the daemon and all observers."""
        self.logger.info("Stopping File Monitor Daemon")
        for observer in self.observers:
            observer.stop()
            observer.join()
