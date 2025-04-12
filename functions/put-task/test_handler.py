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

    from handler import put, check_payload


class TestPutHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_check_payload_valid(self):
        payload = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "medium",
            "status": "in-progress"
        }
        result = check_payload(payload)
        self.assertTrue(result)

    def test_check_payload_invalid(self):
        # Various invalid payload tests
        payloads = [
            # Missing required field
            {
                "title": "Updated Title",
                "description": "Updated Description",
                "priority": "medium"
            },
            # Empty title
            {
                "title": "",
                "description": "Updated Description",
                "priority": "medium",
                "status": "in-progress"
            },
            # Invalid priority
            {
                "title": "Updated Title",
                "description": "Updated Description",
                "priority": "extreme",
                "status": "in-progress"
            },
            # Invalid status
            {
                "title": "Updated Title",
                "description": "Updated Description",
                "priority": "medium",
                "status": "pending"
            }
        ]

        for payload in payloads:
            result = check_payload(payload)
            self.assertFalse(result)

    def test_successful_update(self):
        payload = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "medium",
            "status": "in-progress"
        }

        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = {
                "_id": "task-123",
                "title": "Original Title",
                "description": "Original Description",
                "priority": "low",
                "status": "todo"
            }

            mock_update_result = MagicMock()
            mock_update_result.modified_count = 1
            mock_collection.update_one.return_value = mock_update_result

            event = {
                "pathParameters": {"task_id": "task-123"},
                "body": json.dumps(payload)
            }
            context = {}
            response = put(event, context)

            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            response_body = json.loads(response['body'])
            self.assertEqual(response_body['modified_count'], 1)
            self.assertEqual(response_body['task_id'], "task-123")

    def test_task_not_found(self):
        payload = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "medium",
            "status": "in-progress"
        }

        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = None

            event = {
                "pathParameters": {"task_id": "non-existent-task"},
                "body": json.dumps(payload)
            }
            context = {}
            response = put(event, context)

            self.assertEqual(response['statusCode'], 404)
            self.assertIn('Task not found', response['body'])

    def test_missing_request_body(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            event = {
                "pathParameters": {"task_id": "task-123"}
                # No body field
            }
            context = {}
            response = put(event, context)

            self.assertEqual(response['statusCode'], 400)
            self.assertIn('Bad Request', response['body'])

    def test_invalid_payload(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            event = {
                "pathParameters": {"task_id": "task-123"},
                # Missing required fields
                "body": json.dumps({"title": "Only Title"})
            }
            context = {}
            response = put(event, context)

            self.assertEqual(response['statusCode'], 400)
            self.assertIn('Bad Request', response['body'])

    def test_client_not_initialized(self):
        payload = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "medium",
            "status": "in-progress"
        }

        with patch('handler.client', None):
            event = {
                "pathParameters": {"task_id": "task-123"},
                "body": json.dumps(payload)
            }
            context = {}
            response = put(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Internal server error', response['body'])

    def test_database_error_during_update(self):
        payload = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "medium",
            "status": "in-progress"
        }

        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = {
                "_id": "task-123",
                "title": "Original Title",
                "description": "Original Description",
                "priority": "low",
                "status": "todo"
            }

            mock_collection.update_one.side_effect = Exception(
                "Database update error")

            event = {
                "pathParameters": {"task_id": "task-123"},
                "body": json.dumps(payload)
            }
            context = {}
            response = put(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Internal server error', response['body'])


if __name__ == '__main__':
    unittest.main()
