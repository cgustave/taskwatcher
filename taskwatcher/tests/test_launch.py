# -*- coding: utf-8 -*-
'''
Created on May 8, 2020

@author: cgustave
'''
import logging as log
import unittest
import json

from launch import Launch

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-10.10s.\
    %(funcName)-20.20s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

log.debug("Start unittest")

class LaunchTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.lnc = Launch(db='sqlite.db', debug=True)

    #def test_reserve(self):

   
    def test_execute_nofeedback(self):
        command = "tests/testprog.py  --scenario sleeping --sleep 10 --debug"
        self.lnc.execute(command=command)
        

if __name__ == '__main__':
    unittest.main()

