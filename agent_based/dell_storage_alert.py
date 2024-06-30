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


class ScAlert(NamedTuple):
    alertDefinition: str
    message: str
    acknowledged: bool = False
    supportUrl: str = None


def parse_dell_storage_alert(string_table):
    return [ScAlert(*alert) for alert in string_table]


agent_section_dell_storage_alert = AgentSection(
    name='dell_storage_alert',
    parse_function=parse_dell_storage_alert,
)


def discovery_dell_storage_alert(section):
    yield Service()


def check_dell_storage_alert(section):
    if not section:
        yield Result(state=State.OK, summary='No active alerts present')

    for alert in section:
        if alert.acknowledged == 'True':
            yield Result(state=State.OK, summary=f'Acknowledged {alert.alertDefinition}: {alert.message} {alert.supportUrl}')
        else:
            yield Result(state=State.WARN, summary=f'{alert.alertDefinition}: {alert.message} {alert.supportUrl}')


check_plugin_dell_storage_alert = CheckPlugin(
    name='dell_storage_alert',
    service_name='StorageCenter Alert',
    discovery_function=discovery_dell_storage_alert,
    check_function=check_dell_storage_alert,
)
