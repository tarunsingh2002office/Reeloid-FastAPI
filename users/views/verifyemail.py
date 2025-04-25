from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import verificationEmail, client
from datetime import datetime, timedelta, timezone
from helper_function.sendEmail import sendEmail
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
            return JSONResponse({"msg": "email is required"}, status_code=400)
        
        records_cursor = verificationEmail.find({"email": email}, {"_id":0})
        if not await records_cursor.fetch_next:
            return JSONResponse(
                {"msg": "No valid OTP found for given email"},
                status_code=400,
            )

        fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
        flag = False
        async for record in records_cursor:
            if record.get("otp") == int(otp):
                record_time = record.get("createdTime")

                if record_time.tzinfo is None:
                    record_time = record_time.replace(tzinfo=timezone.utc)  

                if record_time  >= fifteen_min_ago and record.get("isUsed") == False:
                    flag = True
                    break
                elif record_time  < fifteen_min_ago:
                    return JSONResponse(
                        {"msg": "OTP has expired"},
                        status_code=400,
                    )
                else:
                    return JSONResponse(
                        {"msg": "OTP has already been used"},
                        status_code=400,
                    )

        if not flag:
            return JSONResponse(
                {"msg": "No valid OTP found for email verification within the last 15 minutes"},
                status_code=400,
            )
        
        # Find the OTP record in the database and mark it as used if it's valid
        existing_request = await verificationEmail.find_one_and_update(
            {
                "isUsed": False,
                "otp": int(otp),
                "email": email,
                "createdTime": {"$gte": fifteen_min_ago},
            },
            {
                "$set": {
                    "isUsed": True
                }
            },
            projection={"name":1,"password":1},
        )

        # If no valid OTP record is found, return an error
        if not existing_request:
            return JSONResponse(
                {"msg": "No valid OTP found for email verification within the last 15 minutes"},
                status_code=400,
            )
        name = existing_request.get("name")
        password = existing_request.get("password")
        # Save the user's data to the main database
        async with await client.start_session() as session:
            async def txn(sess):
                user_data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "session": sess
                }
                userCreated = await saveUserInDataBase(user_data)

                ans = await sendEmail({"name": name, "email": email}, "registration")
                print(ans)
                token = await tokenCreator({
                    "otpId": str(existing_request["_id"]),
                    "id": str(userCreated.inserted_id)
                })
                return token
            try:
                token= await session.with_transaction(txn)
            except Exception as err:
                return JSONResponse({"msg": f"Verification failed: {str(err)}"}, status_code=500)
        return JSONResponse(
            {
                "msg": "Email verified and user created successfully",
                "token": token
            },
            status_code=200,
        )

    except Exception as err:
        return JSONResponse({"msg": f"Verification failed: {str(err)}"}, status_code=500)
