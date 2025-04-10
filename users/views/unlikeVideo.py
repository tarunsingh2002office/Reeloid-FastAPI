from django.http import JsonResponse
import json
from bson import ObjectId
from streaming_app_backend.mongo_client import (
    shorts_collection,
    userReactionLogs,
    users_collection,
)
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to unlike the videos. The request should contain the user token in headers and shortsId in body.",
    manual_parameters=[
        openapi.Parameter(
            "token",  # The name of the header parameter
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",  # Description of the token
            type=openapi.TYPE_STRING,  # Specifies that the type is a string
            required=True,  # Marks the token as required
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "shortsId": openapi.Schema(
                type=openapi.TYPE_STRING, description="User email"
            ),
        },
        required=["shortsId"],
    ),
    responses={
        200: openapi.Response(description="video unliked successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["POST"])
def unlikeVideo(request):
    if request.method == "POST":
        body = json.loads(request.body)
        userId = request.userId
        shortsId = body.get("shortsId")

        if not shortsId:
            return JsonResponse({"msg": "Mandatory fields are not present"}, status=400)

        # heart
        # laugh
        # sad
        # Ovation
        # clap

        try:
            if not ObjectId.is_valid(shortsId):
                return JsonResponse({"msg": "Please provide a valid shorts ID"})

            user = users_collection.find_one({"_id": ObjectId(userId)})
            if not user:
                return JsonResponse({"msg": "User not found"}, status=404)

            usersReactionResponse = userReactionLogs.find_one_and_delete(
                {"shortsId": ObjectId(shortsId), "userId": ObjectId(userId)},
            )
            if not usersReactionResponse:
                return JsonResponse(
                    {"msg": "something went wrong while saving reaction"},
                    status=400,
                )

            # if "LikedVideos" in user and shortsId in user["LikedVideos"]:
            #     # Remove the shortsId if already present
            #     users_collection.update_one(
            #         {"_id": ObjectId(userId)}, {"$pull": {"LikedVideos": shortsId}}
            #     )
            #     return JsonResponse({"msg": "Video unliked"}, status=200)
            # else:
            #     # Add the shortsId if not present
            #     users_collection.update_one(
            #         {"_id": ObjectId(userId)}, {"$push": {"LikedVideos": shortsId}}
            #     )
            return JsonResponse({"msg": "You Unliked A video"}, status=200)

        except Exception as err:
            return JsonResponse({"msg": str(err)}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)
