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
from typing import Optional, Sequence
import time
import datetime
import logging
import requests
from functools import cached_property

from cmk.special_agents.v0_unstable.agent_common import (
    ConditionalPiggybackSection,
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import (
    Args,
    create_default_argument_parser
)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGING = logging.getLogger('agent_dell_storage')


class BytesString:
    def __init__(self, value):
        self.value = value.split(' ')[0]

    def __str__(self):
        return self.value


class DellStorageApiParser:
    @staticmethod
    def temperature(value):
        if value:
            return int(value.split('°')[0])
        return None

    @staticmethod
    def kbps(value):
        return int(value) * 1024

    @staticmethod
    def latency(value):
        return int(value) / 1000000.0

    @staticmethod
    def space(value):
        return int(value.split(' ')[0])


class DellStorageApi:
    reqcnt = 0

    HISTORICAL_FILTER = {
        'HistoricalFilter': {
            'UseCurrent': True,
            'MaxCountReturn': 1,
            'StartTime': (datetime.datetime.now() - datetime.timedelta(minutes=20)).isoformat(),
        }
    }

    def __init__(self, url, user, password, verify_cert):
        LOGGING.info('Initialize DellStorageApi Clinet')
        self._url = url
        self._verify_cert = verify_cert

        self._login(user, password)

    @cached_property
    def _connection(self):
        conn = requests.Session()
        conn.headers.update({
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'x-dell-api-version': '4.0',
        })
        return conn

    def _login(self, user: str, password: str) -> None:
        self._api = self._request('POST', '/ApiConnection/Login', auth=(user, password))
        LOGGING.info('Login to {provider} v{providerVersion}'.format(**self._api))

    def _request(self, methode, call, payload=None, **kwargs) -> requests.Response:
        url = self.url(call)
        LOGGING.debug('>> {methode} {url}'.format(methode=methode, url=url))
        resp = self._connection.request(methode, url, json=payload, verify=self._verify_cert, **kwargs)
        LOGGING.debug('<< {status} {reason}'.format(status=resp.status_code, reason=resp.reason))
        resp.raise_for_status()
        self.reqcnt += 1
        return resp.json()

    def url(self, call):
        return f'{self._url.rstrip("/")}/{call.strip("/")}'

    @cached_property
    def storage_centers(self):
        storage_centers = self.get('/ApiConnection/ApiConnection/{instanceId}/StorageCenterList'.format(**self._api))
        return [self.StorageCenter(self, **sc) for sc in storage_centers]

    def get(self, call) -> requests.Response:
        return self._request('GET', call)

    def post(self, call, payload={}) -> requests.Response:
        return self._request('POST', call, payload=payload)

    @property
    def provider(self):
        return getattr(self, '_api', {}).get('provider', 'UNKNOWN')

    @property
    def providerVersion(self):
        return getattr(self, '_api', {}).get('providerVersion', 'UNKNOWN')

    class ApiObject(object):
        AGENT_DEFAULT_FIELDS = ['instanceName', 'status', 'statusMessage']
        AGENT_FIELDS = []

        def __init__(self, api, **kwargs):
            self._api = api

            for key, vtype in self.__annotations__.items():
                self.__setattr__(key, vtype(kwargs.get(key, None)))

        def __getattribute__(self, name):
            if '.' in name:
                name, subpath = name.split('.', 1)
                return getattr(object.__getattribute__(self, name), subpath)
            return object.__getattribute__(self, name)

        def __repr__(self):
            return f'<{self.__class__.__name__} {self.instanceName} {self.instanceId}>'

        def _get_association(self, url):
            return self._instanciate(self._api.get(url))

        def _get_historical_association(self, url):
            assoc = self._api.post(url, payload=DellStorageApi.HISTORICAL_FILTER)
            if len(assoc) > 0:
                return self._instanciate(assoc[0])
            return None

        def _get_associations(self, url):
            return [self._instanciate(obj) for obj in self._api.get(url)]

        def _instanciate(self, obj):
            otype = obj['objectType']
            cls = getattr(DellStorageApi, otype, None)
            if cls:
                return cls(self._api, **obj)
            return obj

        def _fields(self):
            return self.AGENT_DEFAULT_FIELDS + self.AGENT_FIELDS

        def __str__(self, separator=';'):
            return separator.join([str(getattr(self, field, '')) for field in self._fields()])

        @property
        def safeInstanceName(self):
            return re.sub(r"[^a-zA-Z0-9-_]", "", getattr(self, 'instanceName'))

    class StorageCenter(ApiObject):
        AGENT_FIELDS = [
            'modelSeries', 'version',
            'serviceTag', 'serialNumber',
            'objectCount.numberOfDevicesInUse', 'objectCount.numberOfControllers',
            'objectCount.numberOfDisks', 'objectCount.numberOfLiveVolumes',
            'objectCount.numberOfReplays', 'objectCount.numberOfReplications',
            'objectCount.numberOfServers', 'objectCount.numberOfVolumes',
            'storageUsage.availableSpace', 'storageUsage.allocatedSpace', 'storageUsage.usedSpace'
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        modelSeries: str
        serviceTag: str
        serialNumber: str
        version: str
        chassisPresent: bool

        @cached_property
        def chassi(self):
            return self._get_association(f'/StorageCenter/StorageCenter/{self.instanceId}/Chassis')

        @cached_property
        def objectCount(self):
            return self._get_association(f'/StorageCenter/StorageCenter/{self.instanceId}/ObjectCount')

        @cached_property
        def storageUsage(self):
            return self._get_association(f'/StorageCenter/StorageCenter/{self.instanceId}/StorageUsage')

        @cached_property
        def controllers(self):
            return self._get_associations(f'/StorageCenter/StorageCenter/{self.instanceId}/ControllerList')

        @cached_property
        def enclosures(self):
            return self._get_associations(f'/StorageCenter/StorageCenter/{self.instanceId}/EnclosureList')

        @cached_property
        def volumes(self):
            return self._get_associations(f'/StorageCenter/StorageCenter/{self.instanceId}/VolumeList')

        @cached_property
        def activeAlerts(self):
            return self._get_associations(f'/StorageCenter/StorageCenter/{self.instanceId}/ActiveAlertList')

    class ScChassis(ApiObject):
        instanceId: str
        instanceName: str

        @cached_property
        def enclosure(self):
            return self._get_association(f'/StorageCenter/ScChassis/{self.instanceId}/Enclosure')

        @cached_property
        def fans(self):
            return self._get_associations(f'/StorageCenter/ScChassis/{self.instanceId}/FanSensorList')

        @cached_property
        def powersupplies(self):
            return self._get_associations(f'/StorageCenter/ScChassis/{self.instanceId}/PowerSupplyList')

        @cached_property
        def temperatures(self):
            return self._get_associations(f'/StorageCenter/ScChassis/{self.instanceId}/TemperatureSensorList')

    class ScObjectCount(ApiObject):
        numberOfControllers: int
        numberOfDevicesInUse: int
        numberOfDisks: int
        numberOfLiveVolumes: int
        numberOfReplays: int
        numberOfReplications: int
        numberOfServers: int
        numberOfVolumes: int

    class StorageCenterStorageUsage(ApiObject):
        availableSpace: BytesString
        allocatedSpace: BytesString
        usedSpace: BytesString

    class ScController(ApiObject):
        AGENT_FIELDS = [
            'lastBootTime', 'leader',
            'model', 'version',
            'serviceTag', 'expressServiceCode', 'hardwareSerialNumber',
        ]

        instanceId: str
        instanceName: str
        lastBootTime: str
        leader: bool
        model: str
        status: str
        statusMessage: str
        version: str
        serviceTag: str
        expressServiceCode: str
        hardwareSerialNumber: str

        @cached_property
        def ports(self):
            return self._get_associations(f'/StorageCenter/ScController/{self.instanceId}/PhysicalControllerPortList')

        @cached_property
        def fans(self):
            return self._get_associations(f'/StorageCenter/ScController/{self.instanceId}/FanSensorList')

        @cached_property
        def powersupplies(self):
            return self._get_associations(f'/StorageCenter/ScController/{self.instanceId}/PowerSupplyList')

        @cached_property
        def temperatures(self):
            return self._get_associations(f'/StorageCenter/ScController/{self.instanceId}/TemperatureSensorList')

    class ScControllerPort(ApiObject):
        AGENT_FIELDS = [
            'cabled', 'transportType', 'wwn',
            'iousage.readIops', 'iousage.readKbPerSecond', 'iousage.readLatency',
            'iousage.writeIops', 'iousage.writeKbPerSecond', 'iousage.writeLatency',
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        cabled: bool
        transportType: str
        wwn: str

        @cached_property
        def iousage(self):
            return self._get_historical_association(f'/StorageCenter/ScControllerPort/{self.instanceId}/GetHistoricalIoUsage')

    class ScControllerPortIoUsage(ApiObject):
        readIops: int
        readKbPerSecond: DellStorageApiParser.kbps
        readLatency: DellStorageApiParser.latency
        writeIops: int
        writeKbPerSecond: DellStorageApiParser.kbps
        writeLatency: DellStorageApiParser.latency

    class ScControllerFanSensor(ApiObject):
        AGENT_FIELDS = [
            'location',
            'currentRpm',
            'lowerCriticalThreshold', 'lowerWarningThreshold', 'lowerNormalThreshold',
            'upperNormalThreshold', 'upperWarningThreshold', 'upperCriticalThreshold',
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        location: str
        currentRpm: int
        lowerCriticalThreshold: str
        lowerWarningThreshold: str
        lowerNormalThreshold: str
        upperNormalThreshold: str
        upperWarningThreshold: str
        upperCriticalThreshold: str

    class ScControllerPowerSupply(ApiObject):
        AGENT_FIELDS = ['location']

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        location: str

    class ScControllerTemperatureSensor(ApiObject):
        AGENT_FIELDS = [
            'location',
            'currentTemperature',
            'lowerCriticalThreshold', 'lowerWarningThreshold', 'lowerNormalThreshold',
            'upperNormalThreshold', 'upperWarningThreshold', 'upperCriticalThreshold',
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        location: str
        currentTemperature: DellStorageApiParser.temperature
        lowerCriticalThreshold: DellStorageApiParser.temperature
        lowerWarningThreshold: DellStorageApiParser.temperature
        lowerNormalThreshold: DellStorageApiParser.temperature
        upperNormalThreshold: DellStorageApiParser.temperature
        upperWarningThreshold: DellStorageApiParser.temperature
        upperCriticalThreshold: DellStorageApiParser.temperature

    class ScEnclosure(ApiObject):
        AGENT_FIELDS = [
            'model', 'revision', 'type', 'enclosureCapacity',
            'serviceTag', 'expressServiceCode'
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        model: str
        revision: str
        type: str
        enclosureCapacity: str
        serviceTag: str
        expressServiceCode: str

        @cached_property
        def fans(self):
            return self._get_associations(f'/StorageCenter/ScEnclosure/{self.instanceId}/CoolingFanSensorList')

        @cached_property
        def disks(self):
            return self._get_associations(f'/StorageCenter/ScEnclosure/{self.instanceId}/DiskList')

        @cached_property
        def powersupplies(self):
            return self._get_associations(f'/StorageCenter/ScEnclosure/{self.instanceId}/PowerSupplyList')

        @cached_property
        def temperatures(self):
            return self._get_associations(f'/StorageCenter/ScEnclosure/{self.instanceId}/TemperatureSensorList')

    class ScEnclosureCoolingFanSensor(ApiObject):
        AGENT_FIELDS = ['location']

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        location: str

    class ScDisk(ApiObject):
        AGENT_FIELDS = [
            'usage.allocatedSpace', 'usage.totalSpace',
            'iousage.readIops', 'iousage.readKbPerSecond', 'iousage.readLatency',
            'iousage.writeIops', 'iousage.writeKbPerSecond', 'iousage.writeLatency',
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str

        @cached_property
        def usage(self):
            return self._get_association(f'/StorageCenter/ScDisk/{self.instanceId}/StorageUsage')

        @cached_property
        def iousage(self):
            return self._get_historical_association(f'/StorageCenter/ScDisk/{self.instanceId}/GetHistoricalIoUsage')

    class ScDiskIoUsage(ScControllerPortIoUsage):
        pass

    class ScDiskStorageUsage(ApiObject):
        allocatedSpace: DellStorageApiParser.space
        totalSpace: DellStorageApiParser.space

    class ScEnclosureTemperatureSensor(ScControllerTemperatureSensor):
        AGENT_FIELDS = [
            'location',
            'currentTemperature',
            'None', 'lowerCriticalThreshold', 'lowerWarningThreshold',
            'upperWarningThreshold', 'upperCriticalThreshold', 'None',
        ]

    class ScEnclosurePowerSupply(ScControllerPowerSupply):
        pass

    class ScVolume(ApiObject):
        AGENT_FIELDS = [
            'usage.activeSpace', 'usage.configuredSpace',
            'iousage.readIops', 'iousage.readKbPerSecond', 'iousage.readLatency',
            'iousage.writeIops', 'iousage.writeKbPerSecond', 'iousage.writeLatency',
        ]

        instanceId: str
        instanceName: str
        status: str
        statusMessage: str
        active: bool

        @cached_property
        def usage(self):
            return self._get_association(f'/StorageCenter/ScVolume/{self.instanceId}/StorageUsage')

        @cached_property
        def iousage(self):
            return self._get_historical_association(f'/StorageCenter/ScVolume/{self.instanceId}/GetHistoricalIoUsage')

    class ScVolumeIoUsage(ScControllerPortIoUsage):
        pass

    class ScVolumeStorageUsage(ScDiskStorageUsage):
        activeSpace: DellStorageApiParser.space
        configuredSpace: DellStorageApiParser.space

    class ScAlert(ApiObject):
        AGENT_DEFAULT_FIELDS = []
        AGENT_FIELDS = [
            'alertDefinition',
            'message',
            'acknowledged',
            'supportUrl',
        ]

        alertDefinition: str
        message: str
        acknowledged: str
        supportUrl: str


class AgentDellStorage:
    def run(self):
        special_agent_main(self.parse_arguments, self.main)

    def parse_arguments(self, argv: Optional[Sequence[str]]) -> Args:
        parser = create_default_argument_parser(description=__doc__)

        parser.add_argument('-u', '--user', dest='user', required=True,
                            help='User to access the DSM.')
        parser.add_argument('-p', '--password', dest='password', required=True,
                            help='Password to access the DSM.')
        parser.add_argument('-U', '--url', dest='url', required=True,
                            help='URL of the DSM RESt API. (Example https://host:3033/api/rest/)')
        parser.add_argument('--ignore-cert', dest='verify_cert', action='store_false',
                            help='Do not verify the SSL cert from the REST andpoint.')

        return parser.parse_args(argv)

    def main(self, args: Args):
        self.args = args

        start = time.time()

        try:
            self._api = DellStorageApi(args.url, args.user, args.password, args.verify_cert)
            for storageCenter in self._api.storage_centers:
                with ConditionalPiggybackSection(storageCenter.safeInstanceName):
                    with SectionWriter('dell_storage_center', separator=';') as writer:
                        writer.append(storageCenter)

                    with SectionWriter('dell_storage_controller', separator=';') as writer:
                        writer.append(c for c in storageCenter.controllers)

                    with SectionWriter('dell_storage_enclosure', separator=';') as writer:
                        writer.append(e for e in storageCenter.enclosures)

                    with SectionWriter('dell_storage_volume', separator=';') as writer:
                        writer.append(v for v in storageCenter.volumes)

                    with SectionWriter('dell_storage_alert', separator=';') as writer:
                        writer.append(a for a in storageCenter.activeAlerts)

                if storageCenter.chassisPresent:
                    with ConditionalPiggybackSection(f'{storageCenter.safeInstanceName}-{storageCenter.chassi.enclosure.safeInstanceName}'):
                        with SectionWriter('dell_storage_fan', separator=';') as writer:
                            writer.append(f for f in storageCenter.chassi.fans)

                        with SectionWriter('dell_storage_psu', separator=';') as writer:
                            writer.append(p for p in storageCenter.chassi.powersupplies)

                        with SectionWriter('dell_storage_temp', separator=';') as writer:
                            writer.append(t for t in storageCenter.chassi.temperatures)

                for controller in storageCenter.controllers:
                    with ConditionalPiggybackSection(f'{storageCenter.safeInstanceName}-{controller.safeInstanceName}'):
                        with SectionWriter('dell_storage_controller', separator=';') as writer:
                            writer.append(controller)

                        with SectionWriter('dell_storage_port', separator=';') as writer:
                            writer.append(p for p in controller.ports)

                        with SectionWriter('dell_storage_fan', separator=';') as writer:
                            writer.append(f for f in controller.fans)

                        with SectionWriter('dell_storage_psu', separator=';') as writer:
                            writer.append(p for p in controller.powersupplies)

                        with SectionWriter('dell_storage_temp', separator=';') as writer:
                            writer.append(t for t in controller.temperatures)

                for enclosure in storageCenter.enclosures:
                    with ConditionalPiggybackSection(f'{storageCenter.safeInstanceName}-{enclosure.safeInstanceName}'):
                        with SectionWriter('dell_storage_enclosure', separator=';') as writer:
                            writer.append(enclosure)

                        with SectionWriter('dell_storage_fan', separator=';') as writer:
                            writer.append(f for f in enclosure.fans)

                        with SectionWriter('dell_storage_disk', separator=';') as writer:
                            writer.append(d for d in enclosure.disks)

                        with SectionWriter('dell_storage_psu', separator=';') as writer:
                            writer.append(p for p in enclosure.powersupplies)

                        with SectionWriter('dell_storage_temp', separator=';') as writer:
                            writer.append(t for t in enclosure.temperatures)
        except Exception as exc:
            if args.debug:
                raise
            end = time.time()
            with SectionWriter('dell_storage_agent', separator=';') as writer:
                writer.append(f'1;;;{end - start};;{exc}')
        else:
            end = time.time()
            with SectionWriter('dell_storage_agent', separator=';') as writer:
                writer.append(f'0;{self._api.provider};{self._api.providerVersion};{end - start};{self._api.reqcnt};')
