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
    DSResult
)


class ScVolume(NamedTuple):
    name: str
    status: str
    statusMessage: str
    activeSpace: str
    configuredSpace: str
    readIops: str
    readBps: str
    readLatency: str
    writeIops: str
    writeBps: str
    writeLatency: str


def parse_dell_storage_volume(string_table):
    return [ScVolume(*vol) for vol in string_table]


register.agent_section(
    name='dell_storage_volume',
    parse_function=parse_dell_storage_volume,
)


def discovery_dell_storage_volume(section):
    for vol in section:
        yield Service(item=vol.name)


def check_dell_storage_volume(item, section):
    for vol in section:
        if not vol.name == item:
            continue

        yield from DSResult(vol)

        yield Metric('usage',
                     int(vol.activeSpace),
                     boundaries=(0, int(vol.configuredSpace)))
        yield Metric('disk_read_ios', int(vol.readIops))
        yield Metric('disk_read_throughput', int(vol.readBps))
        yield Metric('read_latency', float(vol.readLatency))
        yield Metric('disk_write_ios', int(vol.writeIops))
        yield Metric('disk_write_throughput', int(vol.writeBps))
        yield Metric('write_latency', float(vol.writeLatency))

        return

    yield Result(state=State.UNKNOWN, summary='Volume %s not found.' % item)


register.check_plugin(
    name='dell_storage_volume',
    service_name='Volume %s',
    discovery_function=discovery_dell_storage_volume,
    check_function=check_dell_storage_volume,
)
