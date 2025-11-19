# Examples for Hump Yard

This folder contains example configuration files to demonstrate hump-yard capabilities.

## Files

### config.example.json
Example configuration file with various folder monitoring setup options.

**Contains examples of:**
- Monitoring with recursive file search
- File extension filtering
- Built-in plugin usage (rename, exif)
- Passing parameters to plugins

## Built-in Plugin Templates

Hump Yard comes with two plugin templates that serve as starting points:

### rename
Plugin template for file renaming operations.

**Status:** Template (full implementation coming soon)

### exif
Plugin template for EXIF data extraction from images.

**Status:** Template (full implementation coming soon)

**Note:** These are starter templates. You can use them as a reference for creating your own plugins.

## How to Use Examples

### 1. Using the example configuration

```bash
# Copy and edit the configuration
cp examples/config.example.json config.json
# Edit paths in config.json for your system
```

### 2. Run

```bash
hump-yard -c config.json
```

## Creating Your Own Plugin

Use the examples as a template for creating your own plugins:

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
        # Your validation logic
        return True
    
    def process(self, file_path: str, config: Dict[str, Any]) -> bool:
        # Your processing logic
        self.logger.info(f"Processing {file_path}")
        return True
```

## Additional Resources

- [Documentation](../README.md)
- [API Reference](../src/hump_yard/)
