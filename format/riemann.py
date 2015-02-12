#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)


class RiemannFormat(object):
    format_name = 'riemann'

    def __init__(self, bind, host, time, service, metric, ttl=60, state='ok', tags=['eve']):
        self.bind = bind
        self.host = host
        self.time = time
        self.service = service
        self.state = state
        self.metric = metric
        self.ttl = ttl
        self.tags = tags

    def _transform(self, orig):
        metric = dict()
        metric['host'] = self.host.format(**orig)
        metric['tags'] = self.tags
        metric['time'] = int(float(self.time.format(**orig)))
        metric['service'] = self.service.format(**orig)
        metric['state'] = self.state.format(**orig)
        metric['metric'] = float(self.metric.format(**orig))
        metric['ttl'] = int(self.ttl)
        return metric

    def encode(self, data):
        if isinstance(data, list):
            return [ self._transform(item) for item in data ]
        else:
            return self._transform(data)

    def decode(self, data):
        raise AttributeError('riemann format for input processing is not yet implemented')
