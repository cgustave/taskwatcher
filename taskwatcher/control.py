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
import sys
import psutil
from taskwatcher.database import Database

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


    def update(self):
        """
        Update database timing information like tasks duration
        """
        log.info("Enter")
        self._DB.update()

    def reserve(self, taskname="", unique=False):
        """
        Reserve a free taskid and return it
        Should be called before a task can be created
        Task is reserved with taskname 'taskname'
        If unique is set, the reservation will only complete if no other task
        with this name is running
        """
        log.info("Enter with taskname={}".format(taskname))
        taskid = self._DB.reserve_task(taskname=taskname, unique=unique)
        if not taskid:
            log.error("Could not reserve task, already exist and unique is set")
            sys.exit("Could not reserve task, already exist and unique is set")
        return taskid

    def get_tasks(self, reserved=True):
        """
        Returns a dictionary listing the current tasks
        By default, reserved tasks are returned, use reserved=Fasle otherwise
        """
        log.info("Enter")
        task = self._DB.get_tasks(reserved=reserved)
        log.debug("task={}".format(task))
        return task


    def kill_task(self, taskid=None):
        """
        Kills a task from its taskid
        """
        log.info("Enter with taskid={}".format(taskid))
        if not taskid:
            log.error("taskid is required")
            sys.exit("taskid is required")

        # make sure task is still active
        tasks = json.loads(self.get_tasks())
        if str(taskid) in tasks:
            if tasks[taskid]['status'] == "RESERVED":
                log.warning("task is in status reserved, not running, won't kill")
                sys.exit("task is in status reserved, not running, won't kill")
                
            pid = tasks[taskid]['pid']
            status = tasks[taskid]['status']
            log.debug("Task is still active killing pid={} status={}".format(pid,status))
            p = psutil.Process(pid)
            if p.username != 'SYSTEM':
                p.kill()
            else:
                log.warning("This is a system process, won't kill")

        else:
            log.warning("unknown taskid={} won't kill".format(taskid))
            sys.exit("unknown taskid, won't kill")


    def killall_tasks(self, taskname=None):
        """
        Kills all tasks with the given name
        """
        log.info("Enter with taskname={}".format(taskname))

        # Sanity
        if not taskname:
            log.error("Taskname is required")
            sys.exit("Taskname is required")

        if taskname == "":
            log.error("Taskname cannot be empty string")
            sys.exit("Taskname cannot be empty string")

        # Go through task list, check name, make sure this is not a task in
        # status RESERVED and kill if not a system task 
        tasks = json.loads(self.get_tasks())
        for taskid in tasks:
            name = tasks[taskid]['name']
            pid = tasks[taskid]['pid']
            status = tasks[taskid]['status']

            if name == taskname:
                log.debug("Found taskid={} pid={} status={}".format(taskid, pid, status))
                if status == "RESERVED":
                    log.info("task is in status reserved, not running, won't kill")

                p = psutil.Process(pid)
                if p.username != 'SYSTEM':
                    log.info("killing taskid={} name={} pid={} status={}".format(taskid,name,pid,status))
                    p.kill()
                else:
                    log.warning("This is a system process, won't kill")


    def get_number_of_tasks(self):
        """
        Returns number of active tasks, 0 if none
        Return : integer
        """
        log.info("Enter")
        nb_task = self._DB.get_number_of_tasks()
        return nb_task


    def print_tasks(self):
        """
        Prints a human formatted listing of the current tasks
        """
        log.info("Enter")
        tasklist = json.loads(self.get_tasks())


        line = 1 ;
        for task in tasklist:
            if line == 1:
                print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                print("| task id  |      task name       |     info1    |     info2    |     info3    |   pid  |   status   | feedback | reserve time | starting time | duration | last update  | timeout  |")
                print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                print("| {:>8} | {:20} | {:12} | {:12} | {:12} | {:>6} | {:>10} | {:>8} | {:>12} | {:>13} | {:>8} | {:>12} | {:>8} |".
                  format(task, 
                         str(tasklist[task]['name']),
                         str(tasklist[task]['info1']),
                         str(tasklist[task]['info2']),
                         str(tasklist[task]['info3']),
                         str(tasklist[task]['pid']),
                         str(tasklist[task]['status']),
                         str(tasklist[task]['feedback']),
                         str(tasklist[task]['reservetime']),
                         str(tasklist[task]['starttime']),
                         str(tasklist[task]['duration']),
                         str(tasklist[task]['lastupdate']),
                         str(tasklist[task]['timeout']),
                        ))
            line = line+1
        if line > 1:
                print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        if line==1:
            print("No tasks.")


    def get_history(self):
        """
        Returns history list in json format
        """
        log.info("Enter")
        history = self._DB.get_history()
        log.debug("history={}".format(history))
        return history


    def print_history(self):
        """
        Print a human formatted listing of history
        """
        log.info("Enter")
        historylist =  json.loads(self.get_history())

        print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("|    id    | task id  |      task name       |     info1    |     info2    |     info3    |termsignal | termerror | starting time | ending time | duration |      feedback         |") 
        print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        for task in historylist:
            print("| {:>8} | {:>8} | {:20} | {:12} | {:12} | {:12} |{:>10} | {:>9} | {:>13} | {:>11} | {:>8} | {:>21} |".format(
                task,
                str(historylist[task]['taskid']),
                str(historylist[task]['taskname']),
                str(historylist[task]['info1']),
                str(historylist[task]['info2']),
                str(historylist[task]['info3']),
                str(historylist[task]['termsignal']),
                str(historylist[task]['termerror']),
                str(historylist[task]['starttime']),
                str(historylist[task]['endtime']),
                str(historylist[task]['duration']),
                str(historylist[task]['feedback'])
            ))

        print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")


