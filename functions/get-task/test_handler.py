import unittest
from unittest.mock import patch, MagicMock
import os
import logging

logging.disable(logging.CRITICAL)

os.environ['MONGO_HOST'] = 'mongodb://mockhost:27017'

with patch('pymongo.MongoClient') as mock_mongo:
    mock_client = MagicMock()
    mock_mongo.return_value = mock_client

    from handler import get


class TestGetHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_successful_get_tasks(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_tasks = [
                {"_id": "1", "title": "Task 1", "description": "Description 1",
                    "priority": "high", "status": "todo"},
                {"_id": "2", "title": "Task 2", "description": "Description 2",
                    "priority": "medium", "status": "in-progress"}
            ]

            mock_collection.find.return_value = mock_tasks

            event = {}
            context = {}
            response = get(event, context)

            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            self.assertIn('Task 1', response['body'])
            self.assertIn('Task 2', response['body'])

    def test_no_tasks_found(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find.return_value = []

            event = {}
            context = {}
            response = get(event, context)

            self.assertEqual(response['statusCode'], 404)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            self.assertIn('No tasks found', response['body'])

    def test_client_not_initialized(self):
        with patch('handler.client', None):
            event = {}
            context = {}
            response = get(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            self.assertIn('Internal server error', response['body'])

    def test_database_error_during_query(self):
        with patch('handler.client') as mock_client:
            mock_db = MagicMock()
            mock_client.tasks_dashboard = mock_db

            mock_collection = MagicMock()
            mock_db.tasks = mock_collection

            mock_collection.find.side_effect = Exception(
                "Database query error")

            event = {}
            context = {}
            response = get(event, context)

            self.assertEqual(response['statusCode'], 500)
            self.assertEqual(response['headers']
                             ['Content-Type'], 'application/json')
            self.assertIn('Internal server error', response['body'])


if __name__ == '__main__':
    unittest.main()
