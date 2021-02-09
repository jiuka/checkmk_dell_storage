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
    register,
    Result,
    Service,
    State,
)
from .utils import diskstat
from .utils.dell_storage import (
    DSResult
)


class ScPort(NamedTuple):
    name: str
    status: str
    statusMessage: str
    cabled: str
    type: str
    wwn: str
    readIops: str
    readBps: str
    readLatency: str
    writeIops: str
    writeBps: str
    writeLatency: str


def parse_dell_storage_port(string_table):
    return [ScPort(*port) for port in string_table]


register.agent_section(
    name='dell_storage_port',
    parse_function=parse_dell_storage_port,
)


def discovery_dell_storage_port(section):
    for port in section:
        yield Service(item=port.name)


def check_dell_storage_port(item, params, section):
    for port in section:
        if not port.name == item:
            continue

        yield from DSResult(port)

        yield Result(state=State.OK, summary=f'Cabled: {port.cabled}')
        yield Result(state=State.OK, summary=f'Type: {port.type}')
        yield Result(state=State.OK, summary=f'WWN: {port.wwn}')

        value_store = get_value_store()
        yield from diskstat.check_diskstat_dict(
            params=params,
            disk={
                'read_ios': int(port.readIops),
                'read_throughput': int(port.readBps),
                'read_latency': float(port.readLatency),
                'write_ios': int(port.writeIops),
                'write_throughput': int(port.writeBps),
                'write_latency': float(port.writeLatency),
            },
            value_store=value_store,
            this_time=time.time(),
        )

        return


register.check_plugin(
    name='dell_storage_port',
    service_name='Port %s',
    discovery_function=discovery_dell_storage_port,
    check_function=check_dell_storage_port,
    check_ruleset_name='diskstat',
    check_default_parameters={},
)
