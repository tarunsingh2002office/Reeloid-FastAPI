from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from core.database import mintsPlanCollection
from helper_function.apis_requests import get_current_user
async def getPackage(request:Request, token: str = Depends(get_current_user)):
    try:
        mintsPlanResponse = mintsPlanCollection.find()
        
        mintsPlanList = []
        if not mintsPlanResponse:
            return JSONResponse({"data": []}, status_code=200)
        for plans in mintsPlanResponse:
            
            plans["_id"] = str(plans.get("_id"))
            mintsPlanList.append(plans)
        return JSONResponse({"mintsPlanList": mintsPlanList}, status_code=200)
    except Exception as err:
        return JSONResponse({"msg": str(err)}, status_code=400)
