import json
import random
import hashlib
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from core.database import verificationEmail, users_collection
from helper_function.verifycodeEmailSender import verifycodeEmailSender
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def generate_otp():
    return random.randint(100000, 999999)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def createUser(request: Request, body: dict = Body(
    example={
        "email": "viveksingh5568@gmail.com",
        "name": "Vivek Singh",
        "password": "1234",
        "confirmPassword": "1234"
    }
)):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)

    email = body.get("email", "").strip().lower()
    name = body.get("name", "").strip()
    password = body.get("password", "")
    confirmPassword = body.get("confirmPassword", "")

    # Validate fields
    if not email:
        return JSONResponse({"msg": "Email is required"}, status_code=400)
    if not name:
        return JSONResponse({"msg": "Name is required"}, status_code=400)
    if not password or not confirmPassword:
        return JSONResponse({"msg": "Password and confirm password are required"}, status_code=400)
    if password != confirmPassword:
        return JSONResponse({"msg": "Password and confirm password do not match"}, status_code=400)

    # Check if user already exists (case insensitive)
    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        return JSONResponse({"msg": "User with this email already exists"}, status_code=400)

    # Generate OTP
    otp = generate_otp()
    current_time = datetime.now(timezone.utc)

    # Upsert OTP in verificationEmail collection
    try:
        update_result = await verificationEmail.update_one(
            {"email": email},
            {
                "$set": {
                    "otp": otp,
                    "createdTime": current_time,
                    "isUsed": False,
                    "status": "Pending"
                }
            },
            upsert=True
        )
        if update_result.upserted_id:
            logging.info(f"New OTP document inserted: {update_result.upserted_id}")
        else:
            logging.info(f"OTP updated for existing email: {email}")
    except Exception as e:
        logging.error(f"Error upserting OTP into database: {str(e)}")
        return JSONResponse({"msg": "Failed to store OTP in database"}, status_code=500)

    # Send OTP via email
    try:
        await verifycodeEmailSender({
            "name": name,
            "otp": otp,
            "email": email
        })
        logging.info(f"OTP sent to {email}")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return JSONResponse({"msg": "Failed to send OTP email"}, status_code=500)

    return JSONResponse({
        "msg": "Verification OTP sent to email",
        "email": email
    }, status_code=200)
