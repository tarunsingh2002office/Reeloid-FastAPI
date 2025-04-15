from bson import ObjectId
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import users_collection
from helper_function.apis_requests import get_current_user
async def fetchWalletPoints(request:Request, token: str = Depends(get_current_user)):
    userId = request.state.userId
    userData = users_collection.find_one(
        {"_id": ObjectId(userId)}, {"allocatedPoints": 1, "_id": 1}
    )

    if not userData:
        return JSONResponse(
            {"msg": "err while fetching the user. please provide a valid token"},
            status_code=400,
        )
    return JSONResponse(
        {"allocatedPoints": userData.get("allocatedPoints")}, status_code=200
    )