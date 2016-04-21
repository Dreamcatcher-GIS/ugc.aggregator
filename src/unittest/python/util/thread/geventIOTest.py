#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gevent
import gevent.monkey

gevent.monkey.patch_thread()
gevent.monkey.patch_socket()
import random

def task(pid):
    """
    Some non-deterministic task
    """
    gevent.sleep(random.randint(0,2)*0.001)
    print('Task', pid, 'done')

def synchronous():
    for i in range(1,10):
        task(i)

def asynchronous():
    threads = [gevent.spawn(task, i) for i in xrange(10)]
    gevent.joinall(threads)

print('Synchronous:')
synchronous()

print('Asynchronous:')
asynchronous()