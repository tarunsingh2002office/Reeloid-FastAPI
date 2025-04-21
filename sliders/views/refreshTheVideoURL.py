from fastapi import Depends, Request, Body
from fastapi.responses import JSONResponse
from helper_function.checkSignedVideo import checkSignedVideo
from helper_function.apis_requests import get_current_user
async def refreshTheVideoURL(request:Request, token: str = Depends(get_current_user),body: dict = Body(
        example={
            "url": "https://abc.com"
        }
    )):

    try:
        body = await request.json()
        data = await checkSignedVideo(body.get("url"))
        return JSONResponse({"data": data}, status_code=200)
    except Exception as e:
        return JSONResponse({"err": str(e)}, status_code=400)