from bson import ObjectId
from fastapi import Request, Body, Depends
from fastapi.responses import JSONResponse
from core.database import layouts_collection, movies_collection
from helper_function.apis_requests import get_current_user
async def getDataRelatedToLayOuts(request:Request, layoutID: str, 
                                   token: str = Depends(get_current_user)):

    result = layouts_collection.find({"_id": ObjectId(layoutID), "visible": True})
    movieObj = []

    for layout in result:

        # print(layout)
        linkedMovies = layout["linkedMovies"]

        for currentMovieId in linkedMovies:
            #   print(currentMovieId)
            movieData = movies_collection.find_one(
                {"_id": ObjectId(currentMovieId), "visible": True},
                {"fileLocation": 1, "name": 1, "screenType": 1},
            )

            if movieData:
                movieData["_id"] = str(movieData["_id"])
                movieObj.append(movieData)

    return JSONResponse({"moviesList": movieObj})
