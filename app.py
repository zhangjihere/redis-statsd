#!/usr/bin/python -u
# -*- coding: UTF-8 -*-

import logging
import os
import socket
import sys
import time

from redis.client import StrictRedis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
STATSD_HOST = os.environ.get('CONFIG_kamon_statsd_hostname', '172.31.60.150')
STATSD_PORT = int(os.environ.get('CONFIG_kamon_statsd_port', 8125))
STATSD_PREFIX = os.environ.get('STATSD_PREFIX', 'openwhisk-workerfarm')
WORKFARM_NAME = os.environ.get('HOSTNAME', 'my-work-farm').split('.')[0].replace('-', '')
PERIOD = int(os.environ.get('PERIOD', 30))

VERBOSE = '-v' in sys.argv or os.environ.get('VERBOSE', '').lower() in ['true', 'yes']

logger = logging.getLogger()

if VERBOSE:
    handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

last_seens = {}


def send_metric(out_sock, mkey, mtype, value):
    finalvalue = value

    if mtype == 'c':
        if mkey in last_seens:
            finalvalue = max(0, value - last_seens[mkey])
        else:
            finalvalue = 0
        last_seens[mkey] = value

    met = '{}:{}|{}'.format(mkey, finalvalue, mtype)
    out_sock.sendto(met, (STATSD_HOST, STATSD_PORT))
    logger.debug('{}:{} = {}'.format(mtype, mkey, finalvalue))


def main():
    while True:
        try:
            run_once()
        except Exception as e:
            logger.exception(e)
            time.sleep(5)


def run_once():
    for port in REDIS_PORT.split(','):

        if ',' in REDIS_PORT:
            statsd_prefix = STATSD_PREFIX + '-{}'.format(port)
        else:
            statsd_prefix = STATSD_PREFIX

        redis = StrictRedis(REDIS_HOST, port)
        out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        lang_list_len = redis.llen('language_list')
        lang_list = redis.lrange('language_list', 0, lang_list_len)

        for lang in lang_list:
            max_ctn = redis.llen('{}_{}_{}'.format('language', lang, 'list'))
            idle_ctn = redis.llen('{}_{}'.format(lang, 'list'))
            send_metric(out_sock, '{}.{}.{}.{}'.format(statsd_prefix, WORKFARM_NAME, lang, 'idle'), 'g',
                        float(idle_ctn))
            send_metric(out_sock, '{}.{}.{}.{}'.format(statsd_prefix, WORKFARM_NAME, lang, 'in-use'), 'g',
                        float(max_ctn - idle_ctn))

        out_sock.close()
        time.sleep(PERIOD)


if __name__ == '__main__':
    main()
