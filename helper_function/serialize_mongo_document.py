from bson import ObjectId
from datetime import datetime

async def serialize_document(document):
    if isinstance(document, dict):
        return {key: await serialize_document(value) for key, value in document.items()}
    elif isinstance(document, list):
        return [await serialize_document(item) for item in document]
    elif isinstance(document, ObjectId):
        return str(document)
    elif isinstance(document, datetime):
        return document.isoformat()
    else:
        return document