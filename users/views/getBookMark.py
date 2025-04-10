from django.http import JsonResponse
import json
from streaming_app_backend.mongo_client import users_collection, shorts_collection
from bson import ObjectId

from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API allows the user to fETCH ALL THE BOOKMARK. The request should contain the user token in headers .",
    manual_parameters=[
        openapi.Parameter(
            "token",  # The name of the header parameter
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",  # Description of the token
            type=openapi.TYPE_STRING,  # Specifies that the type is a string
            required=True,  # Marks the token as required
        )
    ],
    responses={
        200: openapi.Response(description="bokmarked fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["GET"])
@csrf_exempt
def getBookMark(request):
    if request.method == "GET":

        userId = request.userId
        
        user = users_collection.find_one(
            {"_id": ObjectId(userId)},
        )
        if not user:
            return JsonResponse({"msg": "no user found"}, status=400)
        try:

            if user and user.get("BookMark"):

                bookMarkData = []
                for shortsId in user["BookMark"]:

                    if shortsId:

                        if ObjectId.is_valid(shortsId):

                            shortsData = shorts_collection.find_one(
                                {
                                    "_id": ObjectId(shortsId),
                                },
                                {"genre": 0, "language": 0},
                            )

                            if shortsData:
                                shortsData["_id"] = str(shortsData["_id"])
                                bookMarkData.append(shortsData)

                return JsonResponse(
                    {"msg": "bookmarked data is here", "bookMarkData": bookMarkData},
                    status=200,
                )
            else:
                return JsonResponse(
                    {"msg": "bookmarked data not found", "bookMarkData": []}, status=200
                )

        except Exception as err:
            print(err)
            return JsonResponse(
                {"msg": "something went wrong", "err": str(err)}, status=500
            )
    else:
        return JsonResponse({"msg": "method not allowed"}, status=400)
