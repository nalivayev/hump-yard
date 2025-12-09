"""
Folder Monitor - File monitoring daemon with plugin support.
"""
from folder_monitor.daemon import FileMonitorDaemon
from folder_monitor.base_plugin import FileProcessorPlugin, PluginManager

__all__ = ['FileMonitorDaemon', 'FileProcessorPlugin', 'PluginManager']

__version__ = '0.3.0'
