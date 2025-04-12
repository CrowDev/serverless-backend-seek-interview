import os
import json
import logging
from pymongo import MongoClient

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
    PUT /edit/{task_id} - Update an existing task

    Path Parameters:
    - task_id: string (required) - ID of the task to update

    Request Body (at least one of these fields must be provided):
    - title: string - Task title
    - description: string - Task description
    - priority: number - Task priority (high, medium, low)
    - status: string - Task status (todo, in-review, in-progress, done, blocked)

    Response Codes:
    - 200: Updated successfully
    - 400: Bad request (validation errors)
    - 404: Task not found
    - 500: Server error

    Returns:
    - JSON response with status code, headers and body
"""


def put(event, context):
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

        task_id = event['pathParameters']['task_id']
        db = client.tasks_dashboard
        tasks = db.tasks

        task = tasks.find_one({"_id": task_id})
        if not task:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Task not found"})
            }

        valid_fields = ["title", "description", "priority", "status"]
        update_data = {key: value for key,
                       value in payload.items() if key in valid_fields}
        result = tasks.update_one(
            {"_id": task_id},
            {"$set": update_data}
        )
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'modified_count': result.modified_count,
                'task_id': task_id
            })
        }

    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


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
