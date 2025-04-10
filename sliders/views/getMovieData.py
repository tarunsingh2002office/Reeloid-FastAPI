from django.http import JsonResponse
from streaming_app_backend.mongo_client import movies_collection
from django.views.decorators.csrf import csrf_exempt
from streaming_app_backend.mongo_client import (
    movies_collection,
    shorts_collection,
    users_collection,
    videoPurchasedLogs,
    userReactionLogs,
)
import json
from bson import ObjectId
from users.views.checkSignedVideo import checkSignedVideo
from helper_function.checkPurchasedVideoData import checkPurchasedVideoData


@csrf_exempt
def getMovieData(request):
    if request.method == "POST":
        userId = request.userId
        try:
            bodyData = json.loads(request.body)

            movieID = bodyData.get("movieID")

            data = movies_collection.find_one(
                {"_id": ObjectId(movieID), "visible": True}
            )

            shorts = []

            if data:
                # Increment the 'views' field by 1
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
                )  # later we will change this to fileLocation because now i am taking direct video serving link and for shorts we are using localhost:8765 so later we will replace localhost with direct link
                # print(trailerUrl)
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

                            # we will check if the current fetched video is present in purchase log history or not if not then we  will deduct a point else we we will not

                            # if userPoints > videosPointsSpend or purchased:
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
                                
                                # Convert ObjectId fields to strings in shortsData
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

            return JsonResponse({"shortsData": shorts}, status=200)
        except Exception as err:

            return JsonResponse(
                {"msg": "something went wrong", err: str(err)}, status=400
            )
    # moviesData = movies_collection.find_one({_id: request.params.id})
    return JsonResponse({"msg": "method not allowed"}, status=500)
