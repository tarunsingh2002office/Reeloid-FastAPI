import hashlib
import time
from urllib.parse import urlparse
from core.config import TENANT_KEY

def check_signed_video(url: str) -> str | None:
    try:
        if not url:
            return None

        # Extract path: e.g. /drm_stream/abc123
        path = urlparse(url).path
        path_parts = path.strip("/").split("/")  # ['drm_stream', 'video_id']

        if len(path_parts) < 2:
            return None

        video_id = path_parts[-1]
        path_to_sign = "/".join(path_parts[:-1]) + "/"

        # Create signature with key + video_id
        key = TENANT_KEY.TENANT_KEY + video_id

        expiry_timestamp = int(time.time()) + 30  # 30-second expiry
        hex_timestamp = hex(expiry_timestamp)[2:]

        signature_raw = f"{key}/{path_to_sign}/{hex_timestamp}"
        signature = hashlib.md5(signature_raw.encode("utf-8")).hexdigest()

        # Return signed URL
        return f"{url}?t={hex_timestamp}&sign={signature}"
    except Exception:
        return None
