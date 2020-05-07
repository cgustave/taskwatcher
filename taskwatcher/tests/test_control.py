# -*- coding: utf-8 -*-
'''
Created on May 6, 2020

@author: cgustave
'''
import logging as log
import unittest
import json

from control import Control

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-10.10s.\
    %(funcName)-20.20s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

log.debug("Start unittest")

class ControlTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.ctrl = Control(db='sqlite.db', debug=True)

    # Initialize 
    def test_initialize(self):
        self.ctrl.initialize()

    # Reserve
    def test_reserve(self):
        taskid = self.ctrl.reserve()
        self.assertEqual(taskid, 1)

    # List tasks
    def test_return_tasks(self):
        result =  json.loads(self.ctrl.return_tasks())
        self.assertEqual(result['1']['status'], 'RESERVED')

if __name__ == '__main__':
    unittest.main()

