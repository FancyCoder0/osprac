import unittest
import json
import time
import os

from flask import current_app, url_for
from app import create_app


class BasicsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()

    def test_app_exists(self):
        """ Check start of app successfully.
        """
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """ Check app using TestConfig.
        """
        self.assertTrue(current_app.config['TESTING'])
    
    def test_app_homepage(self):
        response = self.client.get(url_for('main.index'))
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response is not None)

    def test_server_response_and_task_success(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task1",
            "commandLine": "sleep 10 && echo 10",
        })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["code"], 0)

        time.sleep(30)

        response = self.client.get(url_for('main.status'), json={"name" : "test-task1", })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["status"], "Succeeded")

        
    def test_task_fail(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task2",
            "commandLine": "sl",
            "maxRetryCount": "3", 
        })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["code"], 0)

        time.sleep(20)

        response = self.client.get(url_for('main.status'), json={
            "name" : "test-task2",     
        })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["status"], "Failed")

    def test_task_kill(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task3",
            "commandLine": "sleep 30",
        })

        time.sleep(10)

        response = self.client.get(url_for('main.kill'), json={"name" : "test-task3", })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["code"], 0)
        self.assertEqual(json_response["data"], "success")
        
        time.sleep(10)

        response = self.client.get(url_for('main.kill'), json={"name" : "test-task3", }, follow_redirects=True)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["code"], 0)
        self.assertEqual(json_response["data"], "")

        time.sleep(10)

        response = self.client.get(url_for('main.status'), json={"name" : "test-task3", }, follow_redirects=True)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["status"], "Failed")

    def test_task_timeout(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task4",
            "commandLine": "sleep 100",
            "timeout": "5",
        })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["code"], 0)

        time.sleep(15)

        response = self.client.get(url_for('main.status'), json={"name" : "test-task4", })
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["status"], "Failed")

    def test_task_on_load_packagepath_with_outputfile(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task5",
            "commandLine": "python /home/test5.py",
            "packagePath": "/home/pkusei/osprac/hw6/slave/data/testdir",
            "outputPath": "data/output.txt",
        })

        time.sleep(10)

        outputpath = '/home/pkusei/osprac/hw6/slave/data/output.txt'
        self.assertTrue(os.path.exists(outputpath))
        with open(outputpath) as f:
            self.assertEqual(f.read().strip(),"ok for test5")

    def test_task_run_on_user_define_image(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task6",
            "commandLine": "cat /home/test6.txt",
            "outputPath": "data/output.txt",
            "image": "my-test-image",
        })
        
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response["code"], 0)

        """
        time.sleep(10)

        outputpath = '/home/pkusei/osprac/hw6/slave/data/output.txt'
        self.assertTrue(os.path.exists(outputpath))
        with open(outputpath) as f:
            self.assertEqual(f.read().strip(),"Hello!")
        """

    


        
        

