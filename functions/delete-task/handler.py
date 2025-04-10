import os
import json
from pymongo import MongoClient

client = MongoClient(host=os.environ.get('MONGO_HOST'))


def delete(event, context):
    task_id = event['pathParameters']['task_id']
    db = client.tasks_dashboard
    tasks = db.tasks
    result = tasks.delete_one({"_id": task_id})
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Task deleted!',
            'task_id': result.deleted_count
        })
    }
