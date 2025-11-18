# plugin_base.py
import abc
import logging
from typing import Dict, Any

class FileProcessorPlugin(abc.ABC):
    """Базовый класс для всех плагинов обработки файлов"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Уникальное имя плагина"""
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Версия плагина"""
        pass
    
    @abc.abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """
        Проверяет, может ли плагин обработать данный файл
        """
        pass
    
    @abc.abstractmethod
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        """
        Обрабатывает файл
        Returns: True если обработка успешна
        """
        pass
    
    def on_error(self, file_path: str, error: Exception):
        """Обработчик ошибок (можно переопределить)"""
        self.logger.error(f"Error processing {file_path}: {error}")


# plugin_base.py (продолжение)
import importlib
import pkgutil
import sys
from pathlib import Path

class PluginManager:
    """Менеджер для загрузки и управления плагинами"""
    
    def __init__(self):
        self.plugins: Dict[str, FileProcessorPlugin] = {}
        self._discovered_plugins = {}
    
    def register_plugin(self, plugin_class):
        """Регистрирует класс плагина"""
        plugin_instance = plugin_class()
        if plugin_instance.name in self.plugins:
            raise ValueError(f"Plugin '{plugin_instance.name}' already registered")
        
        self.plugins[plugin_instance.name] = plugin_instance
        print(f"Registered plugin: {plugin_instance.name} v{plugin_instance.version}")
    
    def discover_plugins(self, package_name: str):
        """Автоматически обнаруживает плагины в пакете"""
        try:
            package = importlib.import_module(package_name)
            package_path = Path(package.__file__).parent
            
            for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
                if is_pkg:
                    continue
                
                full_module_name = f"{package_name}.{module_name}"
                self._load_plugins_from_module(full_module_name)
                
        except ImportError as e:
            print(f"Error discovering plugins in {package_name}: {e}")
    
    def _load_plugins_from_module(self, module_name: str):
        """Загружает плагины из модуля"""
        try:
            module = importlib.import_module(module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    issubclass(attr, FileProcessorPlugin) and 
                    attr != FileProcessorPlugin):
                    
                    self.register_plugin(attr)
                    
        except Exception as e:
            print(f"Error loading plugins from {module_name}: {e}")
    
    def discover_external_plugins(self):
        """Обнаруживает плагины из внешних пакетов через entry points"""
        try:
            import importlib.metadata
            discovered_plugins = importlib.metadata.entry_points(group='file_monitor.plugins')
            
            for entry_point in discovered_plugins:
                try:
                    plugin_class = entry_point.load()
                    self.register_plugin(plugin_class)
                except Exception as e:
                    print(f"Error loading plugin from entry point {entry_point.name}: {e}")
                    
        except ImportError:
            # Для Python < 3.8 используем pkg_resources
            try:
                import pkg_resources
                discovered_plugins = pkg_resources.iter_entry_points('file_monitor.plugins')
                
                for entry_point in discovered_plugins:
                    try:
                        plugin_class = entry_point.load()
                        self.register_plugin(plugin_class)
                    except Exception as e:
                        print(f"Error loading plugin from entry point {entry_point.name}: {e}")
            except ImportError:
                print("Entry points not supported")
    
    def get_plugin(self, name: str) -> FileProcessorPlugin:
        """Возвращает плагин по имени"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> list:
        """Возвращает список всех зарегистрированных плагинов"""
        return list(self.plugins.keys())
