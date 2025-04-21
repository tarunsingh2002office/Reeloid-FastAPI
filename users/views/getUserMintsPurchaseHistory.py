# new code for mints history plan->(
from fastapi.responses import JSONResponse
from core.database import (
    users_collection,
    paidMintsBuyerCollection,
)
from bson import ObjectId
from fastapi import Request,Depends
from helper_function.apis_requests import get_current_user
from helper_function.serialize_mongo_document import serialize_document

async def getUserMintPurchaseHistory(request:Request,token: str = Depends(get_current_user)):
    try:
        userId = request.state.userId
        if not userId:
            return JSONResponse({"msg": "userId is missing"}, status_code=400)

        userDetails = await users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"msg": "no user found"}, status_code=400)

        userMintsPurchaseHistory = paidMintsBuyerCollection.find(
            {"userId": userId},
            {
                "_id": 1,
                "txnid": 1,
                "date": 1,
                "netAmountDeducted": 1,
                "status": 1,
                "quantity": 1,
                "amount": 1,
            },
        )

        if not userMintsPurchaseHistory:
            return JSONResponse({"msg": "no purchase history found"}, status_code=400)

        history = [await serialize_document(planPurchaseData) async for planPurchaseData in userMintsPurchaseHistory]

        return JSONResponse({"userMintsPurchaseHistory": history}, status_code=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=500)

   