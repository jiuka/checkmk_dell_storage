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

import pytest  # type: ignore[import]
from cmk.agent_based.v2 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell_storage.agent_based import dell_storage_temp


def get_value_store():
    return {}


SAMPLE_STRING_TABLE = [
    ['Ambient', 'Up', '', 'None', '22', '-128', '-7', '3', '42', '47', '127'],
    ['02-02', 'Up', '', 'Midplane', '27', 'None', '4', '9', '54', '57', 'None']
]

SAMPLE_SECTION = [
    dell_storage_temp.ScTemp(
        name='Ambient',
        status='Up',
        statusMessage='',
        location='None',
        currentTemp='22',
        lowerCriticalThreshold='-128',
        lowerWarningThreshold='-7',
        lowerNormalThreshold='3',
        upperNormalThreshold='42',
        upperWarningThreshold='47',
        upperCriticalThreshold='127',
    ),
    dell_storage_temp.ScTemp(
        name='02-02',
        status='Up',
        statusMessage='',
        location='Midplane',
        currentTemp='27',
        lowerCriticalThreshold='None',
        lowerWarningThreshold='4',
        lowerNormalThreshold='9',
        upperNormalThreshold='54',
        upperWarningThreshold='57',
        upperCriticalThreshold='None',
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
def test_parse_dell_storage_temp(string_table, result):
    assert list(dell_storage_temp.parse_dell_storage_temp(string_table)) == result


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
def test_discovery_dell_storage_temp(section, result):
    assert list(dell_storage_temp.discovery_dell_storage_temp(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    ('01-08', SAMPLE_SECTION, []),
    (
        SAMPLE_SECTION[0].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Metric('temp', 22.0, levels=(42.0, 47.0)),
            Result(state=State.OK, summary='Temperature: 22 °C'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (used device levels)')
        ]
    ),
    (
        SAMPLE_SECTION[1].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='Midplane'),
            Metric('temp', 27.0, levels=(54.0, 57.0)),
            Result(state=State.OK, summary='Temperature: 27 °C'),
            Result(state=State.OK, notice='Configuration: prefer user levels over device levels (used device levels)')
        ]
    ),
])
def test_check_dell_storage_temp(item, section, result, monkeypatch):
    monkeypatch.setattr(dell_storage_temp, 'get_value_store', get_value_store)

    assert list(dell_storage_temp.check_dell_storage_temp(item, {}, section)) == result


@pytest.mark.parametrize('params, result', [
    (
        {'levels': (24, 26)},
        Result(state=State.OK, summary='Temperature: 22 °C'),
    ),
    (
        {'levels': (18, 26)},
        Result(state=State.WARN, summary='Temperature: 22 °C (warn/crit at 18 °C/26 °C)'),
    ),
    (
        {'levels': (18, 20)},
        Result(state=State.CRIT, summary='Temperature: 22 °C (warn/crit at 18 °C/20 °C)'),
    ),
    (
        {'levels_lower': (20, 18)},
        Result(state=State.OK, summary='Temperature: 22 °C'),
    ),
    (
        {'levels_lower': (26, 18)},
        Result(state=State.WARN, summary='Temperature: 22 °C (warn/crit below 26 °C/18 °C)'),
    ),
    (
        {'levels_lower': (26, 24)},
        Result(state=State.CRIT, summary='Temperature: 22 °C (warn/crit below 26 °C/24 °C)'),
    ),
    (
        {'output_unit': 'c'},
        Result(state=State.OK, summary='Temperature: 22 °C'),
    ),
    (
        {'output_unit': 'f'},
        Result(state=State.OK, summary='Temperature: 71 °F'),
    ),
    (
        {'output_unit': 'k'},
        Result(state=State.OK, summary='Temperature: 295 K'),
    ),
])
def test_check_dell_storage_temp_w_param(params, result, monkeypatch):
    monkeypatch.setattr(dell_storage_temp, 'get_value_store', get_value_store)

    assert result in list(dell_storage_temp.check_dell_storage_temp(SAMPLE_SECTION[0].name, params, [SAMPLE_SECTION[0]]))
