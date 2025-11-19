# Hump Yard

A file system monitoring daemon with plugin support for file processing.

## Description

Hump Yard is a flexible file monitoring system that allows automatic processing of files when they are created in specified folders. The system is built on a plugin architecture, making it easy to extend functionality.

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
# For EXIF plugin support
pip install -e ".[exif]"

# For development (with tests and linters)
pip install -e ".[dev]"

# Everything together
pip install -e ".[exif,dev]"
```

## Configuration

Create a `config.json` file with the following structure:

```json
{
  "folders": [
    {
      "path": "/absolute/path/to/folder",
      "recursive": true,
      "extensions": [".jpg", ".png", ".pdf"],
      "plugin": "plugin_name"
    }
  ]
}
```

### Configuration Parameters:

- **path** - Absolute path to the folder to monitor
- **recursive** - Whether to track subfolders (true/false)
- **extensions** - List of file extensions to process (optional)
- **plugin** - Name of the plugin to process files

## Usage

### Running from Command Line

```bash
# Run with config.json in current directory
hump-yard

# With custom configuration path
hump-yard -c /path/to/config.json

# With logging level
hump-yard --log-level DEBUG

# Show version
hump-yard --version

# Help
hump-yard --help
```

### Using as a Library

```python
from hump_yard import FileMonitorDaemon

daemon = FileMonitorDaemon("config.json")
daemon.start()
```

## Creating Plugins

To create your own plugin:

1. Create a class inheriting from `FileProcessorPlugin`
2. Implement required methods
3. Place the plugin in the `hump_yard/plugins/` folder

Example plugin:

```python
from hump_yard.base_plugin import FileProcessorPlugin
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
usage: hump-yard [-h] [-c CONFIG] [-v] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Hump Yard - File monitoring daemon with plugin support

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file (default: config.json)
  -v, --version         show program's version number and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level (default: INFO)
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

- Python 3.7+
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
