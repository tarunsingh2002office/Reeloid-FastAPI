from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import languages_collection


async def usersContentLanguageList(request:Request):
        languageArray = []
        languageList = languages_collection.find()
        
        for language in languageList:
            language['_id']=str(language['_id'])
            languageArray.append(language)
        return JSONResponse({"languageList": languageArray},status=200)
