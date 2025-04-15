from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import movies_collection, shorts_collection
from core.apis_requests import get_current_user
async def TrailerTrendingSection(request:Request,token: str = Depends(get_current_user)):

    moviesData = (
        movies_collection.find(
            {},
            {"_id": 1, "name": 1, "shorts": 1, "trailerUrl": 1, "fileLocation": 1},
        )
        .sort("views", -1)
        .limit(10)
    )
    moviesArray = []
    for movie in moviesData:

        movie["_id"] = str(movie["_id"])
        shortsArray = []
        for shortid in movie["shorts"]:
            if shortid != "Ads":
                shortsData = shorts_collection.find_one(
                    {"_id": shortid, "visible": True},
                    {"_id": 1, "name": 1, "fileLocation": 1},
                )
                if shortsData:
                    shortsData["_id"] = str(shortsData["_id"])
                    shortsArray.append(shortsData)

        movie["shorts"] = shortsArray
        moviesArray.append(movie)
    return JSONResponse({"trailersData": moviesArray}, status_code=200)
