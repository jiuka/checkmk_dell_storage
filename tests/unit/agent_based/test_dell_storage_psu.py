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
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell_storage.agent_based import dell_storage_psu

SAMPLE_STRING_TABLE = [
    ['PowerSupply1', 'Up', '', 'None'],
    ['02-04', 'Degraded', 'FooBar', 'In Power Supply - Back Right']
]

SAMPLE_SECTION = [
    dell_storage_psu.ScPSU(
        name='PowerSupply1',
        status='Up',
        statusMessage='',
        location='None',
    ),
    dell_storage_psu.ScPSU(
        name='02-04',
        status='Degraded',
        statusMessage='FooBar',
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
def test_parse_dell_storage_psu(string_table, result):
    assert list(dell_storage_psu.parse_dell_storage_psu(string_table)) == result


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
def test_discovery_dell_storage_psu(section, result):
    assert list(dell_storage_psu.discovery_dell_storage_psu(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    ('01-08', SAMPLE_SECTION, []),
    (
        SAMPLE_SECTION[0].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
        ]
    ),
    (
        SAMPLE_SECTION[1].name,
        SAMPLE_SECTION,
        [
            Result(state=State.WARN, summary='Degraded: FooBar'),
            Result(state=State.OK, summary='In Power Supply - Back Right'),
        ]
    ),
])
def test_check_dell_storage_psu(item, section, result):
    assert list(dell_storage_psu.check_dell_storage_psu(item, section)) == result
