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
from cmk.base.plugins.agent_based import dell_storage_center


@pytest.mark.parametrize('string_table, result', [
    (
        [['SAN', 'Up', '', 'Sc5000Series', '7.3.20.19', 'ABCD123', '987654', '0', '2', '4', '0', '19', '0', '8', '19']],
        [dell_storage_center.StorageCenter(
            name='SAN',
            status='Up',
            statusMessage='',
            modelSeries='Sc5000Series',
            version='7.3.20.19',
            serviceTag='ABCD123',
            serialNumber='987654',
            numberOfControllers= '0',
            numberOfDevicesInUse='2',
            numberOfDisks='4',
            numberOfLiveVolumes='0',
            numberOfReplays='19',
            numberOfReplications='0',
            numberOfServers='8',
            numberOfVolumes='19',
        )]
    ),
])
def test_parse_dell_storage_center(string_table, result):
    assert list(dell_storage_center.parse_dell_storage_center(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [
            dell_storage_center.StorageCenter(
                name='SAN',
                status='Up',
                statusMessage='',
                modelSeries='Sc5000Series',
                version='7.3.20.19',
                serviceTag='ABCD123',
                serialNumber='987654',
                numberOfControllers= '0',
                numberOfDevicesInUse='2',
                numberOfDisks='4',
                numberOfLiveVolumes='0',
                numberOfReplays='19',
                numberOfReplications='0',
                numberOfServers='8',
                numberOfVolumes='19',
            )
        ],
        [Service(item='SAN')]
    ),
    (
        [
            dell_storage_center.StorageCenter(
                name='SAN',
                status='Up',
                statusMessage='',
                modelSeries='Sc5000Series',
                version='7.3.20.19',
                serviceTag='ABCD123',
                serialNumber='987654',
                numberOfControllers= '0',
                numberOfDevicesInUse='2',
                numberOfDisks='4',
                numberOfLiveVolumes='0',
                numberOfReplays='19',
                numberOfReplications='0',
                numberOfServers='8',
                numberOfVolumes='19',
            ),
            dell_storage_center.StorageCenter(
                name='SAN2',
                status='Up',
                statusMessage='',
                modelSeries='Sc5000Series',
                version='7.3.20.19',
                serviceTag='ABCD123',
                serialNumber='987654',
                numberOfControllers= '0',
                numberOfDevicesInUse='2',
                numberOfDisks='4',
                numberOfLiveVolumes='0',
                numberOfReplays='19',
                numberOfReplications='0',
                numberOfServers='8',
                numberOfVolumes='19',
            )
        ],
        [
            Service(item='SAN'),
            Service(item='SAN2')
        ]
    ),
])
def test_discovery_dell_storage_center(section, result):
    assert list(dell_storage_center.discovery_dell_storage_center(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    (
        'SAN',
        [
            dell_storage_center.StorageCenter(
                name='SAN2',
                status='Up',
                statusMessage='',
                modelSeries='Sc5000Series',
                version='7.3.20.19',
                serviceTag='ABCD123',
                serialNumber='987654',
                numberOfControllers= '0',
                numberOfDevicesInUse='2',
                numberOfDisks='4',
                numberOfLiveVolumes='0',
                numberOfReplays='19',
                numberOfReplications='0',
                numberOfServers='8',
                numberOfVolumes='19',
            )
        ],
        []
    ),
    (
        'SAN',
        [
            dell_storage_center.StorageCenter(
                name='SAN',
                status='Up',
                statusMessage='',
                modelSeries='Sc5000Series',
                version='7.3.20.19',
                serviceTag='ABCD123',
                serialNumber='987654',
                numberOfControllers= '0',
                numberOfDevicesInUse='2',
                numberOfDisks='4',
                numberOfLiveVolumes='6',
                numberOfReplays='8',
                numberOfReplications='10',
                numberOfServers='12',
                numberOfVolumes='14',
            )
        ],
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='Model: Sc5000Series v7.3.20.19'),
            Result(state=State.OK, summary='ST: ABCD123'),
            Result(state=State.OK, summary='SN: 987654'),
            Metric('controller', 0),
            Metric('device', 2),
            Metric('disk', 4),
            Metric('live_volume', 6),
            Metric('replay', 8),
            Metric('replication', 10),
            Metric('server', 12),
            Metric('volume', 14),
        ]
    ),
])
def test_check_dell_storage_center(item, section, result):
    assert list(dell_storage_center.check_dell_storage_center(item, section)) == result
