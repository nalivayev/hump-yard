# Changelog

## [Unreleased]

### Changed
- ✅ **Package renamed from `hump_yard` to `file_monitor`** - More descriptive package name
  - Repository name remains `hump-yard`
  - CLI command changed from `hump-yard` to `folder-monitor`
  - Import path changed: `from file_monitor import ...`

### Added
- ✅ **Automatic configuration creation** - Default config is created on first run
- ✅ **Standard config paths** - Uses platform-specific config directories:
  - Windows: `%APPDATA%\hump-yard\config.json`
  - Linux/Unix: `~/.config/hump-yard/config.json`
- ✅ **Config priority system** - Searches for config in multiple locations:
  1. `./config.json` (current directory)
  2. Standard config directory
  3. Custom path with `-c` option
- ✅ **Template-based config** - Ships with `config.template.json` in package

### Changed
- ✅ `ConfigReader` now accepts `None` as config_path (auto-detection)
- ✅ `FileMonitorDaemon` now accepts `None` as config_path
- ✅ CLI no longer requires config file to exist before starting

### Removed
- ✅ Removed redundant `src/hump_yard/config.json` (kept only template)
- ✅ Removed `[tool.setuptools.package-data]` for `*.json` files

## [0.3.0] - 2025-11-25

### Changed
- ✅ **Minimum Python version raised to 3.10+**
- ✅ Simplified code by using `Path.is_relative_to()` (available since Python 3.9)
- ✅ Simplified entry points discovery using stable Python 3.10+ API
- ✅ Replaced deprecated `_getexif()` with `getexif()` in EXIF plugin
- ✅ Improved type hints and removed compatibility workarounds
- ✅ Updated all package docstrings to follow PEP 257

### Removed
- ✅ Removed test dependencies (pytest, pytest-cov) - no tests in project yet
- ✅ Removed flake8 dependency - using black for formatting
- ✅ Removed pytest configuration from pyproject.toml

### Fixed
- ✅ Fixed type checking issues in `base_plugin.py` and `daemon.py`
- ✅ Fixed import issues by using `importlib.metadata` instead of deprecated `pkg_resources`
- ✅ Added proper None checks for `package.__file__`

## [0.2.0] - 2025-11-20

### Added
- ✅ **Daemon management commands:** start, stop, restart, status
- ✅ **PID file management** for tracking daemon process
- ✅ **Signal handlers** for graceful shutdown (SIGTERM, SIGINT)
- ✅ **Background execution** (daemonize on Unix, detached process on Windows)
- ✅ **Foreground mode** with --foreground flag for debugging
- ✅ **Process status checking** across Windows and Unix platforms

### Improved
- Complete CLI rewrite with proper daemon management
- Cross-platform support for Windows and Unix
- Better error handling and user feedback
- Updated documentation with new command examples

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
- Python >= 3.10
- watchdog >= 2.1.0
- Pillow (optional, for exif_plugin)
