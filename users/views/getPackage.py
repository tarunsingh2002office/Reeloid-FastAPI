from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import mintsPlanCollection

async def getPackage(request:Request):
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
