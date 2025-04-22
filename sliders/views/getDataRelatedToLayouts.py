from bson import ObjectId
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import layouts_collection, movies_collection
from helper_function.apis_requests import get_current_user

async def getDataRelatedToLayOuts(
    request: Request,
    layoutID: str,
    token: str = Depends(get_current_user)
):
    try:
        # Aggregation pipeline to fetch a single visible layout's linked, visible movies
        pipeline = [
            {"$match": {"_id": ObjectId(layoutID), "visible": True}},
            {"$project": {"linkedMovies": 1}},
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
                "movies": {"$push": "$movieData"}
            }},
            {"$project": {
                "_id": 0,
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
        docs = await cursor.to_list(length=1)
        movies_list = docs[0]["movies"] if docs else []

        return JSONResponse({"moviesList": movies_list}, status_code=200)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
