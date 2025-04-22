from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import movies_collection, shorts_collection
from helper_function.apis_requests import get_current_user

async def TrailerTrendingSection(request: Request, token: str = Depends(get_current_user)):
    try:
        # Build aggregation pipeline to fetch top 10 trailers with their visible shorts
        pipeline = [
            {"$sort": {"views": -1}},
            {"$limit": 10},
            {"$project": {
                "_id": 1,
                "name": 1,
                "views": 1,       
                "shorts": 1,
                "trailerUrl": 1,
                "fileLocation": 1
            }},
            {"$unwind": {"path": "$shorts", "preserveNullAndEmptyArrays": True}},
            {"$match": {"shorts": {"$ne": "Ads"}}},
            {"$lookup": {
                "from": shorts_collection.name,
                "let": {"shortId": "$shorts"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$shortId"]}}},
                    {"$match": {"visible": True}},
                    {"$project": {"_id": {"$toString": "$_id"}, "name": 1, "fileLocation": 1}}
                ],
                "as": "shortData"
            }},
            {"$unwind": {"path": "$shortData", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$_id",
                "name": {"$first": "$name"},
                "views": {"$first": "$views"},     
                "trailerUrl": {"$first": "$trailerUrl"},
                "fileLocation": {"$first": "$fileLocation"},
                "shorts": {"$push": "$shortData"}
            }},
            {"$sort": {"views": -1}},
            {"$project": {
                "_id": {"$toString": "$_id"},
                "name": 1,
                "trailerUrl": 1,
                "fileLocation": 1,
                "shorts": 1
            }}
        ]

        # Execute aggregation
        cursor = movies_collection.aggregate(pipeline)
        trailers = []  
        async for doc in cursor:
            trailers.append(doc)

        return JSONResponse({"trailersData": trailers}, status_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)