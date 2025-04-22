from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from helper_function.apis_requests import get_current_user
from core.database import layouts_collection, movies_collection

async def getLayouts(request: Request, token: str = Depends(get_current_user)):
    try:
        # Aggregation pipeline to fetch visible layouts with their linked, visible movies
        pipeline = [
            {"$match": {"visible": True}},
            {"$project": {"_id": 1, "name": 1, "linkedMovies": 1}},
            {"$unwind": {"path": "$linkedMovies", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": movies_collection.name,
                "let": {"movieId": "$linkedMovies"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$_id", "$$movieId"]},
                        {"$eq": ["$visible", True]}
                    ]}}},
                    {"$project": {"_id": 1, "fileLocation": 1, "name": 1, "screenType": 1}}
                ],
                "as": "movieData"
            }},
            {"$unwind": {"path": "$movieData", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$_id",
                "layoutName": {"$first": "$name"},
                "movies": {"$push": "$movieData"}
            }},
            {"$project": {
                "_id": {"$toString": "$_id"},
                "layoutName": 1,
                "movies": {
                    "$map": {
                        "input": "$movies",
                        "as": "m",
                        "in": {
                            "_id": {"$toString": "$$m._id"},
                            "fileLocation": "$$m.fileLocation",
                            "name": "$$m.name",
                            "screenType": "$$m.screenType"
                        }
                    }
                }
            }}
        ]

        cursor = layouts_collection.aggregate(pipeline)
        layOutsData = {}
        async for doc in cursor:
            # Build the list: first the layout info, then its movies
            items = [
                {"layoutId": doc["_id"], "layoutName": doc["layoutName"]}
            ] + doc.get("movies", [])
            layOutsData[doc["_id"]] = items

        return JSONResponse({"layouts": layOutsData}, status_code=200)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
