# Folder Monitor (Hump Yard)

A file system monitoring daemon with plugin support for file processing.

## Description

Folder Monitor (formerly Hump Yard) is a flexible file monitoring system that allows automatic processing of files when they are created in specified folders. The system is built on a plugin architecture, making it easy to extend functionality.

## Features

- 🔍 **Folder Monitoring** - Track new file creation
- 🔌 **Plugin System** - Easy functionality extension
- ⚙️ **Flexible Configuration** - Settings via JSON file
- 🎯 **Extension Filtering** - Process only needed file types
- 📁 **Recursive Monitoring** - Track subfolders
- 📝 **Logging** - Complete system operation information

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nalivayev/hump-yard.git
cd hump-yard
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install the package in development mode:
```bash
pip install -e .
```

Or install with additional dependencies:
```bash
# For development (with code formatters and type checking)
pip install -e ".[dev]"
```

## Configuration

The system uses a plugin-centric configuration approach. Each plugin has its own configuration file located in the `plugins` subdirectory of the main configuration folder.

### Configuration Directory

- **Windows**: `%APPDATA%\folder-monitor\plugins\`
- **Linux/Unix**: `~/.config/folder-monitor/plugins/`

### Plugin Configuration

When you install a new plugin and run `folder-monitor`, the plugin will automatically create a default configuration file (e.g., `rename.json` for the rename plugin) in the plugins directory if it doesn't exist.

You can edit these JSON files to configure which folders to watch and how to process files.

**Example `rename.json`:**

```json
{
  "folders": [
    {
      "path": "C:/Users/YourName/Pictures",
      "recursive": true,
      "prefix": "IMG_",
      "timestamp_format": "%Y%m%d_%H%M%S"
    }
  ]
}
```

### Creating Custom Plugins

To create a custom plugin:

1. Inherit from `FileProcessorPlugin`.
2. Implement `name`, `version`, `can_handle`, and `process`.
3. Create a `config.template.json` file in the same package as your plugin code. This file will be used as a template for the user's configuration.

Example structure:
```
my_plugin/
  __init__.py
  plugin.py
  config.template.json
```

The `config.template.json` should contain a valid JSON structure with example settings.

## Usage

### Daemon Management

```bash
# Start daemon in background (auto-creates config if needed)
folder-monitor start

# Start with logging level
folder-monitor start --log-level DEBUG

# Start in foreground (Ctrl+C to stop)
folder-monitor start --foreground

# Stop daemon
folder-monitor stop

# Restart daemon
folder-monitor restart

# Check daemon status
folder-monitor status

# Show version
folder-monitor --version

# Help
folder-monitor --help
```

**Note**: On first run, folder-monitor will create default configuration files for available plugins in the standard configuration directory (e.g., `~/.config/folder-monitor/plugins/`). Edit these files to configure folders to monitor.

### Using as a Library

```python
from folder_monitor.daemon import FileMonitorDaemon

daemon = FileMonitorDaemon()
daemon.start()
```

## Creating Plugins

To create your own plugin:

1. Create a class inheriting from `FileProcessorPlugin`
2. Implement required methods
3. Place the plugin in the `file_monitor/plugins/` folder

Example plugin:

```python
from file_monitor.base_plugin import FileProcessorPlugin
from typing import Dict, Any

class MyPlugin(FileProcessorPlugin):
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_handle(self, file_path: str) -> bool:
        # Check if the plugin can handle the file
        return file_path.endswith('.txt')
    
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        # File processing logic
        try:
            self.logger.info(f"Processing {file_path}")
            # Your processing code here
            return True
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False
```

## Command Line Options

```
usage: folder-monitor [-h] [-v] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--foreground]
                      {start,stop,restart,status}

Folder Monitor - File monitoring daemon with plugin support

Commands:
  {start,stop,restart,status}
                        Command to execute (default: start)
    start               Start the daemon in background
    stop                Stop the daemon
    restart             Restart the daemon
    status              Check daemon status

Options:
  -h, --help            Show this help message and exit
  -v, --version         Show program's version number and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level (default: INFO)
  --foreground          Run in foreground (for start command)
```

## Requirements

- Python 3.10+
- watchdog >= 2.1.0

## Installation from PyPI

```bash
pip install hump-yard
```

For EXIF plugin support:
```bash
pip install hump-yard[exif]
```

## License

MIT License

## Author

nalivayev
