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
from cmk.base.plugins.agent_based import dell_storage_disk


@pytest.mark.parametrize('string_table, result', [
    (
        [['01-16', 'Up', '', '360081014784', '1800360124416', '1', '49152', '0.003444', '2', '14336', '0.0']],
        [dell_storage_disk.ScDisk(
            name='01-16',
            status='Up',
            statusMessage='',
            allocatedSpace='360081014784',
            totalSpace='1800360124416',
            readIops='1',
            readBps='49152',
            readLatency='0.003444',
            writeIops='2',
            writeBps='14336',
            writeLatency='0.0',
        )]
    ),
    (
        [
            ['01-16', 'Up', '', '360081014784', '1800360124416', '1', '49152', '0.003444', '2', '14336', '0.0'],
            ['01-08', 'Up', '', '1661088579584', '1800360124416', '4', '121856', '0.003447', '2', '22528', '0.0'],
        ],
        [
            dell_storage_disk.ScDisk(
                name='01-16',
                status='Up',
                statusMessage='',
                allocatedSpace='360081014784',
                totalSpace='1800360124416',
                readIops='1',
                readBps='49152',
                readLatency='0.003444',
                writeIops='2',
                writeBps='14336',
                writeLatency='0.0',
            ),
            dell_storage_disk.ScDisk(
                name='01-08',
                status='Up',
                statusMessage='',
                allocatedSpace='1661088579584',
                totalSpace='1800360124416',
                readIops='4',
                readBps='121856',
                readLatency='0.003447',
                writeIops='2',
                writeBps='22528',
                writeLatency='0.0',
            )
        ]
    ),
])
def test_parse_dell_storage_disk(string_table, result):
    assert list(dell_storage_disk.parse_dell_storage_disk(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [
            dell_storage_disk.ScDisk(
                name='01-16',
                status='Up',
                statusMessage='',
                allocatedSpace='360081014784',
                totalSpace='1800360124416',
                readIops='1',
                readBps='49152',
                readLatency='0.003444',
                writeIops='2',
                writeBps='14336',
                writeLatency='0.0',
            ),
        ],
        [Service(item='01-16')]
    ),
    (
        [
            dell_storage_disk.ScDisk(
                name='01-16',
                status='Up',
                statusMessage='',
                allocatedSpace='360081014784',
                totalSpace='1800360124416',
                readIops='1',
                readBps='49152',
                readLatency='0.003444',
                writeIops='2',
                writeBps='14336',
                writeLatency='0.0',
            ),
            dell_storage_disk.ScDisk(
                name='01-08',
                status='Up',
                statusMessage='',
                allocatedSpace='1661088579584',
                totalSpace='1800360124416',
                readIops='4',
                readBps='121856',
                readLatency='0.003447',
                writeIops='2',
                writeBps='22528',
                writeLatency='0.0',
            ),
        ],
        [
            Service(item='01-16'),
            Service(item='01-08')
        ]
    ),
])
def test_discovery_dell_storage_disk(section, result):
    assert list(dell_storage_disk.discovery_dell_storage_disk(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    (
        '01-08',
        [
            dell_storage_disk.ScDisk(
                name='01-16',
                status='Up',
                statusMessage='',
                allocatedSpace='360081014784',
                totalSpace='1800360124416',
                readIops='1',
                readBps='49152',
                readLatency='0.003444',
                writeIops='2',
                writeBps='14336',
                writeLatency='0.0',
            ),
        ],
        []
    ),
    (
        '01-16',
        [
            dell_storage_disk.ScDisk(
                name='01-16',
                status='Up',
                statusMessage='',
                allocatedSpace='360081014784',
                totalSpace='1800360124416',
                readIops='1',
                readBps='49152',
                readLatency='0.003444',
                writeIops='2',
                writeBps='14336',
                writeLatency='0.0',
            ),
        ],
        [
            Result(state=State.OK, summary='Up'),
            Metric('usage', 360081014784, boundaries=(0, 1800360124416)),
            Result(state=State.OK, summary='Read: 49.2 kB/s'),
            Metric('disk_read_throughput', 49152),
            Result(state=State.OK, summary='Write: 14.3 kB/s'),
            Metric('disk_write_throughput', 14336),
            Result(state=State.OK, notice='Read operations: 1.00/s'),
            Metric('disk_read_ios', 1),
            Result(state=State.OK, notice='Write operations: 2.00/s'),
            Metric('disk_write_ios', 2),
            Result(state=State.OK, notice='Read latency: 3 milliseconds'),
            Metric('disk_read_latency', 0.003444),
            Result(state=State.OK, notice='Write latency: 0 seconds'),
            Metric('disk_write_latency', 0.0),
        ]
    ),
])
def test_check_dell_storage_disk(item, section, result):
    assert list(dell_storage_disk.check_dell_storage_disk(item, {}, section)) == result


