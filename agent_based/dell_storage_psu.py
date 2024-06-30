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
from cmk_addons.plugins.dell_storage.lib.dell_storage import (
    DSResult
)


class ScPSU(NamedTuple):
    name: str
    status: str
    statusMessage: str
    location: str


def parse_dell_storage_psu(string_table):
    return [ScPSU(*psu) for psu in string_table]


agent_section_dell_storage_psu = AgentSection(
    name='dell_storage_psu',
    parse_function=parse_dell_storage_psu,
)


def discovery_dell_storage_psu(section):
    for psu in section:
        yield Service(item=psu.name)


def check_dell_storage_psu(item, section):
    for psu in section:
        if not psu.name == item:
            continue

        yield from DSResult(psu)
        if psu.location != 'None':
            yield Result(state=State.OK, summary=psu.location)

        return


check_plugin_dell_storage_psu = CheckPlugin(
    name='dell_storage_psu',
    service_name='PSU %s',
    discovery_function=discovery_dell_storage_psu,
    check_function=check_dell_storage_psu,
)
