#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import json
import argparse

import logging.config
try:
    logging.config.dictConfig(json.load(open('logging.json')))
except Exception as err:
    print '[-] error loading logging configuration from %s: %s' % ('logging.json', str(err))
    sys.exit(-1)
else:
    logger = logging.getLogger('eve')

from inspect import getmembers
from inspect import isclass
from importlib import import_module

from multiprocessing import Process


__version__ = '0.0.1'


class CustomException(Exception):
    pass


class ConfigException(CustomException):
    pass


class Configuration(dict):
    def __init__(self, configfile):
        dict.__init__(self)
        try:
            self.update(json.load(open(configfile), object_hook=self._string_decode_hook))
        except Exception as err:
            logger.error('Unable to open configuration file %s: %s' % (configfile, str(err)))
            raise ConfigException('Unable to open configuration file %s: %s' % (configfile, str(err)))

    def _string_decode_hook(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            rv[key] = value
        return rv

    def get_instances(self, handlertype):
        instances = []

        for name in self[handlertype].keys():
            module = import_module('%s.%s' % (handlertype, name))
            for obj_name, obj in getmembers(module):
                if isclass(obj) and getattr(obj, handlertype + '_name', None) == name:
                    logger.debug('loaded %s module: %s' % (handlertype, name))
                    instances.append(obj(**self[handlertype][name]))

        return instances

    def get_input(self):
        return self.get_instances('input')

    def get_output(self):
        return self.get_instances('output')

    def get_format(self):
        return self.get_instances('format')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-c", "--config", help="path to the configuration file", default="worker.json")
    args = parser.parse_args()

    conf = Configuration(args.config)
    input_modules = conf.get_input()
    output_modules = conf.get_output()
    format_modules = conf.get_format()

    # use one process per input
    logger.debug('starting input processes')
    input_processes = []
    for input_module in input_modules:
        input_processes.append(Process(target=input_module.run, args=(format_modules, output_modules)))

    for proc in input_processes:
        proc.start()

    for proc in input_processes:
        proc.join()

if __name__ == '__main__':
    main()
