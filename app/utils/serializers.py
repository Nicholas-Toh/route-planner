from sqlalchemy import inspect
import json

def table_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

def collection_to_dict(list):
    return [table_to_dict(s) for s in list]
    
def serialize_collection(list):
    return json.dumps(collection_to_dict(list), default=str)

def is_true(str):
    if str:
        if str.lower() in ['true', '1']:
            return True
    
    return False