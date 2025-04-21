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
import asyncio

async def purchasePremiumVideo(
    request: Request,
    token: str = Depends(get_current_user),
    body: dict = Body(
        example={
            "shortsID": "1234"
        }
    )
):
    max_retries = 3  
    try:
        bodyData = await request.json()
        currentShortsID = bodyData.get("shortsID")
        userId = request.state.userId

        if not currentShortsID:
            return JSONResponse({"err": "Shorts ID is required"}, status_code=400)
        if not userId:
            return JSONResponse({"err": "Invalid user"}, status_code=400)

        for attempt in range(max_retries):
            session = await client.start_session()
            session.start_transaction()
            try:
                shortsData = await shorts_collection.find_one(
                    {"_id": ObjectId(currentShortsID)}, session=session
                )
                if not shortsData:
                    session.abort_transaction()
                    return JSONResponse({"err": "Invalid shorts ID"}, status_code=404)

                videosPointsSpend = shortsData.get("purchasePoints") or 1

                purchaseThisShorts = await videoPurchasedLogs.insert_one(
                    {
                        "shorts_Id": currentShortsID,
                        "user_Id": userId,
                    },
                    session=session,
                )
                if not purchaseThisShorts.acknowledged:
                    session.abort_transaction()
                    return JSONResponse(
                        {
                            "err": "Unable to purchase the shorts. Please try again or contact customer support."
                        },
                        status_code=400,
                    )

                # Fetch user data
                user = await users_collection.find_one(
                    {"_id": ObjectId(userId)}, {"allocatedPoints": 1}, session=session
                )
                if not user:
                    session.abort_transaction()
                    return JSONResponse(
                        {"err": "Unable to find the user with the given user ID"},
                        status_code=404,
                    )

                userWalletPoints = user.get("allocatedPoints") or 0
                if userWalletPoints < videosPointsSpend:
                    session.abort_transaction()
                    return JSONResponse(
                        {
                            "msg": "Not enough points to purchase this video. Please purchase more points and try again."
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
                            "err": "Problem while updating the allocated points after purchasing the video."
                        },
                        status_code=400,
                    )

                session.commit_transaction()

                return JSONResponse(
                    {
                        "medium": await checkSignedVideo(shortsData.get("medium")),
                        "high": await checkSignedVideo(shortsData.get("high")),
                    },
                    status_code=200,
                )
            except Exception as err:
                if session and session.in_transaction:
                    session.abort_transaction()
                if "TransientTransactionError" in str(err) and attempt < max_retries - 1:
                    await asyncio.sleep(0.1)  # Small delay before retrying
                    continue
                return JSONResponse({"err": f"Error: {str(err)}"}, status_code=500)
            finally:
                session.end_session()
    except Exception as err:
        return JSONResponse({"err": f"Unexpected error: {str(err)}"}, status_code=500)