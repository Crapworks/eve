#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

from msgpack import packb

class HorizonFormat(object):
    format_name = 'horizon'

    def __init__(self, bind, metric, time, value, full_uniques):
        self.bind = bind
        self.metric = metric
        self.time = time
        self.value = value
        self.full_uniques = full_uniques

    def _transform(self, metric):
        tmp = dict()
        for key, value in metric.iteritems():
            if hasattr(value, 'replace'):
                value = value.replace('/', '_slsh_')
                value = value.replace('.', '_')
                value = value.replace(' ', '_')
            if hasattr(value, 'strip'):
                value = value.strip('\'')
                value = value.strip('"')
            tmp[key] = value

        return tmp

    def encode(self, data):
        return [
            packb((
                self.metric.format(**self._transform(item)),
                (
                    float(self.time.format(**item)),
                    float(self.value.format(**item))
                )
            )) for item in data
        ]

    def decode(self, data):
        raise AttributeError('horizon format for input processing is not yet implemented')
