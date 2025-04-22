from bson import ObjectId
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import layouts_collection, movies_collection
from helper_function.apis_requests import get_current_user

async def getDataRelatedToLayOuts(request: Request, layoutID: str, 
                                   token: str = Depends(get_current_user)):

    # Start timing for performance measurement

    # Fetch layout document with the specified layoutID and visible flag
    result = await layouts_collection.find_one({"_id": ObjectId(layoutID), "visible": True})
    movieObj = []

    if result:
        linkedMovies = result.get("linkedMovies", [])
        movie_ids = [ObjectId(mid) for mid in linkedMovies]

        # Fetch all movies at once using the $in operator
        cursor = movies_collection.find(
            {"_id": {"$in": movie_ids}, "visible": True},
            {"fileLocation": 1, "name": 1, "screenType": 1}  # Only return necessary fields
        )

        # Convert cursor to list to fetch all at once and reduce iteration overhead
        movies = await cursor.to_list(length=len(movie_ids))

        # Process the movies and convert the _id field to a string
        for movieData in movies:
            movieData["_id"] = str(movieData["_id"])
            movieObj.append(movieData)


    return JSONResponse({"moviesList": movieObj})
