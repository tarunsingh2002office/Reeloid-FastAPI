from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import users_collection, verificationCode, client
from helper_function.emailSender import emailSender
from helper_function.saveUserInDataBase import saveUserInDataBase
from datetime import datetime, timedelta, timezone

async def verifyEmail(request: Request, body: dict = Body(
    example={
        "email": "tarunsingh2002office@gmail.com",
        "otp": "123456"
    }
)):
    session = await client.start_session()  # Start a MongoDB session

    try:
        body = await request.json()
        email = body.get("email")
        otp = body.get("otp")

        # Validate that both email and OTP are provided
        if not email or not otp:
            return JSONResponse({"msg": "Email and OTP are required"}, status_code=400)

        fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)

        # Start transaction
        async with session.start_transaction():
            # Find the OTP record
            otp_record = await verificationCode.find_one({
                "email": email,
                "otp": int(otp),
                "isUsed": False,
                "createdTime": {"$gte": fifteen_min_ago},
            }, session=session)

            if not otp_record:
                return JSONResponse({"msg": "Invalid or already used OTP"}, status_code=400)

            # Check if the user already exists
            existing_user = await users_collection.find_one({"email": email}, session=session)
            if existing_user:
                return JSONResponse({"msg": "User already registered"}, status_code=400)

            # Mark OTP as used and verified
            await verificationCode.update_one(
                {"_id": otp_record["_id"]},
                {"$set": {
                    "isUsed": True,
                    "status": "Verified",
                    "verifiedAt": datetime.utcnow()
                }},
                session=session
            )

            # Save the user into users_collection
            await saveUserInDataBase({
                "name": otp_record["name"],
                "email": otp_record["email"],
                "password": otp_record["password"]
            }, session=session)

            # Send the welcome email
            await emailSender({"name": otp_record["name"], "email": otp_record["email"]})

            # Commit transaction if everything succeeds
            await session.commit_transaction()

            return JSONResponse({"msg": "OTP verified and user created", "success": True}, status_code=200)

    except Exception as err:
        # Rollback transaction if there's an error
        await session.abort_transaction()
        
        # Log the error for better traceability
        print(f"Error during verification: {err}")  # Consider using logging instead of print in production
        return JSONResponse({"msg": f"Verification failed: {err}", "success": False}, status_code=500)
    finally:
        # Ensure the session is ended properly
        await session.end_session()
