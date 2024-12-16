import socket
import time
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import SOCK_STREAM

from .logger import get_network_console
from .thread import get_running
import psutil
from .config import settings
from threading import Thread

AD = "-"
AF_INET6 = getattr(socket, 'AF_INET6', object())
proto_map = {
    (AF_INET, SOCK_STREAM): 'tcp',
    (AF_INET6, SOCK_STREAM): 'tcp6',
    (AF_INET, SOCK_DGRAM): 'udp',
    (AF_INET6, SOCK_DGRAM): 'udp6',
}

_tcp_link = {}
udp_link = {}


def compare_dicts(dict1, dict2):
    added = [v for k, v in dict2.items() if k not in dict1.keys()]
    removed = [v for k, v in dict1.items() if k not in dict2.keys()]
    modified = [dict2[k] for k, v in dict1.items() if k in dict2.keys() and dict1[k].status != dict2[k].status]

    return added, removed, modified


def check_link():
    global _tcp_link, _udp_link
    new_tcp_link = {}
    new_udp_link = {}
    for c in psutil.net_connections(kind='inet4'):
        laddr = "%s:%s" % (c.laddr)
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % (c.raddr)
        if c.pid is None:
            continue
        if (c.family, c.type) == (AF_INET, SOCK_STREAM):
            new_tcp_link[laddr] = c
        else:
            new_udp_link[laddr] = c
    if _tcp_link == {}:
        _tcp_link = new_tcp_link
        _udp_link = new_udp_link
        return
    logger = get_network_console()
    added, removed, modified = compare_dicts(_tcp_link, new_tcp_link)
    for c in added:
        logger.log(f"add|{proto_map[(c.family, c.type)]}|{laddr}-{raddr or ''}: {c.status}")
    for c in removed:
        logger.log(f"removed|{proto_map[(c.family, c.type)]}|{laddr}-{raddr or ''}: {c.status}")
    for c in modified:
        logger.log(f"modified|{proto_map[(c.family, c.type)]}|{laddr}-{raddr or ''}: {c.status}")
    _tcp_link = new_tcp_link

    added, removed, modified = compare_dicts(_udp_link, new_udp_link)
    for c in added:
        logger.log(f"add|{proto_map[(c.family, c.type)]}|{laddr}-{raddr or ''}: {c.status}")
    for c in removed:
        logger.log(f"removed|{proto_map[(c.family, c.type)]}|{laddr}-{raddr or ''}: {c.status}")
    for c in modified:
        logger.log(f"modified|{proto_map[(c.family, c.type)]}|{laddr}-{raddr or ''}: {c.status}")
    _udp_link = new_udp_link


def link_start():
    check_link()
    while get_running():
        time.sleep(settings.link_check_interval)
        check_link()


network_background_thread = Thread(target=link_start)
