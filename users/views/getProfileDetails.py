from django.http import JsonResponse
from streaming_app_backend.mongo_client import users_collection,genre_collection,languages_collection
import json
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API will give profile details to the user . We need to pass the token in the headers using the 'token' key.",
    manual_parameters=[
        openapi.Parameter(
            "token",  # The name of the header parameter
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",  # Description for the header
            type=openapi.TYPE_STRING,  # Specifies that the type is a string
            required=True,  # Marks the token as required
        )
    ],
    responses={
        200: openapi.Response(description="profile data  fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["GET"])
@csrf_exempt
def getProfileDetails(request):
    if request.method == "GET":
        try:

            userId = request.userId
            userDetails = users_collection.find_one(
                {"_id": ObjectId(userId)},
                {"password": 0},
            )
            if not userDetails:
                return JsonResponse({"userDetails": []}, status=200)
            userDetails["_id"] = str(userDetails["_id"])

            genreList = []
            if "selectedGenre" in userDetails and userDetails["selectedGenre"]:
                for genreId in userDetails["selectedGenre"]:
                    genreData = genre_collection.find_one(
                        {"_id": ObjectId(genreId)}, {"_id": 1, "name": 1, "icon": 1}
                    )
                    genreData["_id"] = str(genreData["_id"])
                    genreList.append(genreData)
            userDetails["selectedGenre"] = genreList
            languageList = []

            if (
                "selectedLanguages" in userDetails
                and userDetails["selectedLanguages"]
            ):
                for languageId in userDetails["selectedLanguages"]:
                    languageData = languages_collection.find_one(
                        {"_id": ObjectId(languageId)}, {"_id": 1, "name": 1}
                    )
                    languageData["_id"] = str(languageData["_id"])
                    languageList.append(languageData)
            userDetails["selectedLanguages"] = languageList
            return JsonResponse({"userDetails": userDetails}, status=200)
        except Exception as err:
            return JsonResponse({"msg": str(err)})

    else:
        return JsonResponse({"msg": "method not allowed"}, status=500)
