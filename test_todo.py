import unittest
import app
import requests
import json
from base64 import b64encode

# Note unit testing has not been completed. This is interpritation of https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

class UnitTests(unittest.TestCase): 

    @classmethod
    def setUpClass(cls):

        pass 

    @classmethod
    def tearDownClass(cls):

        pass

    def setUp(self):

        self.app = app.app.test_client()
        self.app.testing = True
        self.auth_header = {
            'Authorization': 'Basic ' + b64encode("{0}:{1}".format('user1', 'password1'))
        }
        self.task = {
            'id': app.tasks[-1]['id'] + 1,
            'title': 'title',
            'description': 'description',
            'complete': False
            }
        self.data = {
            "title": "title here",
            "description": "description",
            "complete": False,
        }

    def tearDown(self):

        pass 

    def test_verify_passwordd(self):

        t1 = app.verify_password( "user1","password1")
        t2 = app.verify_password('miguel','python')

        self.assertEqual(True, t1)
        self.assertEqual(False, t2)

    def test_unauthorized(self):

        result = self.app.get('/todo/api/v1.0/tasks') 

        self.assertEqual(result.status_code, 403)
        self.assertIn('Unauthorized access', result.data)

    def test_get_task(self):

        t1, t2 = self.app.get('/todo/api/v1.0/task/1', headers=self.auth_header)
        t3, t4 = self.app.get('/todo/api/v1.0/task/11', headers=self.auth_header)

        self.assertIn('task', t1.data)
        self.assertEqual('Task not found', t3)

    def test_get_tasks(self):

        t1, t2 = self.app.get('/todo/api/v1.0/tasks', headers=self.auth_header)

        self.assertIn('tasks', t1.data)

    def test_delete_task(self):
        
        t1, t2  = self.app.delete('/todo/api/v1.0/task/1', headers=self.auth_header)
        t3, t4  = self.app.delete('/todo/api/v1.0/task/11', headers=self.auth_header)

        self.assertIn("Deleted successfully", t1.data)
        self.assertEqual("Unable to delete task", t3)

if __name__ == "__main__":
    unittest.main()