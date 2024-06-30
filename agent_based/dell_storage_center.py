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

from typing import NamedTuple
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Metric,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell_storage.lib.dell_storage import (
    DSResult
)


class StorageCenter(NamedTuple):
    name: str
    status: str
    statusMessage: str
    modelSeries: str
    version: str
    serviceTag: str
    serialNumber: str
    numberOfControllers: int
    numberOfDevicesInUse: int
    numberOfDisks: int
    numberOfLiveVolumes: int
    numberOfReplays: int
    numberOfReplications: int
    numberOfServers: int
    numberOfVolumes: int


def parse_dell_storage_center(string_table):
    return [StorageCenter(*sc) for sc in string_table]


agent_section_dell_storage_center = AgentSection(
    name='dell_storage_center',
    parse_function=parse_dell_storage_center,
)


def discovery_dell_storage_center(section):
    for sc in section:
        yield Service(item=sc.name)


def check_dell_storage_center(item, section):
    for sc in section:
        if not sc.name == item:
            continue

        yield from DSResult(sc)

        yield Result(state=State.OK, summary=f'Model: {sc.modelSeries} v{sc.version}')
        yield Result(state=State.OK, summary=f'ST: {sc.serviceTag}')
        yield Result(state=State.OK, summary=f'SN: {sc.serialNumber}')

        yield Metric('controller', float(sc.numberOfControllers))
        yield Metric('device', float(sc.numberOfDevicesInUse))
        yield Metric('disk', float(sc.numberOfDisks))
        yield Metric('live_volume', float(sc.numberOfLiveVolumes))
        yield Metric('replay', float(sc.numberOfReplays))
        yield Metric('replication', float(sc.numberOfReplications))
        yield Metric('server', float(sc.numberOfServers))
        yield Metric('volume', float(sc.numberOfVolumes))

        return


check_plugin_dell_storage_center = CheckPlugin(
    name='dell_storage_center',
    service_name='StorageCenter %s',
    discovery_function=discovery_dell_storage_center,
    check_function=check_dell_storage_center,
)
