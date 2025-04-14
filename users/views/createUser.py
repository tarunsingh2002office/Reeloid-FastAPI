import json
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection, client
from helper_function.emailSender import emailSender
from helper_function.saveUserInDataBase import saveUserInDataBase

async def createUser(request: Request):
    try:
        body = await request.body
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status=400)
    
    email = body.get("email")
    name = body.get("name")
    password = body.get("password")
    confirmPassword = body.get("confirmPassword")

    if not name:
        return JSONResponse({"msg": "name is not present"}, status=400)
    if not email:
        return JSONResponse({"msg": "email is not present"}, status=400)
    if not password:
        return JSONResponse({"msg": "password is not present"}, status=400)
    if not confirmPassword:
        return JSONResponse({"msg": "confirm password is not present"}, status=400)
    if password != confirmPassword:
        return JSONResponse(
            {"msg": "password and confirm password is not same"}, status=400
        )
    
    session = client.start_session()
    session.start_transaction()

    try:
        user = users_collection.find_one({"email": email})

        if user:
            return JSONResponse(
                {"msg": "user is already registered with us with this email"},
                status=400,
            )

        userCreated = saveUserInDataBase(
            {"name": name, "email": email, "password": password, "session": session}
        )
        emailSender({"name": name, "email": email})
        session.commit_transaction()
        return JSONResponse(
            {"msg": "added user successfully", "success": True}, status=200
        )
    except Exception as err:
        if session:
            session.abort_transaction()
        return JSONResponse(
            {"msg": str(err), "success": False},
            status=400,
        )
    finally:
        session.end_session()
