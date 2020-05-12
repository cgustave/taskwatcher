# -*- coding: utf-8 -*-
'''
Created on May 12, 2020

@author: cgustave
'''
import logging as log
import unittest
import json

from parse import Parse

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-10.10s.\
    %(funcName)-20.20s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

log.debug("Start unittest")

class ParseTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.parse = Parse(debug=True)

    def test_load_sample_feedback(self):
        self.parse.load_file("tests/textfile_mixed.txt")
        js = json.loads(self.parse.get_data())
        self.assertEqual(js['town'], "Paris")

if __name__ == '__main__':
    unittest.main()

