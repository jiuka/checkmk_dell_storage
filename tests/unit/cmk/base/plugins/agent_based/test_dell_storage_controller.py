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
from cmk.base.plugins.agent_based import dell_storage_controller


@pytest.mark.parametrize('string_table, result', [
    (
        [['Top Controller', 'Up', '', '2020-08-21T19:38:12+02:00', 'True', 'Sc5020', '7.3.20.19', 'ABCD123', '123-456-789-00', '456789']],
        [dell_storage_controller.ScController(
            name='Top Controller',
            status='Up',
            statusMessage='',
            bootDate='2020-08-21T19:38:12+02:00',
            master='True',
            modelSeries='Sc5020',
            version='7.3.20.19',
            serviceTag= 'ABCD123',
            expressServiceCode='123-456-789-00',
            serialNumber='456789',
        )]
    ),
    (
        [
            ['Top Controller', 'Up', '', '2020-08-21T19:38:12+02:00', 'True', 'Sc5020', '7.3.20.19', 'ABCD123', '123-456-789-00', '456789'],
            ['Bottom Controller', 'Up', '', '2020-08-21T19:38:12+02:00', 'False', 'Sc5020', '7.3.20.19', 'ABCD123', '123-456-789-00', '456790']
        ],
        [
            dell_storage_controller.ScController(
                name='Top Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='True',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456789',
            ),
            dell_storage_controller.ScController(
                name='Bottom Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='False',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456790',
            )
        ]
    ),
])
def test_parse_dell_storage_controller(string_table, result):
    assert list(dell_storage_controller.parse_dell_storage_controller(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [
            dell_storage_controller.ScController(
                name='Top Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='True',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456789',
            ),
        ],
        [Service(item='Top Controller')]
    ),
    (
        [
            dell_storage_controller.ScController(
                name='Top Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='True',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456789',
            ),
            dell_storage_controller.ScController(
                name='Bottom Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='False',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456790',
            )
        ],
        [
            Service(item='Top Controller'),
            Service(item='Bottom Controller')
        ]
    ),
])
def test_discovery_dell_storage_controller(section, result):
    assert list(dell_storage_controller.discovery_dell_storage_controller(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    (
        'Bottom Controller',
        [
            dell_storage_controller.ScController(
                name='Top Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='True',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456789',
            ),
        ],
        []
    ),
    (
        'Top Controller',
        [
            dell_storage_controller.ScController(
                name='Top Controller',
                status='Up',
                statusMessage='',
                bootDate='2020-08-21T19:38:12+02:00',
                master='True',
                modelSeries='Sc5020',
                version='7.3.20.19',
                serviceTag= 'ABCD123',
                expressServiceCode='123-456-789-00',
                serialNumber='456789',
            ),
        ],
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='Model: Sc5020 v7.3.20.19'),
            Result(state=State.OK, summary='ST: ABCD123'),
            Result(state=State.OK, summary='SN: 456789'),
        ]
    ),
])
def test_check_dell_storage_controller(item, section, result):
    assert list(dell_storage_controller.check_dell_storage_controller(item, section)) == result
