#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from copy import deepcopy

import logging
logger = logging.getLogger(__name__)

class CollectdFormat(object):
    keys = ['values', 'dstypes', 'dsnames', 'time', 'interval', 'host', 'plugin', 'plugin_instance', 'type', 'type_instance']
    keys_list = ['values', 'dstypes', 'dsnames']
    format_name = 'collectd'

    def __init__(self, bind):
        self.bind = bind

    def _identify(self, data):
        for key in self.keys:
            for metric in data:
                if not key in metric.keys():
                    logger.warning('this is not a collectd event')

    def decode(self, data):
        self._identify(data)

        result = []

        for metric in data:
            # now it's getting ugly...
            for num, item in enumerate(metric['values']):
                tmp = deepcopy(metric)
                for key in self.keys_list:
                    del tmp[key]

                tmp['value'] = item
                tmp['dstype'] = metric['dstypes'][num]
                tmp['dsname'] = metric['dsnames'][num]

                # if we have an instance of type/plugin add a combined field
                if tmp['plugin_instance']:
                    tmp['plugin_combined'] = '%s-%s' % (tmp['plugin'], tmp['plugin_instance'])
                else:
                    tmp['plugin_combined'] = tmp['plugin']

                if tmp['type_instance']:
                    tmp['type_combined'] = '%s-%s' % (tmp['type'], tmp['type_instance'])
                else:
                    tmp['type_combined'] = tmp['type']
                result.append(tmp)

        return result
