# Examples for Folder Monitor

This folder contains example configuration files to demonstrate folder-monitor capabilities.

## Files

### config.example.json
Example configuration file with various folder monitoring setup options.

**Contains examples of:**
- Monitoring with recursive file search
- File extension filtering
- Built-in plugin usage (rename)
- Passing parameters to plugins

## Built-in Plugin Templates

Folder Monitor comes with a plugin template that serves as a starting point:

### rename
Plugin for file renaming operations.

**Status:** Ready to use

**Note:** This is a starter template. You can use it as a reference for creating your own plugins.

## How to Use Examples

### 1. Using the example configuration

```bash
# Copy and edit the configuration
cp examples/config.example.json config.json
# Edit paths in config.json for your system
```

### 2. Run

```bash
folder-monitor -c config.json
```

## Creating Your Own Plugin

Use the examples as a template for creating your own plugins:

```python
from folder_monitor.base_plugin import FileProcessorPlugin
from typing import Dict, Any

class MyPlugin(FileProcessorPlugin):
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_handle(self, file_path: str) -> bool:
        # Your validation logic
        return True
    
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        # Your processing logic
        self.logger.info(f"Processing {file_path}")
        return True
```

## Additional Resources

- [Documentation](../README.md)
- [API Reference](../src/folder_monitor/)
