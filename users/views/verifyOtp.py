from fastapi import Request, Body
from fastapi.responses import JSONResponse
from core.database import forgotPasswordRequests
from datetime import datetime, timedelta, timezone
from helper_function.tokenCreator import tokenCreator
async def verifyOtp(request:Request, body: dict = Body(
        example={
            "otp": "123456"
        },
    )):
    body = await request.json()
    otp = body.get("otp")  # this is the request for getting already created otp
    try:
        fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
        existing_Requests = await forgotPasswordRequests.find_one_and_update(
            {
                "isUsed": False,
                "otp": int(otp),
                "createdTime": {"$gte": fifteen_min_ago},
                
            },
            {
                "$set": {
                    "isUsed": True,"status": "Pending",
                }
            },
            projection={"_id": True, "userId": True},
        )

        if not existing_Requests:
            return JSONResponse(
                {"msg": "No request found for changing otp in previous 15 minutes"},
                status_code=400,
            )
        id = await tokenCreator(
                    {
                        "otpId": str(existing_Requests["_id"]),
                        "id": str(existing_Requests["userId"]),
                    }
            )
        return JSONResponse(
            {
                "msg": "otp verified successFully",
                "id":  id
                
            },
            status_code=200,
        )
    except Exception as err:
        return JSONResponse({"msg": f"{err}"}, status_code=400)
