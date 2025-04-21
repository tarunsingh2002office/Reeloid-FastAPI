import json
import random
import asyncio
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
    max_retries = 3  
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

        for attempt in range(max_retries):
            session = await client.start_session()
            session.start_transaction()
            try:
                await forgotPasswordRequests.insert_one(
                    {
                        "userId": existing_user["_id"],
                        "createdTime": datetime.now(timezone.utc),
                        "otp": otp,
                        "isUsed": False,
                    },
                    session=session,
                )
                await forgotPasswordEmailSender(
                    {
                        "name": existing_user["name"],
                        "otp": otp,
                        "email": email,
                    }
                )
                
                session.commit_transaction()

                return JSONResponse(
                    {"msg": "Password reset request sent successfully. Please check your email inbox."},
                    status_code=200,
                )
            except Exception as err:
                if session and session.in_transaction:
                    session.abort_transaction()
                if "TransientTransactionError" in str(err) and attempt < max_retries - 1:
                    await asyncio.sleep(0.1)  
                    continue
                return JSONResponse({"msg": f"Error: {str(err)}"}, status_code=500)
            finally:
                session.end_session()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    except Exception as err:
        return JSONResponse({"msg": f"Unexpected error: {str(err)}"}, status_code=500)