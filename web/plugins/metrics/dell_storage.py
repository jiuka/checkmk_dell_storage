#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Copyright (C) 2020  Marius Rieder <marius.rieder@durchmesser.ch>
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
)

check_metrics['check_mk-dell_storage_disk'] = {
    'usage': {'name': 'dell_storage_disk_usage'},
}

check_metrics['check_mk-dell_storage_port'] = {
    'read_ios': {'name': 'dell_storage_port_read_ios'},
    'read_throughput': {'name': 'dell_storage_port_read_throughput'},
    'write_ios': {'name': 'dell_storage_port_write_ios'},
    'write_throughput': {'name': 'dell_storage_port_write_throughput'},
}

check_metrics['check_mk-dell_storage_volume'] = {
    'usage': {'name': 'dell_storage_volume_usage'},
}

metric_info['dell_storage_port_read_ios'] = metric_info['disk_write_ios']
metric_info['dell_storage_port_write_ios'] = metric_info['disk_write_ios']
metric_info['dell_storage_port_read_throughput'] = metric_info['disk_read_throughput']
metric_info['dell_storage_port_write_throughput'] = metric_info['disk_write_throughput']

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

graph_info['dell_storage_disk_usage'] = {
    'title': _('Disk usage'),
    'metrics': [
        ('dell_storage_disk_usage', 'area'),
    ],
    'range': (0, 'dell_storage_disk_usage:max'),
}

graph_info['dell_storage_port_ios'] = {
    'title': _('Port I/O operations'),
    'metrics': [
        ('dell_storage_port_read_ios', 'area'),
        ('dell_storage_port_write_ios', '-area'),
    ],
}

graph_info['dell_storage_port_throughput'] = {
    'title': _('Port throughput'),
    'metrics': [
        ('dell_storage_port_read_throughput', 'area'),
        ('dell_storage_port_write_throughput', '-area'),
    ],
}

graph_info['dell_storage_volume_usage'] = {
    'title': _('Volume usage'),
    'metrics': [
        ('dell_storage_volume_usage', 'area'),
    ],
    'range': (0, 'dell_storage_volume_usage:max'),
}
