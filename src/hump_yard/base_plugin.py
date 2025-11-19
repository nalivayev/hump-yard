"""
Base classes for file processing plugins.
"""
import abc
import logging
from typing import Dict, Any
import importlib
import pkgutil
import sys
from pathlib import Path
from typing import Type, List, Optional


class FileProcessorPlugin(abc.ABC):
    """
    Abstract base class for all file processing plugins.
    
    Attributes:
        logger: Logger instance for the plugin.
    """
    
    def __init__(self) -> None:
        """Initialize the plugin with a logger."""
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Get the unique name of the plugin.
        
        Returns:
            The plugin name.
        """
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            The plugin version string.
        """
        pass
    
    @abc.abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """
        Check if the plugin can handle the given file.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if the plugin can process the file, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        """
        Process the file.
        
        Args:
            file_path: Path to the file to process.
            config: Plugin-specific configuration parameters.
            
        Returns:
            True if processing was successful, False otherwise.
        """
        pass
    
    def on_error(self, file_path: str, error: Exception) -> None:
        """
        Handle errors during file processing.
        
        Can be overridden in subclasses for custom error handling.
        
        Args:
            file_path: Path to the file that caused the error.
            error: The exception that occurred.
        """
        self.logger.error(f"Error processing {file_path}: {error}")


class PluginManager:
    """
    Manager for loading and managing file processing plugins.
    
    Attributes:
        plugins: Dictionary mapping plugin names to plugin instances.
        logger: Logger instance for the manager.
    """
    
    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self.plugins: Dict[str, FileProcessorPlugin] = {}
        self._discovered_plugins: Dict[str, Any] = {}
        self.logger: logging.Logger = logging.getLogger("PluginManager")
    
    def register_plugin(self, plugin_class: Type[FileProcessorPlugin]) -> None:
        """
        Register a plugin class.
        
        Args:
            plugin_class: The plugin class to register.
            
        Raises:
            ValueError: If a plugin with the same name is already registered.
        """
        plugin_instance = plugin_class()
        if plugin_instance.name in self.plugins:
            raise ValueError(f"Plugin '{plugin_instance.name}' already registered")
        
        self.plugins[plugin_instance.name] = plugin_instance
        self.logger.info(f"Registered plugin: {plugin_instance.name} v{plugin_instance.version}")
    
    def discover_plugins(self, package_name: str) -> None:
        """
        Automatically discover plugins in a package.
        
        Args:
            package_name: Name of the package to search for plugins.
        """
        try:
            package = importlib.import_module(package_name)
            package_path = Path(package.__file__).parent
            
            for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
                if is_pkg:
                    continue
                
                full_module_name = f"{package_name}.{module_name}"
                self._load_plugins_from_module(full_module_name)
                
        except ImportError as e:
            self.logger.error(f"Error discovering plugins in {package_name}: {e}")
    
    def _load_plugins_from_module(self, module_name: str) -> None:
        """
        Load plugins from a module.
        
        Args:
            module_name: Name of the module to load plugins from.
        """
        try:
            module = importlib.import_module(module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    issubclass(attr, FileProcessorPlugin) and 
                    attr != FileProcessorPlugin):
                    
                    self.register_plugin(attr)
                    
        except Exception as e:
            self.logger.error(f"Error loading plugins from {module_name}: {e}")
    
    def discover_external_plugins(self) -> None:
        """Discover plugins from external packages via entry points."""
        try:
            import importlib.metadata
            discovered_plugins = importlib.metadata.entry_points(group='file_monitor.plugins')
            
            for entry_point in discovered_plugins:
                try:
                    plugin_class = entry_point.load()
                    self.register_plugin(plugin_class)
                except Exception as e:
                    self.logger.error(f"Error loading plugin from entry point {entry_point.name}: {e}")
                    
        except ImportError:
            # For Python < 3.8 use pkg_resources
            try:
                import pkg_resources
                discovered_plugins = pkg_resources.iter_entry_points('file_monitor.plugins')
                
                for entry_point in discovered_plugins:
                    try:
                        plugin_class = entry_point.load()
                        self.register_plugin(plugin_class)
                    except Exception as e:
                        self.logger.error(f"Error loading plugin from entry point {entry_point.name}: {e}")
            except ImportError:
                self.logger.warning("Entry points not supported")
    
    def get_plugin(self, name: str) -> Optional[FileProcessorPlugin]:
        """
        Get a plugin by name.
        
        Args:
            name: Name of the plugin.
            
        Returns:
            The plugin instance or None if not found.
        """
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """
        Get a list of all registered plugin names.
        
        Returns:
            List of plugin names.
        """
        return list(self.plugins.keys())
