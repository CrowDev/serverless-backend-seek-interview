import os
import json
import uuid
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient(host=os.environ.get('MONGO_HOST'))


def post(event, context):
    payload = json.loads(event['body'])
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
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Task posted!',
            'task_id': dumps(task_id.inserted_id),
        })
    }
