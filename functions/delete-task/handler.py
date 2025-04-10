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


def delete(event, context):
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
        result = tasks.delete_one({"_id": task_id})
        if result.deleted_count == 0:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Failed to delete task"})
            }
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'task_id': task_id
            })
        }

    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
