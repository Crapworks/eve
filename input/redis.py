#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import json

from time import sleep
from Queue import Queue

from hotqueue import HotQueue

class OutputThreads(object):
    def __init__(self, output_modules, format_modules, max_queue_size=1000):
        self.threads = []
        self.format_modules = format_modules
        for output in output_modules:
            queue = Queue(max_queue_size)
            output.set_in_queue(queue)
            output.start()
            self.threads.append((output, queue))

    def write(self, metric):
        for thread, queue in self.threads:
            for fmt in self.format_modules:
                if fmt.bind and thread.output_name in fmt.bind:
                    encoded = fmt.encode(metric)

            queue.put(encoded)


class EveConnectionError(Exception):
    pass


class RedisInput(object):
    input_name = 'redis'

    def __init__(self, host, queue,  port=6379):
        self.host = host
        self.port = port
        self.queue = queue

    def handle_input(self):
        try:
            self.queue = HotQueue(self.queue, serializer=json, host=self.host, port=self.port, db=0)
        except Exception as err:
            raise EveConnectionError(err)

        for data in self.queue.consume():
            for fmt in self.format_modules:
                if fmt.bind and self.input_name in fmt.bind:
                    data = fmt.decode(data)

            self.output_threads.write(data)

    def run(self, format_modules, output_modules):
        # Start output threads
        self.format_modules = format_modules
        self.output_modules = output_modules
        self.output_threads = OutputThreads(self.output_modules, self.format_modules)
        while True:
            try:
                self.handle_input()
            except EveConnectionError as err:
                logger.error('connection error in input handler %s: %r - retrying in 1 second' % (self.input_name, err))
                sleep(1)

