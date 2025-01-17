#!/usr/bin/env python3

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A clone of 'netstat -antp' on Linux.

$ python3 scripts/netstat.py
Proto Local address      Remote address   Status        PID    Program name
tcp   127.0.0.1:48256    127.0.0.1:45884  ESTABLISHED   13646  chrome
tcp   127.0.0.1:47073    127.0.0.1:45884  ESTABLISHED   13646  chrome
tcp   127.0.0.1:47072    127.0.0.1:45884  ESTABLISHED   13646  chrome
tcp   127.0.0.1:45884    -                LISTEN        13651  GoogleTalkPlugi
tcp   127.0.0.1:60948    -                LISTEN        13651  GoogleTalkPlugi
tcp   172.17.42.1:49102  127.0.0.1:19305  CLOSE_WAIT    13651  GoogleTalkPlugi
tcp   172.17.42.1:55797  127.0.0.1:443    CLOSE_WAIT    13651  GoogleTalkPlugi
...
"""

import socket
import time
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import SOCK_STREAM

import psutil

AD = "-"
AF_INET6 = getattr(socket, 'AF_INET6', object())
proto_map = {
    (AF_INET, SOCK_STREAM): 'tcp',
    (AF_INET6, SOCK_STREAM): 'tcp6',
    (AF_INET, SOCK_DGRAM): 'udp',
    (AF_INET6, SOCK_DGRAM): 'udp6',
}


def main():
    templ = "%-5s %-30s %-30s %-13s %-6s %s"
    header = templ % (
        "Proto",
        "Local address",
        "Remote address",
        "Status",
        "PID",
        "Program name",
    )
    print(header)
    proc_names = {}
    for p in psutil.process_iter(['pid', 'name']):
        proc_names[p.info['pid']] = p.info['name']
    for c in psutil.net_connections(kind='inet4'):
        laddr = "%s:%s" % (c.laddr)
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % (c.raddr)
        name = proc_names.get(c.pid, '?') or ''
        line = templ % (
            proto_map[(c.family, c.type)],
            laddr,
            raddr or AD,
            c.status,
            c.pid or AD,
            name[:15],
        )
        print(line)


_tcp_link = {}
udp_link = {}


def compare_dicts(dict1, dict2):
    added = [v for k, v in dict2.items() if k not in dict1.keys()]
    removed = [v for k, v in dict1.items() if k not in dict2.keys()]
    modified = [dict2[k] for k, v in dict1.items() if k in dict2.keys() and dict1[k].status != dict2[k].status]

    return added, removed, modified


def a():
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
    added, removed, modified = compare_dicts(_tcp_link, new_tcp_link)
    for c in added:
        print(f"[add][{proto_map[(c.family, c.type)]}]{laddr}-{raddr or ''}: {c.status}")
    for c in removed:
        print(f"[removed][{proto_map[(c.family, c.type)]}]{laddr}-{raddr or ''}: {c.status}")
    for c in modified:
        print(f"[modified][{proto_map[(c.family, c.type)]}]{laddr}-{raddr or ''}: {c.status}")
    _tcp_link = new_tcp_link

    added, removed, modified = compare_dicts(_udp_link, new_udp_link)
    for c in added:
        print(f"[add][{proto_map[(c.family, c.type)]}]{laddr}-{raddr or ''}: {c.status}")
    for c in removed:
        print(f"[removed][{proto_map[(c.family, c.type)]}]{laddr}-{raddr or ''}: {c.status}")
    for c in modified:
        print(f"[modified][{proto_map[(c.family, c.type)]}]{laddr}-{raddr or ''}: {c.status}")
    _udp_link = new_udp_link


if __name__ == '__main__':
    for i in range(2):
        a()
        print(1)
        time.sleep(5)
