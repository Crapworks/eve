#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Avoid this module to load itself
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import json
import socket

from influxdb.client import InfluxDBClient
from threading import Thread


class InfluxDBOutput(Thread):
    output_name = 'influxdb'

    def __init__(self, host, port, username, password, database, prefetch=10, proto='http'):
        Thread.__init__(self)
        self.prefetch = prefetch
        self.proto = proto
        self.host = host
        self.port = port

        if self.proto == 'http':
            self.client = InfluxDBClient(host, port, username, password, database)
        elif self.proto == 'udp':
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            raise ValueError('unknown protocol: %s' % (self.proto, ))

    def set_in_queue(self, queue):
        self._queue = queue

    def run(self):
        metrics = []
        while True:
            metrics += self._queue.get()

            if len(metrics) >= self.prefetch:
                try:
                    if self.proto == 'http':
                        self.client.write_points(metrics)
                    elif self.proto == 'udp':
                        self.client.sendto(json.dumps(metrics), (self.host, self.port))
                except Exception as err:
                    logger.warning('error while processing event: %s' % (str(err), ))
                finally:
                    metrics = []
