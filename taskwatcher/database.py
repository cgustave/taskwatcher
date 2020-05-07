#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on May 6th, 2020
@author: cgustave

database from the taskwatcher suite
"""

import logging as log
import os
import sqlite3
import json
import time

class Database(object):
    """
    Datanse from the taskwatcher suite
    Called with db : sqlite file
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

        # Sanity checks
        if not db:
            log.error("db filename is required")
            raise SystemExit

        # Attributs
        self.db = db

        # Private Attributs
        self._DB = None


    def create(self):
        """
        Create a new database from the given filename
        If a file already exist, delete it before creation
        """
        log.info("Enter")

        # Create new db file
        if os.path.isfile(self.db):
            log.debug("{} exists, delete it".format(self.db))
            os.remove(self.db)
        
        log.debug("Create database {}".format(self.db))
        try:
            self._DB = sqlite3.connect(self.db)
            cursor = self._DB.cursor()
            cursor.execute('''
                CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT, pid INTEGER, status TEXT, feedback INTEGER,
                           reservetime INTEGER, starttime INTEGER, duration INTEGER, lastupdate INTEGER, timeout INTEGER)
            ''')
            cursor.execute('''
                CREATE TABLE feedbacks (id INTEGER PRIMARY KEY, feedback BLOB, lastupdate INTEGER)
            ''')
            cursor.execute('''
                CREATE TABLE history (id INTEGER PRIMARY KEY, taskid INTEGER,
                           taskname TEXT, termsignal TEXT, termerror TEXT,
                           starttime INTEGER, endtime INTEGER, duration INTEGER,
                           feedback BLOB)
            ''')
            self._DB.commit()

        except Exception as e:
            # Roll back
            self._DB.rollback()
            raise e

        finally:
             self._DB.close()

    # --- tasks ---

    def reserve_task(self):
        """
        Inserts a new task for a reservation
        Returns the id of the created return_tasks
        """
        log.info("Enter with entry")

        lastid = None
        reservetime=int(time.time())

        try:
            self._DB = sqlite3.connect(self.db)
            cursor = self._DB.cursor()
            cursor.execute('''INSERT INTO tasks(id, status, reservetime)
                           VALUES(?,?,?)''', [ None,'RESERVED', reservetime])
            lastid = cursor.lastrowid
            self._DB.commit()

        except Exception as e:
            # Roll back
            self._DB.rollback()
            raise e

        finally:
             self._DB.close()

        log.debug("lastid={}".format(lastid))
        return lastid


    def task_is_reserved(self, taskid=''):
        """
        Test if the provided task id has been reserved
        Parameter : taskid
        Returns : True/False
        """
        log.info("Enter")

        try:
            self._DB = sqlite3.connect(self.db)
            cursor = self._DB.cursor()
            cursor.execute('''SELECT id, status FROM tasks WHERE status="RESERVED" and id=?''',taskid)  
            task = cursor.fetchone()
            if task:
                return True
            else:
                return False

        except Exception as e:
            raise e

        finally:
            self._DB.close()

    def update_task(self, taskid='', update=None):
        """
        Updates a task from its taskid with the given information in the update dictionary
        Updates the lastupdate timer
        """
        log.info("Enter")

        if not taskid:
            log.error("no taskid provided")
            raise SystemExit
        if not update:
            log.warning("no updated provided, ignoring")
            return 

        task = json.loads(self.return_tasks(taskid=taskid))
        for key in update:
            if key not in task[taskid]:
                log.error("key={} is unknown from table tasks".format(key))
                raise SystemExit
            current_value = task[taskid][key]
            if current_value==update[key]:
                log.debug("key={} has already value={}, do nothing".format(key,update[key]))
            else:
                log.debug("update key={} with value={}".format(key,update[key]))
                task[taskid][key] = update[key]

        log.debug("updating with task={}".format(task[taskid]))

        updatetime = int(time.time())

        try:
            self._DB = sqlite3.connect(self.db)
            cursor = self._DB.cursor()
            cursor.execute('''UPDATE tasks SET name=?, pid=?, status=?,
                           feedback=?, reservetime=?, starttime=?, duration=?,
                           lastupdate=?, timeout=?  WHERE id=?''',
                           (task[taskid]['name'],
                            task[taskid]['pid'],
                            task[taskid]['status'],
                            task[taskid]['feedback'],
                            task[taskid]['reservetime'],
                            task[taskid]['starttime'],
                            task[taskid]['duration'],
                            updatetime,
                            task[taskid]['timeout'],
                            taskid))
            self._DB.commit()

        except Exception as e:
            # Roll back
            self._DB.rollback()
            raise e

        finally:
             self._DB.close()

    
    def return_tasks(self, taskid=None):
        """
        Returns all tasks as a string in a json format
        If a taskid is provided, only return for this task
        """
        log.info("Enter with taskid={}".format(taskid))
        result={}

        try:
            self._DB = sqlite3.connect(self.db)
            cursor = self._DB.cursor()
            if taskid:
                cursor.execute('''SELECT id, name, pid, status, feedback, reservetime, 
                                  starttime, duration, lastupdate, timeout FROM
                                  tasks WHERE id=?''',taskid)
            else:
                cursor.execute('''SELECT id, name, pid, status, feedback, reservetime, 
                                  starttime, duration, lastupdate, timeout FROM tasks''')
 
            for row in cursor:
                log.debug('''tasks {0} : name={1}, pid={2}, status={3}, feedback={4}, reservetime={5}, starttime={6}, duration={7}, lastupdate={8} timeout={9}'''
                          .format(row[0], row[1], row[2], row[3],row[4], row[5], row[6], row[7], row[8], row[9]))
                result[row[0]]= {}
                result[row[0]]['name'] = row[1]
                result[row[0]]['pid'] = row[2]
                result[row[0]]['status'] = row[3]
                result[row[0]]['feedback'] = row[4]
                result[row[0]]['reservetime'] = row[5]
                result[row[0]]['starttime'] = row[6]
                result[row[0]]['duration'] = row[7]
                result[row[0]]['lastupdate'] = row[8]
                result[row[0]]['timeout'] = row[9]

        except Exception as e:
            self._DB.rollback()
            raise e

        finally:
            self._DB.close()

        result_json = json.dumps(result)
        log.debug("return result_json={}".format(result_json))
        
        return result_json


    # --- feedbacks ---

    def return_feedbacks(self, taskid=None):
        """
        Returns all feedbacks as a string in a json format
        If a taskid is provided, only return for this task
        """
        log.info("Enter with taskid={}".format(taskid))
        result={}

        try:
            self._DB = sqlite3.connect(self.db)
            cursor = self._DB.cursor()
            if taskid:
                cursor.execute('''SELECT id, feedback FROM feedbacks WHERE id=?''',taskid)
            else:
                cursor.execute('''SELECT id, feedback FROM feedbacks''')

            for row in cursor:
                log.debug('''feedbacks {0} : feedback={1}'''.format(row[0], row[1]))
                result[row[0]]= {}
                result[row[0]]['feedback'] = row[1]

        except Exception as e:
            self._DB.rollback()
            raise e

        finally:
            self._DB.close()

        result_json = json.dumps(result)
        log.debug("return result_json={}".format(result_json))

        return result_json


    def update_feedback(self, taskid=None, feedback=None):
        """
        Updates feedback from given taskid
        Feedback is created if not
        """
        log.info("Enter with taskid={} feedback={}".format(taskid, feedback))

        if not taskid:
            log.error("no taskid provided")
            raise SystemExit
        if not feedback:
            log.error("no feedback provided")
            raise SystemExit

        fb = json.loads(self.return_feedbacks(taskid=taskid))

        if not fb:
            # This is a new entry 
            log.debug("No feedback for this taskid, need new entry")
            updatetime = int(time.time())

            try:
                self._DB = sqlite3.connect(self.db)
                cursor = self._DB.cursor()
                cursor.execute('''INSERT INTO feedbacks(id,feedback,lastupdate) 
                               VALUES(?,?,?)''',(None,feedback,updatetime))
                self._DB.commit()

            except Exception as e:
                # Roll back
                self._DB.rollback()
                raise e

            finally:
                 self._DB.close()


        else :
            # This is an update
            current_value = fb[taskid]['feedback']
            log.debug("Current feedback={}".format(current_value))
            if current_value==feedback:
                log.debug("feedback is unchanged, do nothing")
            else:
                log.debug("update feedback with {}".format(feedback))
                fb[taskid]['feedback'] = feedback

            log.debug("updating with feedback={}".format(fb[taskid]))
            updatetime = int(time.time())

            try:
                self._DB = sqlite3.connect(self.db)
                cursor = self._DB.cursor()
                cursor.execute('''UPDATE feedbacks SET feedback=?, lastupdate=? WHERE  id=?''',
                               (fb[taskid]['feedback'], updatetime, taskid))
                self._DB.commit()

            except Exception as e:
                # Roll back
                self._DB.rollback()
                raise e

            finally:
                 self._DB.close()

