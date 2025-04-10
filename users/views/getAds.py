from django.http import JsonResponse
from streaming_app_backend.mongo_client import adsCollection


def getAds(request, path, sessionType):

    if not path:
        return JsonResponse({"msg": "path is not present"}, status=400)
    pathname = f"/{path.lower()}"
    sessionType = sessionType
    if request.method == "GET":
        try:
            adsResponse = adsCollection.find(
                {"position": pathname, "sessionType": sessionType},
                {"type": 1, "sessionType": 1, "provider": 1},
            )

            adsList = []
            if not adsResponse:
                return JsonResponse({"msg": "no data "})
            for ads in adsResponse:

                ads["_id"] = str(ads.get("_id"))
                adsList.append(ads)
            if not adsList:
                return JsonResponse(
                    {"msg": "no ads  data found", "adsList": adsList}, status=200
                )
            return JsonResponse(
                {"msg": "hello getting ads are you ready to fire", "adsList": adsList}
            )
        except:
            return JsonResponse({"msg": "something went wrong"}, status=500)
    else:
        return JsonResponse({"msg": "method not allowed"}, status=400)
