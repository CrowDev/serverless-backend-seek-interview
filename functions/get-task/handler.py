import os
import json
import logging
from pymongo import MongoClient
from bson.json_util import dumps

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    client = MongoClient(host=os.environ.get('MONGO_HOST'))
    client.admin.command('ping')
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    client = None

"""
    GET / - Retrieve all tasks

    Response Codes:
    - 200: Success, returns array of tasks
    - 404: No tasks found
    - 500: Server error (DB connection issues, etc)

    Returns:
    - JSON response with status code, headers and body
"""


def get(event, context):
    try:
        if client is None:
            logger.error("MongoDB client is not initialized")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'Internal server error'})
            }

        db = client.tasks_dashboard
        tasks = db.tasks
        tasks_list = list(tasks.find())
        if not tasks_list:
            logger.info("No tasks found")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'No tasks found'})
            }

        result = dumps(tasks_list)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': result
        }
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
