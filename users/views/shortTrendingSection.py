from django.http import JsonResponse
from streaming_app_backend.mongo_client import movies_collection, shorts_collection

from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API will give all the trending movies trailers to the user . We need to pass the token in the headers using the 'token' key.",
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
        200: openapi.Response(description="trending shorts fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["GET"])
def TrailerTrendingSection(request):
    if request.method == "GET":

        moviesData = (
            movies_collection.find(
                {},
                {"_id": 1, "name": 1, "shorts": 1, "trailerUrl": 1, "fileLocation": 1},
            )
            .sort("views", -1)
            .limit(10)
        )
        moviesArray = []
        for movie in moviesData:

            movie["_id"] = str(movie["_id"])
            shortsArray = []
            for shortid in movie["shorts"]:
                if shortid != "Ads":
                    shortsData = shorts_collection.find_one(
                        {"_id": shortid, "visible": True},
                        {"_id": 1, "name": 1, "fileLocation": 1},
                    )
                    # print(shortsData,"sddddd")
                    if shortsData:
                        shortsData["_id"] = str(shortsData["_id"])
                        shortsArray.append(shortsData)

            movie["shorts"] = shortsArray
            moviesArray.append(movie)
        return JsonResponse({"trailersData": moviesArray}, status=200)
    else:
        return JsonResponse({"msg": "method not allowed"}, status=500)
