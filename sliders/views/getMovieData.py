from bson import ObjectId
from fastapi import Depends, Request, Body
from fastapi.responses import JSONResponse
from core.database import (
    movies_collection,
    shorts_collection,
    users_collection,
    userReactionLogs
)
from helper_function.checkSignedVideo import checkSignedVideo
from helper_function.checkPurchasedVideoData import checkPurchasedVideoData
from helper_function.apis_requests import get_current_user
from helper_function.serialize_mongo_document import serialize_document

async def getMovieData(
    request: Request,
    token: str = Depends(get_current_user),
    body: dict = Body(example={"movieID": "1234"})
):
    userId = request.state.userId
    try:
        bodyData = await request.json()
        movieID = bodyData.get("movieID")

        # Aggregation pipeline to get movie and shorts
        movie = await movies_collection.aggregate([
            {"$match": {"_id": ObjectId(movieID), "visible": True}},
            {"$lookup": {
                "from": "shorts",
                "let": {"shortsList": "$shorts"},
                "pipeline": [
                    {"$match": {
                        "$expr": {
                            "$and": [
                                {"$in": ["$_id", "$$shortsList"]},
                                {"$eq": ["$visible", True]}
                            ]
                        }
                    }},
                    {"$project": {"genre": 0, "language": 0}}
                ],
                "as": "shortsData"
            }}
        ]).to_list(length=1)

        shorts = []

        if movie:
            data = await serialize_document(movie[0])
            await movies_collection.update_one(
                {"_id": ObjectId(movieID)},
                {"$inc": {"views": 1}}
            )

            trailerUrl = data.get("trailerUrl")
            low = data.get("low")
            medium = data.get("medium")
            high = data.get("high")

            shorts.append({
                "trailerUrl": await checkSignedVideo(trailerUrl),
                "low": await checkSignedVideo(low),
                "medium": await checkSignedVideo(medium),
                "high": await checkSignedVideo(high),
            })

            if data.get("shorts"):
                user = await users_collection.find_one(
                    {"_id": ObjectId(userId)},
                    {"allocatedPoints": 1}
                )

                for currentShortsID in data["shorts"]:
                    if currentShortsID == "Ads":
                        shorts.append({"type": "Promotional Ads"})
                    else:
                        if isinstance(currentShortsID, str):
                            currentShortsID = ObjectId(currentShortsID)

                        shortsData = next(
                            (short for short in data["shortsData"] if short["_id"] == str(currentShortsID) or short["_id"] == currentShortsID),
                            None
                        )

                        if shortsData:
                            shortsData = await serialize_document(shortsData)
                            purchased = await checkPurchasedVideoData(currentShortsID, userId)

                            shortsReaction = await userReactionLogs.find_one(
                                {
                                    "shortsId": currentShortsID,
                                    "userId": ObjectId(userId),
                                },
                                {"reaction": 1}
                            )

                            shortsData["_id"] = str(shortsData["_id"])
                            shortsData["low"] = await checkSignedVideo(shortsData.get("low"))
                            shortsData["medium"] = (
                                await checkSignedVideo(shortsData.get("medium"))
                                if purchased else "Not Purchased"
                            )
                            shortsData["high"] = (
                                await checkSignedVideo(shortsData.get("high"))
                                if purchased else "Not Purchased"
                            )
                            shortsData["reaction"] = (
                                shortsReaction.get("reaction") if shortsReaction else "none"
                            )
                            shorts.append(shortsData)

        return JSONResponse({"shortsData": shorts}, status_code=200)

    except Exception as err:
        return JSONResponse(
            {"msg": "something went wrong", "error": str(err)}, status_code=400
        )
