import json
import asyncio
from pymongo.errors import OperationFailure
from fastapi import Request,Body
from fastapi.responses import JSONResponse
from core.database import users_collection, client
from helper_function.emailSender import emailSender
from helper_function.saveUserInDataBase import saveUserInDataBase

async def createUser(request: Request,body: dict = Body(
        example={
            "email": "tarunsingh2002office@gmail.com",
            "name": "Mr. Tarun Singh",    
            "password": "1234",
            "confirmPassword": "1234",
        }
    )):
    try:
        body =  await request.json()
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
    
    try:
        user = await users_collection.find_one({"email": email})
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)

    if user:
        return JSONResponse(
            {"msg": "user is already registered with us with this email"},
            status_code=400,
        )
    
    max_retries = 3
    for attempt in range(max_retries):
        session = await client.start_session()
        session.start_transaction()
        try:
            # Save user in the database
            userCreated = await saveUserInDataBase(
                {"name": name, "email": email, "password": password, "session": session}
            )
            session.commit_transaction()

            # Send email after committing the transaction
            await emailSender({"name": name, "email": email})
            return JSONResponse(
                {"msg": "added user successfully", "success": True}, status_code=200
            )
        except OperationFailure as err:
            if session.in_transaction:
                session.abort_transaction()
            if "TransientTransactionError" in str(err) and attempt < max_retries - 1:
                await asyncio.sleep(0.1)  # Small delay before retrying
                continue
            return JSONResponse(
                {"msg": "Database operation failed: " + str(err), "success": False},
                status_code=500,
            )
        except Exception as err:
            if session.in_transaction:
                session.abort_transaction()
            return JSONResponse(
                {"msg": "An unexpected error occurred: " + str(err), "success": False},
                status_code=500,
            )
        finally:
            session.end_session()