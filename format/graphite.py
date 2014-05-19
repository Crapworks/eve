#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pickle
import struct
import logging
logger = logging.getLogger(__name__)

class GraphiteFormat(object):
    format_name = 'graphite'

    def __init__(self, bind, metric, time, value, codec='pickle'):
        self.bind = bind
        self.metric = metric
        self.time = time
        self.value = value
        self.codec = codec

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
        if self.codec == 'line':
            return ''.join([
                "%s %s %s\n" % (
                    self.metric.format(**self._transform(item)),
                    self.value.format(**item),
                    int(float(self.time.format(**item)))
                ) for item in data
            ])
        if self.codec == 'pickle':
            metric = [
                (
                    self.metric.format(**self._transform(item)),
                    (float(self.time.format(**item)), self.value.format(**item))
                ) for item in data
            ]
            payload = pickle.dumps(metric)
            header = struct.pack("!L", len(payload))
            return header + payload

    def decode(self, data):
        raise AttributeError('graphite format for input processing is not yet implemented')
