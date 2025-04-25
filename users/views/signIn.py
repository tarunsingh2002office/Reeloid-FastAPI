import json
from datetime import datetime
from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import users_collection, verificationEmail
from helper_function.verifyPassword import verifyPassword
from helper_function.updateLoginStatus import updateLoginStatus

# Utility function to handle datetime serialization
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

async def signIn(request: Request, body: dict = Body(
        example={
            "email": "tarunsingh2002office@gmail.com",
            "password": "123456",
        }
    )):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)
    
    email = body.get("email")
    password = body.get("password") 
    fcmtoken = body.get("nId")  # notification id
    deviceType = body.get("deviceType") 

    if not email:
        return JSONResponse({"msg": "email is not present"}, status_code=400)
    if not password:
        return JSONResponse({"msg": "password is not present"}, status_code=400)

    userResponse = await users_collection.find_one({"email": email})

    if not userResponse:
        verification_data = await verificationEmail.find_one({"email": email, "isUsed": False})
        if verification_data:
            return JSONResponse(
                {
                    "msg": "Email is not verified. Please verify your email first.",
                    "success": False,
                },
                status_code=400,
            )
        return JSONResponse(
            {
                "msg": "No user found with this email",
                "success": False,
            },
            status_code=400,
        )
    
    try:
        # Verify password
        storedPassword = userResponse.get("password")
        password_match = await verifyPassword(password, storedPassword)

        if not password_match:
            return JSONResponse(
                {
                    "msg": "The password you entered does not match the stored password"
                },
                status_code=401,
            )

        # Remove password from the response
        del userResponse["password"]
        
        # Update login status and generate token
        updatedUserResponse, token = await updateLoginStatus(
            userResponse, fcmtoken, deviceType
        )
        
        # Serialize datetime fields in the response
        updatedUserResponse = json.loads(
            json.dumps(updatedUserResponse, default=serialize_datetime)
        )
        
        return JSONResponse(
            {
                "msg": "Successfully logged in",
                "userData": updatedUserResponse,
                "token": token,
            },
            status_code=200,
        )
    
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)
