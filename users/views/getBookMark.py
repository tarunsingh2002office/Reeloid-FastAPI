from fastapi import Request, Depends
from bson import ObjectId
from fastapi.responses import JSONResponse
from helper_function.apis_requests import get_current_user
from core.database import users_collection, shorts_collection
from helper_function.serialize_mongo_document import serialize_document

async def getBookMark(request:Request, token: str = Depends(get_current_user)):

    userId = request.state.userId
    
    user = users_collection.find_one(
        {"_id": ObjectId(userId)},
    )
    if not user:
        return JSONResponse({"msg": "no user found"}, status_code=400)
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
                            serialized_shortsData = serialize_document(shortsData)
                            bookMarkData.append(serialized_shortsData)


            return JSONResponse(
                {"msg": "bookmarked data is here", "bookMarkData": bookMarkData},
                status_code=200,
            )
        else:
            return JSONResponse(
                {"msg": "bookmarked data not found", "bookMarkData": []}, status_code=200
            )

    except Exception as err:
        return JSONResponse(
            {"msg": "something went wrong", "err": str(err)}, status_code=500
        )
