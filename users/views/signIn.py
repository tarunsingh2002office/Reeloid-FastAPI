from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timezone
from streaming_app_backend.mongo_client import (
    users_collection,
    genre_collection,
    languages_collection,
)
from bson import ObjectId
from helper_function.tokenCreator import tokenCreator
from helper_function.updateLoginStatus import updateLoginStatus

from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from helper_function.verifyPassword import verifyPassword


@swagger_auto_schema(
    method="POST",
    operation_description="This api will checkuser in database and give them access to use the app if they are registered with us. The request should contain user details like  email, and password.in response we will get a token for further accessing the app ",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, description="User password"
            ),
        },
        required=["email", "password"],
    ),
    responses={
        201: openapi.Response(description="User created successfully"),
        400: openapi.Response(description="Invalid input or validation error"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def signIn(request):

    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON"}, status=400)
        email = body.get("email")
        password = body.get("password")
        fcmtoken = body.get("nId")  # notification id
        deviceType = body.get("deviceType")

        if not email:
            return JsonResponse({"msg": "email is not present"}, status=400)
        if not password:
            return JsonResponse({"msg": "password is not present"}, status=400)
        # if not fcmtoken:
        #     return JsonResponse(
        #         {"msg": "please give us access for notification"}, status=400
        #     )

        userResponse = users_collection.find_one({"email": email})

        if not userResponse:
            return JsonResponse(
                {
                    "msg": "No user Found with this email and password combination",
                    "success": False,
                },
                status=400,
            )
        else:
            try:
                storedPAssword = userResponse.get("password")
                
                password_match = verifyPassword(password, storedPAssword)

                if not password_match:
                    return JsonResponse(
                        {
                            "msg": "The password you Entered not matched with stored password"
                        },
                        status=401,
                    )
                del userResponse["password"]
                updatedUserResponse, token = updateLoginStatus(
                    userResponse, fcmtoken, deviceType
                )
                return JsonResponse(
                    {
                        "msg": "successfully logged in",
                        "userData": updatedUserResponse,
                        "token": token,
                    },
                    status=200,
                )
            except Exception as err:

                return JsonResponse({"msg": str(err)}, status=400)

    else:
        return JsonResponse({"msg": "wrong method"}, status=500)
