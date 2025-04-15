from core.database import (
    videoPurchasedLogs,
    users_collection,
    shorts_collection,
    client,
)
import json
from bson import ObjectId
from fastapi import Depends
from fastapi.responses import JSONResponse
from helper_function.checkSignedVideo import checkSignedVideo
from core.apis_requests import get_current_user, PurchasePremiumVideoRequest
async def purchasePremiumVideo(request:PurchasePremiumVideoRequest, token: str = Depends(get_current_user)):

        userId = request.state.userId

        session = client.start_session()
        session.start_transaction()
        try:
            
            bodyData = request.model_dump()

            currentShortsID = bodyData.get("shortsID")
            
            shortsData = shorts_collection.find_one(
                {"_id": ObjectId(currentShortsID)}, session=session
            )
            
            if not shortsData:
                session.abort_transaction()
                return JSONResponse({"err": "Invalid shorts Id"})
            videosPointsSpend = shortsData.get("purchasePoints") or 1
            purchaseThisShorts = videoPurchasedLogs.insert_one(
                {
                    "shorts_Id": currentShortsID,
                    "user_Id": (userId),
                },
                session=session,
            )
            if not purchaseThisShorts.acknowledged:
                session.abort_transaction()
                return JSONResponse(
                    {
                        "err": "unable to purchase the shorts... please try again or contact the customer support team "
                    },
                    status_code=400,
                )
            
            user = users_collection.find_one(
                {"_id": ObjectId(userId)}, {"allocatedPoints": 1}, session=session
            )
            if not user:
                session.abort_transaction()
                return JSONResponse(
                    {"err": "unable to find the user with the given user id "},
                    status_code=400,
                )
            userWalletPoints = user.get("allocatedPoints") or 0
            if userWalletPoints < videosPointsSpend:
                session.abort_transaction()
                return JSONResponse(
                    {
                        "msg": "Not enough mints to purchase this video ...please purchase some mints then try to unlock this Paid features"
                    },
                    status_code=400,
                )
            updateAllocationPoints = users_collection.update_one(
                {"_id": ObjectId(userId)},
                {"$inc": {"allocatedPoints": -videosPointsSpend}},
                session=session,
            )
            
            if updateAllocationPoints.modified_count == 0:
                session.abort_transaction()
                return JSONResponse(
                    {
                        "err": "problem while updating the allocating points after purchasing the video"
                    },
                    status_code=400,
                )
            session.commit_transaction()
            return JSONResponse(
                {
                    "medium": checkSignedVideo(shortsData.get("medium")),
                    "high": checkSignedVideo(shortsData.get("high")),
                },
                status_code=200,
            )
        except Exception as err:
            session.abort_transaction()
            return JSONResponse({"err": str(err)}, status_code=400)
        finally:
            session.end_session()