from fastapi import APIRouter

from utils.views.checksignedVideo import check_signed_video
from utils.views.drmstream import drm_stream

router = APIRouter(prefix="/utils", tags=["Utils"])


router.add_api_route("/check_signed_video", check_signed_video, methods=["POST"])
router.add_api_route("/drm_stream/{video_id}", drm_stream, methods=["GET"])


router.add_api_route("/check_signed_video/", check_signed_video, methods=["POST"])
router.add_api_route("/drm_stream/{video_id}/", drm_stream, methods=["GET"])