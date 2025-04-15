import json
from bson import ObjectId
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from core.database import users_collection
from helper_function.apis_requests import  get_current_user
async def editProfileDetails(request: Request, token: str = Depends(get_current_user),body: dict = Body(
        example={
            "name": "Mr. a",
            "email": "a@gmailcom",
            "gender": "male",
            "mobile": "1234567890"
        }
    )):
    try:
        body = await request.json()
        email = body.get("email")
        name = body.get("name")
        gender = body.get("gender")
        mobile = body.get("mobile")

        userId = request.state.userId
        
        userDetails = users_collection.find_one_and_update(
            {"_id": ObjectId(userId)},
            {
                "$set": {
                    "email": email,
                    "mobile": mobile,
                    "name": name,
                    "gender": gender,
                }
            },
        )

        userDetails["_id"] = str(userDetails["_id"])
        return JSONResponse({"msg": "data updated successFully..."}, status_code=200)
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)
