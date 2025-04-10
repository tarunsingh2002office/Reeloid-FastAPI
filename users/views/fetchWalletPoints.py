from django.http import JsonResponse
from streaming_app_backend.mongo_client import users_collection
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt

from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="GET",
    operation_description="This API allows the user to fetch wallet points. The request should contain the user token in headers ",
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
        200: openapi.Response(description="fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["GET"])

@csrf_exempt
def fetchWalletPoints(request):
    if request.method == "GET":
        userId = request.userId
        userData = users_collection.find_one(
            {"_id": ObjectId(userId)}, {"allocatedPoints": 1, "_id": 1}
        )

        if not userData:
            return JsonResponse(
                {"msg": "err while fetching the user. please provide a valid token"},
                status=400,
            )
        return JsonResponse(
            {"allocatedPoints": userData.get("allocatedPoints")}, status=200
        )
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=200)
