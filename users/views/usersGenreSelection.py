import json
from bson import ObjectId
from fastapi import Depends,Request,Body
from fastapi.responses import JSONResponse
from core.database import users_collection, genre_collection
from helper_function.apis_requests import get_current_user
async def genreSelection(request:Request, token: str = Depends(get_current_user),body: dict = Body(
        example={
            "selectedGenre": ["1234", "2345"]
        }
    )):

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)
    selectedGenre = body.get(
        "selectedGenre"
    )  
    userId = request.state.userId
    if not selectedGenre:
        return JSONResponse({"msg": "could not get mandatory fields "}, status_code=400)

    if len(selectedGenre) == 0:
        return JSONResponse(
            {"msg": "no genre is selected,please select a genre"}, status_code=400
        )
    afterRemovingWrongGenre = []
    for genreId in selectedGenre:
        if ObjectId.is_valid(genreId):
            validGenre = genre_collection.find_one({"_id": ObjectId(genreId)})
            if validGenre:
                afterRemovingWrongGenre.append(genreId)

    if len(afterRemovingWrongGenre) == 0:
        return JSONResponse(
            {"msg": "no genre is selected,please select a genre"}, status_code=400
        )

    updatedData = users_collection.update_one(
        {"_id": ObjectId(userId)},
        {"$set": {"selectedGenre": afterRemovingWrongGenre}},
    )
    if updatedData:
        return JSONResponse(
            {
                "msg": "successfully selected the genre  ",
                "userData": "userResponse",
            },
            status_code=200,
        )
    else:
        return JSONResponse({"msg": "user is invalid"}, status_code=400)