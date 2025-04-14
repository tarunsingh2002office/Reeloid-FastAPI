from fastapi import Request
from fastapi.responses import JSONResponse
from helper_function.checkSignedVideo import checkSignedVideo

async def refreshTheVideoURL(request:Request):

    try:
        body = await request.body
        data = checkSignedVideo(body.get("url"))
        return JSONResponse({"data": data}, status=200)
    except Exception as e:
        return JSONResponse({"err": str(e)}, status=400)