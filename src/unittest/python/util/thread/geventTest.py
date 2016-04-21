#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
import gevent
import urllib2
from time import time

def fetch(pid):
    ts = time()
    print 'Process %s ' % pid ,'start , time %s' % format(time() - ts)
    response = urllib2.urlopen('http://api.map.baidu.com/place/v2/search?ak=DW2CwL3B3271CiVyw7GdBsfR&output=json&query=公司')
    result = response.read()
    gevent.sleep(3)
    print 'Process %s done' % pid ,', Took %s' % format(time() - ts)
    return result

def synchronous():
    for i in range(1,10):
        fetch(i)

def asynchronous():
    ts = time()
    threads = []
    for i in range(1,10):
        threads.append(gevent.spawn(fetch, i))
    gevent.joinall(threads)
    print 'Took %s' % format(time() - ts)

print 'Synchronous:'
# synchronous()

print 'Asynchronous:'
asynchronous()