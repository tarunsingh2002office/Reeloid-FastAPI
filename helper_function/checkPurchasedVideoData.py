from core.database import videoPurchasedLogs

def checkPurchasedVideoData(videoId, userId):
    try:
        videoData = videoPurchasedLogs.find_one(
            {"shorts_Id": str(videoId), "user_Id": str(userId)}
        )

        if videoData:
            return True

        return False
    except Exception as err:
        raise ValueError("something went wrong in videoPurchasedLogs checking...{err}")
