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
    check_levels,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell_storage.lib.dell_storage import (
    DSResult
)


class ScFan(NamedTuple):
    name: str
    status: str
    statusMessage: str
    location: str
    currentRpm: Optional[int] = None
    lowerCriticalThreshold: Optional[int] = None
    lowerWarningThreshold: Optional[int] = None
    lowerNormalThreshold: Optional[int] = None
    upperNormalThreshold: Optional[int] = None
    upperWarningThreshold: Optional[int] = None
    upperCriticalThreshold: Optional[int] = None


def parse_dell_storage_fan(string_table):
    return [ScFan(*fan) for fan in string_table]


agent_section_dell_storage_fan = AgentSection(
    name='dell_storage_fan',
    parse_function=parse_dell_storage_fan,
)


def discovery_dell_storage_fan(section):
    for fan in section:
        yield Service(item=fan.name)


def check_dell_storage_fan(item, params, section):
    for fan in section:
        if not fan.name == item:
            continue

        yield from DSResult(fan)
        yield Result(state=State.OK, summary=fan.location)

        if fan.currentRpm:
            yield from check_levels(
                value=int(fan.currentRpm),
                metric_name='fan' if params.get('output_metrics', True) else None,
                levels_lower=params.get('lower', ('fixed', (int(fan.lowerNormalThreshold), int(fan.lowerWarningThreshold)))),
                levels_upper=params.get('upper', ('fixed', (int(fan.upperNormalThreshold), int(fan.upperWarningThreshold)))),
                boundaries=(int(fan.lowerCriticalThreshold), int(fan.upperCriticalThreshold)),
                label='Fan Speed',
            )

        return


check_plugin_dell_storage_fan = CheckPlugin(
    name='dell_storage_fan',
    service_name='Fan %s',
    discovery_function=discovery_dell_storage_fan,
    check_function=check_dell_storage_fan,
    check_ruleset_name='hw_fans',
    check_default_parameters={},
)
