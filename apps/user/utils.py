import datetime
import json
import random


def generate_reset_code():
    return random.randint(1000, 9999)


def datetime_serializer(obj):
    datetime_str = str(obj)
    return json.dumps({'date': datetime_str})


def datetime_deserializer(obj):
    loaded_json = json.loads(obj)
    return datetime.datetime.strptime(
        loaded_json['date'], '%Y-%m-%d %H:%M:%S.%f'
    )
