"""
Configuration reader for folder monitoring settings.
"""
import sys
import os
from pathlib import Path


def get_config_dir() -> Path:
    """
    Get the standard configuration directory for hump-yard.
    
    Returns:
        Path to the configuration directory.
    """
    if sys.platform == 'win32':
        # Windows: %APPDATA%\folder-monitor
        config_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'folder-monitor'
    else:
        # Linux/Unix: ~/.config/folder-monitor
        config_dir = Path.home() / '.config' / 'folder-monitor'
    
    return config_dir

