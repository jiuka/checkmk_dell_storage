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

from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Alternative,
    Dictionary,
    FixedValue,
    HTTPUrl,
    TextAscii,
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware


def _valuespec_special_agents_dell_storage():
    return Dictionary(
        title = _('Dell Storage via Dell Storage API'),
        help = _('This rule selects the Dell Storage API agent instead of '
                 'the normal Check_MK Agent and allows monitoring of '
                 'Dell Storage Manager systems and volumes by REST. '
                 'You can configure your connection settings here.'
                 ),
        elements=[
            (
                'url',
                HTTPUrl(
                    title = _('URL of the Dell Storage API, e.g. https://host:3033/api/rest/'),
                    allow_empty = False,
                )
            ),
            (
                'user',
                TextAscii(
                    title = _('Dell Storage API username.'),
                    allow_empty = False,
                )
            ),
            (
                'password',
                IndividualOrStoredPassword(
                    title = _('Dell Storage API password'),
                    allow_empty = False,
                )
            ),
            (
                'ignore_cert',
                Alternative(
                    title = _('SSL certificate checking'),
                    elements = [
                        FixedValue(True, title = _('Ignore Cert'), totext=''),
                        FixedValue(False, title = _('Check Cert'), totext=''),
                    ],
                    default_value = False
                )
            ),
        ]
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name='special_agents:dell_storage',
        valuespec=_valuespec_special_agents_dell_storage,
    ))