SAMPLE_DISK = dell_storage_disk.ScDisk(
    name='01-16',
    status='Up',
    statusMessage='',
    allocatedSpace='360081014784',
    totalSpace='1800360124416',
    readIops='1',
    readBps='49152',
    readLatency='0.003444',
    writeIops='2',
    writeBps='14336',
    writeLatency='0.002333',
)


@pytest.mark.parametrize('params, result', [
    (
        {'read': (0.1, 1)},
        Result(state=State.OK, summary='Read: 49.2 kB/s')
    ),
    (
        {'read': (0.04, 1)},
        Result(state=State.WARN, summary='Read: 49.2 kB/s (warn/crit at 40.0 kB/s/1.00 MB/s)')
    ),
    (
        {'read': (0.03, 0.04)},
        Result(state=State.CRIT, summary='Read: 49.2 kB/s (warn/crit at 30.0 kB/s/40.0 kB/s)')
    ),
    (
        {'write': (0.5, 1)},
        Result(state=State.OK, summary='Write: 14.3 kB/s')
    ),
    (
        {'write': (0.01, 1)},
        Result(state=State.WARN, summary='Write: 14.3 kB/s (warn/crit at 10.0 kB/s/1.00 MB/s)')
    ),
    (
        {'write': (0.008, 0.01)},
        Result(state=State.CRIT, summary='Write: 14.3 kB/s (warn/crit at 8.00 kB/s/10.0 kB/s)')
    ),
    (
        {'read_ios': (2, 3)},
        Result(state=State.OK, notice='Read operations: 1.00/s'),
    ),
    (
        {'read_ios': (1, 3)},
        Result(state=State.WARN, notice='Read operations: 1.00/s (warn/crit at 1.00/s/3.00/s)'),
    ),
    (
        {'read_ios': (0, 1)},
        Result(state=State.CRIT, notice='Read operations: 1.00/s (warn/crit at 0.00/s/1.00/s)'),
    ),
    (
        {'write_ios': (3, 4)},
        Result(state=State.OK, notice='Write operations: 2.00/s'),
    ),
    (
        {'write_ios': (2, 3)},
        Result(state=State.WARN, notice='Write operations: 2.00/s (warn/crit at 2.00/s/3.00/s)'),
    ),
    (
        {'write_ios': (1, 2)},
        Result(state=State.CRIT, notice='Write operations: 2.00/s (warn/crit at 1.00/s/2.00/s)'),
    ),
    (
        {'read_latency': (4, 5)},
        Result(state=State.OK, notice='Read latency: 3 milliseconds'),
    ),
    (
        {'read_latency': (1, 5)},
        Result(state=State.WARN, notice='Read latency: 3 milliseconds (warn/crit at 1 millisecond/5 milliseconds)'),
    ),
    (
        {'read_latency': (1, 2)},
        Result(state=State.CRIT, notice='Read latency: 3 milliseconds (warn/crit at 1 millisecond/2 milliseconds)'),
    ),
    (
        {'write_latency': (4, 5)},
        Result(state=State.OK, notice='Write latency: 2 milliseconds'),
    ),
    (
        {'write_latency': (1, 5)},
        Result(state=State.WARN, notice='Write latency: 2 milliseconds (warn/crit at 1 millisecond/5 milliseconds)'),
    ),
    (
        {'write_latency': (0, 1)},
        Result(state=State.CRIT, notice='Write latency: 2 milliseconds (warn/crit at 0 seconds/1 millisecond)'),
    ),
])
def test_check_dell_storage_disk_w_param(params, result):
    assert result in list(dell_storage_disk.check_dell_storage_disk(SAMPLE_DISK.name, params, [SAMPLE_DISK]))
