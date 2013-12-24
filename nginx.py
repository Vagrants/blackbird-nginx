#!/usr/bin/env python
# -*- encodig: utf-8 -*-
"""
Get the nginx's "stub_status"
"""

import requests
from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executer".
    Get nginx's stub_status,
    and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def _enqueue(self, item):
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue nginx.stat[{key}]:{value}'
            ''.format(key=item.key, value=item.value)
        )

    def looped_method(self):

        # get information from stub_status
        self._get_stub()

        if 'response_check_uri' in self.options:
            self._get_response_time()

    def _get_stub(self):
        """
        notes: cps = connection per seconds
        """
        if self.options['ssl']:
            method = 'https://'
        else:
            method = 'http://'
        url = (
            '{method}{host}:{port}/{uri}'
            ''.format(
                method=method,
                host=self.options['host'],
                port=self.options['port'],
                uri=self.options['status_uri']
            )
        )
        response = requests.get(url)

        if response.status_code == 200:
            stats = dict()
            contents = response.content.splitlines()
            
            # each values in stub_status
            # Active Connection: INTEGER
            key = 'active_connections'
            value = int(contents[0].split(':')[1])
            stats[key] = value

            # server accepts handled requests
            # INTEGER INTEGER INTEGER
            keys = contents[1].split()[1:]
            values = contents[2].split()

            for key, value in zip(keys, values):
                stats[key] = value
                stats[key + '.cps'] = value

            # Reading: INTEGER
            # Writing: INTEGER
            # Waiting: INTEGER
            values = contents[3].split()
            for key, value in zip(values[0::2], values[1::2]):
                key = key.lower().rstrip(':')
                stats[key] = int(value)

            for key, value in stats.items():
                item = NginxItem(
                    key=key,
                    value=value,
                    host=self.options['hostname']
                )
                self._enqueue(item)

    def _get_response_time(self):
        if self.options['response_check_ssl']:
            method = 'https://'
        else:
            method = 'http://'

        url = (
            '{method}{host}:{port}{uri}'
            ''.format(
                method=method,
                host=self.options['response_check_host'],
                port=self.options['response_check_port'],
                uri=self.options['response_check_uri']
            )
        )

        headers = {
            'Host': self.options['response_check_vhost'],
            'User-Agent': self.options['response_check_uagent'],
        }

        with base.Timer() as timer:
            response = requests.get(url, headers=headers)

        if response.status_code == 200:
            time = timer.sec
        else:
            time = 0

        item = NginxItem(
            key='response_check,time',
            value=time,
            host=self.options['hostname']
        )
        self._enqueue(item)

        item = NginxItem(
            key='response_check,status_code',
            value=response.status_code,
            host=self.options['hostname']
        )
        self._enqueue(item)


class NginxItem(base.ItemBase):
    """
    Enqued item.
    """

    def __init__(self, key, value, host):
        super(NginxItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        return self._data

    def _generate(self):
        self._data['key'] = 'nginx.stat[{0}]'.format(self.key)
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        """
        "user" and "password" in spec are
        for BASIC and Digest authentication.
        """
        self.__spec = (
            "[{0}]".format(__name__),
            "host = string(default='127.0.0.1')",
            "port = integer(0, 65535, default=80)",
            "status_uri = string(default='nginx_status')",
            "user = string(default=None)",
            "password = string(default=None)",
            "ssl = boolean(default=False)",
            "response_check_port = integer(0, 65535, default=80)",
            "response_check_host = string(default='127.0.0.1')",
            "response_check_vhost = string(default='localhost')",
            "response_check_uagent = string(default='blackbird response check')",
            "response_check_ssl = boolean(default=False)",
            "hostname = string(default={0})".format(self.gethostname()),
        )
        return self.__spec
