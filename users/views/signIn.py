import json
from fastapi.responses import JSONResponse
from core.database import users_collection
from helper_function.verifyPassword import verifyPassword
from helper_function.updateLoginStatus import updateLoginStatus
from core.apis_requests import SignInRequest
async def signIn(request: SignInRequest):
    try:
        body = request.model_dump()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)
    email = body.get("email")
    password = body.get("password") 
    fcmtoken = body.get("nId") or "" # notification id
    deviceType = body.get("deviceType") or ""

    if not email:
        return JSONResponse({"msg": "email is not present"}, status_code=400)
    if not password:
        return JSONResponse({"msg": "password is not present"}, status_code=400)

    userResponse = users_collection.find_one({"email": email})

    if not userResponse:
        return JSONResponse(
            {
                "msg": "No user Found with this email and password combination",
                "success": False,
            },
            status_code=400,
        )
    else:
        try:
            storedPAssword = userResponse.get("password")
            
            password_match = verifyPassword(password, storedPAssword)

            if not password_match:
                return JSONResponse(
                    {
                        "msg": "The password you Entered not matched with stored password"
                    },
                    status_code=401,
                )
            del userResponse["password"]
            updatedUserResponse, token = updateLoginStatus(
                userResponse, fcmtoken, deviceType
            )
            return JSONResponse(
                {
                    "msg": "successfully logged in",
                    "userData": updatedUserResponse,
                    "token": token,
                },
                status_code=200,
            )
        except Exception as err:

            return JSONResponse({"msg": str(err)}, status_code=400)
