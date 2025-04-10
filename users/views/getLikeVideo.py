from django.http import JsonResponse
import json
from streaming_app_backend.mongo_client import users_collection, shorts_collection
from bson import ObjectId


def getLikedVideo(request):
    body = json.loads(request.body)
    userId = request.userId
    # shortsId = body.get("shortsId")
    user = users_collection.find_one(
        {"_id": ObjectId(userId)},
    )
    if not user:
        return JsonResponse({"msg": "no user found"}, status=400)
    try:

        if user and user["LikedVideos"]:

            LikedVideosData = []
            for shortsId in user["LikedVideos"]:
                
                shortsData = shorts_collection.find_one(
                    {
                        "_id": ObjectId(shortsId),
                    },
                    {"genre": 0, "language": 0},
                )
               
                if shortsData:
                    shortsData["_id"] = str(shortsData["_id"])
                    LikedVideosData.append(shortsData)

            return JsonResponse(
                {"msg": "Liked Videos data is here", "LikedVideos": LikedVideosData},
                status=200,
            )
        else:
            return JsonResponse(
                {"msg": "Liked Videos data not found", "LikedVideos": []}, status=200
            )

    except:
        return JsonResponse({"msg": "something went wrong"}, status=500)
