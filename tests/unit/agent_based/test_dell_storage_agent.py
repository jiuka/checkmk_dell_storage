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
from cmk_addons.plugins.dell_storage.agent_based import dell_storage_agent


@pytest.mark.parametrize('string_table, result', [
    ([], []),
    ([['FooBar']], [Service()]),
])
def test_discovery_dell_storage_agent(string_table, result):
    assert list(dell_storage_agent.discovery_dell_storage_agent(string_table)) == result


@pytest.mark.parametrize('string_table, result', [
    ([['0', 'provider', 'version', '23', '42', '']], Result(state=State.OK, summary='provider vversion')),
    ([['0', 'provider', 'version', '23', '42', '']], Metric('request', 42.0)),
    ([['0', 'provider', 'version', '23', '42', '']], Metric('time', 23)),
    ([['1', '', '', '23', '', 'Yolo']], Result(state=State.CRIT, summary='Exception: Yolo')),
])
def test_check_dell_storage_agent(string_table, result):
    assert result in list(dell_storage_agent.check_dell_storage_agent(string_table))
