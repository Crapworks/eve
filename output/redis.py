#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Avoid this module to load itself
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

from threading import Thread
from time import sleep

import redis


class RedisOutput(Thread):
    output_name = 'redis'

    def __init__(self, host, port, prefix=''):
        Thread.__init__(self)
        self.prefix = prefix
        self.host = host
        self.port = port
        self._setup_connection()

    def set_in_queue(self, queue):
        self._queue = queue

    def _setup_connection(self):
        self.redis = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.pipe = self.redis.pipeline()

    def run(self):
        while True:
            try:
                self.redis.ping()
            except redis.ConnectionError as err:
                logger.warning('connection to redis server lost: %s - retrying in 1 second' % (str(err), ))
                sleep(1)
                self._setup_connection()
                continue

            metrics = self._queue.get()

            for metric in metrics:
                try:
                    key, value, group = metric
                    if self.prefix:
                        key = '.'.join([self.prefix, key])
                    self.pipe.append(key, value)
                    if group:
                        group = '.'.join([self.prefix, group])
                        self.pipe.sadd(group, key)
                    self.pipe.execute()
                except Exception as err:
                    logger.warning('error while processing event: %s' % (str(err), ))
