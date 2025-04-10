from django.http import JsonResponse
from streaming_app_backend.mongo_client import movies_collection
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API allows the user to serach the content  by providing  a query  and a token as a header.",
    manual_parameters=[
        openapi.Parameter(
            "name",  # Query parameter for name
            openapi.IN_QUERY,  # Specifies that this is a query parameter
            description="Search Query",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "token",  # Header parameter for token
            openapi.IN_HEADER,  # Specifies that this is a header parameter
            description="User authentication token",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(description="query searched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="Internal server error"),
    },
    tags=["User"],
)
@api_view(["GET"])
def serachItem(request):
    if request.method == "GET":
        searchedItem = request.GET.get("name")
        if not searchedItem:
            return JsonResponse(
                {"msg": "searched item is invalid", "status": False}, status=404
            )
        # print(searchedItem)
        searchedResult = movies_collection.find(
            {"name": {"$regex": searchedItem, "$options": "i"}},
            {"_id": 1, "name": 1, "fileLocation": 1},
        )

        moviesList = []
        for data in searchedResult:

            data["_id"] = str(data.get("_id"))
            moviesList.append(data)
        if len(moviesList) == 0:
            return JsonResponse(
                {
                    "msg": "no data Found for serached Query",
                    "data": moviesList,
                    "success": False,
                },
                status=200,
            )
        return JsonResponse(
            {"msg": "got it", "data": moviesList, "success": False}, status=200
        )
    else:
        return JsonResponse(
            {
                "msg": "wrong method",
            }
        )
