#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json

import logging
logger = logging.getLogger(__name__)

from time import sleep
from Queue import Queue

from pika import BlockingConnection
from pika import ConnectionParameters
from pika import PlainCredentials
# from pika.exceptions import AMQPConnectionError

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


class RabbitInput(object):
    input_name = 'rabbitmq'

    def __init__(self, host, port=5672, vhost='/', username='guest', password='guest', queue='default', prefetch=10):
        credentials = PlainCredentials(username, password)
        self.connection_params = ConnectionParameters(host=host, port=port, virtual_host=vhost, credentials=credentials)
        self.queue = queue
        self.prefetch = prefetch

    def _worker(self, ch, method, properties, body):
        # TODO: find out why rabbitmq sucks
        if not body:
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return 

        try:
            data = json.loads(body)
        except Exception as err:
            logger.debug('unable to decode json: %s' % (str(err), ))
        else:
            for fmt in self.format_modules:
                if fmt.bind and self.input_name in fmt.bind:
                    data = fmt.decode(data)

            self.output_threads.write(data)

        finally:
            ch.basic_ack(delivery_tag = method.delivery_tag)

    def setup_amqp_connection(self):
        #try:
        self.connection = BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.basic_qos(prefetch_count=self.prefetch)
        self.channel.basic_consume(self._worker, queue=self.queue)

        self.connection.channel()
        #except Exception as err:
        #logger.error('error connecting to rabbitmq server %r' % (err, ))
        #sleep(1)
        #logger.error('reconnecting to rabbitmq server')

        self.channel.start_consuming()

    def run(self, format_modules, output_modules):
        # Start output threads
        self.format_modules = format_modules
        self.output_modules = output_modules
        self.output_threads = OutputThreads(self.output_modules, self.format_modules)
        while True:
            self.setup_amqp_connection()
