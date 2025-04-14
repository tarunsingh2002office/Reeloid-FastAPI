from fastapi import Request
from bson import ObjectId
from fastapi.responses import JSONResponse
from core.database import users_collection, shorts_collection

async def getBookMark(request:Request):

    userId = request.state.userId
    
    user = users_collection.find_one(
        {"_id": ObjectId(userId)},
    )
    if not user:
        return JSONResponse({"msg": "no user found"}, status=400)
    try:

        if user and user.get("BookMark"):

            bookMarkData = []
            for shortsId in user["BookMark"]:

                if shortsId:

                    if ObjectId.is_valid(shortsId):

                        shortsData = shorts_collection.find_one(
                            {
                                "_id": ObjectId(shortsId),
                            },
                            {"genre": 0, "language": 0},
                        )

                        if shortsData:
                            shortsData["_id"] = str(shortsData["_id"])
                            bookMarkData.append(shortsData)

            return JSONResponse(
                {"msg": "bookmarked data is here", "bookMarkData": bookMarkData},
                status=200,
            )
        else:
            return JSONResponse(
                {"msg": "bookmarked data not found", "bookMarkData": []}, status=200
            )

    except Exception as err:
        return JSONResponse(
            {"msg": "something went wrong", "err": str(err)}, status=500
        )
