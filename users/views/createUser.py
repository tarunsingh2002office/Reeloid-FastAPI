import json
from fastapi.responses import JSONResponse
from core.apis_requests import CreateUserRequest
from core.database import users_collection, client
from helper_function.emailSender import emailSender
from helper_function.saveUserInDataBase import saveUserInDataBase

async def createUser(request: CreateUserRequest):
    try:
        body =  request.model_dump()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)
    
    email = body.get("email")
    name = body.get("name")
    password = body.get("password")
    confirmPassword = body.get("confirmPassword")

    if not name:
        return JSONResponse({"msg": "name is not present"}, status_code=400)
    if not email:
        return JSONResponse({"msg": "email is not present"}, status_code=400)
    if not password:
        return JSONResponse({"msg": "password is not present"}, status_code=400)
    if not confirmPassword:
        return JSONResponse({"msg": "confirm password is not present"}, status_code=400)
    if password != confirmPassword:
        return JSONResponse(
            {"msg": "password and confirm password is not same"}, status_code=400
        )
    
    session = client.start_session()
    session.start_transaction()

    try:
        user = users_collection.find_one({"email": email})

        if user:
            return JSONResponse(
                {"msg": "user is already registered with us with this email"},
                status_code=400,
            )

        userCreated = saveUserInDataBase(
            {"name": name, "email": email, "password": password, "session": session}
        )
        emailSender({"name": name, "email": email})
        session.commit_transaction()
        return JSONResponse(
            {"msg": "added user successfully", "success": True}, status_code=200
        )
    except Exception as err:
        if session and session.in_transaction:
            session.abort_transaction()
        return JSONResponse(
            {"msg": str(err), "success": False},
            status_code=400,
        )
    finally:
        session.end_session()
