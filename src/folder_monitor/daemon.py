"""
File monitoring daemon with plugin support.
"""
import time
import logging
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .base_plugin import PluginManager
from .config_reader import ConfigReader


class FileEventHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, daemon: 'FileMonitorDaemon') -> None:
        """
        Initialize the event handler.
        
        Args:
            daemon: The FileMonitorDaemon instance to handle events.
        """
        self.daemon = daemon
    
    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle file creation events.
        
        Args:
            event: The file system event.
        """
        if not event.is_directory:
            self.daemon.process_file(str(event.src_path))


class FileMonitorDaemon:
    """
    Main daemon class for monitoring files and processing them with plugins.
    
    Attributes:
        config_reader: Configuration reader instance.
        plugin_manager: Plugin manager instance.
        observers: List of watchdog observers.
        event_handler: File system event handler.
        logger: Logger instance.
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the file monitor daemon.
        
        Args:
            config_path: Path to the configuration file. 
                        If None, uses default path (current dir or standard config dir).
        """
        self.config_reader = ConfigReader(config_path)
        self.plugin_manager = PluginManager()
        self.observers = []
        self.event_handler = FileEventHandler(self)
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
        """Load all available plugins."""
        self.plugin_manager.discover_plugins('folder_monitor.plugins')
        self.plugin_manager.discover_external_plugins()
        self.logger.info(f"Loaded plugins: {self.plugin_manager.list_plugins()}")
    
    def setup_observers(self) -> None:
        """Set up file system observers for all configured folders."""
        for folder_config in self.config_reader.get_all_folders():
            if not folder_config.path.exists():
                self.logger.warning(f"Folder does not exist: {folder_config.path}")
                continue
            
            observer = Observer()
            observer.schedule(
                self.event_handler, 
                str(folder_config.path), 
                recursive=folder_config.recursive
            )
            self.observers.append(observer)
            self.logger.info(f"Monitoring folder: {folder_config}")
    
    def process_file(self, file_path: str) -> None:
        """
        Process a file using the appropriate plugin.
        
        Args:
            file_path: Path to the file to process.
        """
        folder_config = self.config_reader.get_folder_config(file_path)
        if not folder_config:
            self.logger.debug(f"No configuration found for file: {file_path}")
            return
        
        plugin = self.plugin_manager.get_plugin(folder_config.plugin)
        if not plugin:
            self.logger.error(f"Plugin '{folder_config.plugin}' not found for {file_path}")
            return
        
        if plugin.can_handle(file_path):
            self.logger.info(f"Processing {file_path} with {folder_config.plugin}")
            try:
                success = plugin.process(file_path, folder_config.plugin_config)
                if success:
                    self.logger.info(f"Successfully processed {file_path}")
                else:
                    self.logger.error(f"Failed to process {file_path}")
            except Exception as e:
                self.logger.error(f"Exception while processing {file_path}: {e}", exc_info=True)
                plugin.on_error(file_path, e)
        else:
            self.logger.warning(f"Plugin {folder_config.plugin} cannot handle {file_path}")
    
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
