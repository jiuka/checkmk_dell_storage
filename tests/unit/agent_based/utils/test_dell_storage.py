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
from typing import NamedTuple
from cmk.agent_based.v2 import (
    Result,
    State,
)
from cmk.base.plugins.agent_based.utils import dell_storage


@pytest.mark.parametrize('value, result', [
    ('Up', State.OK),
    ('Degraded', State.WARN),
    ('Down', State.CRIT),
    ('Unknown', State.UNKNOWN),
    ('FooBar', State.UNKNOWN),
    (None, State.UNKNOWN),
])
def test_dsstatus(value, result):
    assert dell_storage.DSStatus(value) == result


class MockDsObject(NamedTuple):
    status: str = None
    statusMessage: str = None


@pytest.mark.parametrize('dsobject, result', [
    (MockDsObject('Up'), Result(state=State.OK, summary='Up')),
    (MockDsObject('Up', 'foo'), Result(state=State.OK, summary='Up: foo')),
    (MockDsObject('Degraded', 'foo'), Result(state=State.WARN, summary='Degraded: foo')),
    (MockDsObject('Down', 'foo'), Result(state=State.CRIT, summary='Down: foo')),
    (MockDsObject('Unknown', 'foo'), Result(state=State.UNKNOWN, summary='Unknown: foo')),
    (MockDsObject('Foo', 'foo'), Result(state=State.UNKNOWN, summary='Foo: foo')),
])
def test_dsresult(dsobject, result):
    assert list(dell_storage.DSResult(dsobject)) == [result]
