import json
from bson import ObjectId
from fastapi import Depends
from fastapi import Request,Body
from fastapi.responses import JSONResponse
from core.database import users_collection
from helper_function.apis_requests import get_current_user
async def markAsBookMark(request: Request, token: str = Depends(get_current_user),body: dict = Body(
        example={
            "shortsId": "1234"
        },
    )):
    body = await request.json()
    userId = request.state.userId
    shortsId = body.get("shortsId")

    if not shortsId:
        return JSONResponse({"msg": "Important field is missing"}, status_code=400)

    if not ObjectId.is_valid(shortsId):
        return JSONResponse({"msg": "Shorts ID is not valid"}, status_code=400)

    try:
        user = users_collection.find_one({"_id": ObjectId(userId)})
        if not user:
            return JSONResponse({"msg": "User not found"}, status_code=404)

        if "BookMark" in user and shortsId in user["BookMark"]:
            # Remove the shortsId from BookMark if already present
            users_collection.update_one(
                {"_id": ObjectId(userId)}, {"$pull": {"BookMark": shortsId}}
            )
            return JSONResponse({"msg": "Video removed from bookmarks"}, status_code=200)
        else:
            # Add the shortsId to BookMark if not present
            users_collection.update_one(
                {"_id": ObjectId(userId)}, {"$push": {"BookMark": shortsId}}
            )
            return JSONResponse({"msg": "Video bookmarked"}, status_code=200)

    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)