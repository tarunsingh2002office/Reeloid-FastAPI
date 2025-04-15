from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import (
    userReactionLogs,
    users_collection,
)
from fastapi import Depends,Request
from helper_function.apis_requests import get_current_user

async def unlikeVideo(request:Request, token: str = Depends(get_current_user)):
    
    body = await request.json()
    userId = request.state.userId
    shortsId = body.get("shortsId")
    if not shortsId:
        return JSONResponse({"msg": "Mandatory fields are not present"}, status_code=400)
    try:
        if not ObjectId.is_valid(shortsId):
            return JSONResponse({"msg": "Please provide a valid shorts ID"})

        user = users_collection.find_one({"_id": ObjectId(userId)})
        if not user:
            return JSONResponse({"msg": "User not found"}, status_code=404)

        usersReactionResponse = userReactionLogs.find_one_and_delete(
            {"shortsId": ObjectId(shortsId), "userId": ObjectId(userId)},
        )
        if not usersReactionResponse:
            return JSONResponse(
                {"msg": "something went wrong while saving reaction"},
                status_code=400,
            )
        return JSONResponse({"msg": "You Unliked A video"}, status_code=200)

    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)