#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on May 6th, 2020
@author: cgustave

launcher from the taskwatcher suite
"""

import logging as log
import os
import sys
import argparse

class Launch(object):
    """
    Launcher from taskwatcher suite
    Called with taskid, db
    Optional : name, feedpath, timeout
    Requirement : a taskid should have been reserved
    """
    def __init__(self, taskid='', db='', name='', feedpath=None, timeout=30, debug=False):

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
        if not (os.path.isfile(db)):
            print ("db file {} does not exist\n".format(db))
            raise SystemExit

        if feedpath:
           if not (os.path.exists(feedpath) and os.path.isdir(feedpath)): 
               print ("feedpath does not exist or is not a directory\n")
               raise SystemExit

        log.info("Constructor with taskid={} db={}  name={} feedpath={} timeout={} debug={}".
          format(taskid, db, name, feedpath, timeout, debug))
 
        # Attributes
        self.taskid = taskid
        self.db = db
        self.name = name 
        self.feedpath = feedpath
        self.timeout = timeout
        self.command = None


    def execute(self, command=""):
        """
        Execute provided command in a child process
        """
        log.info("Enter with command={}".format(command))

        # Prepare command and args for exec
        # args : starts with the command name
        # Example or args for ./launch.py --taskid 1 --db sqlite.db  --  ls
        # ./launch.py --taskid 1 --db sqlite.db -- tests/testprog.py --scenario sleeping
        #  ==> cmd_list ['tests/testprog.py', '--scenario', 'sleeping']
        
        cmd_list = command.split()
        log.debug("cmd_list {}".format(cmd_list))

        try:
            os.execvp(cmd_list[0], cmd_list)
        except Exception as e:
            log.debug("Error {}".format(e))
            raise SystemExit

        log.debug("End of program")
        os._exit(0)

                 
if __name__ == '__main__': #pragma: no cover

    parser = argparse.ArgumentParser(description='Launch program as a task.')
    parser.add_argument('--taskid', help="reserved task identifier", required=True)
    parser.add_argument('--name', help="Task name")
    parser.add_argument('--db', help="sqlite db file", required=True)
    parser.add_argument('--feedpath', help="Path where feedback file is expected")
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
    #if not args.name:
    #    name=args.command[1]
    #else:

    launcher=Launch(taskid=args.taskid, name=args.name, db=args.db,
                    feedpath=args.feedpath, debug=args.debug)

    launcher.execute(command_line)


