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
from cmk.base.plugins.agent_based import dell_storage_fan

SAMPLE_STRING_TABLE = [
    ['Fan 1', 'Up', '', 'Fan 1 Single rotor, Power Supply 1', '5880', '0', '1800', '2040', '18000', '20000', '30600'],
    ['02-03', 'Up', '', 'In Power Supply - Back Right']
]

SAMPLE_SECTION = [
    dell_storage_fan.ScFan(
        name='Fan 1',
        status='Up',
        statusMessage='',
        location='Fan 1 Single rotor, Power Supply 1',
        currentRpm='5880',
        lowerCriticalThreshold='0',
        lowerWarningThreshold='1800',
        lowerNormalThreshold='2040',
        upperNormalThreshold='18000',
        upperWarningThreshold='20000',
        upperCriticalThreshold='30600',
    ),
    dell_storage_fan.ScFan(
        name='02-03',
        status='Up',
        statusMessage='',
        location='In Power Supply - Back Right',
    ),
]


@pytest.mark.parametrize('string_table, result', [
    (
        [SAMPLE_STRING_TABLE[0]],
        [SAMPLE_SECTION[0]]
    ),
    (
        SAMPLE_STRING_TABLE,
        SAMPLE_SECTION
    ),
])
def test_parse_dell_storage_fan(string_table, result):
    assert list(dell_storage_fan.parse_dell_storage_fan(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [SAMPLE_SECTION[0]],
        [Service(item=SAMPLE_SECTION[0].name)]
    ),
    (
        SAMPLE_SECTION,
        [
            Service(item=SAMPLE_SECTION[0].name),
            Service(item=SAMPLE_SECTION[1].name),
        ]
    ),
])
def test_discovery_dell_storage_fan(section, result):
    assert list(dell_storage_fan.discovery_dell_storage_fan(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    ('01-08', SAMPLE_SECTION, []),
    (
        SAMPLE_SECTION[0].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='Fan 1 Single rotor, Power Supply 1'),
            Result(state=State.OK, summary='Fan Speed: 5880.00'),
            Metric('fan', 5880.0, levels=(18000.0, 20000.0), boundaries=(0.0, 30600.0))
        ]
    ),
    (
        SAMPLE_SECTION[1].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='In Power Supply - Back Right'),
        ]
    ),
])
def test_check_dell_storage_fan(item, section, result):
    assert list(dell_storage_fan.check_dell_storage_fan(item, {}, section)) == result


@pytest.mark.parametrize('params, result', [
    (
        {'lower': (2400, 1800)},
        Result(state=State.OK, summary='Fan Speed: 5880.00'),
    ),
    (
        {'lower': (7000, 1800)},
        Result(state=State.WARN, summary='Fan Speed: 5880.00 (warn/crit below 7000.00/1800.00)'),
    ),
    (
        {'lower': (7000, 6000)},
        Result(state=State.CRIT, summary='Fan Speed: 5880.00 (warn/crit below 7000.00/6000.00)'),
    ),
    (
        {'upper': (6000, 7000)},
        Result(state=State.OK, summary='Fan Speed: 5880.00'),
    ),
    (
        {'upper': (4000, 7000)},
        Result(state=State.WARN, summary='Fan Speed: 5880.00 (warn/crit at 4000.00/7000.00)'),
    ),
    (
        {'upper': (4000, 5000)},
        Result(state=State.CRIT, summary='Fan Speed: 5880.00 (warn/crit at 4000.00/5000.00)'),
    ),
])
def test_check_dell_storage_fan_w_param(params, result):
    assert result in list(dell_storage_fan.check_dell_storage_fan(SAMPLE_SECTION[0].name, params, [SAMPLE_SECTION[0]]))
