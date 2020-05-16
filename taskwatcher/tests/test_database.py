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
    def test010_create(self):
        self.db.create()

    # Reserve task
    def test020_reserve(self):
        self.db.reserve_task()
        self.assertTrue(self.db.is_task_reserved(taskid='1'))

    def test030_reserve_unique(self):
        self.db.reserve_task(taskname="MyTask")
        taskid = self.db.reserve_task(taskname="MyTask", unique=True)
        self.assertEqual(taskid, 0)

    def test040_count_nb_tasks(self):
        self.db.reserve_task(taskname="MyTask")
        nb_tasks = self.db.get_number_of_tasks()
        self.assertEqual(nb_tasks, 3)

    # Update task
    def test050_update_task(self):
        update = {}
        update['name'] = "MyTestTask"
        update['info1'] = "information1"
        update['info2'] = "information2"
        update['info3'] = "information3"
        update['pid'] = 120
        update['status'] = "RUNNING"
        update['starttime'] = int(time.time())
        self.db.update_task(taskid='1', update=update)
        js = json.loads(self.db.get_tasks(taskid='1'))
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

    def test060_update(self):
        self.force_task_started(taskid='1')
        self.db.update()

    def test070_timeout_status(self):
        self.force_task_started(taskid='1')
        status = self.db.timeout_status(taskid='1')
        self.assertTrue(status)

    # Update feedback
    def test080_update_feedback_insert(self):
        # First time would be a creation
        feedback = "{ 'person' : 'john', 'animal' : { 'name' : 'Lune', 'color' : 'black', 'gender' : 'female'} }"
        self.db.update_feedback(taskid='1', feedback=feedback)
        js = json.loads(self.db.get_feedbacks(taskid='1'))
        self.assertEqual(js['1']['feedback'], feedback)

    def test090_update_feedback_update(self):
        # Second time and update
        feedback = "{ 'person' : 'Lucie', 'animal' : { 'name' : 'Rex', 'color' : 'white', 'gender' : 'male'} }"
        self.db.update_feedback(taskid='1', feedback=feedback)
        js = json.loads(self.db.get_feedbacks(taskid='1'))
        self.assertEqual(js['1']['feedback'], feedback)

    # history

    def add_history(self):
        entry = {}
        entry['taskid'] = 100
        entry['taskname'] = 'MyTestTask'
        entry['info1'] = 'Information1'
        entry['info2'] = 'Information2'
        entry['info3'] = 'Information3'
        entry['termsignal'] = 'SIGTERM'
        entry['termerror'] = ''
        entry['starttime'] = 1588874292
        entry['endtime'] = 1588875292
        entry['duration'] = 1000
        entry['feedback'] = "{ 'person' : 'john', 'animal' : { 'name' : 'Lune', 'color' : 'black', 'gender' : 'female'} }"
        self.db.add_history(entry=entry)

    def test100_get_history(self):
        self.add_history()
        js = json.loads(self.db.get_history())
        self.assertEqual(js['1']['taskname'],"MyTestTask")

if __name__ == '__main__':
    unittest.main()

