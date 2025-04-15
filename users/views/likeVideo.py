import json
from bson import ObjectId
from fastapi import Request,Depends, Body
from fastapi.responses import JSONResponse
from core.database import (
    users_collection,
    userReactionLogs,
    shorts_collection,
)
from helper_function.apis_requests import get_current_user

async def likeVideo(request:Request,token: str = Depends(get_current_user),body: dict = Body(
        example={
            "shortsId": "1234",
            "reactionType": "Laugh"
        },
    )):
        body = await request.json()
        userId = request.state.userId
        shortsId = body.get("shortsId")
        reactionType = body.get("reactionType")
        if not shortsId:
            return JSONResponse({"msg": "Mandatory fields are not present"}, status_code=400)
        if not reactionType:
            return JSONResponse({"msg": "please provide  valid fields"}, status_code=400)
        if (
            reactionType != "Laugh"
            and reactionType != "Heart"
            and reactionType != "Sad"
            and reactionType != "Clap"
            and reactionType != "Ovation"
        ):
            return JSONResponse({"msg": "invalid type of reaction"}, status_code=400)

        try:
            if not ObjectId.is_valid(shortsId):
                return JSONResponse({"msg": "Please provide a valid shorts ID"})
            shorts = shorts_collection.find_one({"_id": ObjectId(shortsId)})
            if not shorts:
                return JSONResponse({"msg": "shorts not found"}, status_code=404)

            user = users_collection.find_one({"_id": ObjectId(userId)})
            if not user:
                return JSONResponse({"msg": "User not found"}, status_code=404)

            usersReactionResponse = userReactionLogs.find_one_and_update(
                {"shortsId": ObjectId(shortsId), "userId": ObjectId(userId)},
                {"$set": {"reaction": reactionType}},
                upsert=True,  
                return_document=True,
            )
            if not usersReactionResponse:
                return JSONResponse(
                    {"msg": "something went wrong while saving reaction"},
                    status_code=400,
                )

            return JSONResponse(
                {"msg": f"You Gave a {reactionType} Reaction to This Video"}, status_code=200
            )

        except Exception as err:
            return JSONResponse({"msg": str(err)}, status_code=400)
