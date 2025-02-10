# src/utils/progress.py

from colorama import Fore, Style


class ProgressTracker:
    """Handles progress tracking and status updates for backtesting."""

    def __init__(self):
        self.status = {}

    def update_status(self, task: str, message: str) -> None:
        """Updates the status of a given task in the backtesting process."""
        self.status[task] = message
        print(f"{Fore.CYAN}[Progress] {task}: {message}{Style.RESET_ALL}")

    def get_status(self) -> dict:
        """Returns the current status of all tracked tasks."""
        return self.status
