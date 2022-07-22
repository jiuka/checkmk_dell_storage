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
from cmk.base.plugins.agent_based import dell_storage_volume

SAMPLE_STRING_TABLE = [
    ['SAN-LUN01', 'Up', '', '420166500352', '2748779069440', '0', '0', '0.0', '1', '1024', '5.6e-05'],
    ['SAN-LUN02(6)', 'Up', '', '3607283892224', '6597069766656', '14', '292864', '0.002162', '117', '1913856', '0.000857'],
    ['SAN-LUN03', 'Up', '', '3607283892224', '6597069766656', '', '', '', '', '', ''],
]

SAMPLE_SECTION = [
    dell_storage_volume.ScVolume(
        name='SAN-LUN01',
        status='Up',
        statusMessage='',
        activeSpace='420166500352',
        configuredSpace='2748779069440',
        readIops='0',
        readBps='0',
        readLatency='0.0',
        writeIops='1',
        writeBps='1024',
        writeLatency='5.6e-05',
    ),
    dell_storage_volume.ScVolume(
        name='SAN-LUN02(6)',
        status='Up',
        statusMessage='',
        activeSpace='3607283892224',
        configuredSpace='6597069766656',
        readIops='14',
        readBps='292864',
        readLatency='0.002162',
        writeIops='117',
        writeBps='1913856',
        writeLatency='0.000857',
    ),
    dell_storage_volume.ScVolume(
        name='SAN-LUN03',
        status='Up',
        statusMessage='',
        activeSpace='3607283892224',
        configuredSpace='6597069766656',
        readIops='',
        readBps='',
        readLatency='',
        writeIops='',
        writeBps='',
        writeLatency='',
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
def test_parse_dell_storage_volume(string_table, result):
    assert list(dell_storage_volume.parse_dell_storage_volume(string_table)) == result


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
            Service(item=SAMPLE_SECTION[2].name),
        ]
    ),
])
def test_discovery_dell_storage_volume(section, result):
    assert list(dell_storage_volume.discovery_dell_storage_volume(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    ('01-08', SAMPLE_SECTION, []),
    (
        SAMPLE_SECTION[1].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Metric('usage', 3607283892224, boundaries=(0, 6597069766656)),
            Result(state=State.OK, summary='Read: 293 kB/s'),
            Metric('disk_read_throughput', 292864),
            Result(state=State.OK, summary='Write: 1.91 MB/s'),
            Metric('disk_write_throughput', 1913856),
            Result(state=State.OK, notice='Read operations: 14.00/s'),
            Metric('disk_read_ios', 14),
            Result(state=State.OK, notice='Write operations: 117.00/s'),
            Metric('disk_write_ios', 117),
            Result(state=State.OK, notice='Read latency: 2 milliseconds'),
            Metric('disk_read_latency', 0.002162),
            Result(state=State.OK, notice='Write latency: 857 microseconds'),
            Metric('disk_write_latency', 0.000857),
        ]
    ),
    (
        SAMPLE_SECTION[2].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Metric('usage', 3607283892224, boundaries=(0, 6597069766656)),
        ]
    ),
])
def test_check_dell_storage_volume(item, section, result, mocker):
    mocker.patch(
        'cmk.base.plugins.agent_based.dell_storage_volume.get_value_store',
        return_value={}
    )

    assert list(dell_storage_volume.check_dell_storage_volume(item, {}, section)) == result


@pytest.mark.parametrize('params, result', [
    (
        {'read': (1, 2)},
        Result(state=State.OK, summary='Read: 293 kB/s')
    ),
    (
        {'read': (0.1, 2)},
        Result(state=State.WARN, summary='Read: 293 kB/s (warn/crit at 100 kB/s/2.00 MB/s)')
    ),
    (
        {'read': (0.1, 0.2)},
        Result(state=State.CRIT, summary='Read: 293 kB/s (warn/crit at 100 kB/s/200 kB/s)')
    ),
    (
        {'write': (2, 3)},
        Result(state=State.OK, summary='Write: 1.91 MB/s')
    ),
    (
        {'write': (1, 3)},
        Result(state=State.WARN, summary='Write: 1.91 MB/s (warn/crit at 1.00 MB/s/3.00 MB/s)')
    ),
    (
        {'write': (1, 1.5)},
        Result(state=State.CRIT, summary='Write: 1.91 MB/s (warn/crit at 1.00 MB/s/1.50 MB/s)')
    ),
    (
        {'read_ios': (20, 30)},
        Result(state=State.OK, notice='Read operations: 14.00/s'),
    ),
    (
        {'read_ios': (5, 30)},
        Result(state=State.WARN, notice='Read operations: 14.00/s (warn/crit at 5.00/s/30.00/s)'),
    ),
    (
        {'read_ios': (5, 10)},
        Result(state=State.CRIT, notice='Read operations: 14.00/s (warn/crit at 5.00/s/10.00/s)'),
    ),
    (
        {'write_ios': (200, 400)},
        Result(state=State.OK, notice='Write operations: 117.00/s'),
    ),
    (
        {'write_ios': (50, 400)},
        Result(state=State.WARN, notice='Write operations: 117.00/s (warn/crit at 50.00/s/400.00/s)'),
    ),
    (
        {'write_ios': (50, 100)},
        Result(state=State.CRIT, notice='Write operations: 117.00/s (warn/crit at 50.00/s/100.00/s)'),
    ),
    (
        {'read_latency': (4, 5)},
        Result(state=State.OK, notice='Read latency: 2 milliseconds'),
    ),
    (
        {'read_latency': (1, 5)},
        Result(state=State.WARN, notice='Read latency: 2 milliseconds (warn/crit at 1 millisecond/5 milliseconds)'),
    ),
    (
        {'read_latency': (1, 2)},
        Result(state=State.CRIT, notice='Read latency: 2 milliseconds (warn/crit at 1 millisecond/2 milliseconds)'),
    ),
    (
        {'write_latency': (2, 3)},
        Result(state=State.OK, notice='Write latency: 857 microseconds'),
    ),
    (
        {'write_latency': (0.5, 3)},
        Result(state=State.WARN, notice='Write latency: 857 microseconds (warn/crit at 500 microseconds/3 milliseconds)'),
    ),
    (
        {'write_latency': (0.5, 0.6)},
        Result(state=State.CRIT, notice='Write latency: 857 microseconds (warn/crit at 500 microseconds/600 microseconds)'),
    ),
])
def test_check_dell_storage_volume_w_param(params, result, mocker):
    mocker.patch(
        'cmk.base.plugins.agent_based.dell_storage_volume.get_value_store',
        return_value={}
    )

    assert result in list(dell_storage_volume.check_dell_storage_volume(SAMPLE_SECTION[1].name, params, [SAMPLE_SECTION[1]]))
