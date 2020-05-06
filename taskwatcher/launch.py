#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on May 6th, 2020
@author: cgustave

launcher from the taskwatcher suite
"""

import logging as log
import os
import argparse

class Launcher(object):
    """
    Launcher from taskwatcher suite
    Called with :
        - taskid
        - dbpath

    Optional :
        - name
        - feedpath
        - timeout
    """

    def __init__(self, taskid='', dbpath='', name='', feedpath=None, timeout=30, debug=False):

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

        # Sanity checks
        if not (os.path.exists(dbpath) and os.path.isdir(dbpath)):
            print ("dbpath {} does not exist or is not a directory\n".format(dbpath))
            raise SystemExit

        if feedpath:
           if not (os.path.exists(feedpath) and os.path.isdir(feedpath)): 
               print ("feedpath does not exist or is not a directory\n")
               raise SystemExit

        log.info("Constructor with taskid={} dbpath={}  name={} feedpath={} timeout={} debug={}".
          format(taskid, dbpath, name, feedpath, timeout, debug))
 
        # Attributes
        self.taskid = taskid
        self.dbpath = dbpath
        self.name = name 
        self.feedpath = feedpath
        self.timeout = timeout
                 
if __name__ == '__main__': #pragma: no cover

    parser = argparse.ArgumentParser(description='Launch program as a task.')
    parser.add_argument('--taskid', help="Task identifier")
    parser.add_argument('--name',  help="Task name")
    parser.add_argument('--dbpath', help="Path where sqlite db file is located")
    parser.add_argument('--feedpath', help="Path where feedback file is located")
    parser.add_argument('--debug', '-d', help="Debugging on", action="store_true")

    # Get our command args, after the --
    parser.add_argument('command', nargs=argparse.REMAINDER, help="Our command to run (ex: ./command -option1 -option2 foo)")
    args = parser.parse_args()

    # Retrieve command line to run with its options after the --
    command_line = ""
    i=1
    for item in args.command:
        if item=='--':
            continue
        if i==1:
            space=""
        else:
            space=" "
        command_line=command_line+space+str(item)
        i=i+1
    print ("Command_line={}".format(command_line))

    # If no name is provided, use program name
    if not args.name:
        name=args.command[1]
    else:
        name=args.name

    launcher=Launcher(taskid=args.taskid, name=name, dbpath=args.dbpath,
                      feedpath=args.feedpath, debug=args.debug)
