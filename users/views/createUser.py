import json
import random
from datetime import datetime
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import verificationCode, client
from helper_function.verifycodeEmailSender import verifycodeEmailSender
from helper_function.passwordEncryption import passwordEncryption

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

    if not all([email, name, password, confirmPassword]):
        return JSONResponse({"msg": "All fields are required"}, status_code=400)

    if password != confirmPassword:
        return JSONResponse({"msg": "Password and Confirm Password do not match"}, status_code=400)

    # Check if OTP already sent
    existing_otp = await verificationCode.find_one({
        "email": email,
        "status": "Pending",
        "isUsed": False
    })
    if existing_otp:
        return JSONResponse({"msg": "OTP already sent to this email. Please verify."}, status_code=400)

    otp = random.randint(100000, 999999)
    session = await client.start_session()
    hashedPassword = await passwordEncryption(password)
    try:
        async with session.start_transaction():
            await verificationCode.update_one(
                {"email": email},
                {
                    "$set": {
                        "name": name,
                        "otp": otp,
                        "password": hashedPassword,
                        "status": "Pending",
                        "isUsed": False
                    }
                },
                upsert=True,
                session=session
            )
            await verifycodeEmailSender({"name": name, "otp": otp, "email": email})
        return JSONResponse({"msg": "OTP sent for verification", "success": True}, status_code=200)

    except Exception as err:
        return JSONResponse({"msg": f"Failed to send OTP: {err}", "success": False}, status_code=500)

    finally:
        await session.end_session()
