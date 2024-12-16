import time
from datetime import timedelta

import psutil
from rich import box
from rich.table import Table

processes = [i for i in psutil.process_iter()]


def update_process_table():
    process_table = Table(box=box.ROUNDED, expand=True)
    process_table.add_column("PID", style="cyan")
    process_table.add_column("Name", style="magenta")
    process_table.add_column("CPU", style="green", width=6)
    process_table.add_column("MEM", style="green", width=6)
    process_table.add_column("TIME", style="green")

    process_list = []
    t = time.time()
    # 打印所有进程的详细信息
    for process in processes:
        if not process.is_running():
            continue
        process_list.append(
            (f"{process.pid}", f"{process.name()}", f"{process.cpu_percent(interval=0):.2f}",
             f"{process.memory_percent():.2f}", f"{str(timedelta(seconds=int(t - process.create_time())))}"))
    process_list.sort(key=lambda item: -float(item[2]))
    process_table.rows.clear()
    for i in range(min(len(process_list), 15)):
        process_table.add_row(*process_list[i])
    return process_table
