from bson import ObjectId
from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import users_collection,genre_collection,languages_collection

async def getProfileDetails(request:Request):
    try:
        userId = request.state.userId
        userDetails = users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"userDetails": []}, status=200)
        userDetails["_id"] = str(userDetails["_id"])

        genreList = []
        if "selectedGenre" in userDetails and userDetails["selectedGenre"]:
            for genreId in userDetails["selectedGenre"]:
                genreData = genre_collection.find_one(
                    {"_id": ObjectId(genreId)}, {"_id": 1, "name": 1, "icon": 1}
                )
                genreData["_id"] = str(genreData["_id"])
                genreList.append(genreData)
        userDetails["selectedGenre"] = genreList
        languageList = []

        if (
            "selectedLanguages" in userDetails
            and userDetails["selectedLanguages"]
        ):
            for languageId in userDetails["selectedLanguages"]:
                languageData = languages_collection.find_one(
                    {"_id": ObjectId(languageId)}, {"_id": 1, "name": 1}
                )
                languageData["_id"] = str(languageData["_id"])
                languageList.append(languageData)
        userDetails["selectedLanguages"] = languageList
        return JSONResponse({"userDetails": userDetails}, status=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)})
