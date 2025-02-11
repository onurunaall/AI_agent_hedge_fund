# new_project/src/utils/progress.py

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.style import Style
from typing import Dict

console = Console()

class ProgressTracker:
    """Handles progress tracking and status updates for backtesting."""
    def __init__(self):
        self.status: Dict[str, str] = {}
        self.table = Table(show_header=False, box=None, padding=(0, 1))
        self.live = Live(self.table, console=console, refresh_per_second=4)
        self.started = False

    def start(self):
        if not self.started:
            self.live.start()
            self.started = True

    def stop(self):
        if self.started:
            self.live.stop()
            self.started = False

    def update_status(self, task: str, message: str) -> None:
        self.status[task] = message
        self._refresh_display()

    def _refresh_display(self):
        self.table.columns.clear()
        self.table.add_column(width=100)
        for task, message in self.status.items():
            self.table.add_row(f"[cyan]{task}:[/cyan] {message}")

    def get_status(self) -> Dict[str, str]:
        return self.status
