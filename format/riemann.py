#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)


class RiemannFormat(object):
    format_name = 'riemann'

    def __init__(self, bind, time, service, state, description, metric, ttl):
        self.bind = bind
        self.metric = metric
        self.time = time
        self.service = service
        self.description = description
        self.ttl = ttl

    def _transform(self, orig):
        metric = dict()
        metric['tags'] = [ str(v) for v in orig.values() ]
        metric['time'] = int(self.time.format(**orig))
        metric['service'] = self.service.format(**orig)
        metric['state'] = self.state.format(**orig)
        metric['description'] = self.state.format(**orig)
        metric['metric'] = self.metric.format(**orig)
        metric['ttl'] = int(self.state.format(**orig))
        return metric

    def encode(self, data):
        return self._transform(data)

    def decode(self, data):
        raise AttributeError('riemann format for input processing is not yet implemented')
