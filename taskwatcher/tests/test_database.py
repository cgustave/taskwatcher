# -*- coding: utf-8 -*-
'''
Created on May 6, 2020

@author: cgustave
'''
import logging as log
import unittest
import json
import time
from database import Database

# create logger
log.basicConfig(
    format='%(asctime)s,%(msecs)3.3d %(levelname)-8s[%(module)-10.10s.\
    %(funcName)-20.20s:%(lineno)5d] %(message)s',
    datefmt='%Y%m%d:%H:%M:%S',
    filename='debug.log',
    level=log.DEBUG)

log.debug("Start unittest")

class DatabaseTestCase(unittest.TestCase):

    # Always run before any test
    def setUp(self):
        self.db = Database(db='sqlite.db', debug=True)

    # Database creation
    def test_create(self):
        self.db.create()

    # Reserve task
    def test_reserve(self):
        self.db.reserve_task()
        self.assertTrue(self.db.is_task_reserved(taskid='1'))

    # Update task
    def test_update_task(self):
        update = {}
        update['name'] = "MyTestTask"
        update['pid'] = 120
        update['status'] = "RUNNING"
        update['starttime'] = int(time.time())
        self.db.update_task(taskid='1', update=update)
        js = json.loads(self.db.return_tasks(taskid='1'))
        self.assertEqual(js['1']['status'], 'RUNNING')

    # Database update

    def force_task_started(self, taskid='1'):
        # Force some tasks to be started (in timeout state)
        update = {}
        update['name'] = "MyTestTask"
        update['pid'] = 120
        update['status'] = "RUNNING"
        update['starttime'] = int(time.time()-100)
        update['timeout'] = 30
        self.db.update_task(taskid=taskid, update=update)

    def test_update(self):
        self.force_task_started(taskid='1')
        self.db.update()

    def test_timeout_status(self):
        self.force_task_started(taskid='1')
        status = self.db.timeout_status(taskid='1')
        self.assertTrue(status)

    # Update feedback
    def test_update_feedback_insert(self):
        # First time would be a creation
        feedback = "{ 'person' : 'john', 'animal' : { 'name' : 'Lune', 'color' : 'black', 'gender' : 'female'} }"
        self.db.update_feedback(taskid='1', feedback=feedback)
        js = json.loads(self.db.return_feedbacks(taskid='1'))
        self.assertEqual(js['1']['feedback'], feedback)

    def test_update_feedback_update(self):
        # Second time and update
        feedback = "{ 'person' : 'Lucie', 'animal' : { 'name' : 'Rex', 'color' : 'white', 'gender' : 'male'} }"
        self.db.update_feedback(taskid='1', feedback=feedback)
        js = json.loads(self.db.return_feedbacks(taskid='1'))
        self.assertEqual(js['1']['feedback'], feedback)

    # history

    def add_history(self):
        entry = {}
        entry['taskid'] = 100
        entry['taskname'] = 'MyTestTask'
        entry['termsignal'] = 'SIGTERM'
        entry['termerror'] = ''
        entry['starttime'] = 1588874292
        entry['endtime'] = 1588875292
        entry['duration'] = 1000
        entry['feedback'] = "{ 'person' : 'john', 'animal' : { 'name' : 'Lune', 'color' : 'black', 'gender' : 'female'} }"
        self.db.add_history(entry=entry)

    def test_return_history(self):
        self.add_history()
        js = json.loads(self.db.return_history())
        self.assertEqual(js['1']['taskname'],"MyTestTask")

if __name__ == '__main__':
    unittest.main()

