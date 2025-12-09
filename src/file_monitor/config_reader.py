"""
Configuration reader for folder monitoring settings.
"""
import json
import logging
import sys
import os
from pathlib import Path
from typing import Any, Optional
from importlib.resources import files


def get_config_dir() -> Path:
    """
    Get the standard configuration directory for hump-yard.
    
    Returns:
        Path to the configuration directory.
    """
    if sys.platform == 'win32':
        # Windows: %APPDATA%\hump-yard
        config_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'hump-yard'
    else:
        # Linux/Unix: ~/.config/hump-yard
        config_dir = Path.home() / '.config' / 'hump-yard'
    
    return config_dir


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.
    
    Searches for config in the following order:
    1. ./config.json (current directory)
    2. <config_dir>/config.json (standard config directory)
    
    Returns:
        Path to the configuration file (may not exist yet).
    """
    # First check current directory
    local_config = Path('config.json')
    if local_config.exists():
        return local_config
    
    # Otherwise use standard config directory
    return get_config_dir() / 'config.json'


def create_default_config(config_path: Path) -> None:
    """
    Create a default configuration file from the template.
    
    Args:
        config_path: Path where to create the configuration file.
    """
    try:
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load template from package
        template_path = files('file_monitor').joinpath('config.template.json')
        with template_path.open('r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Write to config path
        config_path.write_text(template_content, encoding='utf-8')
        
    except Exception as e:
        raise RuntimeError(f"Failed to create default config: {e}")


class FolderConfig:
    """
    Configuration for a single monitored folder.
    
    Attributes:
        path: Path to the monitored folder.
        recursive: Whether to monitor subfolders recursively.
        extensions: List of file extensions to process.
        plugin: Name of the plugin to use for processing.
        plugin_config: Additional configuration for the plugin.
    """
    
    def __init__(self, config_dict: dict[str, Any]) -> None:
        """
        Initialize folder configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing folder configuration.
        """
        self.path: Path = Path(config_dict['path'])
        self.recursive: bool = config_dict.get('recursive', False)
        self.extensions: list[str] = config_dict.get('extensions', ['.tiff', '.tif', '.jpg'])
        self.plugin: str = config_dict['plugin']
        self.plugin_config: dict[str, Any] = {k: v for k, v in config_dict.items() 
                            if k not in ['path', 'recursive', 'extensions', 'plugin']}
    
    def should_process_file(self, file_path: Path) -> bool:
        """
        Check if a file should be processed based on extension filters.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if the file should be processed, False otherwise.
        """
        if not self.extensions:
            return True
        
        file_ext = file_path.suffix.lower()
        return any(file_ext == ext.lower() for ext in self.extensions)
    
    def __repr__(self) -> str:
        return f"FolderConfig(path={self.path}, recursive={self.recursive}, plugin={self.plugin})"


class ConfigReader:
    """
    Reader and manager for configuration.
    
    Attributes:
        config_path: Path to the configuration file.
        folders: List of folder configurations.
        logger: Logger instance.
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the configuration reader.
        
        Args:
            config_path: Path to the configuration JSON file. 
                        If None, uses default path (current dir or standard config dir).
        """
        if config_path is None:
            self.config_path = get_default_config_path()
        else:
            self.config_path = Path(config_path)
        
        self.folders: list[FolderConfig] = []
        self.logger: logging.Logger = logging.getLogger("ConfigReader")
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if not self.config_path.exists():
                self.logger.info(f"Config file {self.config_path} not found, creating default config")
                try:
                    create_default_config(self.config_path)
                    self.logger.info(f"Created default config at {self.config_path}")
                except Exception as e:
                    self.logger.error(f"Failed to create default config: {e}")
                    self.logger.warning("Using empty configuration")
                    return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._parse_config(config_data)
            self.logger.info(f"Loaded configuration with {len(self.folders)} folders")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
    
    def _parse_config(self, config_data: dict[str, Any]) -> None:
        """
        Parse configuration data.
        
        Args:
            config_data: Dictionary containing configuration data.
        """
        self.folders = []
        
        if 'folders' not in config_data:
            self.logger.warning("No 'folders' section in config")
            return
        
        for folder_data in config_data['folders']:
            try:
                # Skip example/comment entries (those that have _comment as first key or missing required fields)
                if '_comment' in folder_data and len(folder_data) <= 3:
                    self.logger.debug("Skipping example/comment entry in config")
                    continue
                
                # Skip entries with placeholder paths
                if folder_data.get('path', '').startswith('/absolute/path/'):
                    self.logger.debug("Skipping example entry with placeholder path")
                    continue
                
                folder_config = FolderConfig(folder_data)
                self.folders.append(folder_config)
                self.logger.debug(f"Added folder config: {folder_config}")
                
            except KeyError as e:
                self.logger.error(f"Missing required field in folder config: {e}")
            except Exception as e:
                self.logger.error(f"Error parsing folder config {folder_data}: {e}")
    
    def get_folder_config(self, file_path: str) -> Optional[FolderConfig]:
        """
        Find folder configuration for a given file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            The first matching folder configuration or None if not found.
        """
        file_path_obj = Path(file_path).resolve()
        
        for folder_config in self.folders:
            try:
                # Check if file is in monitored folder
                folder_path = folder_config.path.resolve()
                if file_path_obj.is_relative_to(folder_path):
                    # Check extension filter
                    if folder_config.should_process_file(file_path_obj):
                        return folder_config
            except Exception as e:
                self.logger.error(f"Error checking folder config: {e}")
                continue
        
        return None
    
    def get_all_folders(self) -> list[FolderConfig]:
        """
        Get all folder configurations.
        
        Returns:
            Copy of the list of folder configurations.
        """
        return self.folders.copy()
