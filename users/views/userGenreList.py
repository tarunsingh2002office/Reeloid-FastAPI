from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import genre_collection

async def genreList(request: Request):
    genresArray = []
    genrelist = genre_collection.find({}, {"_id": 1, "name": 1, "icon": 1})

    for genre in genrelist:
        genre["_id"] = str(genre["_id"])
        genresArray.append(genre)
    return JSONResponse({"genreList": genresArray}, status=200)

