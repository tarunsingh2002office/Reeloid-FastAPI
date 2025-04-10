from streaming_app_backend.mongo_client import mintsPlanCollection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def getPackage(request):
    if request.method == "GET":
        try:
            mintsPlanResponse = mintsPlanCollection.find()
           
            mintsPlanList = []
            if not mintsPlanResponse:
                return JsonResponse({"data": []}, status=200)
            for plans in mintsPlanResponse:
                
                plans["_id"] = str(plans.get("_id"))
                mintsPlanList.append(plans)
            return JsonResponse({"mintsPlanList": mintsPlanList}, status=200)
        except Exception as err:
            return JsonResponse({"msg": str(err)}, status=400)
    else:
        return JsonResponse({"msg": "method not allowed"}, status=405)
