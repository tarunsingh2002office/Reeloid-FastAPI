from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from streaming_app_backend.mongo_client import genre_collection
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi





@swagger_auto_schema(
    method="GET",
    operation_description="This API will give all the available genres to the user for selection. We need to pass the token in the headers using the 'token' key.",
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
        200: openapi.Response(description="Genres fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
    },
    tags=["User"],
)
@api_view(["GET"])
@csrf_exempt
def genreList(request):
    if request.method == "GET":
        genresArray = []
        genrelist = genre_collection.find({}, {"_id": 1, "name": 1, "icon": 1})

        for genre in genrelist:
            genre["_id"] = str(genre["_id"])
            genresArray.append(genre)
        return JsonResponse({"genreList": genresArray}, status=200)
    else:
        return JsonResponse({"msg": "method not allowed"}, status=500)
