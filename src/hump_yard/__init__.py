"""
Hump Yard - File monitoring daemon with plugin support.
"""
from .daemon import FileMonitorDaemon
from .base_plugin import FileProcessorPlugin, PluginManager

__all__ = ['FileMonitorDaemon', 'FileProcessorPlugin', 'PluginManager']

__version__ = '0.3.0'
