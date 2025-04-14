
import json
from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import (
    users_collection,
    movies_collection,
    continueWatching,
)

async def continueWatchingHistorySaving(request:Request):
    try:
        body = await request.body
        moviesId = body.get("moviesId")
        currentShortsId = body.get("currentShortsId")
        timestamp = body.get("timestamp")
        userId = request.userId

        if not userId:
            return JSONResponse({"msg": "userId is missing"}, status=400)
        elif not moviesId:
            return JSONResponse({"msg": "moviesId is missing"}, status=400)
        elif not currentShortsId:
            return JSONResponse({"msg": "currentShortsId is missing"}, status=400)
        elif not timestamp:
            return JSONResponse({"msg": "timestamp is missing"}, status=400)

        userDetails = users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"msg": "no user found"}, status=400)
        # if(not ObjectId())
        
        # if not isinstance(currentShortsId):
        #     currentShortsId=ObjectId(currentShortsId)
        movieDetails = movies_collection.find_one(
            {
                "_id": ObjectId(moviesId),
                "shorts": currentShortsId,
                # Directly match the ObjectId in the array
            }
        )
        print(movieDetails)
        if not movieDetails:
            return JSONResponse(
                {"msg": "no movie found or short not found"}, status=400
            )

        result = continueWatching.update_one(
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
                {"msg": "History inserted successFully..."}, status=200
            )
        elif result.modified_count > 0:
            return JSONResponse(
                {"msg": "History updated successfully..."}, status=200
            )
        else:
            return JSONResponse(
                {
                    "msg": "No changes were necessary; history is up-to-date. (Document existed but no modification occurred (possibly already updated with the same values))"
                },
                status=200,
            )
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status=400)