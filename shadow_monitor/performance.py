import time
from threading import Thread

import psutil
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from .logger import get_console
from .thread import get_running
from .config import settings


def bytes_to_gb(_bytes):
    gb = _bytes / (1024 ** 3)
    return gb


performance_table = Table.grid()
_performance_progress = Progress(
    TextColumn("{task.description}"),
    BarColumn(),
    TaskProgressColumn()
)
_cpu_task = _performance_progress.add_task("[cyan]CPU", total=100)
_memory_task = _performance_progress.add_task("[cyan]Memory", total=100)
_swap_task = _performance_progress.add_task("[cyan]Swap", total=100)
_cpu_percent = 0.0
_virtual_memory_percent = 0.0
_swap_memory_percent = 0.0


def log_performance():
    time.sleep(1.5)
    while get_running():
        logger = get_console()
        logger.log(
            f"CPU: {_cpu_percent:>3.2f}%  MEM: {_virtual_memory_percent:>3.2f}%  SWAP: {_swap_memory_percent:>3.2f}%")
        if _cpu_percent > settings.cpu_warning:
            logger.log(f"CPU预警:{_cpu_percent:>3.2f}%(预警线{settings.cpu_warning}%)")
        if _virtual_memory_percent > settings.memory_warning:
            logger.log(f"MEM预警:{_virtual_memory_percent:>3.2f}%(预警线{settings.memory_warning}%)")
        time.sleep(settings.log_interval)


def update_performance_table():
    global _cpu_percent, _virtual_memory_percent, _swap_memory_percent
    _cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
    virtual_memory = psutil.virtual_memory()
    swap_memory = psutil.swap_memory()
    _virtual_memory_percent = virtual_memory.percent
    _swap_memory_percent = swap_memory.percent

    _performance_progress.update(_cpu_task, completed=_cpu_percent)
    _performance_progress.update(_memory_task, completed=_virtual_memory_percent)
    _performance_progress.update(_swap_task, completed=_swap_memory_percent)
    performance_table.columns[0]._cells[1] = (Text()
                                              .append("Memory Detail:", style="cyan")
                                              .append(
        f"{bytes_to_gb(virtual_memory.used): .2f} /{bytes_to_gb(virtual_memory.total):>5.2f} GiB", style="magenta")
                                              .append(" Free:", style="cyan")
                                              .append(f"{bytes_to_gb(virtual_memory.available):>5.2f} GiB",
                                                      style="magenta")
                                              )

    performance_table.columns[0]._cells[2] = (Text()
                                              .append("Swap   Detail:", style="cyan")
                                              .append(
        f"{bytes_to_gb(swap_memory.used): .2f} /{bytes_to_gb(swap_memory.total):>5.2f} GiB", style="magenta")
                                              .append(" Free:", style="cyan")
                                              .append(f"{bytes_to_gb(swap_memory.free):>5.2f} GiB", style="magenta")
                                              )


def init_performance_table():
    performance_table.add_row(_performance_progress)
    performance_table.add_row(
        Text()
        .append("Memory Detail:", style="cyan")
        .append(" 00.00 / 00.00 GiB", style="magenta")
        .append(" Free:", style="cyan")
        .append(" 00.00 GiB", style="magenta")
    )
    performance_table.add_row(
        Text()
        .append("Swap   Detail:", style="cyan")
        .append(" 00.00 / 00.00 GiB", style="magenta")
        .append(" Free:", style="cyan")
        .append(" 00.00 GiB", style="magenta")
    )


log_performance_thread = Thread(target=log_performance)
