import unittest
import json

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
        self.assertTrue('Homepage' in response.get_data(as_text=True))
    
    def test_task(self):
        response = self.client.get(url_for('main.submit'), json={
            "name" : "test-task1",
            "commandLine": "sleep 10 && echo 10",
            "outputPath": "data/output.txt",
            "logPath": "data/log.txt",
            "maxRetryCount": "0", 
            "timeout": "21600",
            "imageId": "my-ubuntu-16.04",       
        })

        json_response = json.loads(response.get_data(as_text=True))

        self.assertEqual(json_response["code"], 0)
