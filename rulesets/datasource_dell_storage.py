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

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    migrate_to_password,
    Password,
    SingleChoice,
    SingleChoiceElement,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def migrate_bool_to_choice(model: object) -> str:
    if isinstance(model, bool):
        return 'ignore_cert' if model else 'check_cert'
    return model


def _form_special_agents_dell_storage() -> Dictionary:
    return Dictionary(
        title=Title('Dell Storage via Dell Storage API'),
        elements={
            'url': DictElement(
                parameter_form=String(
                    title=Title('URL of the Dell Storage API, e.g. https://host:3033/api/rest/'),
                    custom_validate=(
                        validators.Url(
                            [validators.UrlProtocol.HTTP, validators.UrlProtocol.HTTPS],
                        ),
                    ),
                ),
                required=True,
            ),
            'user': DictElement(
                parameter_form=String(
                    title=Title('Dell Storage API username.'),
                ),
                required=True,
            ),
            'password': DictElement(
                parameter_form=Password(
                    title=Title('Dell Storage API password'),
                    migrate=migrate_to_password
                ),
                required=True,
            ),
            'ignore_cert': DictElement(
                parameter_form=SingleChoice(
                    title=Title('SSL certificate checking'),
                    elements=[
                        SingleChoiceElement(name='ignore_cert', title=Title('Ignore Cert')),
                        SingleChoiceElement(name='check_cert', title=Title('Check Cert')),
                    ],
                    prefill=DefaultValue('check_cert'),
                    migrate=migrate_bool_to_choice,
                ),
                required=True,
            ),
        }
    )


rule_spec_dell_storage_datasource = SpecialAgent(
    name="dell_storage",
    title=Title('Dell Storage via Dell Storage API'),
    help_text=Help(
        'This rule selects the Dell Storage API agent instead of '
        'the normal Check_MK Agent and allows monitoring of '
        'Dell Storage Manager systems and volumes by REST. '
        'You can configure your connection settings here.'
    ),
    topic=Topic.STORAGE,
    parameter_form=_form_special_agents_dell_storage,
)
