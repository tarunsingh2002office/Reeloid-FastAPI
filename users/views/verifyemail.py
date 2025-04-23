import json
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import verificationCode, users_collection, client
from helper_function.emailSender import emailSender
from helper_function.saveUserInDataBase import saveUserInDataBase
from datetime import datetime, timedelta, timezone

async def verifyEmail(request: Request, body: dict = Body(
    example={
        "email": "tarunsingh2002office@gmail.com",
        "otp": "123456"
    }
)):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)

    email = body.get("email")
    otp = body.get("otp")

    if not email or not otp:
        return JSONResponse({"msg": "Email or OTP is missing"}, status_code=400)

    session = None

    try:
        session = await client.start_session()
        async with session.start_transaction():

            otp_record = await verificationCode.find_one(
                {"email": email, "otp": int(otp), "isUsed": False},
                session=session
            )

            if not otp_record:
                return JSONResponse({"msg": "Invalid OTP or OTP already used"}, status_code=400)

            created_time = otp_record.get("createdTime")
            if not created_time:
                return JSONResponse({"msg": "OTP record is invalid"}, status_code=400)

            if created_time.tzinfo is None:
                created_time = created_time.replace(tzinfo=timezone.utc)

            if datetime.now(timezone.utc) > created_time + timedelta(minutes=15):
                return JSONResponse({"msg": "OTP has expired"}, status_code=400)

            await verificationCode.update_one(
                {"_id": otp_record["_id"]},
                {"$set": {"isUsed": True, "status": "Verified"}},
                session=session
            )

            user_data = {
                "email": otp_record["email"],
                "name": otp_record["name"],
                "password": otp_record["password"],
            }

            await saveUserInDataBase(user_data)

            try:
                await emailSender({
                    "name": otp_record["name"],
                    "email": otp_record["email"]
                })
            except Exception as e:
                print(f"Email sending failed: {e}")
                raise

        return JSONResponse(
            {"msg": "OTP verified and user successfully registered."},
            status_code=200
        )

    except Exception as err:
        print(f"Verification failed: {err}")
        return JSONResponse({
            "msg": f"Verification failed: {str(err)}",
            "success": False
        }, status_code=500)

    finally:
        if session:
            await session.end_session()
