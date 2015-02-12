#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logger = logging.getLogger(__name__)

import json

from time import sleep
from Queue import Queue

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

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


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        payload = self.rfile.read(int(self.headers.getheader('content-length')))
        data = json.loads(payload)
        #if isinstance(data, list):
            #for item in data:
        for fmt in self.format_modules:
            if fmt.bind and self.input_name in fmt.bind:
                data = fmt.decode(data)
        self.output_threads.write(data)
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    def serve_forever(self, input_name, format_modules, output_modules, output_threads):
        self.RequestHandlerClass.input_name = input_name
        self.RequestHandlerClass.format_modules = format_modules
        self.RequestHandlerClass.output_modules = output_modules
        self.RequestHandlerClass.output_threads = output_threads
        HTTPServer.serve_forever(self)


class HttpInput(object):
    input_name = 'http'

    def __init__(self, port=80):
        self.port = port

    def run(self, format_modules, output_modules):
        output_threads = OutputThreads(output_modules, format_modules)
        while True:
            try:
                server = ThreadedHTTPServer(('0.0.0.0', self.port), HttpHandler)
                server.serve_forever(self.input_name, format_modules, output_modules, output_threads)
            except EveConnectionError as err:
                logger.error('connection error in input handler %s: %r - retrying in 1 second' % (self.input_name, err))
                sleep(1)

