import json
import asyncio
import random
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import verificationCode, users_collection
from core.database import client
from helper_function.verifycodeEmailSender import verifycodeEmailSender
from datetime import datetime, timedelta, timezone

# Helper function to generate a 6-digit OTP
def generate_otp():
    return random.randint(100000, 999999)

async def createUser(request: Request, body: dict = Body(
        example={
            "email": "tarunsingh2002office@gmail.com",
            "name": "Mr. Tarun Singh",
            "password": "1234",
            "confirmPassword": "1234"
        }
    )):

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)

    email = body.get("email")
    name = body.get("name")
    password = body.get("password")
    confirmPassword = body.get("confirmPassword")

    # Input validation
    if not email:
        return JSONResponse({"msg": "Email is not present"}, status_code=400)
    if not name:
        return JSONResponse({"msg": "Name is not present"}, status_code=400)
    if not password:
        return JSONResponse({"msg": "Password is not present"}, status_code=400)
    if not confirmPassword:
        return JSONResponse({"msg": "Confirm password is not present"}, status_code=400)
    if password != confirmPassword:
        return JSONResponse({"msg": "Password and confirm password do not match"}, status_code=400)

    try:
        existing_user = await users_collection.find_one({"email": email})
        otp = generate_otp()
        otp_data = {
            "email": email,
            "name": name,
            "password": password,
            "otp": otp,
            "isUsed": False,
            "createdTime": datetime.now(timezone.utc),
            "status": "Pending"
        }

        if existing_user:
            # If the user exists, just update the OTP data
            await verificationCode.update_one(
                {"email": email},
                {"$set": otp_data},
                upsert=True
            )
        else:
            # New user: insert new OTP data
            await verificationCode.insert_one(otp_data)

        # Send verification email
        await verifycodeEmailSender({"name": name, "otp": otp, "email": email})

        return JSONResponse({"msg": "OTP sent for verification", "success": True}, status_code=200)

    except Exception as err:
        return JSONResponse({"msg": f"Error: {err}"}, status_code=500)
