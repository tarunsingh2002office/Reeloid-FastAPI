from django.http import JsonResponse
import json
from streaming_app_backend.mongo_client import users_collection
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to bookmark the current video. The request should contain the user token in headers and an array of selected genres in the body.",
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
                type=openapi.TYPE_STRING,
                description="current shortsId which you want to bookmark",
            ),
        },
        required=["shortsId"],
    ),
    responses={
        200: openapi.Response(description="shorts bookmarked successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def markAsBookMark(request):
    if request.method == "POST":
        body = json.loads(request.body)
        userId = request.userId
        shortsId = body.get("shortsId")

        if not shortsId:
            return JsonResponse({"msg": "Important field is missing"}, status=400)

        if not ObjectId.is_valid(shortsId):
            return JsonResponse({"msg": "Shorts ID is not valid"}, status=400)

        try:
            user = users_collection.find_one({"_id": ObjectId(userId)})
            if not user:
                return JsonResponse({"msg": "User not found"}, status=404)

            if "BookMark" in user and shortsId in user["BookMark"]:
                # Remove the shortsId from BookMark if already present
                users_collection.update_one(
                    {"_id": ObjectId(userId)}, {"$pull": {"BookMark": shortsId}}
                )
                return JsonResponse({"msg": "Video removed from bookmarks"}, status=200)
            else:
                # Add the shortsId to BookMark if not present
                users_collection.update_one(
                    {"_id": ObjectId(userId)}, {"$push": {"BookMark": shortsId}}
                )
                return JsonResponse({"msg": "Video bookmarked"}, status=200)

        except Exception as err:
            return JsonResponse({"msg": str(err)}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)
