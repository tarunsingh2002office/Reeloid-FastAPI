from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from streaming_app_backend.mongo_client import users_collection, genre_collection
from bson import ObjectId
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema



@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to select genres. The request should contain the user token in headers and an array of selected genres in the body.",
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
            "selectedGenre": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="Array of selected genres",
            )
        },
        required=["selectedGenre"],
    ),
    responses={
        200: openapi.Response(description="Genres selected successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def genreSelection(request):

    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON"}, status=400)
        selectedGenre = body.get(
            "selectedGenre"
        )  # want an arrays of comma seperated genres id
        userId = request.userId
        if not selectedGenre:
            return JsonResponse({"msg": "could not get mandatory fields "}, status=400)

        if len(selectedGenre) == 0:
            return JsonResponse(
                {"msg": "no genre is selected,please select a genre"}, status=400
            )
        afterRemovingWrongGenre = []
        for genreId in selectedGenre:
            if ObjectId.is_valid(genreId):
                validGenre = genre_collection.find_one({"_id": ObjectId(genreId)})
                if validGenre:
                    afterRemovingWrongGenre.append(genreId)

        if len(afterRemovingWrongGenre) == 0:
            return JsonResponse(
                {"msg": "no genre is selected,please select a genre"}, status=400
            )

        updatedData = users_collection.update_one(
            {"_id": ObjectId(userId)},
            {"$set": {"selectedGenre": afterRemovingWrongGenre}},
        )
        if updatedData:
            # validUser["selectedGenre"] = selectedGenre
            return JsonResponse(
                {
                    "msg": "successfully selected the genre  ",
                    "userData": "userResponse",
                },
                status=200,
            )
        else:
            return JsonResponse({"msg": "user is invalid"}, status=400)
    else:
        return JsonResponse({"msg": "wrong method"}, status=500)
