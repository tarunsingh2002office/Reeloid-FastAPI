import json
from bson import ObjectId
from fastapi import Depends
from fastapi.responses import JSONResponse
from core.database import (
    movies_collection,
    shorts_collection,
    users_collection,
    userReactionLogs,
)
from helper_function.checkSignedVideo import checkSignedVideo
from helper_function.checkPurchasedVideoData import checkPurchasedVideoData
from core.apis_requests import get_current_user, GetMovieDataRequest
async def getMovieData(request:GetMovieDataRequest, token: str = Depends(get_current_user)):
    userId = request.state.userId
    try:
        bodyData = request.model_dump()

        movieID = bodyData.get("movieID")

        data = movies_collection.find_one(
            {"_id": ObjectId(movieID), "visible": True}
        )

        shorts = []

        if data:
            movies_collection.update_one(
                {"_id": ObjectId(movieID)}, {"$inc": {"views": 1}}
            )

            trailerUrl = data.get("trailerUrl")
            low = data.get("low")
            medium = data.get("medium")
            high = data.get("high")
            shorts.append(
                {
                    "trailerUrl": checkSignedVideo(trailerUrl),
                    "low": checkSignedVideo(low),
                    "medium": checkSignedVideo(medium),
                    "high": checkSignedVideo(high),
                }
            )  
            if data.get("shorts"):
                user = users_collection.find_one(
                    {"_id": ObjectId(userId)}, {"allocatedPoints": 1}
                )

                for currentShortsID in data["shorts"]:
                    if currentShortsID == "Ads":
                        shorts.append({"type": "Promotional Ads"})
                    else:
                        if isinstance(currentShortsID, str):
                            currentShortsID = ObjectId(currentShortsID)

                        shortsData = shorts_collection.find_one(
                            {"_id": currentShortsID, "visible": True},
                            {"genre": 0, "language": 0},
                        )

                        if shortsData:
                            purchased = checkPurchasedVideoData(
                                currentShortsID, userId
                            )
                            
                            shortsReaction = userReactionLogs.find_one(
                                {
                                    "shortsId": currentShortsID,
                                    "userId": ObjectId(userId),
                                },
                                {
                                    "reaction": 1,
                                },
                            )
                            
                            shortsData["_id"] = str(shortsData["_id"])
                            shortsData["low"] = checkSignedVideo(
                                shortsData.get("low")
                            )
                            shortsData["medium"] = (
                                purchased
                                and checkSignedVideo(shortsData.get("medium"))
                                or "Not Purchased"
                            )
                            shortsData["high"] = (
                                purchased
                                and checkSignedVideo(shortsData.get("high"))
                                or "Not Purchased"
                            )
                            shortsData["reaction"] = (
                                shortsReaction.get("reaction")
                                if shortsReaction
                                else "none"
                            )
                            shorts.append(shortsData)

        return JSONResponse({"shortsData": shorts}, status_code=200)
    except Exception as err:

        return JSONResponse(
            {"msg": "something went wrong", err: str(err)}, status_code=400
        )
