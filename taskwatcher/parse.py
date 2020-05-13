#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on May 12th, 2020
@author: cgustave

Feedback file parser from the taskwatcher suite
"""

import logging as log
import argparse
import json
import sys
import re

class Parse(object):
    """
    Feedback file parser from the taskwatcher suite
    """
    
    def __init__(self, debug=False):

        # create logger
        log.basicConfig(
            format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-\
            10.10s.%(funcName)-20.20s:%(lineno)5d] %(message)s',
            datefmt='%Y%m%d:%H:%M:%S',
            filename='debug.log',
            level=log.NOTSET)

        # Set debug level first
        if debug:
            self.debug = True
            log.basicConfig(level='DEBUG')
        else:
            self.debug = False
            log.basicConfig(level='ERROR')

        log.info("Constructor debug={}".format(debug))

        # Attributs
        self.file = None
        self.dict = {}


    def load_file(self, file=""):
        """
        Loads feedback file in memory
        Extract key/value pairs
        """
        log.info("Enter with file={}".format(file))

        # Sanity
        if not file:
            log.debug("file is required")
            sys.exit("file is required")

        try:
            with open(file, 'r',encoding='utf-8') as F:
                for line in F:
                    line=line.strip()
                    log.debug("read line={}".format(line))

					# Extract data from feedback lines
                    match_feedback = re.search("^(?:\[)(?P<key>[A-Za-z0-9\-_]+)(?:\])(?P<value>.*)",line)
                    if match_feedback:
                        key = match_feedback.group('key')
                        value = match_feedback.group('value')
                        log.debug("found key={} value={}".format(key,value))

                        # See if we need to remove an entry
                        if not value:
                            log.debug("delete request for key={}".format(key))
                            if key in self.dict:
                                log.debug("key exists, deleting key={}".format(key))
                                self.dict.pop(key)
                        else:
                            log.debug("adding key={} value={} to data".format(key,value))
                            self.dict[key] = value

                        
            F.close()

        except IOError as e:
            log.debug("I/O error filename={} error={}".format(file,e.strerror))


    def get_data(self):
        """
        Returns a json formated string with the resulting key/value pairs
        resulting from the feedback file
        Requirements : file loaded

        Return : json formated string
        """
        log.info("Enter")
        return json.dumps(self.dict)




if __name__ == '__main__': #pragma: no cover

    argparser = argparse.ArgumentParser(description='Task controller')
    argparser.set_defaults(func='none')
    argparser.add_argument('--debug', '-d', help="turn on debug", action="store_true")
    argparser.add_argument('--feedback', metavar='filename', help="selects feedback file to process", required=True)

    args = argparser.parse_args()
    
    parser=Parse(debug=args.debug)
    parser.load_file(file=args.feedback)
    print(json.dumps(parser.get_data()))

