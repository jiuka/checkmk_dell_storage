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

from typing import NamedTuple, Optional
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    get_value_store,
    Result,
    Service,
    State,
)
from cmk.plugins.lib.temperature import check_temperature
from cmk_addons.plugins.dell_storage.lib.dell_storage import (
    DSResult,
)


class ScTemp(NamedTuple):
    name: str
    status: str
    statusMessage: str
    location: str
    currentTemp: Optional[int] = None
    lowerCriticalThreshold: Optional[int] = None
    lowerWarningThreshold: Optional[int] = None
    lowerNormalThreshold: Optional[int] = None
    upperNormalThreshold: Optional[int] = None
    upperWarningThreshold: Optional[int] = None
    upperCriticalThreshold: Optional[int] = None


def parse_dell_storage_temp(string_table):
    return [ScTemp(*temp) for temp in string_table]


agent_section_dell_storage_temp = AgentSection(
    name='dell_storage_temp',
    parse_function=parse_dell_storage_temp,
)


def discovery_dell_storage_temp(section):
    for temp in section:
        yield Service(item=temp.name)


def check_dell_storage_temp(item, params, section):
    for temp in section:
        if not temp.name == item:
            continue

        yield from DSResult(temp)
        if temp.location != 'None':
            yield Result(state=State.OK, summary=temp.location)

        yield from check_temperature(
            reading=int(temp.currentTemp),
            params=params,
            unique_name="dell_storage_temp.%s" % item,
            value_store=get_value_store(),
            dev_levels= (int(temp.upperNormalThreshold), int(temp.upperWarningThreshold)),
            dev_levels_lower = (int(temp.lowerNormalThreshold), int(temp.lowerWarningThreshold)),
        )

        return


check_plugin_dell_storage_temp = CheckPlugin(
    name='dell_storage_temp',
    service_name='Temperature %s',
    discovery_function=discovery_dell_storage_temp,
    check_function=check_dell_storage_temp,
    check_ruleset_name='temperature',
    check_default_parameters={},
)
