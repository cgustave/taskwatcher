# -*- coding: utf-8 -*-
'''
Created on May 6, 2020

@author: cgustave
'''
import logging as log
import unittest
import json
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
        self.assertTrue(self.db.task_is_reserved(taskid='1'))

    # Update task
    def test_update_task(self):
        update = {}
        update['name'] = "MyTestTask"
        update['pid'] = 120
        update['status'] = "RUNNING"
        self.db.update_task(taskid='1', update=update)
        js = json.loads(self.db.return_tasks(taskid='1'))
        self.assertEqual(js['1']['status'], 'RUNNING')

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

if __name__ == '__main__':
    unittest.main()

