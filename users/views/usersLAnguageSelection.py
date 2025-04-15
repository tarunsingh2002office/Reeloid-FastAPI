import json
from bson import ObjectId
from fastapi import Depends
from fastapi.responses import JSONResponse
from core.database import languages_collection, users_collection
from core.apis_requests import get_current_user, UsersLanguaseSelectionRequest
async def usersLanguaseSelection(request:UsersLanguaseSelectionRequest,token:str=Depends(get_current_user)):
    try:
        body = request.model_dump()
    except json.JSONDecodeError:
        return JSONResponse({"msg": "Invalid JSON"}, status_code=400)
    selectedLanguages = body.get("selectedLanguages")
    if not selectedLanguages:
        return JSONResponse({"msg": "could not get mandatory fields "}, status_code=400)
    userId = request.state.userId
    if len(selectedLanguages) == 0:
        return JSONResponse(
            {"msg": "no language is selected,please select a language first"},
            status_code=400,
        )
    afterRemovingWrongLanguage = []
    for languageId in selectedLanguages:
        if ObjectId.is_valid(languageId):
            validGenre = languages_collection.find_one(
                {"_id": ObjectId(languageId)}
            )
            if validGenre:
                afterRemovingWrongLanguage.append(languageId)
    if len(afterRemovingWrongLanguage) == 0:
        return JSONResponse(
            {"msg": "no language is selected,please select a language first"},
            status_code=400,
        )
    updatedData = users_collection.update_one(
        {"_id": ObjectId(userId)},
        {"$set": {"selectedLanguages": afterRemovingWrongLanguage}},
    )
    if updatedData:
        # validUser["selectedGenre"] = selectedGenre
        return JSONResponse(
            {"msg": "successfully saved the languages  ", "success": True},
            status_code=200,
        )
    else:
        return JSONResponse({"msg": "user is invalid"})