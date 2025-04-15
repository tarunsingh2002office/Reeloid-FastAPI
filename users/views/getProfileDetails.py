from bson import ObjectId
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from helper_function.apis_requests import get_current_user
from helper_function.serialize_mongo_document import serialize_document
from core.database import users_collection, genre_collection, languages_collection

async def getProfileDetails(request: Request, token: str = Depends(get_current_user)):
    try:
        userId = request.state.userId
        userDetails = users_collection.find_one(
            {"_id": ObjectId(userId)},
            {"password": 0},
        )
        if not userDetails:
            return JSONResponse({"userDetails": []}, status_code=200)

        # Serialize the userDetails document
        userDetails = serialize_document(userDetails)

        genreList = []
        if "selectedGenre" in userDetails and userDetails["selectedGenre"]:
            for genreId in userDetails["selectedGenre"]:
                genreData = genre_collection.find_one(
                    {"_id": ObjectId(genreId)}, {"_id": 1, "name": 1, "icon": 1}
                )
                if genreData:
                    serialized_genreData = serialize_document(genreData)
                    genreList.append(serialized_genreData)
        userDetails["selectedGenre"] = genreList

        languageList = []
        if "selectedLanguages" in userDetails and userDetails["selectedLanguages"]:
            for languageId in userDetails["selectedLanguages"]:
                languageData = languages_collection.find_one(
                    {"_id": ObjectId(languageId)}, {"_id": 1, "name": 1}
                )
                if languageData:
                    serialized_languageData = serialize_document(languageData)
                    languageList.append(serialized_languageData)
        userDetails["selectedLanguages"] = languageList

        return JSONResponse({"userDetails": userDetails}, status_code=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=500)