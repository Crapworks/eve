#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

class InfluxDBFormat(object):
    format_name = 'influxdb'

    def __init__(self, bind, series):
        self.bind = bind
        self.series = series

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
            {
                'name': self.series.format(**self._transform(item)),
                'columns': item.keys(),
                'points': [ item.values(),  ],
            } for item in data
        ]

    def decode(self, data):
        raise AttributeError('influx format for input processing is not yet implemented')
