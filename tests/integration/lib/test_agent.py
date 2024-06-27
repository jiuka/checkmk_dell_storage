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

import re
import os.path
import pytest  # type: ignore[import]
import requests  # noqa: F401

from cmk_addons.plugins.dell_storage.lib.agent import AgentDellStorage, DellStorageApi


def text_callback(request, context):
    path = os.path.abspath(os.path.join(__file__, '../fixtures', request.url[25:]))
    if os.path.isfile(path):
        context.status_code = 200
        return open(path).read()
    else:
        context.status_code = 404
        return '404'


@pytest.fixture
def api(requests_mock):
    matcher = re.compile('^http://dsa:3033/rest/api/.*$')
    requests_mock.register_uri('GET', matcher, text=text_callback)
    requests_mock.register_uri('POST', matcher, text=text_callback)

    return DellStorageApi('http://dsa:3033/rest/api', 'user', 'pass', True)


class Args:
    url = 'http://dsa:3033/rest/api'
    user = 'user'
    password = 'pass'
    verify_cert = True
    debug = True


def test_AgentDellStorage_main(capsys, api):
    agent = AgentDellStorage()
    agent.main(Args())

    captured = capsys.readouterr()

    assert captured.err == ""
    assert captured.out.splitlines()[:-1] == '''\
<<<<SAN>>>>
<<<dell_storage_center:sep(59)>>>
SAN;Up;;Sc5000Series;7.3.20.19;ABCD123;123456;0;2;44;0;38;0;8;19
<<<dell_storage_controller:sep(59)>>>
Bottom Controller;Up;;1970-01-01T01:00:00+01:00;False;Sc5020;7.3.20.19;ABCD123;123-456-789-00;123457
Top Controller;Up;;1970-01-01T01:00:00+01:00;True;Sc5020;7.3.20.19;ABCD123;123-456-789-00;123456
<<<dell_storage_enclosure:sep(59)>>>
Enclosure - 1;Up;;EN-SC5020;1.05;SasEbod12g;30;ABCD123;123-456-789-00
Enclosure - 2;Up;;EN-SC420;1.09;SasEbod12g;24;JKSRF82;123-456-789-01
<<<dell_storage_volume:sep(59)>>>
SAN-LUN1;Up;;420166500352;2748779069440;0;0;0.0;2;1024;5.5e-05
SAN-LUN2;Up;;3673669238784;6597069766656;17;624640;0.00358;128;2139136;0.000768
SAN-LUN3;Up;;3673669238784;6597069766656;;;;;;
<<<dell_storage_alert:sep(59)>>>
VisualIdentifierAlert;Enclosure component 01-01 in Enclosure - 1 has turned on a visual indicator.;True;http://kbredir.compellent.com/troubletree_url/default.html?EventID=012011027&Model=5000&OSVersion=07.03.20
<<<<>>>>
<<<<SAN-Enclosure-1>>>>
<<<dell_storage_fan:sep(59)>>>
Fan 1;Up;;Fan 1, Single rotor, Front Fan rotor furthest from AC inlet, Power Supply 1;5760;0;1800;2040;18000;20000;30600
Fan 2;Up;;Fan 2, Single rotor, Rear Fan rotor closest to AC inlet, Power Supply 1;5520;0;1800;2040;18000;20000;30600
<<<dell_storage_psu:sep(59)>>>
PowerSupply1;Up;;None
PowerSupply2;Up;;None
<<<dell_storage_temp:sep(59)>>>
Ambient;Up;;None;19;-128;-7;3;42;47;127
Midplane One;Up;;None;21;-128;-7;3;48;53;127
<<<<>>>>
<<<<SAN-BottomController>>>>
<<<dell_storage_controller:sep(59)>>>
Bottom Controller;Up;;1970-01-01T01:00:00+01:00;False;Sc5020;7.3.20.19;ABCD123;123-456-789-00;123457
<<<dell_storage_port:sep(59)>>>
5555555555555526;Up;;True;Sas;5555555555555526;619;26691584;0.000336;1360;126127104;0.000118
555555555555552C;Up;;True;Iscsi;555555555555552C;;;;;;
<<<dell_storage_fan:sep(59)>>>
<<<dell_storage_psu:sep(59)>>>
<<<dell_storage_temp:sep(59)>>>
BBU;Up;;None;25;-128;-7;10;55;65;127
CPU One;Up;;None;46;-128;3;8;92;97;127
<<<<>>>>
<<<<SAN-TopController>>>>
<<<dell_storage_controller:sep(59)>>>
Top Controller;Up;;1970-01-01T01:00:00+01:00;True;Sc5020;7.3.20.19;ABCD123;123-456-789-00;123456
<<<dell_storage_port:sep(59)>>>
5555555555555518;Up;;True;Iscsi;5555555555555518;13;657408;0.002293;148;2349056;0.000584
5555555555555516;Up;;True;Iscsi;5555555555555516;14;724992;0.002398;151;2310144;0.000549
<<<dell_storage_fan:sep(59)>>>
<<<dell_storage_psu:sep(59)>>>
<<<dell_storage_temp:sep(59)>>>
CPU One;Up;;None;45;-128;3;8;92;97;127
BBU;Up;;None;27;-128;-7;10;55;65;127
<<<<>>>>
<<<<SAN-Enclosure-1>>>>
<<<dell_storage_enclosure:sep(59)>>>
Enclosure - 1;Up;;EN-SC5020;1.05;SasEbod12g;30;ABCD123;123-456-789-00
<<<dell_storage_fan:sep(59)>>>
<<<dell_storage_disk:sep(59)>>>
01-16;Up;;360081014784;1800360124416;2;74752;0.003753;0;0;0.0
01-08;Up;;1661088579584;1800360124416;;;;;;
<<<dell_storage_psu:sep(59)>>>
<<<dell_storage_temp:sep(59)>>>
<<<<>>>>
<<<<SAN-Enclosure-2>>>>
<<<dell_storage_enclosure:sep(59)>>>
Enclosure - 2;Up;;EN-SC420;1.09;SasEbod12g;24;JKSRF82;123-456-789-01
<<<dell_storage_fan:sep(59)>>>
02-01;Up;;In Power Supply - Back Left
02-02;Up;;In Power Supply - Back Left
<<<dell_storage_disk:sep(59)>>>
02-06;Up;;360081014784;1800360124416;1;68608;0.004245;0;0;0.0
02-22;Up;;1638583517184;1800360124416;3;116736;0.0041;0;1024;0.0
<<<dell_storage_psu:sep(59)>>>
02-01;Up;;Back Left
02-02;Up;;Back Right
<<<dell_storage_temp:sep(59)>>>
02-01;Up;;Ambient;19;;0;5;45;48;
02-02;Up;;Midplane;26;;4;9;54;57;
<<<<>>>>
<<<dell_storage_agent:sep(59)>>>
'''.splitlines()