if __name__ == '__main__': #pragma: no cover

    parser = argparse.ArgumentParser(description='Task controller')
    parser.set_defaults(func='none')
    parser.add_argument('--debug', '-d', help="turn on debug", action="store_true")
    parser.add_argument('--db', help="sqlite file (default sqlite.sb)", default='sqlite.db')
    subparsers = parser.add_subparsers(help='sub-command help')

    # tasks
    parser_task = subparsers.add_parser('task', help='active tasks')
    parser_task.set_defaults(func='task')
    parser_task.add_argument('--list', help='list tasks', action="store_true")
    parser_task.add_argument('--reserve', help="reserve a taskid", action="store_true")
    parser_task.add_argument('--unique', help="taskname should be unique", action="store_true")
    parser_task.add_argument('--taskname', help="taskname")
    parser_task.add_argument('--info1', help="any information")
    parser_task.add_argument('--info2', help="any information")
    parser_task.add_argument('--info3', help="any information")
    parser_task.add_argument('--feedback', metavar='taskid', help="returns feedback")
    parser_task.add_argument('--kill', metavar='taskid', help="kill task from its taskid")
    parser_task.add_argument('--killall', metavar='taskname', help="kill all tasks by name")
    parser_task.add_argument('--json', help="json output", action="store_true")
   

    # history
    parser_history = subparsers.add_parser('history', help='compeleted tasks')
    parser_history.set_defaults(func='history')
    parser_history.add_argument('--list', help="display all completed tasks", action="store_true")
    parser_history.add_argument('--human', help="human readable output", action="store_true")
    parser_history.add_argument('--clear', help="clear history", action="store_true")

    # database
    parser_db =  subparsers.add_parser('database', help='database maintenance')
    parser_db.set_defaults(func='database')
    parser_db.add_argument('--initialize', help="creates or recreates a task database (all info are lost)", action="store_true")
    parser_db.add_argument('--update', help="updates database timing information (taks durations)",  action="store_true")


    args = parser.parse_args()
    #print("args={}".format(args))
    controller=Control(db=args.db,debug=args.debug)



    # tasks
    if args.func == 'task':

        if args.list:
            if args.json:
            	print(controller.get_tasks())
            else:
            	controller.print_tasks()

        elif args.reserve:
            taskname = args.taskname
            if not taskname:
                taskname = "noname"
            taskid = controller.reserve(taskname=taskname, unique=args.unique)
            print("Taskid {} has been reserved".format(taskid))

        elif args.kill:
            controller.kill_task(taskid=args.kill)

        elif args.killall:
            controller.killall_tasks(taskname=args.killall)

    # database
    elif args.func == 'database':
        if args.initialize:
            controller.initialize()
            
        if args.update:
            controller.update()

    # history
    elif args.func == 'history':
        if args.list:
            if args.human:
                controller.print_history()
            else:
                print(controller.get_history())

            controller._DB.get_history()
        

