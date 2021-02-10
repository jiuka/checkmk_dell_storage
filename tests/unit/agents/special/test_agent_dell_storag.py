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
import requests

from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader 

spec = spec_from_loader("agent_dell_storage", SourceFileLoader("agent_dell_storage", "agents/special/agent_dell_storage"))
agent_dell_storage = module_from_spec(spec)
spec.loader.exec_module(agent_dell_storage)


class TestDellStorageApiParser:
    @pytest.mark.parametrize('value, result', [
        ('', None),
        ('0°C / 3°F', 0),
        ('100°C / 212°F', 100),
    ])
    def test_DellStorageApiParser_temperature(self, value, result):
        assert agent_dell_storage.DellStorageApiParser.temperature(value) == result

    @pytest.mark.parametrize('value, result', [
        ('10', 10240),
        ('1', 1024),
    ])
    def test_DellStorageApiParser_kbps(self, value, result):
        assert agent_dell_storage.DellStorageApiParser.kbps(value) == result

    @pytest.mark.parametrize('value, result', [
        ('1000000', 1),
        ('1', 0.000001),
    ])
    def test_DellStorageApiParser_latency(self, value, result):
        assert agent_dell_storage.DellStorageApiParser.latency(value) == result

    @pytest.mark.parametrize('value, result', [
        ('10 Bit', 10),
        ('123 Bit', 123),
    ])
    def test_DellStorageApiParser_space(self, value, result):
        assert agent_dell_storage.DellStorageApiParser.space(value) == result


LOGIN_RESP = dict(provider='PRO', providerVersion='VERS', instanceId='123')
STORAGE_CENTERS = [dict(a=1)]


class TestDellStorageApi:
    @pytest.fixture
    def api(self, requests_mock):
        requests_mock.post('http://dsa:3033/rest/api/ApiConnection/Login', json=LOGIN_RESP)
        requests_mock.get('http://dsa:3033/rest/api/ApiConnection/ApiConnection/123/StorageCenterList', json=STORAGE_CENTERS)

        return agent_dell_storage.DellStorageApi('http://dsa:3033/rest/api', 'user', 'pass', True)

    def test_init(self, api):
        assert api._api['provider'] == 'PRO'

    @pytest.mark.parametrize('call, result', [
        ('/Path', 'http://dsa:3033/rest/api/Path'),
        ('Path', 'http://dsa:3033/rest/api/Path'),
    ])
    def test_url(self, api, call, result):
        assert api.url(call) == result

    def test_storage_centers(self, api, requests_mock):
        assert type(api.storage_centers[0]) == agent_dell_storage.DellStorageApi.StorageCenter

    def test_storage_centers_cached(self, api, requests_mock):
        api.storage_centers
        pre = api.reqcnt
        api.storage_centers
        post = api.reqcnt
        assert pre == post

    def test_get(self, api, requests_mock):
        requests_mock.get('http://dsa:3033/rest/api/PyTest', json=dict(foo='bar'))

        assert api.get('PyTest') == dict(foo='bar')

    def test_post(self, api, requests_mock):
        requests_mock.post('http://dsa:3033/rest/api/PyTest', json=dict(foo='bar'))

        assert api.post('PyTest', payload=None) == dict(foo='bar')

    def test_provider(self, api):
        assert api.provider == 'PRO'

    def test_providerVersion(self, api):
        assert api.providerVersion == 'VERS'

    class TestApiObject:
        class MockApiObject(agent_dell_storage.DellStorageApi.ApiObject):
            AGENT_FIELDS = ['foo']

            instanceId: str
            instanceName: str
            status: str
            foo: int
            bar: str

        @pytest.fixture
        def apiObject(self, api):
            return self.MockApiObject(api, instanceId='#1', instanceName='name', status='Up', foo='123', bar='foo')

        def test_init(self, api):
            assert self.MockApiObject(api, instanceId='#1', instanceName='name', status='Up', foo='123', bar='foo')

        def test_repr(self, apiObject):
            assert repr(apiObject) == '<MockApiObject name #1>'

        def test_fields(self, apiObject):
            assert apiObject._fields() == ['instanceName', 'status', 'statusMessage', 'foo']

        def test_to_agent(self, apiObject):
            assert apiObject.to_agent() == 'name;Up;None;123'

        def test_to_agent_sep(self, apiObject):
            assert apiObject.to_agent('-') == 'name-Up-None-123'
