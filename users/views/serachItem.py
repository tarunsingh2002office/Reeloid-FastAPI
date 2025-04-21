from fastapi import Request, Depends,Query
from fastapi.responses import JSONResponse
from core.database import movies_collection
from helper_function.apis_requests import get_current_user
async def serachItem(request: Request,token: str = Depends(get_current_user),
                     name: str = Query(...)):
    if not name:
        return JSONResponse(
            {"msg": "searched item is invalid", "status": False}, status_code=404
        )
    searchedResult = movies_collection.find(
        {"name": {"$regex": name, "$options": "i"}},
        {"_id": 1, "name": 1, "fileLocation": 1},
    )

    moviesList = []
    async for data in searchedResult:

        data["_id"] = str(data.get("_id"))
        moviesList.append(data)
    if len(moviesList) == 0:
        return JSONResponse(
            {
                "msg": "no data Found for serached Query",
                "data": moviesList,
                "success": False,
            },
            status_code=200,
        )
    return JSONResponse(
        {"msg": "got it", "data": moviesList, "success": False}, status_code=200
    )