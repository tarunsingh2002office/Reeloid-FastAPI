from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import time
from streaming_app_backend.mongo_client import users_collection
from helper_function.tokenCreator import tokenCreator
from helper_function.saveUserInDataBase import saveUserInDataBase
from helper_function.updateLoginStatus import updateLoginStatus
import json
from django.views.decorators.csrf import csrf_exempt
from helper_function.emailSender import emailSender
import os


@csrf_exempt
def googleAuth(request):
    if request.method == "POST":

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON"}, status=400)
        fcmtoken = body.get("nId")  # notification id
        deviceType = body.get("deviceType")

        authToken = body.get("authToken")

        try:

            CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
            # CLIENT_ID = "711384080035-g77aj9ec6d0cnqpns28k6jttd16g1g6u.apps.googleusercontent.com"
            idinfo = id_token.verify_oauth2_token(
                authToken, requests.Request(), CLIENT_ID
            )

            issuer = idinfo.get("iss")
            expiration_time = idinfo.get("exp")
            current_time = time.time()

            if idinfo and issuer == "https://accounts.google.com":

                if expiration_time < current_time:
                    raise ValueError("token is expired")
                email = idinfo.get("email")
                userResponse = users_collection.find_one(
                    {"email": email}, {"password": 0}
                )
                name = idinfo.get("name")

                if userResponse:

                    updatedUserResponse, token = updateLoginStatus(
                        userResponse, fcmtoken, deviceType
                    )

                    return JsonResponse(
                        {
                            "msg": "google authentication done......user is already registered with us",
                            "userData": updatedUserResponse,
                            "token": token,
                        }
                    )
                else:

                    password = "hexagonal"
                    saveUserInDataBase(
                        {"name": name, "email": email, "password": password}
                    )
                    getSavedUser = users_collection.find_one(
                        {"email": email}, {"password": 0}
                    )
                    print("get",getSavedUser)
                    if getSavedUser:
                        updatedUserResponse, token = updateLoginStatus(
                            getSavedUser, fcmtoken, deviceType
                        )
                        # token = tokenCreator({"id": str(getSavedUser.get("_id"))})
                        emailSender({"name": name, "email": email, "type": "direct"})
                        return JsonResponse(
                            {
                                "msg": "google authentication done......registered a new account",
                                "userData": updatedUserResponse,
                                "token": token,
                            }
                        )
            else:
                raise ValueError("Invalid Token or issuer")

        except Exception as err:
            print(err)
            return JsonResponse({"msg": str(err), "err": str(err)}, status=400)
    else:
        return JsonResponse({"msg": "method not allowed"}, status=500)
