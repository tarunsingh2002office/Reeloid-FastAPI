from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
from streaming_app_backend.mongo_client import (
    forgotPasswordRequests,
    users_collection,
    client,
)
import json
from helper_function.forgotPasswordEmailSender import forgotPasswordEmailSender
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
import random


@swagger_auto_schema(
    method="POST",
    operation_description="This API allows the user to generate a request for chamging password. The request should contain the email in body",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            # "name": openapi.Schema(type=openapi.TYPE_STRING, description="User name"),
            # "gender": openapi.Schema(
            #     type=openapi.TYPE_STRING, description="User password"
            # ),
            # "mobile": openapi.Schema(
            #     type=openapi.TYPE_STRING, description="Confirm password"
            # ),
        },
        required=["email"],
    ),
    responses={
        200: openapi.Response(description="fetched successfully"),
        400: openapi.Response(description="Invalid request or token missing"),
        401: openapi.Response(description="Unauthorized - Invalid or missing token"),
        500: openapi.Response(description="method not allowed"),
    },
    tags=["User"],
)
@api_view(["POST"])
@csrf_exempt
def forgotPassword(request):
    if request.method != "POST":
        return JsonResponse({"msg": "Invalid request method"}, status=405)
    session = None
    # email = None
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        email = data.get("email")
        # user_id = request.userId  # Extract userId from request body

        if not email:
            return JsonResponse({"msg": "email is required"}, status=400)

        # Check if a request was already made within the last minute
        one_min_ago = now() - timedelta(minutes=1)
        session = client.start_session()
        session.start_transaction()
        existing_user = users_collection.find_one(
            {"email": email}, {"_id": 1, "name": 1}
        )

        if not existing_user:
            return JsonResponse({"msg": "you are not a valid user"}, status=429)
        existing_request = forgotPasswordRequests.find_one(
            {
                "userId": existing_user["_id"],
                "createdTime": {"$gte": one_min_ago},
            }
        )

        if existing_request:
            return JsonResponse(
                {"msg": "Please wait 1 minute before requesting again"}, status=429
            )
        otp = random.randint(100000, 999999)
        # Insert new request log
        forgotPasswordRequests.insert_one(
            {
                "userId": existing_user["_id"],
                "createdTime": now(),
                "otp": otp,
                "isUsed": False,
            },
            session=session,
        )
        forgotPasswordEmailSender(
            {
                "name": existing_user["name"],
                "otp": otp,
                "email": email,
            }
        )
        session.commit_transaction()
        return JsonResponse(
            {
                "msg": "Password reset request sent successfully.please check your email inbox...."
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"msg": "Invalid JSON format"}, status=400)
    except Exception as err:
        print(err)
        if session:
            session.abort_transaction()
        return JsonResponse({"msg": f"Error: {str(err)}"}, status=500)
    finally:
        if session:
            session.end_session()
