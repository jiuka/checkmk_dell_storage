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

from cmk.gui.i18n import _

from cmk.gui.plugins.metrics import (
    check_metrics,
    metric_info,
    graph_info,
    perfometer_info,
)

check_metrics['check_mk-dell_storage_center'] = {
    'disk': {'name': 'dell_storage_center_disk'},
    'volume': {'name': 'dell_storage_center_volume'},
    'live_volume': {'name': 'dell_storage_center_live_volume'},
}

check_metrics['check_mk-dell_storage_disk'] = {
    'usage': {'name': 'dell_storage_disk_usage'},
}

check_metrics['check_mk-dell_storage_volume'] = {
    'usage': {'name': 'dell_storage_volume_usage'},
}

metric_info['dell_storage_center_disk'] = {
    'title': _('Disks'),
    'unit': 'count',
    'color': '#40c080',
}

metric_info['dell_storage_center_volume'] = {
    'title': _('Volumes'),
    'unit': 'count',
    'color': '#4080c0',
}

metric_info['dell_storage_center_live_volume'] = {
    'title': _('Live Volumes'),
    'unit': 'count',
    'color': '#c04080',
}


metric_info['dell_storage_disk_usage'] = {
    'title': _('Disk Usage'),
    'unit': 'bytes',
    'color': '#a05830',
}

metric_info['dell_storage_volume_usage'] = {
    'title': _('Volume Usage'),
    'unit': 'bytes',
    'color': '#a05830',
}

graph_info['dell_storage_center_disk'] = {
    'title': _('Storage Center Disks'),
    'metrics': [
        ('dell_storage_center_disk', 'line'),
        ('dell_storage_center_volume', 'line'),
        ('dell_storage_center_live_volume', 'line'),
    ],
}

graph_info['dell_storage_disk_usage'] = {
    'title': _('Disk usage'),
    'metrics': [
        ('dell_storage_disk_usage', 'area'),
    ],
    'range': (0, 'dell_storage_disk_usage:max'),
}

graph_info['dell_storage_volume_usage'] = {
    'title': _('Volume usage'),
    'metrics': [
        ('dell_storage_volume_usage', 'area'),
    ],
    'range': (0, 'dell_storage_volume_usage:max'),
}

perfometer_info.append({
    'type': 'stacked',
    'perfometers': [{
        'type': 'logarithmic',
        'metric': 'dell_storage_center_disk',
        'half_value': 10,
        'exponent': 2,
    }, {
        'type': 'logarithmic',
        'metric': 'dell_storage_center_volume',
        'half_value': 10,
        'exponent': 2
    }],
})
