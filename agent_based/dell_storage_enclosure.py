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
    Result,
    Service,
    State,
)
from .utils.dell_storage import (
    DSResult
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


agent_section_dell_storage_enclosure = AgentSection(
    name='dell_storage_enclosure',
    parse_function=parse_dell_storage_enclosure,
)


def discovery_dell_storage_enclosure(section):
    for enc in section:
        yield Service(item=enc.name)


def check_dell_storage_enclosure(item, section):
    for enc in section:
        if not enc.name == item:
            continue

        yield from DSResult(enc)

        yield Result(state=State.OK, summary=f'Model: {enc.modelSeries} v{enc.version}, Type{enc.encType}')
        yield Result(state=State.OK, summary=f'Capacity: {enc.capacity}')

        yield Result(state=State.OK, summary=f'ST: {enc.serviceTag}')
        yield Result(state=State.OK, summary=f'ESC: {enc.expressServiceCode}')

        return


check_plugin_dell_storage_enclosure = CheckPlugin(
    name='dell_storage_enclosure',
    service_name='Enclosure %s',
    discovery_function=discovery_dell_storage_enclosure,
    check_function=check_dell_storage_enclosure,
)
