import json
from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection

async def markAsBookMark(request:Request):
    body = await request.body
    userId = request.state.userId
    shortsId = body.get("shortsId")

    if not shortsId:
        return JSONResponse({"msg": "Important field is missing"}, status=400)

    if not ObjectId.is_valid(shortsId):
        return JSONResponse({"msg": "Shorts ID is not valid"}, status=400)

    try:
        user = users_collection.find_one({"_id": ObjectId(userId)})
        if not user:
            return JSONResponse({"msg": "User not found"}, status=404)

        if "BookMark" in user and shortsId in user["BookMark"]:
            # Remove the shortsId from BookMark if already present
            users_collection.update_one(
                {"_id": ObjectId(userId)}, {"$pull": {"BookMark": shortsId}}
            )
            return JSONResponse({"msg": "Video removed from bookmarks"}, status=200)
        else:
            # Add the shortsId to BookMark if not present
            users_collection.update_one(
                {"_id": ObjectId(userId)}, {"$push": {"BookMark": shortsId}}
            )
            return JSONResponse({"msg": "Video bookmarked"}, status=200)

    except Exception as err:
        return JSONResponse({"msg": str(err)}, status=400)