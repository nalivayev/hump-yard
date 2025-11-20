"""
Command-line interface for hump-yard file monitoring daemon
"""
import argparse
import sys
import os
import signal
import time
import logging
from pathlib import Path
from typing import Optional

from .daemon import FileMonitorDaemon


def get_pid_file() -> Path:
    """
    Get the path to the PID file.
    
    Returns:
        Path to the PID file.
    """
    if sys.platform == 'win32':
        # Windows: use temp directory
        return Path(os.environ.get('TEMP', '.')) / 'hump-yard.pid'
    else:
        # Unix: try /var/run, fall back to ~/.hump-yard.pid
        run_dir = Path('/var/run')
        if run_dir.exists() and os.access(run_dir, os.W_OK):
            return run_dir / 'hump-yard.pid'
        return Path.home() / '.hump-yard.pid'


def read_pid() -> Optional[int]:
    """
    Read PID from PID file.
    
    Returns:
        PID if file exists and is valid, None otherwise.
    """
    pid_file = get_pid_file()
    if not pid_file.exists():
        return None
    
    try:
        pid = int(pid_file.read_text().strip())
        return pid
    except (ValueError, OSError):
        return None


def write_pid(pid: int) -> None:
    """
    Write PID to PID file.
    
    Args:
        pid: Process ID to write.
    """
    pid_file = get_pid_file()
    pid_file.write_text(str(pid))


def remove_pid_file() -> None:
    """Remove PID file."""
    pid_file = get_pid_file()
    if pid_file.exists():
        pid_file.unlink()


def is_process_running(pid: int) -> bool:
    """
    Check if a process is running.
    
    Args:
        pid: Process ID to check.
        
    Returns:
        True if process is running, False otherwise.
    """
    try:
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_INFORMATION = 0x0400
            handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        else:
            # Unix: send signal 0 (doesn't kill, just checks)
            os.kill(pid, 0)
            return True
    except (OSError, AttributeError):
        return False


def cmd_start(config_path: str, log_level: str, foreground: bool = False) -> None:
    """
    Start the daemon.
    
    Args:
        config_path: Path to configuration file.
        log_level: Logging level.
        foreground: Run in foreground (don't daemonize).
    """
    # Check if already running
    pid = read_pid()
    if pid and is_process_running(pid):
        print(f"Error: Daemon is already running (PID: {pid})", file=sys.stderr)
        sys.exit(1)
    
    # Remove stale PID file
    if pid:
        remove_pid_file()
    
    # Check configuration file exists
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    if foreground:
        # Run in foreground
        _run_daemon(config_path, log_level)
    else:
        # Daemonize
        if sys.platform == 'win32':
            # Windows: use pythonw or subprocess
            import subprocess
            python_exe = sys.executable
            if not python_exe.endswith('pythonw.exe'):
                pythonw = python_exe.replace('python.exe', 'pythonw.exe')
                if Path(pythonw).exists():
                    python_exe = pythonw
            
            # Start detached process
            args = [python_exe, '-m', 'hump_yard.cli', '_run', '-c', config_path, '--log-level', log_level]
            subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            time.sleep(1)  # Wait for process to start
            
            # Verify it started
            pid = read_pid()
            if pid and is_process_running(pid):
                print(f"Daemon started successfully (PID: {pid})")
            else:
                print("Error: Failed to start daemon", file=sys.stderr)
                sys.exit(1)
        else:
            # Unix: fork
            pid = os.fork()
            if pid > 0:
                # Parent process
                time.sleep(1)  # Wait for child to start
                child_pid = read_pid()
                if child_pid and is_process_running(child_pid):
                    print(f"Daemon started successfully (PID: {child_pid})")
                else:
                    print("Error: Failed to start daemon", file=sys.stderr)
                    sys.exit(1)
                sys.exit(0)
            
            # Child process
            os.setsid()
            _run_daemon(config_path, log_level)


def _run_daemon(config_path: str, log_level: str) -> None:
    """
    Internal function to run the daemon.
    
    Args:
        config_path: Path to configuration file.
        log_level: Logging level.
    """
    # Write PID
    write_pid(os.getpid())
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        remove_pid_file()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Configure logging level
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create and start daemon
        daemon = FileMonitorDaemon(config_path)
        daemon.start()
    except Exception as e:
        logging.error(f"Daemon error: {e}", exc_info=True)
        remove_pid_file()
        sys.exit(1)


def cmd_stop() -> None:
    """Stop the daemon."""
    pid = read_pid()
    if not pid:
        print("Daemon is not running (no PID file found)", file=sys.stderr)
        sys.exit(1)
    
    if not is_process_running(pid):
        print(f"Daemon is not running (PID {pid} not found)", file=sys.stderr)
        remove_pid_file()
        sys.exit(1)
    
    print(f"Stopping daemon (PID: {pid})...")
    
    try:
        if sys.platform == 'win32':
            # Windows: use taskkill or ctypes
            os.system(f'taskkill /PID {pid} /F >nul 2>&1')
        else:
            # Unix: send SIGTERM
            os.kill(pid, signal.SIGTERM)
        
        # Wait for process to stop
        for _ in range(10):
            time.sleep(0.5)
            if not is_process_running(pid):
                remove_pid_file()
                print("Daemon stopped successfully")
                return
        
        # Force kill if still running
        print("Warning: Daemon did not stop gracefully, force killing...")
        if sys.platform == 'win32':
            os.system(f'taskkill /PID {pid} /F >nul 2>&1')
        else:
            os.kill(pid, signal.SIGKILL)
        
        remove_pid_file()
        print("Daemon force killed")
        
    except OSError as e:
        print(f"Error stopping daemon: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_restart(config_path: str, log_level: str) -> None:
    """
    Restart the daemon.
    
    Args:
        config_path: Path to configuration file.
        log_level: Logging level.
    """
    pid = read_pid()
    if pid and is_process_running(pid):
        cmd_stop()
        time.sleep(1)
    
    cmd_start(config_path, log_level)


def cmd_status() -> None:
    """Check daemon status."""
    pid = read_pid()
    if not pid:
        print("Daemon is not running (no PID file found)")
        sys.exit(3)
    
    if is_process_running(pid):
        print(f"Daemon is running (PID: {pid})")
        sys.exit(0)
    else:
        print(f"Daemon is not running (stale PID file: {pid})")
        remove_pid_file()
        sys.exit(3)


def main() -> None:
    """Entry point for the hump-yard console command."""
    parser = argparse.ArgumentParser(
        description='Hump Yard - File monitoring daemon with plugin support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  start       Start the daemon in background
  stop        Stop the daemon
  restart     Restart the daemon
  status      Check daemon status

Examples:
  hump-yard start                      # Start with config.json
  hump-yard start -c /path/config.json # Start with custom config
  hump-yard stop                        # Stop daemon
  hump-yard restart                     # Restart daemon
  hump-yard status                      # Check status
  hump-yard start --foreground          # Run in foreground (Ctrl+C to stop)
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['start', 'stop', 'restart', 'status', '_run'],
        default='start',
        help='Command to execute (default: start)'
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
        version='%(prog)s 0.2.0'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--foreground',
        action='store_true',
        help='Run in foreground (for start command)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'start':
            cmd_start(args.config, args.log_level, args.foreground)
        elif args.command == 'stop':
            cmd_stop()
        elif args.command == 'restart':
            cmd_restart(args.config, args.log_level)
        elif args.command == 'status':
            cmd_status()
        elif args.command == '_run':
            # Internal command for Windows daemonization
            _run_daemon(args.config, args.log_level)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        remove_pid_file()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
