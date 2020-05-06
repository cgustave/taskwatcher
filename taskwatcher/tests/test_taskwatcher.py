# -*- coding: utf-8 -*-
'''
Created on May 6, 2020

@author: cgustave
'''
import logging as log
import unittest
import json
from taskwatcher import Taskwatcher

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-10.10s.\
    %(funcName)-20.20s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

log.debug("Start unittest")

class TaskwatcherTestCase(unittest.TestCase):

    pass

if __name__ == '__main__':
    unittest.main()

