from bson import ObjectId
from fastapi import Depends
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime, timezone
from helper_function.passwordEncryption import passwordEncryption
from core.database import forgotPasswordRequests, users_collection
from helper_function.updatedPasswordConfirmation import updatedPasswordConfirmation
from core.apis_requests import UpdatePasswordRequest, get_current_user
async def updatePassword(request:UpdatePasswordRequest,token: str = Depends(get_current_user)):
    body = request.model_dump()
    userId = request.state.userId
    passwordRequestId = request.state.otpId
    
    if not passwordRequestId:
        return JSONResponse({"msg": "invalid password request id "}, status_code=400)

    password = body.get("password")
    confirmPassword = body.get("confirmPassword")
    if not password:
        return JSONResponse(
            {"msg": "no password data found in request"}, status_code=400
        )
    if confirmPassword != password:
        return JSONResponse(
            {"msg": "password and confirm password are not same"}, status_code=400
        )
    try:
        fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
        existing_Requests = forgotPasswordRequests.find_one(
            {
                "isUsed": True,
                "_id": ObjectId(passwordRequestId),
                "userId": ObjectId(userId),
                "createdTime": {"$gte": fifteen_min_ago},
            },
            {"userId": 1, "status": 1},
        )
        

        if not existing_Requests:
            return JSONResponse(
                {"msg": "No request found for changing otp in previous 15 minutes"},
                status_code=400,
            )
        if existing_Requests["status"] == "Success":
            return JSONResponse(
                {"msg": "Password already changed with given request"}, status_code=400
            )
        hashedPassword = passwordEncryption(password)
        updatedPassword = users_collection.find_one_and_update(
            {
                "_id": ObjectId(userId),
            },
            {"$set": {"password": hashedPassword}},
            projection={"name": True, "email": True},
        )
        print(updatedPassword)
        updatedPasswordConfirmation(
            {
                "name": updatedPassword.get("name"),
                "email": updatedPassword.get("email"),
            }
        )
        forgotPasswordRequests.update_one(
            {"_id": ObjectId(passwordRequestId)}, {"$set": {"status": "Success"}}
        )
        return JSONResponse({"msg": "Password Changed Successfully"}, status_code=200)
    except Exception as err:

        return JSONResponse({"msg": f"{err}"}, status_code=400)
