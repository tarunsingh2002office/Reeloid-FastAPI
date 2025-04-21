from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import languages_collection
from helper_function.apis_requests import get_current_user
from helper_function.serialize_mongo_document import serialize_document

async def usersContentLanguageList(request: Request, token: str = Depends(get_current_user)):
    
    try:
        languageArray = []
        languageList = languages_collection.find()

        async for language in languageList:
            serialized_language = await serialize_document(language)  # Serialize the document
            languageArray.append(serialized_language)

        return JSONResponse({"languageList": languageArray}, status_code=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=500)