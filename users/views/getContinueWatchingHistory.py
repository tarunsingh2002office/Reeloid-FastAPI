from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection,continueWatching

async def getUserWatchHistory(request:Request):
    try:
        userId = request.state.userId
        if not userId:
            return JSONResponse({"msg": "userId is missing"}, status=400)

        userDetails = users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"msg": "no user found"}, status=400)

        userWatchHistory = continueWatching.find(
            {"userId": userId}, {"_id":0}
        )

        if not userWatchHistory:
            return JSONResponse({"msg": "no watch history found"}, status=400)

        history = []
        for i in userWatchHistory:
            history.append(i)

        return JSONResponse({"userWatchHistory": history}, status=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status=500)
