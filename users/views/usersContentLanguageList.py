from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import languages_collection
from core.apis_requests import get_current_user

async def usersContentLanguageList(request:Request,token: str = Depends(get_current_user)):
        languageArray = []
        languageList = languages_collection.find()
        
        for language in languageList:
            language['_id']=str(language['_id'])
            languageArray.append(language)
        return JSONResponse({"languageList": languageArray},status_code=200)
