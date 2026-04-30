import sys
from datetime import datetime

class Colors:
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def _get_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")

def log_info(msg: str) -> None:
    print(f"{Colors.INFO}[{_get_timestamp()}] ℹ️  {msg}{Colors.RESET}")

def log_success(msg: str) -> None:
    print(f"{Colors.SUCCESS}[{_get_timestamp()}] ✅ {msg}{Colors.RESET}")

def log_warning(msg: str) -> None:
    print(f"{Colors.WARNING}[{_get_timestamp()}] ⚠️  {msg}{Colors.RESET}")

def log_error(msg: str) -> None:
    print(f"{Colors.ERROR}[{_get_timestamp()}] ❌ {msg}{Colors.RESET}")

def log_header(msg: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.INFO}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.INFO}{msg.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.INFO}{'='*60}{Colors.RESET}\n")