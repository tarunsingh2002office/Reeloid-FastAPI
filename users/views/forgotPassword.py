import json
import random
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from core.database import forgotPasswordRequests, users_collection, client
from helper_function.forgotPasswordEmailSender import forgotPasswordEmailSender

async def forgotPassword(request: Request, body: dict = Body(
        example={
            "email": "a@gmail.com",
        },
    )):
    try:
        data = await request.json()
        email = data.get("email")

        if not email:
            return JSONResponse({"msg": "Email is required"}, status_code=400)

        existing_user = await users_collection.find_one(
            {"email": email}, {"_id": 1, "name": 1}
        )
        if not existing_user:
            return JSONResponse({"msg": "You are not a valid user"}, status_code=404)

        one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        existing_request = await forgotPasswordRequests.find_one(
            {
                "userId": existing_user["_id"],
                "createdTime": {"$gte": one_min_ago},
            }
        )
        if existing_request:
            return JSONResponse(
                {"msg": "Please wait 1 minute before requesting again"}, status_code=429
            )

        otp = random.randint(100000, 999999)

        async with await client.start_session() as session:
            async def txn(sess):
                forgotPasswordInsertionResult =await forgotPasswordRequests.insert_one(
                    {
                        "userId": existing_user["_id"],
                        "createdTime": datetime.now(timezone.utc),
                        "otp": otp,
                        "isUsed": False,
                    },
                    session=sess
                )
                if not forgotPasswordInsertionResult.acknowledged:
                    raise Exception("OTP db insertion failed")  # Proper error handling
                await forgotPasswordEmailSender(
                    {
                        "name": existing_user["name"],
                        "otp": otp,
                        "email": email,
                    }
                )
            try:
                await session.with_transaction(txn)
            except Exception as err:
                return JSONResponse(
                    {"msg": f"Error sending password reset request: {err}"},
                    status_code=500,
                )
        return JSONResponse(
            {"msg": "Password reset request sent successfully. Please check your email inbox."},
            status_code=200,
        )    
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    except Exception as err:
        return JSONResponse({"msg": f"Unexpected error: {str(err)}"}, status_code=500)
    
"""
Conditions Met:
DB Insert Success + Email Failure: Transaction aborts → OTP removed.
DB Insert Success + Email Success: Transaction commits → OTP stored.
DB Insert Failure: Transaction aborts → Email not sent.
"""