from streaming_app_backend.mongo_client import movies_collection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API will give all the trending movies to the user . We need to pass the token in the headers using the 'token' key.",
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
        200: openapi.Response(description="movies fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["GET"])
@csrf_exempt
def UserTrendingVideos(request):
    if request.method == "GET":
        # we have to fetch alll the trending videos by views maximum
        # we can add three columns for todays views,weekly views and all time views
        # later we can use any one of views for getting trending videos as per requirements
        # we can also use user choice preferences like if user is interested in some specific genre and language based trending
        trending_movies = (
            movies_collection.find({}, {"_id": 1, "name": 1, "fileLocation": 1})
            .sort("views", -1)
            .limit(10)
        )
        trending_movies_list = []
        # print(trending_movies)
        for movies in trending_movies:

            movies["_id"] = str(movies["_id"])
            trending_movies_list.append(movies)
        return JsonResponse({"movies": trending_movies_list}, status=200)
    return JsonResponse({"msg": "method not allowed"}, status=500)
