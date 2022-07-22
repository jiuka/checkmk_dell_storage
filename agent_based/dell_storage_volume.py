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

import time
from typing import NamedTuple
from .agent_based_api.v1 import (
    get_value_store,
    Metric,
    register,
    Service,
)
from .utils import diskstat
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


def check_dell_storage_volume(item, params, section):
    for vol in section:
        if not vol.name == item:
            continue

        yield from DSResult(vol)

        yield Metric('usage',
                     int(vol.activeSpace),
                     boundaries=(0, int(vol.configuredSpace)))

        value_store = get_value_store()
        try:
            yield from diskstat.check_diskstat_dict(
                params=params,
                disk={
                    'read_ios': int(vol.readIops),
                    'read_throughput': int(vol.readBps),
                    'read_latency': float(vol.readLatency),
                    'write_ios': int(vol.writeIops),
                    'write_throughput': int(vol.writeBps),
                    'write_latency': float(vol.writeLatency),
                },
                value_store=value_store,
                this_time=time.time(),
            )
        except ValueError:
            pass

        return


register.check_plugin(
    name='dell_storage_volume',
    service_name='Volume %s',
    discovery_function=discovery_dell_storage_volume,
    check_function=check_dell_storage_volume,
    check_ruleset_name='diskstat',
    check_default_parameters={},
)
