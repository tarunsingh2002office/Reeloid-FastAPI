
import json
from bson import ObjectId
from fastapi import Depends,Request,Body
from fastapi.responses import JSONResponse
from core.database import (
    users_collection,
    movies_collection,
    continueWatching,
)
from helper_function.apis_requests import get_current_user
async def continueWatchingHistorySaving(request:Request,token: str = Depends(get_current_user),body: dict = Body(
        example={
            "moviesId": "1234",
            "currentShortsId": "1234",
            "timestamp": "1234",
        }
    )):
    try:
        body = await request.json()
        moviesId = body.get("moviesId")
        currentShortsId = body.get("currentShortsId")
        timestamp = body.get("timestamp")
        userId = request.state.userId

        if not userId:
            return JSONResponse({"msg": "userId is missing"}, status_code=400)
        elif not moviesId:
            return JSONResponse({"msg": "moviesId is missing"}, status_code=400)
        elif not currentShortsId:
            return JSONResponse({"msg": "currentShortsId is missing"}, status_code=400)
        elif not timestamp:
            return JSONResponse({"msg": "timestamp is missing"}, status_code=400)

        userDetails = await users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"msg": "no user found"}, status_code=400)

        movieDetails = await movies_collection.find_one(
            {
                "_id": ObjectId(moviesId),
                "shorts": ObjectId(currentShortsId),
            }
        )
        if not movieDetails:
            return JSONResponse(
                {"msg": "no movie found or short not found"}, status_code=400
            )

        result = await continueWatching.update_one(
            {"userId": userId, "moviesId": moviesId},
            {
                "$set": {
                    "currentShortsId": currentShortsId,
                    "timestamp": timestamp,
                }
            },
            upsert=True,
        )
        if result.matched_count == 0:
            return JSONResponse(
                {"msg": "History inserted successFully..."}, status_code=200
            )
        elif result.modified_count > 0:
            return JSONResponse(
                {"msg": "History updated successfully..."}, status_code=200
            )
        else:
            return JSONResponse(
                {
                    "msg": "No changes were necessary; history is up-to-date. (Document existed but no modification occurred (possibly already updated with the same values))"
                },
                status_code=200,
            )
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)