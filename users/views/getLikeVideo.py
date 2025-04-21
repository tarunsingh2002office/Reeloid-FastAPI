from fastapi.responses import JSONResponse
from core.database import users_collection, shorts_collection
from bson import ObjectId
from fastapi import Request, Depends, Body
from helper_function.apis_requests import get_current_user
async def getLikedVideo(request:Request,token: str = Depends(get_current_user),body: dict = Body(
        example={
            "shortsId": ["1234","23456"]
        }
    )):
    body =  await request.json()
    userId = request.state.userId
    shortsId = body.get("shortsId")
    user = await users_collection.find_one(
        {"_id": ObjectId(userId)},
    )
    if not user:
        return JSONResponse({"msg": "no user found"}, status_code=400)
    try:

        if user and user["LikedVideos"]:

            LikedVideosData = []
            for shortsId in user["LikedVideos"]:
                
                shortsData = await shorts_collection.find_one(
                    {
                        "_id": ObjectId(shortsId),
                    },
                    {"genre": 0, "language": 0},
                )
               
                if shortsData:
                    shortsData["_id"] = str(shortsData["_id"])
                    LikedVideosData.append(shortsData)

            return JSONResponse(
                {"msg": "Liked Videos data is here", "LikedVideos": LikedVideosData},
                status_code=200,
            )
        else:
            return JSONResponse(
                {"msg": "Liked Videos data not found", "LikedVideos": []}, status_code=200
            )

    except:
        return JSONResponse({"msg": "something went wrong"}, status_code=500)
