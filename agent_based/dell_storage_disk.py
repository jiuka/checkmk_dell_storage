#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_dell_storage - Checkmk extension for Dell Storage API
#
# Copyright (C) 2021-2024  Marius Rieder <marius.rieder@durchmesser.ch>
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

import time
from typing import NamedTuple
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    get_value_store,
    Metric,
    Service,
)
from cmk.plugins.lib import diskstat
from cmk_addons.plugins.dell_storage.lib.dell_storage import (
    DSResult
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


agent_section_dell_storage_disk = AgentSection(
    name='dell_storage_disk',
    parse_function=parse_dell_storage_disk,
)


def discovery_dell_storage_disk(section):
    for disk in section:
        yield Service(item=disk.name)


def check_dell_storage_disk(item, params, section):
    for disk in section:
        if not disk.name == item:
            continue

        yield from DSResult(disk)

        yield Metric('usage',
                     int(disk.allocatedSpace),
                     boundaries=(0, int(disk.totalSpace)))

        value_store = get_value_store()
        try:
            yield from diskstat.check_diskstat_dict(
                params=params,
                disk={
                    'read_ios': int(disk.readIops),
                    'read_throughput': int(disk.readBps),
                    'read_latency': float(disk.readLatency),
                    'write_ios': int(disk.writeIops),
                    'write_throughput': int(disk.writeBps),
                    'write_latency': float(disk.writeLatency),
                },
                value_store=value_store,
                this_time=time.time(),
            )
        except ValueError:
            pass

        return


check_plugin_dell_storage_disk = CheckPlugin(
    name='dell_storage_disk',
    service_name='Disk %s',
    discovery_function=discovery_dell_storage_disk,
    check_function=check_dell_storage_disk,
    check_ruleset_name='diskstat',
    check_default_parameters={},
)
