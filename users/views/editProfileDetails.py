from django.http import JsonResponse
from streaming_app_backend.mongo_client import users_collection
import json
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to edit profile details. The request should contain the user token in headers and an array of selected genres in the body.",
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
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="User name"),
            "gender": openapi.Schema(
                type=openapi.TYPE_STRING, description="User password"
            ),
            "mobile": openapi.Schema(
                type=openapi.TYPE_STRING, description="Confirm password"
            ),
        },
        required=["email", "name", "gender", "mobile"],
    ),
    responses={
        200: openapi.Response(description="profile updated successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def editProfileDetails(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body.get("email")
            name = body.get("name")
            gender = body.get("gender")
            mobile = body.get("mobile")

            userId = request.userId
            
            userDetails = users_collection.find_one_and_update(
                {"_id": ObjectId(userId)},
                {
                    "$set": {
                        "email": email,
                        "mobile": mobile,
                        "name": name,
                        "gender": gender,
                    }
                },
            )

            userDetails["_id"] = str(userDetails["_id"])
            return JsonResponse({"msg": "data updated successFully..."}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON"}, status=400)

    else:
        return JsonResponse({"msg": "method not allowed"}, status=500)
