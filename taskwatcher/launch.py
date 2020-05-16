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
import json
import psutil
import time
import argparse
from taskwatcher.database import Database

class Launch(object):
    """
    Launcher from taskwatcher suite
    Called with taskid, db
    Optional : name, feedpath, timeout
    Requirement : a taskid should have been reserved
    """
    def __init__(self, taskid='', db='', name='', info1='', info2='', info3='', feedpath=None, timeout=30, debug=False):

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

        log.info("Constructor with taskid={} db={}  name={} info1={} info2={} info3={} feedpath={} timeout={} debug={}".
          format(taskid, db, name, info1, info2, info3, feedpath, timeout, debug))
 
        # Public Attributs
        self.taskid = taskid
        self.db = db
        self.name = name 
        self.info1 = info1
        self.info2 = info2
        self.info3 = info3
        self.feedpath = feedpath
        if not timeout:
            timeout = 30 
            
        self.timeout = int(timeout)
        self.command = None
        self.forked_pid = None 
        self.will_feedback = False
        self.starttime = None
        self.father_check_delay = 2

        # Private attributs
        self._DB = Database(db=db, debug=debug) 
        self._check_feedback_retry = 0


    def clear_to_start_task(self):
        """
        Returns True if task if clear to be started
        This mean taskid has is known in reserve status
        """
        log.info("Enter")
        
        if self._DB.is_task_reserved(taskid=self.taskid):
            return True
        else:
            log.warning("task has no reservation")
            return False


    def execute(self, command=""):
        """
        Execute provided command in a child process
        If program is expected to feedback, it should have an option --feedback
        to provide feedback file name.
        If feedback is expected, a reservation is required (so feedback file is
        determined for both contol and launched program
        """
        log.info("Enter with command={}".format(command))

        # Learn if task is supposed to feedback
        if self._task_will_feedback(command=command):
            self.will_feedback = True

        # Sanity
        if not self.taskid:
            if self.will_feedback:
                # If the program is supposed to feedback, it needs a
                # reservation known in advanced so it can provide the correct
                # feedback file name
                log.error("taskid is required if task is expected to feedback, --feedback is set")
                sys.exit("taskid is required if task is expected to feedback, --feedback is set")
            else:
                log.debug("task is not expected to feedback, doing automatic reservation")
                taskid = self._DB.reserve_task(taskname=self.name)
                self.taskid = taskid
                log.debug("automatique reservation gave taskid={}".format(taskid))

        # Check reservation is ok
        if not self.clear_to_start_task():
            log.error("taskid={} is not clear to start".format(self.taskid))
            sys.exit("taskid={} is not clear to start".format(self.taskid))

        pid = os.fork()
        self.forked_pid = pid

        if not pid:
            log.debug("Son : I am a just forked child process")
            self.child(command=command)
            sys.exit(1)

        log.debug("Father : Forked child with pid={}".format(pid)) 
        self.father_loop()

       
    def father_loop(self):
        """
        Father code after fork
        """
        log.info("Enter")

        self._move_task_to_status_running()

        child_healthy = True
        while child_healthy:

            child_healthy = self.father_check_child_health()
            time.sleep(self.father_check_delay)
            log.debug("Father: still alive, child_healthy={}".format(child_healthy))

        log.debug("Father: child pid={} is not healthy".format(self.forked_pid))

        # Prevent zombies!  Reap the child after exit
        pid, status = os.waitpid(0, 0)
        log.debug("Child exited: pid {} returned status {}".format(pid,status))
        if pid == self.forked_pid:
            self._remove_running_task(pid=pid,status=status)
        else:
            sys.exit("should not see this")


    def father_check_child_health(self):
        """
        Returns True if child is alive
        If childs provide feedback, check the heartbeat   
        Heartbeat should be checked from feedback file update time
        """
        log.info("Enter")
   
        # Avoid race condition, make sure child had time to
        # open the feedback file
        time.sleep(1)

        # check process status
        healthy = self.father_checks_child_process_status_ok()

        if healthy:
            if self.will_feedback:
                if not self.father_checks_child_feedback_ok():
                    healthy = False

        log.debug("taskid {} pid {} healthy={}"
                  .format(self.taskid, self.forked_pid, healthy))

        if healthy:
            self._update_running_task()

        log.debug("healthy={}".format(healthy))
        return healthy


    def father_checks_child_process_status_ok(self):
        """
        Check process pid is known and child is not a zombie
        """
        log.info("Enter")

        healthy = True
        # check process still exists
        if psutil.pid_exists(self.forked_pid):
            log.debug("Father: taskid={} process pid={} exists".
                        format(self.taskid, self.forked_pid))

            # Process may be in defunct state if child has finished
            status = psutil.Process(self.forked_pid).status()
            if status == 'zombie':
                log.warning("Father: taskid={} process pid={} status={}".
                            format(self.taskid, self.forked_pid, status))
                healthy = False

        else:
            log.debug("Father: taskid={} process pid={} is dead".
                      format(self.taskid, self.forked_pid))
            healthy = False

        log.debug("healthy={}".format(healthy))
        return healthy


    def father_checks_child_feedback_ok(self):
        """
        If process is supposed to feedback,
        check if it updates feedbackfile in time
        """
        log.info("Enter")

        healthy = True
        try:
            currenttime = int(time.time())
            updatetime = int(os.path.getmtime(self.updatefile_name()))
            
            if (currenttime - updatetime) > self.timeout:
                log.debug("taskid {} pid {} has timeout: {} > {}"
                       .format(self.taskid, self.forked_pid, (currenttime - updatetime), self.timeout))
                healthy = False

        except Exception as e:
            log.warning("attempt={} : error: {}".format(self._check_feedback_retry, e))
            self._check_feedback_retry = self._check_feedback_retry + 1

        if self._check_feedback_retry > 2:
            log.error("Could not check feedback file after 3 attempts")
            sys.exit("Could not check feedback file after 3 attempts")

        return healthy


    def child(self, command=""):
        """
        Child code after fork
        """

        # Prepare command and args for exec
        # args : starts with the command name
        # Example or args for ./launch.py --taskid 1 --db sqlite.db  --  ls
        # ./launch.py --taskid 1 --db sqlite.db -- tests/testprog.py --scenario sleeping
        #  ==> cmd_list ['tests/testprog.py', '--scenario', 'sleeping']
        
        cmd_list = command.split()
        log.debug("cmd_list {}".format(cmd_list))

        try:
            log.debug("Child : exec with command={}".format(command))
            env_path = os.getenv('PATH')
            log.debug("Child : PATH={}".format(env_path))
            os.execvp(cmd_list[0], cmd_list)
        except Exception as e:
            log.debug("Error {}".format(e))
            raise SystemExit

        log.error("Child : should not see this !")
        os._exit(1)


    def _task_will_feedback(self,command):
        """
        Determine from the command line if a task is expected to provide
        feedack. Checks --feedback pattern in command string
        """
        log.info ("Enter with command={}".format(command))

        cmd_split = command.split()

        if '--feedback' in cmd_split:
            log.debug("task will feedback")
            return True
        else :
            log.debug("task won't feedback")
            return False

    def _move_task_to_status_running(self):
        """
        Change tasks status to reflect the running state just after the task is
        started
        """
        log.info("Enter")

        if not self.taskid:
            log.error("taskid is required")
            raise SystemExit

        update = {}

        if self.name:
            update['name'] = self.name

        update['status'] = 'RUNNING'
        update['pid'] = self.forked_pid
        update['feedback']= self.will_feedback
        self.starttime =  int(time.time())
        update['starttime'] = self.starttime 
        update['timeout']= self.timeout 
        self._DB.update_task(taskid=self.taskid, update=update)


    def _update_running_task(self):
        """
        Update database when child is runninig in good health
        """
        log.info("Enter")

        update = {}
        lastupdate = int(time.time())
        update['lastupdate'] = lastupdate
        update['duration'] = lastupdate - self.starttime 
        self._DB.update_task(taskid=self.taskid, update=update)


    def _remove_running_task(self, pid='', status=''):
        """
        Child is dead, remove running task and archive in history
        """
        log.info("Enter with pid={} status={}".format(pid,status))

        entry = {}
        task = json.loads(self._DB.get_tasks(taskid=self.taskid))

        # taskid must be a string to be used in dictionary
        taskid = str(self.taskid)

        # Add history entry from the latest task info
        entry['taskid'] = taskid
        entry['taskname'] = task[taskid]['name']
        entry['info1'] = task[taskid]['info1']
        entry['info2'] = task[taskid]['info2']
        entry['info3'] = task[taskid]['info3']
        entry['termsignal'] = status
        entry['termerror'] = "TBD"
        entry['starttime'] = task[taskid]['starttime']
        endtime = int(time.time())
        entry['endtime'] = endtime
        entry['duration'] = endtime - task[taskid]['starttime']
        entry['feedback'] = "to be implemented"
        self._DB.add_history(entry=entry)

        # Delete task
        self._DB.delete_task(taskid=taskid)


    def updatefile_name(self):
        """
        Returns the expected task update file name from taskid and feedpath
        """
        log.info("Enter")
        update_file_name = "feedback_"+str(self.taskid)+".log"
        return update_file_name


                 
if __name__ == '__main__': #pragma: no cover

    parser = argparse.ArgumentParser(description='Launch program as a task.')
    parser.add_argument('--taskid', help="reserved task identifier", required=True)
    parser.add_argument('--name', help="Task name")
    parser.add_argument('--info1', help="any information")
    parser.add_argument('--info2', help="any information")
    parser.add_argument('--info3', help="any information")
    parser.add_argument('--db', help="sqlite db file", required=True)
    parser.add_argument('--feedpath', help="Path where feedback file is expected")
    parser.add_argument('--timeout', help="timeout timer for the task")
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

    launcher=Launch(taskid=args.taskid, name=args.name, info1=args.info1,
                    info2=args.info2, info3=args.info3, db=args.db,
                    feedpath=args.feedpath, timeout=args.timeout, debug=args.debug)

    launcher.execute(command_line)


