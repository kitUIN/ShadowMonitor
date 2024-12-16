import psutil
from rich.table import Table
from rich.text import Text
from scapy.all import *
from scapy.layers.inet import TCP, UDP

from .config import settings
from .logger import get_network_console
from .thread import get_running


def read_bytes(_bytes):
    kb = _bytes / 1024
    if kb < 100:
        return f"{kb:>6.2f} KB"
    mb = kb / 1024
    if mb < 100:
        return f"{mb:>6.2f} MB"
    gb = mb / 1024
    if gb < 100:
        return f"{gb:>6.2f} GB"
    tb = gb / 1024
    return f"{tb:>6.2f} TB"


tcp_links = []
udp_links = []
tcp_count = 0
udp_count = 0
tcp_link_count = 0
udp_link_count = 0
upload_speed = "0"
download_speed = "0"
upload_speed_bytes = 0
download_speed_bytes = 0
network_table = Table.grid()


def log_network():
    time.sleep(1.5)
    while get_running():
        logger = get_network_console()
        logger.log(
            f"Upload Speed: {upload_speed}/s Download Speed: {download_speed}/s")
        if upload_speed_bytes > settings.upload_speed_warning:
            logger.log(
                f"上传速度预警:{read_bytes(upload_speed_bytes)}/s(预警线{read_bytes(settings.upload_speed_warning)}/s)")
        if download_speed_bytes > settings.download_speed_warning:
            logger.log(
                f"下载速度预警:{read_bytes(download_speed_bytes)}/s(预警线{read_bytes(settings.download_speed_warning)}/s)")
        time.sleep(settings.log_interval)


def get_bandwidth():
    while get_running():
        old_sent = psutil.net_io_counters().bytes_sent
        old_recv = psutil.net_io_counters().bytes_recv
        time.sleep(1)
        new_sent = psutil.net_io_counters().bytes_sent
        new_recv = psutil.net_io_counters().bytes_recv
        global upload_speed, download_speed, upload_speed_bytes, download_speed_bytes, tcp_links, tcp_link_count, udp_links, udp_link_count
        upload_speed_bytes = new_sent - old_sent
        upload_speed = read_bytes(upload_speed_bytes)
        download_speed_bytes = new_recv - old_recv
        download_speed = read_bytes(download_speed_bytes)
        tcp_links = [i for i in psutil.net_connections("tcp") if i.status != psutil.CONN_CLOSE]
        tcp_link_count = len(tcp_links)
        udp_links = [i for i in psutil.net_connections("udp")]
        udp_link_count = len(udp_links)


def handle_packet(_packet):
    global tcp_count, udp_count
    if _packet.haslayer(TCP):
        tcp_count += 1
    elif _packet.haslayer(UDP):
        udp_count += 1


def init_network_table():
    network_table.add_row(
        Text()
        .append("Tcp Packet: ", style="cyan")
        .append("", style="magenta")
        .append(" Link: ", style="cyan")
        .append("", style="magenta")
    )
    network_table.add_row(
        Text()
        .append("Udp Packet: ", style="cyan")
        .append("", style="magenta")
        .append(" Link: ", style="cyan")
        .append("", style="magenta")
    )
    network_table.add_row(
        Text()
        .append("Upload:    ", style="cyan")
        .append("", style="magenta")
    )
    network_table.add_row(
        Text()
        .append("Download:  ", style="cyan")
        .append("", style="magenta")
    )
    network_table.add_row(Text())


def format_count(count):
    if count < 1000:
        return f"{count:>7d}"
    count /= 1000
    if count < 1000:
        return f"{count:>6.2f}K"
    count /= 1000
    if count < 1000:
        return f"{count:>6.2f}M"
    count /= 1000
    return f"{count:>6.2f}B"


def update_network_table():
    network_table.columns[0]._cells[0] = (Text(justify="full")
                                          .append("Tcp Packet: ", style="cyan")
                                          .append(f"{format_count(tcp_count)}", style="magenta")
                                          .append(" Link: ", style="cyan")
                                          .append(f"{format_count(tcp_link_count)}", style="magenta")
                                          )
    network_table.columns[0]._cells[1] = (Text(justify="full")
                                          .append("Udp Packet: ", style="cyan")
                                          .append(f"{format_count(udp_count)}", style="magenta")
                                          .append(" Link: ", style="cyan")
                                          .append(f"{format_count(udp_link_count)}", style="magenta")
                                          )
    network_table.columns[0]._cells[2] = (Text()
                                          .append("Upload:  ", style="cyan")
                                          .append(f"{upload_speed}/s", style="magenta")
                                          )
    network_table.columns[0]._cells[3] = (Text()
                                          .append("Download:", style="cyan")
                                          .append(f"{download_speed}/s", style="magenta")
                                          )


sniff_thread = Thread(target=sniff, kwargs={"prn": handle_packet})
network_thread = Thread(target=get_bandwidth)
log_network_thread = Thread(target=log_network)

