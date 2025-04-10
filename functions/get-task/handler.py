import os
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient(host=os.environ.get('MONGO_HOST'))


def get(event, context):
    db = client.tasks_dashboard
    tasks = db.tasks
    tasks_list = list(tasks.find())
    result = dumps(tasks_list)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': result
    }
