import os
import json
from pymongo import MongoClient
# import uuid
# from bson.json_util import dumps

client = MongoClient(host=os.environ.get('MONGO_HOST'))


def put(event, context):
    payload = json.loads(event['body'])
    task_id = event['pathParameters']['task_id']
    db = client.tasks_dashboard
    tasks = db.tasks

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
            'message': 'Task updated!',
            'task_id': result.modified_count
        })
    }
