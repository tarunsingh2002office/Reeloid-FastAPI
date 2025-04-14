from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import layouts_collection, movies_collection

def getLayouts(request:Request):

    layoutsResult = layouts_collection.find(
        {"visible": True}, {"_id": 1, "linkedMovies": 1, "name": 1}
    )

    layOutsData = {}
    for layout in layoutsResult:

        currentLayoutObj = []
        linkedMovies = layout["linkedMovies"]

        currentLayoutObj.append(
            {"layoutId": str(layout["_id"]), "layoutName": layout["name"]}
        )
        for currentMovie in linkedMovies:
            # print(currentMovie, "currentMovie")
            movieData = movies_collection.find_one(
                {"_id": currentMovie,"visible": True}, {"fileLocation": 1, "name": 1,"screenType":1}
            )

            if movieData:
                movieData["_id"] = str(movieData["_id"])

                currentLayoutObj.append(movieData)
            layOutsData[str(layout["_id"])] = currentLayoutObj

    return JSONResponse({"layouts": layOutsData})

