#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# pylint: disable=C0111,C0301,R0903

__VERSION__ = '0.1.4'

import requests
import subprocess
import re

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executor".
    Get nginx's stub_status,
    and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def build_items(self):
        """
        main loop
        """

        # ping item
        self._ping()

        # detect nginx version
        self._get_version()

        # get information from stub_status
        self._get_stub()

        # get response time and availability
        self._get_response_time()

    def _enqueue(self, key, value):

        item = NginxItem(
            key=key,
            value=value,
            host=self.options['hostname']
        )
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=key, value=value)
        )

    def _request(self, url, timeout):
        """
        Request http connection and return contents.
        """

        try:
            response = requests.get(url, timeout=timeout, verify=False)
        except requests.exceptions.RequestException:
            self.logger.error(
                'Can not connect to {url}'
                ''.format(url=url)
            )
            return []

        if response.status_code == 200:
            return response.content.splitlines()
        else:
            self.logger.error(
                'Can not get status from {url} status:{status}'
                ''.format(url=url, status=response.status_code)
            )
            return []

    def _ping(self):
        """
        send ping item
        """

        self._enqueue('blackbird.nginx.ping', 1)
        self._enqueue('blackbird.nginx.version', __VERSION__)

    def _get_version(self):
        """
        detect nginx version

        $ nginx -v 
        nginx version: nginx/N.N.N
        """

        nginx_version = 'Unknown'
        try:
            output = subprocess.Popen([self.options['path'], '-v'],
                                     stderr=subprocess.PIPE).communicate()[1]
            match = re.match(r"nginx version: nginx/(\S+)", output)
            if match:
                nginx_version = match.group(1)

        except OSError:
            self.logger.debug(
                'can not exec "{0} -v", failed to get nginx version'
                ''.format(self.options['path'])
            )

        self._enqueue('nginx.version', nginx_version)

    def _get_stub(self):
        """
        Active connections: N
        server accepts handled requests
         N N N
        Reading: N Writing: N Waiting: N

        notes: cps = connection per seconds
        """
        if self.options['ssl']:
            method = 'https://'
        else:
            method = 'http://'
        url = (
            '{method}{host}:{port}{uri}'
            ''.format(
                method=method,
                host=self.options['host'],
                port=self.options['port'],
                uri=self.options['status_uri']
            )
        )

        stats = dict()
        contents = self._request(url=url, timeout=self.options['timeout'])
        if len(contents) != 4:
            self.logger.error(
                'Unrecognized stub status'
            )
            return

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
            self._enqueue('nginx.stat[{0}]'.format(key), value)

    def _get_response_time(self):

        # do not monitoring
        if not 'response_check_uri' in self.options:
            self._enqueue('nginx.group.amount', 0)
            return

        # do monitoring
        self._enqueue('nginx.group.amount', 1)

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
            try:
                response = requests.get(url,
                                timeout=self.options['response_check_timeout'],
                                headers=headers)
            except requests.exceptions.RequestException:
                self._enqueue('nginx.group.available', 0)
                return

        if response.status_code == 200:
            time = timer.sec
            available = 1
        else:
            self.logger.error(
                'Response check failed. Response code is {status} on {url}'
                ''.format(status=response.status_code, url=url)
            )
            time = 0
            available = 0

        self._enqueue('nginx.group.available', available)
        self._enqueue('nginx.stat[response_check,time]', time)
        self._enqueue('nginx.stat[response_check,status_code]', response.status_code)


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
        self._data['key'] = self.key
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    Validate configuration.
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
            "port = integer(1, 65535, default=80)",
            "timeout = integer(0, 600, default=3)",
            "status_uri = string(default='/nginx_status')",
            "user = string(default=None)",
            "password = string(default=None)",
            "ssl = boolean(default=False)",
            "path = string(default='/usr/sbin/nginx')",
            "response_check_host = string(default='127.0.0.1')",
            "response_check_port = integer(1, 65535, default=80)",
            "response_check_timeout = integer(0, 600, default=3)",
            "response_check_vhost = string(default='localhost')",
            "response_check_uagent = string(default='blackbird response check')",
            "response_check_ssl = boolean(default=False)",
            "hostname = string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec
