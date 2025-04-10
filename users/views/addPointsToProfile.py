from streaming_app_backend.mongo_client import users_collection
from bson import ObjectId


def addPointsToProfile(userId, allotedPoints, session):

    try:
        if not session:
            raise ValueError("Please provide session for secure transaction")
        # Perform the update with increment and create if not exist (upsert)
        updateUser = users_collection.update_one(
            {"_id": ObjectId(userId)},  # Ensure userId is an ObjectId
            {
                "$inc": {"allocatedPoints": int(allotedPoints)}
            },  # Increment or initialize allocatedPoints
            upsert=True,  # Insert a new document if none matches
            session=session,
        )

        # Check if the update was successful
        if updateUser.acknowledged:

            return {"success": True, "data": updateUser.raw_result}

        else:

            raise ValueError("Failed to update points.")

            # return {"success": False, "error": "Failed to update points."}
    except Exception as e:
        # if session:
        #     session.abort_transaction()

        raise ValueError(str(e))
