#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import bernhard
from threading import Thread


class RiemannOutput(Thread):
    output_name = 'riemann'

    def __init__(self, host, port=5555, protocol='tcp'):
        Thread.__init__(self)
        if protocol == 'tcp':
            transport=bernhard.TCPTransport
        elif protocol == 'udp':
            transport=bernhard.UDPTransport
        else:
            raise ValueError('unknown protocol: %s valid are: tcp, udp' % (protocol, ))

        self.client = bernhard.Client(host=host, port=port, transport=transport)

    def set_in_queue(self, queue):
        self._queue = queue

    def run(self):
        while True:
            metrics = self._queue.get()
            try:
                if isinstance(metrics, list):
                    for item in metrics:
                        self.client.send(item)
                else:
                    self.client.send(metrics)
            except Exception as err:
                logger.warning('error while processing event: %s' % (str(err), ))
