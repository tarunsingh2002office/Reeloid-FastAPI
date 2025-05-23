import json
import time
from google.oauth2 import id_token
from fastapi import Request, Body
from core.config import google_settings
from core.database import users_collection
from google.auth.transport import requests
from fastapi.responses import JSONResponse
from helper_function.sendEmail import sendEmail
from helper_function.saveUserInDataBase import saveUserInDataBase
from helper_function.updateLoginStatus import updateLoginStatus
from helper_function.serialize_mongo_document import serialize_document

async def googleAuth(request: Request, body: dict = Body(
        example={
            "fcmtoken": "1234",
            "deviceType": "web",
            "authToken": "1234"
        }
    )):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)

    fcmtoken = body.get("nId")  # notification id
    deviceType = body.get("deviceType")
    authToken = body.get("authToken")

    try:
        CLIENT_ID = google_settings.GOOGLE_CLIENT_ID
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
            userResponse = await users_collection.find_one(
                {"email": email}, {"password": 0}
            )
            name = idinfo.get("name")

            if userResponse:
                # Serialize the userResponse document
                userResponse = await serialize_document(userResponse)

                updatedUserResponse, token = await updateLoginStatus(
                    userResponse, fcmtoken, deviceType
                )

                return JSONResponse(
                    {
                        "msg": "google authentication done......user is already registered with us",
                        "userData": await serialize_document(updatedUserResponse),
                        "token": token,
                    }
                )
            else:
                password = ""
                await saveUserInDataBase(
                    {"name": name, "email": email, "password": password}
                )
                getSavedUser = await users_collection.find_one(
                    {"email": email}, {"password": 0}
                )
                if getSavedUser:
                    # Serialize the getSavedUser document
                    getSavedUser = await serialize_document(getSavedUser)

                    updatedUserResponse, token = await updateLoginStatus(
                        getSavedUser, fcmtoken, deviceType
                    )
                    await sendEmail({"name": name, "email": email, "type": "direct"}, "registration")
                    return JSONResponse(
                        {
                            "msg": "google authentication done......registered a new account",
                            "userData": await serialize_document(updatedUserResponse),
                            "token": token,
                        }
                    )
        else:
            raise ValueError("Invalid Token or issuer")

    except Exception as err:
        return JSONResponse({"msg": str(err), "err": str(err)}, status_code=400)