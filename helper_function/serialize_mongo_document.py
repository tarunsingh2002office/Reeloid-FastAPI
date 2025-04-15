from bson import ObjectId
from datetime import datetime

def serialize_document(document):
    """
    Recursively serializes a document by converting ObjectId and datetime objects to strings.
    Handles deeply nested dictionaries and lists.
    """
    if isinstance(document, dict):
        # Recursively process each key-value pair in the dictionary
        return {key: serialize_document(value) for key, value in document.items()}
    elif isinstance(document, list):
        # Recursively process each item in the list
        return [serialize_document(item) for item in document]
    elif isinstance(document, ObjectId):
        # Convert ObjectId to string
        return str(document)
    elif isinstance(document, datetime):
        # Convert datetime to ISO 8601 string
        return document.isoformat()
    else:
        # Return the value as is for other types
        return document