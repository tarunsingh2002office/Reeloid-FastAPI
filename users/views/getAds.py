from fastapi import Request
from fastapi.responses import JSONResponse
from core.database import adsCollection

async def getAds(request:Request, path, sessionType):

    if not path:
        return JSONResponse({"msg": "path is not present"}, status_code=400)
    pathname = f"/{path.lower()}"
    sessionType = sessionType
    try:
        adsResponse = adsCollection.find(
            {"position": pathname, "sessionType": sessionType},
            {"type": 1, "sessionType": 1, "provider": 1},
        )

        adsList = []
        if not adsResponse:
            return JSONResponse({"msg": "no data "})
        for ads in adsResponse:

            ads["_id"] = str(ads.get("_id"))
            adsList.append(ads)
        if not adsList:
            return JSONResponse(
                {"msg": "no ads  data found", "adsList": adsList}, status_code=200
            )
        return JSONResponse(
            {"msg": "hello getting ads are you ready to fire", "adsList": adsList}
        )
    except:
        return JSONResponse({"msg": "something went wrong"}, status_code=500)

