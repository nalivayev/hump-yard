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

from folder_monitor.daemon import FileMonitorDaemon


def get_pid_file() -> Path:
    """
    Get the path to the PID file.
    
    Returns:
        Path to the PID file.
    """
    if sys.platform == 'win32':
        # Windows: use temp directory
        return Path(os.environ.get('TEMP', '.')) / 'folder-monitor.pid'
    else:
        # Unix: try /var/run, fall back to ~/.folder-monitor.pid
        run_dir = Path('/var/run')
        if run_dir.exists() and os.access(run_dir, os.W_OK):
            return run_dir / 'folder-monitor.pid'
        return Path.home() / '.folder-monitor.pid'


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
            # Optimization: Import ctypes only once or at module level if used frequently,
            # but here we keep it local to avoid loading it on non-Windows systems unnecessarily,
            # however, we can avoid re-importing inside the loop if this function is called often.
            # For now, standard implementation is fine, but let's clean it up.
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # PROCESS_QUERY_INFORMATION = 0x0400
            # PROCESS_VM_READ = 0x0010
            
            # Using OpenProcess with minimal rights to check existence
            # 0x1000 is SYNCHRONIZE, which is enough to wait on it, but for checking existence
            # we often use PROCESS_QUERY_LIMITED_INFORMATION (0x1000) on newer Windows
            # or just 0 for some checks, but 0x0400 is standard for query info.
            
            handle = kernel32.OpenProcess(0x0400, 0, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            
            # If OpenProcess failed, it might be because of permissions (Access Denied),
            # which means the process exists.
            # GetLastError() == 5 (ERROR_ACCESS_DENIED)
            if ctypes.GetLastError() == 5:
                return True
                
            return False
        else:
            # Unix: send signal 0 (doesn't kill, just checks)
            os.kill(pid, 0)
            return True
    except (OSError, AttributeError):
        return False


def cmd_start(log_level: str, foreground: bool = False) -> None:
    """
    Start the daemon.
    
    Args:
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
    
    if foreground:
        # Run in foreground
        _run_daemon(log_level)
    else:
        # Daemonize
        if sys.platform == 'win32':
            # Windows: use pythonw or subprocess
            import subprocess
            python_exe = sys.executable
            if not python_exe.lower().endswith('pythonw.exe'):
                # Try to find pythonw.exe in the same directory
                python_dir = os.path.dirname(python_exe)
                pythonw = os.path.join(python_dir, 'pythonw.exe')
                if os.path.exists(pythonw):
                    python_exe = pythonw
            
            # Start detached process
            args = [python_exe, '-m', 'folder_monitor.cli', 'start', '--internal-worker']
            args.extend(['--log-level', log_level])
            
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
            _run_daemon(log_level)


def _run_daemon(log_level: str) -> None:
    """
    Internal function to run the daemon.
    
    Args:
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
        daemon = FileMonitorDaemon()
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


def cmd_restart(log_level: str) -> None:
    """
    Restart the daemon.
    
    Args:
        log_level: Logging level.
    """
    pid = read_pid()
    if pid and is_process_running(pid):
        cmd_stop()
        time.sleep(1)
    
    cmd_start(log_level)


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
    """Entry point for the folder-monitor console command."""
    parser = argparse.ArgumentParser(
        description='Folder Monitor - File monitoring daemon with plugin support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  start       Start the daemon in background
  stop        Stop the daemon
  restart     Restart the daemon
  status      Check daemon status

Examples:
  folder-monitor start                       # Start daemon
  folder-monitor start --foreground          # Run in foreground (Ctrl+C to stop)
  folder-monitor stop                        # Stop daemon
  folder-monitor restart                     # Restart daemon
  folder-monitor status                      # Check status
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['start', 'stop', 'restart', 'status'],
        default='start',
        help='Command to execute (default: start)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.3.0'
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
    
    parser.add_argument(
        '--internal-worker',
        action='store_true',
        help=argparse.SUPPRESS
    )
    
    args = parser.parse_args()
    
    try:
        if args.internal_worker:
            _run_daemon(args.log_level)
        elif args.command == 'start':
            cmd_start(args.log_level, args.foreground)
        elif args.command == 'stop':
            cmd_stop()
        elif args.command == 'restart':
            cmd_restart(args.log_level)
        elif args.command == 'status':
            cmd_status()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        remove_pid_file()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
