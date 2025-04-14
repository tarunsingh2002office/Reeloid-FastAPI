from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import layouts_collection, movies_collection

async def getDataRelatedToLayOuts(request:Request, layoutID):

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
