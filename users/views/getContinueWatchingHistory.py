from bson import ObjectId
from fastapi import Request
from fastapi import Depends
from fastapi.responses import JSONResponse
from core.database import users_collection, continueWatching, movies_collection
from helper_function.apis_requests import get_current_user


async def getUserWatchHistory(request:Request,token: str = Depends(get_current_user)):
    try:
        userId = request.state.userId
        if not userId:
            return JSONResponse({"msg": "userId is missing"}, status_code=400)

        userDetails = users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"msg": "no user found"}, status_code=400)

        userWatchHistory = continueWatching.find(
            {"userId": userId}, {"_id":0}
        )

        if not userWatchHistory:
            return JSONResponse({"msg": "no watch history found"}, status_code=400)

        history = []
        for watchHistory in userWatchHistory:
            watchHistory["movieDetails"] = movies_collection.find_one({"_id":ObjectId(watchHistory["moviesId"])},{"_id":0,"name":1,"fileLocation":1})
            history.append(watchHistory)

        return JSONResponse({"userWatchHistory": history}, status_code=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=500)
