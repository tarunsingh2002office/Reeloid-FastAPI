from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import users_collection, verificationCode
from helper_function.emailSender import emailSender
from helper_function.saveUserInDataBase import saveUserInDataBase
from datetime import datetime

async def verifyEmail(request: Request, body: dict = Body(
    example={
        "email": "tarunsingh2002office@gmail.com",
        "otp": "123456"
    }
)):
    try:
        body = await request.json()
        email = body.get("email")
        otp = body.get("otp")

        if not email or not otp:
            return JSONResponse({"msg": "Email and OTP are required"}, status_code=400)

        # Find the OTP record
        otp_record = await verificationCode.find_one({
            "email": email,
            "otp": int(otp),
            "isUsed": False
        })

        if not otp_record:
            return JSONResponse({"msg": "Invalid or already used OTP"}, status_code=400)

        # Check if user already exists
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            return JSONResponse({"msg": "User already registered"}, status_code=400)

        # Mark OTP as used and verified
        await verificationCode.update_one(
            {"_id": otp_record["_id"]},
            {"$set": {
                "isUsed": True,
                "status": "Verified",
                "verifiedAt": datetime.utcnow()
            }}
        )

        # Save user into users_collection
        await saveUserInDataBase({
            "name": otp_record["name"],
            "email": otp_record["email"],
            "password": otp_record["password"]
        })

        # Send welcome email
        await emailSender({"name": otp_record["name"], "email": otp_record["email"]})

        return JSONResponse({"msg": "OTP verified and user created", "success": True}, status_code=200)

    except Exception as err:
        return JSONResponse({"msg": f"Verification failed: {err}", "success": False}, status_code=500)
