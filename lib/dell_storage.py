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

from cmk.agent_based.v2 import (
    State,
    Result,
)


def DSStatus(value):
    return {
        'Up': State.OK,
        'Degraded': State.WARN,
        'Down': State.CRIT,
        'Unknown': State.UNKNOWN,
    }.get(value, State.UNKNOWN)


def DSResult(dsobject):
    if dsobject.statusMessage:
        yield Result(state=DSStatus(dsobject.status), summary=f'{dsobject.status}: {dsobject.statusMessage}')
    else:
        yield Result(state=DSStatus(dsobject.status), summary=dsobject.status)
