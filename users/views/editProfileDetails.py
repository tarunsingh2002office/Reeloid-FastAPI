import json
from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection

async def editProfileDetails(request:Request):
    try:
        body = await request.body
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
        return JSONResponse({"msg": "data updated successFully..."}, status=200)
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status=400)
