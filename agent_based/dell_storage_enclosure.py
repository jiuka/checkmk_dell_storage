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
)
from .utils.dell_storage import (
    DSStatus
)


class ScEnclosure(NamedTuple):
    name: str
    status: str
    statusMessage: str
    modelSeries: str
    version: str
    encType: str
    capacity: str
    serviceTag: str
    expressServiceCode: str


def parse_dell_storage_enclosure(string_table):
    return [ScEnclosure(*enc) for enc in string_table]


register.agent_section(
    name='dell_storage_enclosure',
    parse_function=parse_dell_storage_enclosure,
)


def discovery_dell_storage_enclosure(section):
    for enc in section:
        yield Service(item=enc.name)


def check_dell_storage_enclosure(item, section):
    for sc in section:
        if not sc.name == item:
            continue

        yield Result(state=DSStatus(sc.status), summary=f'{sc.status}')

        if sc.statusMessage:
            yield Result(state=State.OK, summary=f'({sc.statusMessage})')

        yield Result(state=State.OK, summary=f'Model: {sc.modelSeries} v{sc.version}, Type{sc.encType}')
        yield Result(state=State.OK, summary=f'Capacity: {sc.capacity}')

        yield Result(state=State.OK, summary=f'ST: {sc.serviceTag}')
        yield Result(state=State.OK, summary=f'EST: {sc.expressServiceCode}')
        return

    yield Result(state=State.UNKNOWN, summary='Sensor %s not found.' % item)


register.check_plugin(
    name='dell_storage_enclosure',
    service_name='Enclosure %s',
    discovery_function=discovery_dell_storage_enclosure,
    check_function=check_dell_storage_enclosure,
)
