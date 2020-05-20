# -*- coding: utf-8 -*-
'''
Created on May 8, 2020

@author: cgustave
'''
import logging as log
import unittest
import json

from launch import Launch
from control import Control

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-10.10s.\
    %(funcName)-20.20s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

log.debug("Start unittest")

class LaunchTestCase(unittest.TestCase):

    def test10_execute_nofeedback(self):
        self.lnc = Launch(db='sqlite.db', debug=True)
        command = "tests/testprog.py  --scenario sleeping --sleep 1 --debug"
        result = self.lnc.execute(command=command)
        print("test10 result={}".format(result))
        self.assertTrue(result)

    def test20_execute_feedback(self):
        self.ctl = Control(db='sqlite.db')
        self.ctl.initialize()
        self.ctl.reserve()
        self.lnc = Launch(db='sqlite.db', feedpath='/tmp', taskid=1, info1='INFO1', info2='INFO2', info3='INFO3', timeout=10, debug=True)
        command = "tests/testprog.py --scenario progressing --feedback /tmp/feedback_1.log --delay 0.002 --debug"
        result = self.lnc.execute(command=command)
        print("test20 result={}".format(result))
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()

