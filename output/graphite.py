#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import socket

from time import sleep
from threading import Thread


class GraphiteOutput(Thread):
    output_name = 'graphite'

    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self._setup_connection()

    def set_in_queue(self, queue):
        self._queue = queue

    def _setup_connection(self):
        try:
            if hasattr(self, 'socket'):
                self.socket.close()
        except socket.error:
            pass

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            pass

    def run(self):
        while True:
            metrics = self._queue.get()

            try:
                self.socket.send(metrics)
            except socket.error as err:
                logger.warning('connection to graphite server lost: %s - retrying in 1 second' % (str(err), ))
                sleep(1)
                self._setup_connection()
            except Exception as err:
                logger.warning('error while processing event: %s' % (str(err), ))
