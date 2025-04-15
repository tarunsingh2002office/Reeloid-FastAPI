from fastapi import Request,Depends
from fastapi.responses import JSONResponse
from core.database import movies_collection
from helper_function.apis_requests import get_current_user
async def UserTrendingVideos(request:Request,token: str = Depends(get_current_user)):
    trending_movies = (
        movies_collection.find({}, {"_id": 1, "name": 1, "fileLocation": 1})
        .sort("views", -1)
        .limit(10)
    )
    trending_movies_list = []
    for movies in trending_movies:

        movies["_id"] = str(movies["_id"])
        trending_movies_list.append(movies)
    return JSONResponse({"movies": trending_movies_list}, status_code=200)
