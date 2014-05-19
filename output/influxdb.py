#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Avoid this module to load itself
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

from influxdb.client import InfluxDBClient
from threading import Thread


class InfluxDBOutput(Thread):
    output_name = 'influxdb'

    def __init__(self, host, port, username, password, database):
        Thread.__init__(self)
        self.client = InfluxDBClient(host, port, username, password, database)

    def set_in_queue(self, queue):
        self._queue = queue

    def run(self):
        while True:
            metrics = self._queue.get()

            try:
                self.client.write_points(metrics)
            except Exception as err:
                logger.warning('error while processing event: %s' % (str(err), ))
