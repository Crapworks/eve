#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Avoid this module to load itself
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

from threading import Thread
import redis


# TODO: detect redis connection loss
class RedisOutput(Thread):
    output_name = 'redis'

    def __init__(self, host, port, prefix=''):
        Thread.__init__(self)
        self.prefix = prefix
        self.redis = redis.StrictRedis(host=host, port=port, db=0)
        self.pipe = self.redis.pipeline()

    def set_in_queue(self, queue):
        self._queue = queue

    def run(self):
        while True:
            metrics = self._queue.get()

            for metric in metrics:
                try:
                    key, value, group = metric
                    #from msgpack import unpackb
                    #print unpackb(value)
                    if self.prefix:
                        key = '.'.join([self.prefix, key])
                    self.pipe.append(key, value)
                    if group:
                        group = '.'.join([self.prefix, group])
                        self.pipe.sadd(group, key)
                    self.pipe.execute()
                except Exception as err:
                    logger.warning('error while processing event: %s' % (str(err), ))
