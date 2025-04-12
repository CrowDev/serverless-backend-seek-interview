import unittest
from unittest.mock import patch, MagicMock
import json
import os
import logging

logging.disable(logging.CRITICAL)

os.environ['MONGO_HOST'] = 'mongodb://mockhost:27017'

with patch('pymongo.MongoClient') as mock_mongo:
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client

    from handler import post, check_payload


class TestPostHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_check_payload_valid(self):
        payload = {
            "title": "Task Title",
            "description": "Task Description",
            "priority": "high",
            "status": "todo"
        }
        result = check_payload(payload)
        self.assertTrue(result)

    def test_check_payload_invalid_missing_field(self):
        payload = {
            "title": "Task Title",
            "description": "Task Description",
            "priority": "high"
            # Missing status
        }
        result = check_payload(payload)
        self.assertFalse(result)

    def test_check_payload_invalid_empty_title(self):
        payload = {
            "title": "",
            "description": "Task Description",
            "priority": "high",
            "status": "todo"
        }
        result = check_payload(payload)
        self.assertFalse(result)

    def test_check_payload_invalid_priority(self):
        payload = {
            "title": "Task Title",
            "description": "Task Description",
            "priority": "invalid",
            "status": "todo"
        }
        result = check_payload(payload)
        self.assertFalse(result)

    def test_check_payload_invalid_status(self):
        payload = {
            "title": "Task Title",
            "description": "Task Description",
            "priority": "high",
            "status": "invalid"
        }
        result = check_payload(payload)
        self.assertFalse(result)

    def test_successful_post_task(self):
        payload = {
            "title": "New Task",
            "description": "Test Description",
            "priority": "high",
            "status": "todo"
        }

        with patch('handler.client') as mock_client, \
                patch('handler.uuid') as mock_uuid:

            # Mock UUID generation
            mock_uuid.uuid4.return_value = "mocked-uuid"

            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_insert_result = MagicMock()
            mock_insert_result.inserted_id = "mocked-uuid"
            mock_collection.insert_one.return_value = mock_insert_result

            event = {
                "body": json.dumps(payload)
            }
            context = {}
            response = post(event, context)

            self.assertEqual(response['statusCode'], 201)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            self.assertIn('task_id', response['body'])

    def test_missing_request_body(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            event = {}  # No body field
            context = {}
            response = post(event, context)

            self.assertEqual(response['statusCode'], 400)
            self.assertIn('Bad Request', response['body'])

    def test_invalid_payload(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            event = {
                # Missing required fields
                "body": json.dumps({"title": "Only Title"})
            }
            context = {}
            response = post(event, context)

            self.assertEqual(response['statusCode'], 400)
            self.assertIn('Bad Request', response['body'])

    def test_client_not_initialized(self):
        payload = {
            "title": "New Task",
            "description": "Test Description",
            "priority": "high",
            "status": "todo"
        }

        with patch('handler.client', None):
            event = {
                "body": json.dumps(payload)
            }
            context = {}
            response = post(event, context)

            self.assertIn('Internal server error', response['body'])

    def test_database_error_during_insert(self):
        payload = {
            "title": "New Task",
            "description": "Test Description",
            "priority": "high",
            "status": "todo"
        }

        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.insert_one.side_effect = Exception(
                "Database insert error")

            event = {
                "body": json.dumps(payload)
            }
            context = {}
            response = post(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Internal server error', response['body'])


if __name__ == '__main__':
    unittest.main()
