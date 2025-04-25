from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import verificationEmail, client
from datetime import datetime, timedelta, timezone
from helper_function.emailSender import emailSender
from helper_function.tokenCreator import tokenCreator
from helper_function.saveUserInDataBase import saveUserInDataBase

async def verifyEmail(request: Request, body: dict = Body(
    example={
        "otp": "123456",
        "email": "tarunsingh2002office@gmail.com/viveksingh5568@gmail.com"
    }
)):
    try:
        body = await request.json()
        otp = body.get("otp")
        email = body.get("email")

        if not otp:
            return JSONResponse({"msg": "OTP is required"}, status_code=400)
        elif not email:
            return JSONResponse({"msg": "Email is required"}, status_code=400)

        fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)

        # Step 1: Check if there is any recent OTP for this email
        recent_otp_record = await verificationEmail.find_one({
            "email": email,
            "isUsed": False,
            "createdTime": {"$gte": fifteen_min_ago},
        })

        if not recent_otp_record:
            return JSONResponse(
                {"msg": "OTP has expired or not requested. Please request a new one."},
                status_code=400
            )

        # Step 2: Check if the OTP matches
        if recent_otp_record["otp"] != int(otp):
            return JSONResponse(
                {"msg": "Wrong OTP entered, please provide a valid OTP."},
                status_code=400
            )

        # Step 3: Mark OTP as used and proceed
        existing_request = await verificationEmail.find_one_and_update(
            {
                "_id": recent_otp_record["_id"]
            },
            {
                "$set": {"isUsed": True}
            },
            projection={"name": 1, "password": 1},
        )

        name = existing_request.get("name")
        password = existing_request.get("password")

        # Step 4: Save the user's data to the main database
        async with await client.start_session() as session:
            async def txn(sess):
                user_data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "session": sess
                }
                userCreated = await saveUserInDataBase(user_data)

                await emailSender({"name": name, "email": email})

                token = await tokenCreator({
                    "otpId": str(existing_request["_id"]),
                    "id": str(userCreated.inserted_id)
                })
                return token

            try:
                token = await session.with_transaction(txn)
            except Exception as err:
                return JSONResponse({"msg": f"Verification failed: {str(err)}"}, status_code=500)

        # Step 5: Return success response with token
        return JSONResponse(
            {
                "msg": "Email verified and user created successfully",
                "token": token
            },
            status_code=200,
        )

    except Exception as err:
        return JSONResponse({"msg": f"Verification failed: {str(err)}"}, status_code=500)
