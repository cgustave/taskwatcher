#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on May 7th, 2020
@author: cgustave

controller from the taskwatcher suite
"""

import logging as log
import argparse
import json
from database import Database

class Control(object):
    """
    Controller from the taskwatcher suite
    Called with db
    """
    def __init__(self, db='', debug=False):

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

        log.info("Constructor with db={} debug={}".format(db, debug))
 
        # Public attributs
        self.db = db

        # Private attributs
        self._DB = Database(db=db, debug=debug)


    def initialize(self):
        """
        Initializes a database
        """
        log.info("Enter")
        print ("Initializing database {}".format(self.db))
        self._DB.create()


    def reserve(self):
        """
        Reserve a free taskid and return it
        Should be called before a task can be created
        """
        log.info("Enter")
        taskid = self._DB.reserve_task()
        return taskid


    def return_tasks(self):
        """
        Returns a dictionary listing the current tasks
        """
        log.info("Enter")
        data = self._DB.return_tasks()
        log.debug("data={}".format(data))
        return data

    def print_tasks(self):
        """
        Prints a human formatted listing of the current tasks
        """
        log.info("Enter")
        tasklist = json.loads(self.return_tasks())

        print("----------------------------------------------------------------------------------------------------------------------------------------")
        print("| task id  |      task name       |   pid  |   status   | feedback | reserve time | starting time | duration | last update  | timeout  |")
        print("----------------------------------------------------------------------------------------------------------------------------------------")

        for task in tasklist:
            print("| {:>8} | {:20} | {:>6} | {:>10} | {:>8} | {:>12} | {:>13} | {:>8} | {:>12} | {:>8} |".
                  format(task, 
                         str(tasklist[task]['name']),
                         str(tasklist[task]['pid']),
                         str(tasklist[task]['status']),
                         str(tasklist[task]['feedback']),
                         str(tasklist[task]['reservetime']),
                         str(tasklist[task]['starttime']),
                         str(tasklist[task]['duration']),
                         str(tasklist[task]['lastupdate']),
                         str(tasklist[task]['timeout']),
                        ))
        print("----------------------------------------------------------------------------------------------------------------------------------------")
                 
if __name__ == '__main__': #pragma: no cover

    parser = argparse.ArgumentParser(description='Task controller.')
    parser.add_argument('--db', help="sqlite database file", required=True)
    parser.add_argument('--debug', '-d', help="turn on debug", action="store_true")
    parser.add_argument('--human', help="human readable output", action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--initialize', help="create or recreates a task database (all info are lost)", action="store_true")
    group.add_argument('--list', help="list active tasks", action="store_true")
    group.add_argument('--reserve', help="get a reservation for a taskid number", action="store_true")
    group.add_argument('--feedback', metavar='taskid',help="returns a json formatted feedback for the given taskid")
    group.add_argument('--history', help="dump all historical tasks completed", action="store_true")
    group.add_argument('--clear', help="clear all tasks history", action="store_true")
    group.add_argument('--kill', metavar='taskid', help="kills the task from its taskid")
    group.add_argument('--killall', metavar='taskname',help="kills all task with the given taskname")
    args = parser.parse_args()

    controller=Control(db=args.db,debug=args.debug)

    if args.reserve:
        taskid = controller.reserve()
        print("Taskid {} has been reserved".format(taskid))

    elif args.initialize:
        controller.initialize()

    elif args.list:
        if args.human:
            controller.print_tasks()
        else:
           print("{}".format(controller.return_tasks()))


