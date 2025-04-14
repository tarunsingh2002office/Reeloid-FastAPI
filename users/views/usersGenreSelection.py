import json
from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection, genre_collection

async def genreSelection(request:Request):

    try:
        body = await request.body
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status=400)
    selectedGenre = body.get(
        "selectedGenre"
    )  
    userId = request.userId
    if not selectedGenre:
        return JSONResponse({"msg": "could not get mandatory fields "}, status=400)

    if len(selectedGenre) == 0:
        return JSONResponse(
            {"msg": "no genre is selected,please select a genre"}, status=400
        )
    afterRemovingWrongGenre = []
    for genreId in selectedGenre:
        if ObjectId.is_valid(genreId):
            validGenre = genre_collection.find_one({"_id": ObjectId(genreId)})
            if validGenre:
                afterRemovingWrongGenre.append(genreId)

    if len(afterRemovingWrongGenre) == 0:
        return JSONResponse(
            {"msg": "no genre is selected,please select a genre"}, status=400
        )

    updatedData = users_collection.update_one(
        {"_id": ObjectId(userId)},
        {"$set": {"selectedGenre": afterRemovingWrongGenre}},
    )
    if updatedData:
        # validUser["selectedGenre"] = selectedGenre
        return JSONResponse(
            {
                "msg": "successfully selected the genre  ",
                "userData": "userResponse",
            },
            status=200,
        )
    else:
        return JSONResponse({"msg": "user is invalid"}, status=400)