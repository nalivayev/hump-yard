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

On first run, folder-monitor automatically creates a default configuration file with detailed examples and parameter descriptions:
- **Windows**: `%APPDATA%\folder-monitor\config.json` (e.g., `C:\Users\YourName\AppData\Roaming\folder-monitor\config.json`)
- **Linux/Unix**: `~/.config/folder-monitor/config.json`

You can also place `config.json` in the current directory - it will be used with higher priority.

The generated config file contains inline documentation and example entries. Edit it to add your folders to monitor:

```json
{
  "folders": [
    {
      "path": "C:/Users/YourName/Pictures",
      "plugin": "rename",
      "recursive": true,
      "extensions": [".jpg", ".jpeg", ".png", ".tiff"],
      "prefix": "IMG_"
    }
  ]
}
```

**Note:** Remove or modify the example entries in the generated config file. Placeholder paths (starting with `/absolute/path/`) are automatically skipped.

### Configuration Parameters:

#### Required Parameters:
- **path** - Absolute path to the folder to monitor
- **plugin** - Name of the plugin to process files

#### Optional Parameters:
- **recursive** - Monitor subfolders recursively (default: `false`)
- **extensions** - List of file extensions to process (default: all files)
  - Example: `[".jpg", ".jpeg", ".png", ".tiff", ".tif"]`
  - If omitted, all file types will be processed

#### Plugin-Specific Parameters:
Each plugin may accept additional parameters. Add them directly to the folder configuration entry. Refer to your plugin's documentation for available options.

### Configuration File Locations:

The daemon searches for configuration in the following order:
1. `./config.json` - Current directory (highest priority)
2. Standard config directory (platform-specific, as shown above)
3. Custom path specified with `-c` option

## Usage

### Daemon Management

```bash
# Start daemon in background (auto-creates config if needed)
folder-monitor start

# Start with custom config file
folder-monitor start -c /path/to/config.json

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

**Note**: On first run without existing config, folder-monitor creates a default empty configuration file in the standard location. Edit it to add folders to monitor.

### Using as a Library

```python
from file_monitor import FileMonitorDaemon

daemon = FileMonitorDaemon("config.json")
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
usage: folder-monitor [-h] [-c CONFIG] [-v] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--foreground]
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
  -c CONFIG, --config CONFIG
                        Path to configuration file (default: config.json)
  -v, --version         Show program's version number and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level (default: INFO)
  --foreground          Run in foreground (for start command)
```

## Project Structure

```
hump-yard/
├── src/
│   └── hump_yard/
│       ├── __init__.py
│       ├── base_plugin.py      # Base classes for plugins
│       ├── cli.py              # CLI interface
│       ├── config_reader.py    # Configuration reading
│       ├── daemon.py            # Daemon class
│       └── plugins/             # Plugin templates
│           ├── __init__.py
│           ├── rename_plugin.py  # Template for renaming plugin
│           └── exif_plugin.py    # Template for EXIF plugin
├── examples/                    # Configuration examples
│   ├── config.example.json
│   └── README.md
├── pyproject.toml               # Project configuration and dependencies
├── LICENSE                      # MIT License
└── README.md                    # Documentation
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
