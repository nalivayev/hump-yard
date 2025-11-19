"""
Command-line interface for hump-yard file monitoring daemon
"""
import argparse
import sys
from pathlib import Path

from .daemon import FileMonitorDaemon


def main() -> None:
    """Entry point for the hump-yard console command."""
    parser = argparse.ArgumentParser(
        description='Hump Yard - File monitoring daemon with plugin support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hump-yard                          # Run with config.json in current directory
  hump-yard -c /path/to/config.json  # Run with custom config file
  hump-yard --config my_config.json  # Same as above
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Check configuration file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        print(f"Please create a config.json file or specify a valid path with -c option.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create and start daemon
        daemon = FileMonitorDaemon(str(config_path))
        daemon.start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
