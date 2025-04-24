from core.database import (
    videoPurchasedLogs,
    users_collection,
    shorts_collection,
    client,
)
from bson import ObjectId
from fastapi import Depends, Request, Body
from fastapi.responses import JSONResponse
from helper_function.checkSignedVideo import checkSignedVideo
from helper_function.apis_requests import get_current_user

async def purchasePremiumVideo(
    request: Request,
    token: str = Depends(get_current_user),
    body: dict = Body(
        example={
            "shortsID": "1234"
        }
    )
):
    try:
        bodyData = await request.json()
        currentShortsID = bodyData.get("shortsID")
        userId = request.state.userId

        if not currentShortsID:
            return JSONResponse({"err": "Shorts ID is required"}, status_code=400)
        if not userId:
            return JSONResponse({"err": "Invalid user"}, status_code=400)
        
        user = await users_collection.find_one(
                    {"_id": ObjectId(userId)}, {"allocatedPoints": 1}
                )
        
        if not user:
            return JSONResponse(
                {"err": "Unable to find the user with the given user ID"},
                status_code=404,
            )
        
        shortsData = await shorts_collection.find_one(
                    {"_id": ObjectId(currentShortsID)}
                )
        
        if not shortsData:
            return JSONResponse({"err": "Invalid shorts ID"}, status_code=404)
        
        videosPointsSpend = shortsData.get("purchasePoints") or 1
        userWalletPoints = user.get("allocatedPoints") or 0

        if userWalletPoints < videosPointsSpend:
            return JSONResponse(
                {
                    "msg": "Not enough points to purchase this video. Please purchase more points and try again."
                },
                status_code=400,
            )
        
        async with await client.start_session() as session:
            async def txn(sess):
                purchaseThisShorts = await videoPurchasedLogs.insert_one(
                    {
                        "shorts_Id": currentShortsID,
                        "user_Id": userId,
                    },
                    session=sess,
                )
                if not purchaseThisShorts.acknowledged:
                    raise Exception("Purchase record creation failed")  # Proper error handling
                
                updateAllocationPoints = await users_collection.update_one(
                    {"_id": ObjectId(userId)},
                    {"$inc": {"allocatedPoints": -videosPointsSpend}},
                    session=sess,
                )
                if updateAllocationPoints.modified_count == 0:
                    raise Exception("Points update failed")
            try:
                await session.with_transaction(txn)
            except Exception as err:
                return JSONResponse({"err": f"Error: {str(err)}"}, status_code=500) 

        return JSONResponse(
            {
                "medium": await checkSignedVideo(shortsData.get("medium")),
                "high": await checkSignedVideo(shortsData.get("high")),
            },
            status_code=200,
        )
    except Exception as err:
        return JSONResponse({"err": f"Unexpected error: {str(err)}"}, status_code=500)