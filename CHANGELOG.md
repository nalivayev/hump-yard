# Changelog

## [0.1.0] - 2025-11-19

### Fixed
- ✅ Fixed typo in package name (hamp_yard → hump_yard)
- ✅ Fixed imports in daemon.py (plugin_base → base_plugin)
- ✅ Fixed plugin path (file_monitor.plugins → hump_yard.plugins)
- ✅ Added exception handling in daemon.py for plugin calls
- ✅ Fixed comments in files (removed incorrect filename references)
- ✅ Replaced all print() with logger usage in base_plugin.py
- ✅ Added Python < 3.9 compatibility (replaced is_relative_to())

### Added
- ✅ Created pyproject.toml with modern project configuration
- ✅ Created README.md with complete documentation
- ✅ Created LICENSE (MIT)
- ✅ Updated .gitignore for full coverage
- ✅ Created config.example.json with configuration example
- ✅ Added plugin templates:
  - rename_plugin.py - template for file renaming plugin (full implementation coming soon)
  - exif_plugin.py - template for EXIF extraction plugin (full implementation coming soon)
- ✅ Added type hints to PluginManager
- ✅ Added optional dependencies for exif and dev environments
- ✅ Configured development tools (black, pytest, mypy) in pyproject.toml

### Improved
- Improved error handling in all modules
- Added logging to all critical points
- Improved code documentation
- Added entry point support for hump-yard console command
- Split daemon.py into two modules: daemon.py (class) and cli.py (CLI interface)
- Added command line arguments: --config, --log-level, --version
- Added complete type hints in all modules (daemon, cli, base_plugin, config_reader)
- Translated all code, comments, and documentation to English

### Requirements
- Python >= 3.7
- watchdog >= 2.1.0
- Pillow (optional, for exif_plugin)
