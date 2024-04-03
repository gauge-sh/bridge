from contextlib import contextmanager
from datetime import datetime

from rich.console import Console


@contextmanager
def log_task(start_message, end_message):
    console = Console()
    with console.status(
        f"      {start_message}", spinner="aesthetic", spinner_style="blue"
    ):
        try:
            # Before entering the block
            yield
        finally:
            # After exiting the block

            # Format the current time to include leading zeros (HH:MM:SS)
            timestamp_str = datetime.now().strftime("[%H:%M:%S]")
            console.print(
                f"{timestamp_str} [bright_green]✓[/bright_green] {end_message}",
                highlight=False,
            )


def log_error(message):
    console = Console()
    console.print(f"[bright_red]✗ Bridge Error[/bright_red]: {message}")


def log_warning(message):
    console = Console()
    console.print(f"[yellow]Bridge Warning[/yellow]: {message}")
