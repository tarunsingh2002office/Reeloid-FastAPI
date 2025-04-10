from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from streaming_app_backend.mongo_client import users_collection, client
from datetime import datetime, timezone
from helper_function.saveUserInDataBase import saveUserInDataBase
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from helper_function.emailSender import emailSender


@swagger_auto_schema(
    method="POST",
    operation_description="Create a new user in the system. The request should contain user details like name, email, and password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="User name"),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, description="User password"
            ),
            "confirmPassword": openapi.Schema(
                type=openapi.TYPE_STRING, description="Confirm password"
            ),
        },
        required=["email", "name", "password", "confirmPassword"],
    ),
    responses={
        201: openapi.Response(description="User created successfully"),
        400: openapi.Response(description="Invalid input or validation error"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def createUser(request):
    if request.method == "POST":
        try:

            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON"}, status=400)
        email = body.get("email")
        name = body.get("name")
        password = body.get("password")
        confirmPassword = body.get("confirmPassword")
        if not name:
            return JsonResponse({"msg": "name is not present"}, status=400)
        if not email:
            return JsonResponse({"msg": "email is not present"}, status=400)
        if not password:
            return JsonResponse({"msg": "password is not present"}, status=400)
        if not confirmPassword:
            return JsonResponse({"msg": "confirm password is not present"}, status=400)
        if password != confirmPassword:
            return JsonResponse(
                {"msg": "password and confirm password is not same"}, status=400
            )
        session = client.start_session()
        session.start_transaction()
        try:
            user = users_collection.find_one({"email": email})

            if user:
                return JsonResponse(
                    {"msg": "user is already registered with us with this email"},
                    status=400,
                )

            userCreated = saveUserInDataBase(
                {"name": name, "email": email, "password": password, "session": session}
            )
            emailSender({"name": name, "email": email})
            session.commit_transaction()
            return JsonResponse(
                {"msg": "added user successfully", "success": True}, status=200
            )
        except Exception as err:
            if session:
                # session.
                session.abort_transaction()
            return JsonResponse(
                {"msg": str(err), "success": False},
                status=400,
            )
        finally:
            # End session
            session.end_session()
    else:
        return JsonResponse({"msg": "wrong method"}, status=500)
