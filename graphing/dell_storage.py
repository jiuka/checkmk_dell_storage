#!/usr/bin/python
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

from cmk.graphing.v1 import graphs, metrics, perfometers, translations, Title

translation_dell_storage_center = translations.Translation(
    name='dell_storage_center',
    check_commands=[translations.PassiveCheck('dell_storage_center')],
    translations={
        'disk': translations.RenameTo('dell_storage_center_disk'),
        'volume': translations.RenameTo('dell_storage_center_volume'),
        'live_volume': translations.RenameTo('dell_storage_center_live_volume'),
    },
)

translation_dell_storage_disk = translations.Translation(
    name='dell_storage_disk',
    check_commands=[translations.PassiveCheck('dell_storage_disk')],
    translations={
        'usage': translations.RenameTo('dell_storage_disk_usage'),
    },
)

translation_dell_storage_volume = translations.Translation(
    name='dell_storage_volume',
    check_commands=[translations.PassiveCheck('dell_storage_volume')],
    translations={
        'usage': translations.RenameTo('dell_storage_volume_usage'),
    },
)

metric_dell_storage_center_disk = metrics.Metric(
    name='dell_storage_center_disk',
    title=Title('Disks'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.GREEN,
)

metric_dell_storage_center_volume = metrics.Metric(
    name='dell_storage_center_volume',
    title=Title('Volumes'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.GREEN,
)

metric_dell_storage_center_live_volume = metrics.Metric(
    name='dell_storage_center_live_volume',
    title=Title('Live Volumes'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.GREEN,
)

metric_dell_storage_disk_usage = metrics.Metric(
    name='dell_storage_disk_usage',
    title=Title('Disk Usage'),
    unit=metrics.Unit(metrics.SINotation("bytes")),
    color=metrics.Color.ORANGE,
)

metric_dell_storage_volume_usage = metrics.Metric(
    name='dell_storage_volume_usage',
    title=Title('Volume Usage'),
    unit=metrics.Unit(metrics.SINotation("bytes")),
    color=metrics.Color.ORANGE,
)

graph_dell_storage_center_disk = graphs.Graph(
    name='dell_storage_center_disk',
    title=Title('Storage Center Disks'),
    simple_lines=[
        'dell_storage_center_disk',
        'dell_storage_center_volume',
        'dell_storage_center_live_volume',
    ],
)

graph_dell_storage_disk_usage = graphs.Graph(
    name='dell_storage_disk_usage',
    title=Title('Disk usage'),
    minimal_range=graphs.MinimalRange(0, 100),
    compound_lines=['dell_storage_disk_usage'],
)

graph_dell_storage_volume_usage = graphs.Graph(
    name='dell_storage_volume_usage',
    title=Title('Volume usage'),
    minimal_range=graphs.MinimalRange(0, 100),
    compound_lines=['dell_storage_volume_usage'],
)

perfometer_dell_storage_center  = perfometers.Stacked(
    name='dell_storage_center',
    upper=perfometers.Perfometer(
        name='dell_storage_center_disk',
        focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(10)),
        segments=['dell_storage_center_disk'],
    ),
    lower=perfometers.Perfometer(
        name='dell_storage_center_volume',
        focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(10)),
        segments=['dell_storage_center_volume'],
    ),
)
