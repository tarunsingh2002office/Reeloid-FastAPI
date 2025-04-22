from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from helper_function.apis_requests import get_current_user
from core.database import layouts_collection, movies_collection

async def getLayouts(request: Request, token: str = Depends(get_current_user)):

    # Fetch all visible layouts
    layouts_cursor = layouts_collection.find(
        {"visible": True}, {"_id": 1, "linkedMovies": 1, "name": 1}
    )
    layouts = await layouts_cursor.to_list(length=None)

    # Collect all unique movie ObjectIds
    all_movie_ids = set()
    for layout in layouts:
        all_movie_ids.update(layout.get("linkedMovies", []))

    # Bulk fetch all movies
    movie_cursor = movies_collection.find(
        {"_id": {"$in": list(all_movie_ids)}, "visible": True},
        {"fileLocation": 1, "name": 1, "screenType": 1}
    )
    movie_list = await movie_cursor.to_list(length=None)
    movie_map = {movie["_id"]: movie for movie in movie_list}

    # Construct response layout-wise
    layOutsData = {}
    for layout in layouts:
        layout_id_str = str(layout["_id"])
        currentLayoutObj = [{
            "layoutId": layout_id_str,
            "layoutName": layout["name"]
        }]

        for movie_id in layout.get("linkedMovies", []):
            movie = movie_map.get(movie_id)
            if movie:
                movie["_id"] = str(movie["_id"])
                currentLayoutObj.append(movie)

        layOutsData[layout_id_str] = currentLayoutObj

    return JSONResponse({"layouts": layOutsData})
