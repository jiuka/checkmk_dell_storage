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
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import dell_storage_enclosure

SAMPLE_STRING_TABLE = [
    ['Enclosure - 1', 'Up', '', 'EN-SC5020', '1.05', 'SasEbod12g', '30', 'ABCD123', '123-456-789-01'],
    ['Enclosure - 2', 'Degraded', 'FooBar', 'EN-SC420', '1.09', 'SasEbod12g', '24', 'ABCD456', '123-456-789-02'],
]

SAMPLE_SECTION = [
    dell_storage_enclosure.ScEnclosure(
        name='Enclosure - 1',
        status='Up',
        statusMessage='',
        modelSeries='EN-SC5020',
        version='1.05',
        encType='SasEbod12g',
        capacity='30',
        serviceTag='ABCD123',
        expressServiceCode='123-456-789-01',
    ),
    dell_storage_enclosure.ScEnclosure(
        name='Enclosure - 2',
        status='Degraded',
        statusMessage='FooBar',
        modelSeries='EN-SC420',
        version='1.09',
        encType='SasEbod12g',
        capacity='24',
        serviceTag='ABCD456',
        expressServiceCode='123-456-789-02',
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
def test_parse_dell_storage_enclosure(string_table, result):
    assert list(dell_storage_enclosure.parse_dell_storage_enclosure(string_table)) == result


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
def test_discovery_dell_storage_enclosure(section, result):
    assert list(dell_storage_enclosure.discovery_dell_storage_enclosure(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    ('01-08', SAMPLE_SECTION, []),
    (
        SAMPLE_SECTION[0].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='Model: EN-SC5020 v1.05, TypeSasEbod12g'),
            Result(state=State.OK, summary='Capacity: 30'),
            Result(state=State.OK, summary='ST: ABCD123'),
            Result(state=State.OK, summary='ESC: 123-456-789-01')
        ]
    ),
    (
        SAMPLE_SECTION[1].name,
        SAMPLE_SECTION,
        [
            Result(state=State.WARN, summary='Degraded: FooBar'),
            Result(state=State.OK, summary='Model: EN-SC420 v1.09, TypeSasEbod12g'),
            Result(state=State.OK, summary='Capacity: 24'),
            Result(state=State.OK, summary='ST: ABCD456'),
            Result(state=State.OK, summary='ESC: 123-456-789-02')
        ]
    ),
])
def test_check_dell_storage_enclosure(item, section, result):
    assert list(dell_storage_enclosure.check_dell_storage_enclosure(item, section)) == result
