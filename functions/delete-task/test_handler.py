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

    from handler import delete


class TestDeleteHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_successful_delete(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = {
                "_id": "task-123",
                "title": "Task to Delete",
                "description": "This task will be deleted",
                "priority": "low",
                "status": "todo"
            }

            mock_delete_result = MagicMock()
            mock_delete_result.deleted_count = 1
            mock_collection.delete_one.return_value = mock_delete_result

            event = {
                "pathParameters": {"task_id": "task-123"}
            }
            context = {}
            response = delete(event, context)

            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            response_body = json.loads(response['body'])
            self.assertEqual(response_body['task_id'], "task-123")

    def test_task_not_found(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = None

            event = {
                "pathParameters": {"task_id": "non-existent-task"}
            }
            context = {}
            response = delete(event, context)

            self.assertEqual(response['statusCode'], 404)
            self.assertIn('Task not found', response['body'])

    def test_delete_failure(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = {
                "_id": "task-123",
                "title": "Task to Delete",
                "description": "This task will be deleted",
                "priority": "low",
                "status": "todo"
            }

            mock_delete_result = MagicMock()
            mock_delete_result.deleted_count = 0
            mock_collection.delete_one.return_value = mock_delete_result

            event = {
                "pathParameters": {"task_id": "task-123"}
            }
            context = {}
            response = delete(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Failed to delete task', response['body'])

    def test_client_not_initialized(self):
        with patch('handler.client', None):
            event = {
                "pathParameters": {"task_id": "task-123"}
            }
            context = {}
            response = delete(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Internal server error', response['body'])

    def test_missing_path_parameters(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            event = {}  # No pathParameters
            context = {}

            response = delete(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Internal server error', response['body'])

    def test_database_error_during_deletion(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find_one.return_value = {
                "_id": "task-123",
                "title": "Task to Delete",
                "description": "This task will be deleted",
                "priority": "low",
                "status": "todo"
            }

            mock_collection.delete_one.side_effect = Exception(
                "Database deletion error")

            event = {
                "pathParameters": {"task_id": "task-123"}
            }
            context = {}
            response = delete(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Internal server error', response['body'])


if __name__ == '__main__':
    unittest.main()
