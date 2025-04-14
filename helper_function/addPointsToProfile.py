from bson import ObjectId
from core.database import users_collection

def addPointsToProfile(userId, allotedPoints, session):
    try:
        if not session:
            raise ValueError("Please provide session for secure transaction")
        updateUser = users_collection.update_one(
            {"_id": ObjectId(userId)},  # Ensure userId is an ObjectId
            {
                "$inc": {"allocatedPoints": int(allotedPoints)}
            },  
            upsert=True,  # Insert a new document if none matches
            session=session,
        )

        if updateUser.acknowledged:

            return {"success": True, "data": updateUser.raw_result}

        else:

            raise ValueError("Failed to update points.")

    except Exception as e:
        raise ValueError(str(e))
