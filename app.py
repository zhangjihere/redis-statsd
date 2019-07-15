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
WORKFARM_NAME = os.environ.get('HOSTNAME', 'my-work-farm').split(',')[0]
PERIOD = int(os.environ.get('PERIOD', 30))

VERBOSE = '-v' in sys.argv or os.environ.get('VERBOSE', '').lower() in ['true', 'yes']

logger = logging.getLogger()

if VERBOSE:
    handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

GAUGES = {
    'idle': 'idle',
    'in-use': 'in-use'
}

COUNTERS = {
}

KEYSPACE_COUNTERS = {
    'expires': 'expires'
}

KEYSPACE_GAUGES = {
    'avg_ttl': 'avg_ttl',
    'keys': 'keys'
}

last_seens = {}


def send_metric(out_sock, mkey, mtype, value):
    finalvalue = value

    if mtype == 'c':
        # For counters we will calculate our own deltas.
        if mkey in last_seens:
            # global finalvalue
            # calculate our deltas and don't go below 0
            finalvalue = max(0, value - last_seens[mkey])
        else:
            # We'll default to 0, since we don't want our first counter
            # to be some huge number.
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
            used_ctn = redis.llen('{}_{}'.format(lang, 'list'))
            send_metric(out_sock, '{}.{}.{}.{}'.format(statsd_prefix, WORKFARM_NAME, lang, 'in-use'), 'g',
                        float(used_ctn))
            send_metric(out_sock, '{}.{}.{}.{}'.format(statsd_prefix, WORKFARM_NAME, lang, 'idle'), 'g',
                        float(max_ctn - used_ctn))

        out_sock.close()
        time.sleep(PERIOD)


if __name__ == '__main__':
    main()
