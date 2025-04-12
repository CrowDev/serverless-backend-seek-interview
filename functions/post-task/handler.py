import os
import json
import uuid
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
    POST /create - Create a new task

    Request Body:
    - title: string (required) - Task title
    - description: string (required) - Task description
    - priority: number (required) - Task priority (high, medium, low)
    - status: string (required) - Task status (todo, in-progress, in-review, done, blocked)

    Response Codes:
    - 201: Created successfully
    - 400: Bad request (validation errors)
    - 500: Server error

    Returns:
    - JSON response with status code, headers and body
"""


def post(event, context):
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
        if "body" not in event:
            logger.error("No body in the event")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'Bad Request'})
            }
        payload = json.loads(event['body'])
        valid_paylod = check_payload(payload)
        if not valid_paylod:
            logger.error("Invalid payload")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': 'Bad Request'})
            }
        db = client.tasks_dashboard
        tasks = db.tasks
        task_id = tasks.insert_one({
            "_id": str(uuid.uuid4()),
            "title": payload["title"],
            "description": payload["description"],
            "priority": payload["priority"],
            "status": payload["status"]
        })

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'task_id': dumps(task_id.inserted_id),
            })
        }
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


"""
    Validates task data for creation

    Args:
        payload (dict): Task data to validate

    Returns:
        boolean
"""


def check_payload(payload):
    if not payload:
        return False
    required_fields = ["title", "description", "priority", "status"]
    for field in required_fields:
        if field not in payload:
            return False
    if len(payload["title"]) == 0:
        return False
    if len(payload["description"]) == 0:
        return False
    valid_priorities = ["low", "medium", "high"]
    if payload["priority"] not in valid_priorities:
        return False
    valid_statuses = ["todo", "in-progress", "in-review", "done", "blocked"]
    if payload["status"] not in valid_statuses:
        return False
    return True
