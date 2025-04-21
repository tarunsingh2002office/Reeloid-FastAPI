import json
import random
from fastapi import Request, Body
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from datetime import timedelta
from core.database import (
    forgotPasswordRequests,
    users_collection,
    client,
)
from helper_function.forgotPasswordEmailSender import forgotPasswordEmailSender

async def forgotPassword(request:Request,body: dict = Body(
        example={
            "email": "a@gmail.com",
        },
    )):
    session = None
    try:
        # Parse JSON data from request body
        data = await request.json()
        #json.loads(request.body)
        email = data.get("email")
        # user_id = request.state.userId  # Extract userId from request body

        if not email:
            return JSONResponse({"msg": "email is required"}, status_code=400)

        # Check if a request was already made within the last minute
        one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        session = await client.start_session()
        session.start_transaction()
        existing_user = await users_collection.find_one(
            {"email": email}, {"_id": 1, "name": 1}
        )

        if not existing_user:
            return JSONResponse({"msg": "you are not a valid user"}, status_code=429)
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
        # Insert new request log
        await forgotPasswordRequests.insert_one(
            {
                "userId": existing_user["_id"],
                "createdTime": datetime.now(timezone.utc),
                "otp": otp,
                "isUsed": False,
            },
            session=session,
        )
        forgotPasswordEmailSender(
            {
                "name": existing_user["name"],
                "otp": otp,
                "email": email,
            }
        )
        session.commit_transaction()
        return JSONResponse(
            {
                "msg": "Password reset request sent successfully.please check your email inbox...."
            }
        )

    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON format"}, status_code=400)
    except Exception as err:
        if session:
            session.abort_transaction()
        return JSONResponse({"msg": f"Error: {str(err)}"}, status_code=500)
    finally:
        if session:
            session.end_session()
