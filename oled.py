#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display basic system information.

Needs psutil (+ dependencies) installed::

  $ sudo apt-get install python-dev
  $ sudo -H pip install psutil
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import socket
from sht_sensor import Sht

if os.name != 'posix':
    sys.exit('{} platform not supported'.format(os.name))

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

try:
    import psutil
except ImportError:
    print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
    sys.exit()


# TODO: custom font bitmaps for up/down arrows
# TODO: Load histogram


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n


def cpu_usage():
    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    return "Ld:%.1f %.1f %.1f Up: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])


def mem_usage():
    usage = psutil.virtual_memory()
    return "Mem: %s %.0f%%" \
        % (bytes2human(usage.used), 100 - usage.percent)


def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD:  %s %.0f%%" \
        % (bytes2human(usage.used), usage.percent)


def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))
def get_ip():
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    gateway = gw[2]
    host = socket.gethostname()
    return ipaddr
    #print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
def get_trd():
    sht=Sht(24,23)
    t = sht.read_t()
    rh = sht.read_rh(t)
    dew_point = sht.read_dew_point(t, rh)
    return "T:%1.f  RH:%.1f%%  DW:%.1f" \
        % (t,rh,dew_point)

def stats(device):
    # use custom font
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    with canvas(device) as draw:
        draw.text((0, 0), cpu_usage(), font=font2, fill="white")
        if device.height >= 32:
            draw.text((0, 12), mem_usage(), font=font2, fill="white")
            draw.text((0, 22), get_ip(), font=font2, fill="white")
        if device.height >= 64:
            draw.text((0, 26), disk_usage('/'), font=font2, fill="white")
            try:
                draw.text((0, 38), network('wlan0'), font=font2, fill="white")
            except KeyError:
                # no wifi enabled/available
                pass
    time.sleep(5)
    with canvas(device) as draw:
        draw.text((0, 0), get_trd(), font=font2, fill="white")
#        if device.height >= 32:
#            draw.text((0, 12), mem_usage(), font=font2, fill="white")
#            draw.text((0, 22), get_ip(), font=font2, fill="white")
#        if device.height >= 64:
#            draw.text((0, 26), disk_usage('/'), font=font2, fill="white")
#            try:
#                draw.text((0, 38), network('wlan0'), font=font2, fill="white")
#            except KeyError:
                # no wifi enabled/available
#                pass


def main():
    while True:
        stats(device)
        time.sleep(20)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
