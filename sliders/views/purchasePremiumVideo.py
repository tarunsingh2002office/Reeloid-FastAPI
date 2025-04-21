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
async def purchasePremiumVideo(request:Request, token: str = Depends(get_current_user),body: dict = Body(
        example={
            "shortsID": "1234"
        }
    )):

        userId = request.state.userId

        session = await client.start_session()
        session.start_transaction()
        try:
            
            bodyData = await request.json()

            currentShortsID = bodyData.get("shortsID")
            
            shortsData = await shorts_collection.find_one(
                {"_id": ObjectId(currentShortsID)}, session=session
            )
            
            if not shortsData:
                session.abort_transaction()
                return JSONResponse({"err": "Invalid shorts Id"})
            videosPointsSpend = shortsData.get("purchasePoints") or 1
            purchaseThisShorts = await videoPurchasedLogs.insert_one(
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
            
            user = await users_collection.find_one(
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
            updateAllocationPoints = await users_collection.update_one(
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