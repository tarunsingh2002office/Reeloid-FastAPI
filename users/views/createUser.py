import json
import random
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from core.database import verificationEmail, users_collection, client
from helper_function.verifycodeEmailSender import verifycodeEmailSender

async def createUser(request: Request, body: dict = Body(
    example={
        "email": "viveksingh5568@gmail.com/tarunsingh2002office@gmail.com",
        "name": "Developer",
        "password": "1234",
        "confirmPassword": "1234"
    }
)):
    try:
        body = await request.json()
        email = body.get("email").strip().lower()
        name = body.get("name").strip()
        password = body.get("password")
        confirmPassword = body.get("confirmPassword")
        # Validate fields
        if not email:
            return JSONResponse({"msg": "Email is required"}, status_code=400)
        if not name:
            return JSONResponse({"msg": "Name is required"}, status_code=400)
        if not password or not confirmPassword:
            return JSONResponse({"msg": "Password and confirm password are required"}, status_code=400)
        if password != confirmPassword:
            return JSONResponse({"msg": "Password and confirm password do not match"}, status_code=400)
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            return JSONResponse({"msg": "User with this email already exists"}, status_code=400)

        one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        existing_request = await verificationEmail.find_one(
            {
                "email": email,
                "createdTime": {"$gte": one_min_ago},
            }
        )
        if existing_request:
            return JSONResponse(
                {"msg": "Please wait 1 minute before requesting again"}, status_code=429
            )
        # Generate OTP
        otp = random.randint(100000, 999999)
        async with await client.start_session() as session:
            async def txn(sess):

                update_result = await verificationEmail.insert_one(
                    {
                        "email": email,
                        "name": name,
                        "password": password,
                        "otp": otp,
                        "createdTime": datetime.now(timezone.utc),
                        "isUsed": False
                    },
                    session=sess
                )
                
                if not update_result.acknowledged:
                    raise Exception("OTP db insertion failed")  # Proper error handling
                
                await verifycodeEmailSender({
                    "name": name,
                    "otp": otp,
                    "email": email
                })
            try:
                await session.with_transaction(txn)
            except Exception as err:
                return JSONResponse({"msg": f"Failed to create user, error is :- {str(err)}"}, status_code=500)
        
        return JSONResponse({
            "msg": "Verification OTP sent to email",
            "email": email
        }, status_code=200)
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    except Exception as err:
        return JSONResponse({"msg": f"Unexpected error: {str(err)}"}, status_code=500)