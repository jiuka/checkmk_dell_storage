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

from .agent_based_api.v1 import (
    Metric,
    register,
    Result,
    Service,
    State,
)


def discovery_dell_storage_agent(section):
    if len(section) > 0:
        yield Service()


def check_dell_storage_agent(section):
    state, provider, version, time, requests, exc = section[0]

    if state == '0':
        yield Result(state=State.OK, summary=f'{provider} v{version}')
        yield Metric('request', float(requests))
    else:
        yield Result(state=State.CRIT, summary=f'Exception: {exc}')

    yield Metric('time', float(time))


register.check_plugin(
    name='dell_storage_agent',
    service_name='Dell Storage API',
    discovery_function=discovery_dell_storage_agent,
    check_function=check_dell_storage_agent,
)
