import hashlib, time, os
from core.database import users_collection
from bson import ObjectId
import hashlib
import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from core.config import TENANT_KEY


def is_valid_signature(path: str, t: str, sign: str) -> bool:
    if not t or not sign:
        return False
    try:
        expiry_time = int(t, 16)
        if time.time() > expiry_time:
            return False

        # Extract video_id
        path_parts = path.strip("/").split("/")  # ['drm_stream', 'video_id']
        if len(path_parts) < 2:
            return False

        video_id = path_parts[-1]
        path_to_sign = "/".join(path_parts[:-1]) + "/"

        key = TENANT_KEY.TENANT_KEY + video_id
        signature_raw = f"{key}/{path_to_sign}/{t}"
        expected_signature = hashlib.md5(signature_raw.encode("utf-8")).hexdigest()

        return expected_signature == sign
    except:
        return False


async def drm_stream(video_id: str, request: Request, user_id: str, t: str, sign: str):
    if not user_id:
        raise HTTPException(status_code=403, detail="Missing user ID.")

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=403, detail="User not found.")

        if not is_valid_signature(str(request.url.path), t, sign):
            raise HTTPException(status_code=403, detail="Invalid or expired signature.")

        file_path = os.path.join(TENANT_KEY.MEDIA_ROOT, video_id)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found.")

        return FileResponse(file_path, media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))