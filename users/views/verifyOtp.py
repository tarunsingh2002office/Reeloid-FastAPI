from django.http import JsonResponse
from streaming_app_backend.mongo_client import forgotPasswordRequests, users_collection
from django.utils.timezone import now
from datetime import timedelta
from helper_function.passwordEncryption import passwordEncryption
import json
from django.views.decorators.csrf import csrf_exempt
from helper_function.tokenCreator import tokenCreator


@csrf_exempt
def verifyOtp(request):
    body = json.loads(request.body)

    otp = body.get("otp")  # this is the request for getting already created otp
    try:
        fifteen_min_ago = now() - timedelta(minutes=15)
        existing_Requests = forgotPasswordRequests.find_one_and_update(
            {
                "isUsed": False,
                "otp": int(otp),
                "createdTime": {"$gte": fifteen_min_ago},
                
            },
            {
                "$set": {
                    "isUsed": True,"status": "Pending",
                }
            },
            projection={"_id": True, "userId": True},
        )
        print(existing_Requests)

        if not existing_Requests:
            return JsonResponse(
                {"msg": "No request found for changing otp in previous 15 minutes"},
                status=400,
            )

        return JsonResponse(
            {
                "msg": "otp verified successFully",
                "id": tokenCreator(
                    {
                        "otpId": str(existing_Requests["_id"]),
                        "id": str(existing_Requests["userId"]),
                    }
                ),
            },
            status=200,
        )
    except Exception as err:
        return JsonResponse({"msg": f"{err}"}, status=400)
