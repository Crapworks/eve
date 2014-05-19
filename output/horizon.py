#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import socket
from threading import Thread


class HorizonOutput(Thread):
    output_name = 'horizon'

    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_in_queue(self, queue):
        self._queue = queue

    def run(self):
        while True:
            metrics = self._queue.get()

            for metric in metrics:
                try:
                    self.socket.sendto(metric, (self.host, self.port))
                except Exception as err:
                    logger.warning('error while processing event: %s' % (str(err), ))
