from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import genre_collection
from helper_function.apis_requests import get_current_user
async def genreList(request: Request,token: str = Depends(get_current_user)):
    genresArray = []
    genrelist = genre_collection.find({}, {"_id": 1, "name": 1, "icon": 1})

    for genre in genrelist:
        genre["_id"] = str(genre["_id"])
        genresArray.append(genre)
    return JSONResponse({"genreList": genresArray}, status_code=200)

