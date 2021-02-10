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

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import dell_storage_alert


@pytest.mark.parametrize('string_table, result', [
    ([], []),
    (
        [['alertDefinition', 'message', 'acknowledged', 'supportUrl']],
        [dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message', acknowledged='acknowledged', supportUrl='supportUrl')]
    ),
    (
        [['alertDefinition', 'message']],
        [dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message', acknowledged=False, supportUrl=None)]
    ),
])
def test_parse_dell_storage_alert(string_table, result):
    assert list(dell_storage_alert.parse_dell_storage_alert(string_table)) == result


def test_discovery_dell_storage_alert():
    assert list(dell_storage_alert.discovery_dell_storage_alert([])) == [Service()]


@pytest.mark.parametrize('section, result', [
    ([], [Result(state=State.OK, summary='No active alerts present')]),
    (
        [dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message', acknowledged='False', supportUrl='supportUrl')],
        [Result(state=State.WARN, summary='alertDefinition: message supportUrl')]
    ),
    (
        [dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message', acknowledged='True', supportUrl='supportUrl')],
        [Result(state=State.OK, summary='Acknowledged alertDefinition: message supportUrl')]
    ),
    (
        [
            dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message1', acknowledged='False', supportUrl='supportUrl'),
            dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message2', acknowledged='False', supportUrl='supportUrl')
        ],
        [
            Result(state=State.WARN, summary='alertDefinition: message1 supportUrl'),
            Result(state=State.WARN, summary='alertDefinition: message2 supportUrl')
        ]
    ),
    (
        [
            dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message1', acknowledged='True', supportUrl='supportUrl'),
            dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message2', acknowledged='False', supportUrl='supportUrl')
        ],
        [
            Result(state=State.OK, summary='Acknowledged alertDefinition: message1 supportUrl'),
            Result(state=State.WARN, summary='alertDefinition: message2 supportUrl')
        ]
    ),
    (
        [
            dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message1', acknowledged='True', supportUrl='supportUrl'),
            dell_storage_alert.ScAlert(alertDefinition='alertDefinition', message='message2', acknowledged='True', supportUrl='supportUrl')
        ],
        [
            Result(state=State.OK, summary='Acknowledged alertDefinition: message1 supportUrl'),
            Result(state=State.OK, summary='Acknowledged alertDefinition: message2 supportUrl'),
        ]
    )
])
def test_check_dell_storage_alert(section, result):
    assert list(dell_storage_alert.check_dell_storage_alert(section)) == result
