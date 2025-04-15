from fastapi import Depends
from fastapi.responses import JSONResponse
from helper_function.checkSignedVideo import checkSignedVideo
from core.apis_requests import get_current_user, RefreshTheVideoURLRequest
async def refreshTheVideoURL(request:RefreshTheVideoURLRequest, token: str = Depends(get_current_user)):

    try:
        body = request.model_dump()
        data = checkSignedVideo(body.get("url"))
        return JSONResponse({"data": data}, status_code=200)
    except Exception as e:
        return JSONResponse({"err": str(e)}, status_code=400)