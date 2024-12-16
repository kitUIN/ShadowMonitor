from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from shadow_monitor.network_background import network_background_thread
from .logger import set_console, get_console, set_network_console
from .network import update_network_table, init_network_table, network_table, sniff_thread, \
    network_thread, log_network_thread
from .performance import init_performance_table, performance_table, update_performance_table, log_performance_thread
from .process import update_process_table
from .thread import set_running

main_table = Table.grid()
top_table = Table.grid(expand=True)


def init_top_table():
    top_table.add_row(
        Panel.fit(
            performance_table, title="[b]Performance", border_style="green", padding=(1, 2)
        ),
        Panel.fit(
            network_table, title="[b]Network", border_style="green", padding=(1, 2)
        ),
    )
    main_table.add_row(top_table)
    main_table.add_row(update_process_table())


def run_main_task():
    file = open("log.txt", "a+")
    set_console(file)
    file = open("net_link_log.txt", "a+")
    set_network_console(file)
    logger = get_console()
    logger.log("程序启动")
    init_performance_table()
    init_network_table()
    init_top_table()
    sniff_thread.start()
    network_thread.start()
    network_background_thread.start()
    log_performance_thread.start()
    log_network_thread.start()
    try:
        with Live(main_table, refresh_per_second=1) as live:
            while True:
                update_performance_table()
                update_network_table()
                main_table.columns[0]._cells[1] = update_process_table()
    except Exception as e:
        print(e)
    finally:
        file.close()
        set_running(False)


if __name__ == "__main__":
    run_main_task()
