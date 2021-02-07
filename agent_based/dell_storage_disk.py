#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_dell_storage - Checkmk extension for Dell Storage API
#
# Copyright (C) 2021  Marius Rieder <marius.rieder@scs.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from typing import NamedTuple
from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    Metric,
)
from .utils.dell_storage import (
    DSStatus
)


class ScDisk(NamedTuple):
    name: str
    status: str
    statusMessage: str
    allocatedSpace: str
    totalSpace: str
    readIops: str
    readBps: str
    readLatency: str
    writeIops: str
    writeBps: str
    writeLatency: str


def parse_dell_storage_disk(string_table):
    return [ScDisk(*disk) for disk in string_table]


register.agent_section(
    name='dell_storage_disk',
    parse_function=parse_dell_storage_disk,
)


def discovery_dell_storage_disk(section):
    for disk in section:
        yield Service(item=disk.name)


def check_dell_storage_disk(item, section):
    for disk in section:
        if not disk.name == item:
            continue

        yield Result(state=DSStatus(disk.status), summary=f'{disk.status}')

        if disk.statusMessage:
            yield Result(state=State.OK, summary=f'({disk.statusMessage})')

        yield Metric('usage',
                     int(disk.allocatedSpace),
                     boundaries=(0, int(disk.totalSpace)))
        yield Metric('disk_read_ios', int(disk.readIops))
        yield Metric('disk_read_throughput', int(disk.readBps))
        yield Metric('read_latency', float(disk.readLatency))
        yield Metric('disk_write_ios', int(disk.writeIops))
        yield Metric('disk_write_throughput', int(disk.writeBps))
        yield Metric('write_latency', float(disk.writeLatency))

        return

    yield Result(state=State.UNKNOWN, summary='Sensor %s not found.' % item)


register.check_plugin(
    name='dell_storage_disk',
    service_name='Disk %s',
    discovery_function=discovery_dell_storage_disk,
    check_function=check_dell_storage_disk,
)
