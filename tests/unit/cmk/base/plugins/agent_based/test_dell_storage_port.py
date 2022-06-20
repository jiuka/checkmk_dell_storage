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
from cmk.base.plugins.agent_based import dell_storage_port

SAMPLE_STRING_TABLE = [
    ['5000D310055E9018', 'Up', '', 'True', 'Iscsi', '5000D310055E9018', '18', '945152', '0.002458', '147', '2330624', '0.000434'],
    ['5000D310055E9016', 'Up', '', 'True', 'Iscsi', '5000D310055E9016', '16', '899072', '0.002574', '159', '2462720', '0.000459'],
]

SAMPLE_SECTION = [
    dell_storage_port.ScPort(
        name='5000D310055E9018',
        status='Up',
        statusMessage='',
        cabled='True',
        type='Iscsi',
        wwn='5000D310055E9018',
        readIops='18',
        readBps='945152',
        readLatency='0.002458',
        writeIops='147',
        writeBps='2330624',
        writeLatency='0.000434',
    ),
    dell_storage_port.ScPort(
        name='5000D310055E9016',
        status='Up',
        statusMessage='',
        cabled='True',
        type='Iscsi',
        wwn='5000D310055E9016',
        readIops='16',
        readBps='899072',
        readLatency='0.002574',
        writeIops='159',
        writeBps='2462720',
        writeLatency='0.000459',
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
def test_parse_dell_storage_port(string_table, result):
    assert list(dell_storage_port.parse_dell_storage_port(string_table)) == result


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
def test_discovery_dell_storage_port(section, result):
    assert list(dell_storage_port.discovery_dell_storage_port(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', [], []),
    ('01-08', SAMPLE_SECTION, []),
    (
        SAMPLE_SECTION[0].name,
        SAMPLE_SECTION,
        [
            Result(state=State.OK, summary='Up'),
            Result(state=State.OK, summary='Cabled: True'),
            Result(state=State.OK, summary='Type: Iscsi'),
            Result(state=State.OK, summary='WWN: 5000D310055E9018'),
            Result(state=State.OK, summary='Read: 945 kB/s'),
            Metric('disk_read_throughput', 945152),
            Result(state=State.OK, summary='Write: 2.33 MB/s'),
            Metric('disk_write_throughput', 2330624),
            Result(state=State.OK, notice='Read operations: 18.00/s'),
            Metric('disk_read_ios', 18),
            Result(state=State.OK, notice='Write operations: 147.00/s'),
            Metric('disk_write_ios', 147),
            Result(state=State.OK, notice='Read latency: 2 milliseconds'),
            Metric('disk_read_latency', 0.002458),
            Result(state=State.OK, notice='Write latency: 434 microseconds'),
            Metric('disk_write_latency', 0.000434),
        ]
    ),
])
def test_check_dell_storage_port(item, section, result, mocker):
    mocker.patch(
        'cmk.base.plugins.agent_based.dell_storage_port.get_value_store',
        return_value={}
    )

    assert list(dell_storage_port.check_dell_storage_port(item, {}, section)) == result


@pytest.mark.parametrize('params, result', [
    (
        {'read': (1, 2)},
        Result(state=State.OK, summary='Read: 899 kB/s'),
    ),
    (
        {'read': (0.5, 2)},
        Result(state=State.WARN, summary='Read: 899 kB/s (warn/crit at 500 kB/s/2.00 MB/s)')
    ),
    (
        {'read': (0.5, 0.8)},
        Result(state=State.CRIT, summary='Read: 899 kB/s (warn/crit at 500 kB/s/800 kB/s)')
    ),
    (
        {'write': (3, 4)},
        Result(state=State.OK, summary='Write: 2.46 MB/s')
    ),
    (
        {'write': (1, 4)},
        Result(state=State.WARN, summary='Write: 2.46 MB/s (warn/crit at 1.00 MB/s/4.00 MB/s)')
    ),
    (
        {'write': (1, 2)},
        Result(state=State.CRIT, summary='Write: 2.46 MB/s (warn/crit at 1.00 MB/s/2.00 MB/s)')
    ),
    (
        {'read_ios': (20, 30)},
        Result(state=State.OK, notice='Read operations: 16.00/s'),
    ),
    (
        {'read_ios': (5, 30)},
        Result(state=State.WARN, notice='Read operations: 16.00/s (warn/crit at 5.00/s/30.00/s)'),
    ),
    (
        {'read_ios': (5, 10)},
        Result(state=State.CRIT, notice='Read operations: 16.00/s (warn/crit at 5.00/s/10.00/s)'),
    ),
    (
        {'write_ios': (200, 400)},
        Result(state=State.OK, notice='Write operations: 159.00/s'),
    ),
    (
        {'write_ios': (50, 400)},
        Result(state=State.WARN, notice='Write operations: 159.00/s (warn/crit at 50.00/s/400.00/s)'),
    ),
    (
        {'write_ios': (50, 100)},
        Result(state=State.CRIT, notice='Write operations: 159.00/s (warn/crit at 50.00/s/100.00/s)'),
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
        {'write_latency': (2, 3)},
        Result(state=State.OK, notice='Write latency: 459 microseconds'),
    ),
    (
        {'write_latency': (0.05, 3)},
        Result(state=State.WARN, notice='Write latency: 459 microseconds (warn/crit at 50 microseconds/3 milliseconds)'),
    ),
    (
        {'write_latency': (0.05, 0.06)},
        Result(state=State.CRIT, notice='Write latency: 459 microseconds (warn/crit at 50 microseconds/60 microseconds)'),
    ),
])
def test_check_dell_storage_port_w_param(params, result, mocker):
    mocker.patch(
        'cmk.base.plugins.agent_based.dell_storage_port.get_value_store',
        return_value={}
    )

    assert result in list(dell_storage_port.check_dell_storage_port(SAMPLE_SECTION[1].name, params, [SAMPLE_SECTION[1]]))
