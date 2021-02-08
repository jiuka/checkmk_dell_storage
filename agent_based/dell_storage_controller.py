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
    DSResult
)


class ScController(NamedTuple):
    name: str
    status: str
    statusMessage: str
    bootDate: str
    master: str
    modelSeries: str
    version: str
    serviceTag: str
    expressServiceCode: str
    serialNumber: str


def parse_dell_storage_controller(string_table):
    return [ScController(*ctrl) for ctrl in string_table]


register.agent_section(
    name='dell_storage_controller',
    parse_function=parse_dell_storage_controller,
)


def discovery_dell_storage_controller(section):
    for sc in section:
        yield Service(item=sc.name)


def check_dell_storage_controller(item, section):
    for ctrl in section:
        if not ctrl.name == item:
            continue

        yield from DSResult(ctrl)

        yield Result(state=State.OK, summary=f'Model: {ctrl.modelSeries} v{ctrl.version}')
        yield Result(state=State.OK, summary=f'ST: {ctrl.serviceTag}')
        yield Result(state=State.OK, summary=f'SN: {ctrl.serialNumber}')
        return

    yield Result(state=State.UNKNOWN, summary='Controller %s not found.' % item)


register.check_plugin(
    name='dell_storage_controller',
    service_name='Controller %s',
    discovery_function=discovery_dell_storage_controller,
    check_function=check_dell_storage_controller,
)
