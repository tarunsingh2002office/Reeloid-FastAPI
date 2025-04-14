from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection

async def fetchWalletPoints(request:Request):
    userId = request.state.userId
    userData = users_collection.find_one(
        {"_id": ObjectId(userId)}, {"allocatedPoints": 1, "_id": 1}
    )

    if not userData:
        return JSONResponse(
            {"msg": "err while fetching the user. please provide a valid token"},
            status=400,
        )
    return JSONResponse(
        {"allocatedPoints": userData.get("allocatedPoints")}, status=200
    )