from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import verificationEmail, users_collection
from datetime import datetime, timedelta, timezone
from helper_function.tokenCreator import tokenCreator
from helper_function.saveUserInDataBase import saveUserInDataBase
import hashlib

def hash_password(password: str) -> str:
    """Hashes the user's password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

async def verifyEmail(request: Request, body: dict = Body(
    example={
        "otp": "123456",
        "email": "viveksingh5568@gmail.com",
        "name": "vivek singh",
        "password": "1234"
    }
)):
    body = await request.json()
    otp = body.get("otp")
    email = body.get("email")
    name = body.get("name")
    password = body.get("password")

    # Ensure OTP, email, name, and password are provided
    if not all([otp, email, name, password]):
        return JSONResponse({"msg": "OTP, email, name, and password are required"}, status_code=400)

    try:
        # Calculate 15 minutes ago to validate OTP timestamp
        fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)

        # Find the OTP record in the database and mark it as used if it's valid
        existing_request = await verificationEmail.find_one_and_update(
            {
                "isUsed": False,
                "otp": int(otp),
                "email": email,
                "status": "Pending",
                "createdTime": {"$gte": fifteen_min_ago},  # Only consider OTPs within the last 15 minutes
            },
            {
                "$set": {
                    "isUsed": True,
                    "status": "Verified",
                }
            },
            projection={"_id": True},
        )

        # If no valid OTP record is found, return an error
        if not existing_request:
            return JSONResponse(
                {"msg": "No valid OTP found for email verification within the last 15 minutes"},
                status_code=400,
            )

        # Hash the password before saving
        hashed_password = hash_password(password)

        # Save the user's data to the main database
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
        }
        userCreated = await saveUserInDataBase(user_data)

        # Generate a token for the newly created user (if applicable)
        token = await tokenCreator({
            "otpId": str(existing_request["_id"]),
            "id": str(userCreated.inserted_id)
        })

        return JSONResponse(
            {
                "msg": "Email verified and user created successfully",
                "token": token
            },
            status_code=200,
        )

    except Exception as err:
        # Catch unexpected errors and return a response
        return JSONResponse({"msg": f"Verification failed: {str(err)}"}, status_code=500)
